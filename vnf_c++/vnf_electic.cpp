#include "VNF.H"
#include <fstream>
#include <regex>
#include <sstream>
#include <ilcplex/ilocplex.h>
ILOSTLBEGIN
typedef IloArray<IloIntVarArray> IloIntVar2dArray;
typedef IloArray<IloIntVar2dArray> IloIntVar3dArray;
typedef IloArray<IloIntVar3dArray> IloIntVar4dArray;
typedef IloArray<IloIntVar4dArray> IloIntVar5dArray;
typedef IloArray<IloIntVar5dArray> IloIntVar6dArray;
typedef IloArray<IloIntVar6dArray> IloIntVar7dArray;
typedef IloArray<IloIntArray> IloInt2dArray;
typedef IloArray<IloInt2dArray> IloInt3dArray;
typedef IloArray<IloExprArray> IloExpr2dArray;
std::vector<Server> nodelist;
std::vector<Traffic> trafficlist;
std::map<int,std::map<int,std::vector<std::vector<int>>>> k_link;
std::vector<VNF *> &vnf2server;


std::vector<std::string> split(std::string str,std::string pattern)
{
    std::string::size_type pos;
    std::vector<std::string> result;
    str+=pattern;//扩展字符串以方便操作
    int size = str.size();

    for(int i=0; i != size; i++)
    {
        pos=str.find(pattern,i);
        if(pos<size)
        {
            std::string s=str.substr(i,pos-i);
            result.push_back(s);
            i=pos+pattern.size()-1;
        }
    }
    return result;
}

void Loaddata(std::vector<Server> &nodelist,std::vector<Traffic> &trafficlist,std::map<int,std::map<int,std::vector<std::vector<int>>>> &k_link){
	ifstream topofile("topofile.txt");
	ifstream trafficfile("trafficfile.txt");
	ifstream k_linkfile("k_link.txt");
	std::string line;
	std::string splittext1 = ",";
	std::string splittext2 = ";";
	regex reg1 = ("添加了节点(\\w+),cpu数量为(\\d+),");
	regex reg2 = ("流出节点有:(\\S+)");
	regex reg3 = ("节点(\\w+),距离为(\\d+)，带宽为(\\d+)");
	smatch r1;
	smatch r2;
	smatch r3;
	std::stringstream ss;
	std::string text;
	Server *node;
	Traffic *traffic;
	while (getline(topofile,line)){
		if (regex_search(line,reg1,r1))
		{
			const std:string nodename = r1.str(1);
			ss << r1.str(2);
			ss >> const int cpunum;
			node = &Server(nodename,cpunum);
			nodelist.push_back(*node);
		}
		if (regex_search(line,reg2,r2))
		{
			text = r2.str();
		}
		std::map<std::string,std::pair<int,int>> outnodedict;
		for (sregex_iterator it(text.begin(),text.end(),reg3),end;it != end; ++it)
		{
			std::string outnodename = it->str(1);
			ss << it->str(2);
			ss >> int distance;
			ss << it->str(3);
			ss >> int bandwidth;
			outnodedict[outnodename] = make_pair(distance,bandwidth);
		}
		node->setoutnodedict(outnodedict);
	}
	while(getline(trafficfile,line)){
		trafficinf = split(line,splittext1);
		const std::string srcnode = trafficinf[0];
		const std::string dstnode = trafficinf[1];
		ss << trafficinf[2];
		ss >> const int bandwidth;
		std::vector<std::string> vnfsec{"in",trafficinf[3],trafficinf[4],trafficinf[5],"out"};
		traffic = &Traffic(srcnode,dstnode,bandwidth,vnfsec);
		trafficlist.push_back(*traffic);
	}
	while(getline(k_linkfile,line)){
		k_link_inf = spilt(line,splittext2);
		k_link_node = spilt(k_link_inf[0],splittext1);
		ss << k_link_node[0];
		ss >> int u;
		ss << k_link_node[1];
		ss >> int v;
		k_link_1 = spilt(k_link_inf[1],splittext1);
		std::vector<int> k_link_1_int;
		for (std::vector<k_link_1>::iterator i = k_link_1.begin(); i != k_link_1.end(); ++i)
		{
			ss << *it;
			ss >> int k_node;
			k_link_1_int.push_back(k_node);
		}
		k_link_2 = spilt(k_link_inf[2],splittext1);
		std::vector<int> k_link_2_int;
		for (std::vector<k_link_2>::iterator i = k_link_2.begin(); i != k_link_2.end(); ++i)
		{
			ss << *it;
			ss >> int k_node;
			k_link_2_int.push_back(k_node);
		}
		std::vector<std::vector<int>> K_link{k_link_1_int,k_link_2_int};
		if (k_link.count(u) == 0)
		{
			std::map<int,std::vector<std::vector<int>>> V{{v,K_link}};
			k_link[u] = V;	
		}
		else
		{
			k_link[u][v] = K_link;
		}

	}
}
int get_size_of_vnf(std::vector<Server> &nodelist){
	int M;
	for(Server node:nodelist)
	{
		M += node.pesudoweitchdict.size();
	}
	return M;
}
void Vnf_Server(std::vector<Server> &nodelist,std::vector<VNF *> &vnf2server){
	for (auto node : nodelist)
	{
		for (int m = 0; m != node.pesudoweitchdict.size(); ++m)
		{
			vnf2server.push_back(&node.pesudoweitchdict[m]);
		}
	}
}


int main(int argc, char const *argv[])
{
	IloEnv env;
	try 
	{
		Loaddata(nodelist,trafficlist,k_link);
		Vnf_Server(nodelist,vnf2server);
		IloModel model(env);
		IloCplex cplex(model);
		cplex.setparam(IloCplex::DataCheck, 1);
		IloConstraintArray cnst(env);
		IloNumArray pref(env);
		std::vector<string> vnf_type {"in","proxy","firewall","ids","out"};
		std::vector<int> W {1550,1300};
		int K_short_path = 2;
		int middlebox_size = get_size_of_vnf();
		int traffic_size = trafficlist.size();
		//若第 m 个 vnf 是被业务所使用，则 y m =1 ；否则 y m =0
		IloIntVarArray ym(env,middlebox_size,0,1);
		//若第t个业务的第n个网络服务链节点是映射在s上，则为1，否则为0
		IloIntVar3dArray Z_t_n_s(env,traffic_size);
		for (int t = 0; t != traffic_size; ++t)
		{
			Z_t_n_s[t] = IloIntVar2dArray(env,trafficlist[t]->vnfsec.size());
			for (int n = 0; n != trafficlist[t]->vnfsec.size(); ++n)
			{
				Z_t_n_s[t][n] = IloIntVarArray(env,nodelist.size(),0,1);
			}
		}
		IloInt2dArray Amp(env,middlebox_size);
		//若第m个vnf的类型还是属于p时,则为1，否则为0
		for (int m = 0; m != middlebox_size; ++m)
		{
			Amp[m] = IloIntArray(env,vnf_type.size());
			for(int p =0; p != vnf_type.size();++p)
			{
				if(vnf2server[m]->name == vnf_type[p])
				{
					Amp[m][p] = 1;
				}
				else
				{
					Amp[m][p] = 0;
				}
			}
		}
		IloInt3dArray g_t_n_p(env,traffic_size);
		//若第t个业务的第n个网络服务链节点所需的vnf类型为p时，则为1，否则为0
		for (int t = 0; t != traffic_size; ++t)
		{
			g_t_n_p[t] = IloInt2dArray(env,trafficlist[t]->vnfsec.size());
			for (int n = 0; n != trafficlist[t]->vnfsec.size(); ++n)
			{
				g_t_n_p[t][n] = IloIntArray(env,vnf_type.size(),0,1);
				for (int p = 0; p != vnf_type.size(); ++p)
				{
					if (trafficlist[t]->vnfsec[n] == vnf_type[p])
					{
						g_t_n_p[t][n][p] = 1;
					}
					else
					{
						g_t_n_p[t][n][p] = 0;
					}
				}
			}
		}
		IloIntVar3dArray x_t_n_m(env, traffic_size);
		for(int t = 0; t != traffic_size; ++t)
			x_t_n_m[t] = IloIntVar2dArray(env,trafficlist[t]->vnfsec.size());
			for(int n = 0; n != trafficlist[t]->vnfsec.size(); ++n)
			{
				x_t_n_m[t][n] = IloIntVarArray(env,middlebox_size,0,1);
			}
		std::vector<std::vector<std::vector<std::vector<std::map<int,IloIntVar2dArray>>>>> C_t_n1_n2_u_v_k_w;
		C_t_n1_n2_u_v_k_w.reserve(traffic_size);
		for (int t = 0; t != traffic_size; ++t)
		{
			std::vector<std::vector<std::vector<std::map<int,IloIntVar2dArray>>>> traffic;
			C_t_n1_n2_u_v_k_w.push_back(traffic);
			for (int n1 = 0;n1 != trafficlist[t]->vnfsec.size(), ++n1)
			{
				std::vector<std::vector<std::map<int,IloIntVar2dArray>>> n1_vnf;
				C_t_n1_n2_u_v_k_w[t].push_back(n1_vnf);
				int n2 = 0;
				std::vector<std::map<int,IloIntVar2dArray>> n2_vnf;
				C_t_n1_n2_u_v_k_w[t][n1].push_back(n2_vnf);
				for (int u = 0; u != nodelist.size(); ++u)
				{
					std::map<int,IloIntVar2dArray> u_v;
					C_t_n1_n2_u_v_k_w[t][n1][n2].push_back(u_v);
					for (int v = 0; v != nodelist.size(); ++v)
					{
						if (v == u)
						{
							continue;
						}
						else
						{
							C_t_n1_n2_u_v_k_w[t][n1][n2][u][v] = IloIntVar2dArray(env,K_short_path);
							for (int k = 0; k != K_short_path, ++k)
							{
								C_t_n1_n2_u_v_k_w[t][n1][n2][u][v][k] = IloIntVarArray(env,W.size(),0,1);
							}
						}
					}
				}
			}
		}
		IloIntVar2dArray O_u_v(env,nodelist.size());
		for (int u = 0;u != nodelist.size(),++u)
		{
			O_u_v[u] = IloIntVarArray(env,nodelist[u]->outnodedict.size());

		}
		///////////////////////////////////////////////////////
		//                    构造约束                       //
		///////////////////////////////////////////////////////
		// 约束式(1):
		int M = 0;
		for (auto node : nodelist)
		{
			IloExpr cpu_constraints(env);
			for (int m = 0;m != node->pesudoweitchdict.size();++m)
			{
				cpu_constraints +=  ym[M+m]*node->pesudoweitchdict[m].cpu_required;
				model.add(cpu_constraints <= node->cpunum);
			}
			 
		}
		// 约束式(2):
		for (int m =0; m != middlebox_size; ++m)
		{
			IloExpr beta_vnf(env);
			for (int t = 0; t != traffic_size; ++t)
			{
				for (int n = 0; n != trafficlist[t]->vnfsec.size(); ++n)
				{
					beta_vnf += x_t_n_m[t][n][m] * trafficlist[t]->bandwidth;	
				}
			}
			model.add(beta_vnf <= vnf2server[m]->pro_capacity);
		}
		// 约束式(3):
		for (int t = 0; t != traffic_size; ++t)
		{
			for (int n = 0; n != trafficlist[t]->vnfsec.size(); ++n)
			{
				IloExpr Sum3(env);
				for (int m = 0; m != middlebox_size; ++m)
				{
					Sum3 += x_t_n_m[t][n][m];
				}
				model.add(Sum3 == 1);
			}
		}
		// 约束式(4):
		for (int m = 0; m != middlebox_size; ++m)
		{
			IloExpr Sum4(env);
			for (int t = 0; t != traffic_size; ++t)
			{
				for (int n = 0; n != trafficlist[t]->vnfsec.size(); ++n)
				{
					Sum4 += x_t_n_m[t][n][m];
				}
			}
			model.add(ym[m] <= Sum4);
			model.add(Sum4 <= ym[m]*INF);
		}
		// 约束式(5):
		for (int t = 0; t != traffic_size; ++t)
		{
			for (int n = 0; n != trafficlist[t]->vnfsec.size(); ++n)
			{
				for (int m = 0;m != middlebox_size; ++m)
				{
					IloExpr Sum5(env);
					for (int p = 0; p != vnf_type.size(); ++p)
					{
						Sum5 += Amp[m][p] * g_t_n_p[t][n][p];
					}
					model.add(x_t_n_m[t][n][m] <= Sum5);
				}
			}
		}
		// 约束式(6):
		for (int t = 0; t != traffic_size; ++t)
		{
			for (int n = 0; n != trafficlist[t]->vnfsec.size(); ++n)
			{
				int M = 0;
				for (int s = 0; s != nodelist.size(); ++s)
				{
					IloExpr Sum6(env);
					for (int m = M; m != M + nodelist[s]->pesudoweitchdict.size(); ++m)
					{
						Sum6 += x_t_n_m[t][n][m];
					}
					model.add(Sum6 == Z_t_n_s[t][n][s]); 
					M += nodelist[s]->pesudoweitchdict.size();
				}
			}
		}
		// 约束式(7):
		for (int t = 0; t != traffic_size; ++t)
		{
			for (int n1 = 0; n1 != trafficlist[t]->vnfsec.size()-1; ++n1)
			{
				int n2 = 0;
				IloExpr Sum7(env);
				for (int u = 0; u != nodelist.size(); ++u)
				{
					for (int v = 0; v != nodelist.size(); ++v)
					{
						if (v == u)
						{
							continue;
						}
						else
						{
							for (int k = 0; k != K_short_path; ++k)
							{
								for (int w = 0; w != W.size(); ++W)
								{
									Sum7 += C_t_n1_n2_u_v_k_w[t][n1][n2][u][v][k][w];
								}
							}
							model.add(Sum7 <= 1);
						}
					}
				}
			}
		}
		// 约束式(8):
		for (int t  =0; t != traffic_size; ++t)
		{
			for (int n1 = 0; n1 != trafficlist[t]->vnfsec.size()-1; ++n1)
			{
				int n2 = 0;
				for (int u = 0; u != nodelist.size(); ++u)
				{
					for (int k = 0; k != K_short_path; ++k)
					{
						for (int w = 0; w != W.size(); ++w)
						{
							IloExpr Sum9(env);
							for (int v = 0; v != nodelist.size(); ++v)
							{	
								if (v == u)
								{
									continue;
								}
								else
								{
									Sum9 += (C_t_n1_n2_u_v_k_w[t][n1][n2][u][v][k][w] - C_t_n1_n2_u_v_k_w[t][n1][n2][v][u][k][w]);
								}
							}
							model.add(Sum9 == (Z_t_n_s[t][n1][u]-Z_t_n_s[t][n1+1][u]));
						}
					}
				}
			}
		}
		// 约束式(9):
		for (int w = 0; w != W.size(); ++w)
		{
			for (int u = 0; u != nodelist.size(); ++u)
			{
				for (int v = 0; v != nodelist.size(); ++v)
				{
					
				}
			}
		}
	}







	return 0;
}
