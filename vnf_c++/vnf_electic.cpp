#include "VNF.H"
#include <fstream>
#include <regex>
#include <sstream>
std::vector<Server> nodelist;
std::vector<Traffic> trafficlist;
std::vector<std::map<int, std::vector<int>>> k_link;
void Loaddata(std::vector<Server> &nodelist,std::vector<Traffic> &trafficlist,std::vector<std::map<int,std::vector<int>>> &k_link){
	ifstream topofile("topofile.txt");
	ifstream trafficfile("trafficfile.txt");
	ifstream k_linkfile("k_link.txt");
	std::string line;
	regex reg1 = ("添加了节点(\\w+),cpu数量为(\\d+),");
	regex reg2 = ("流出节点有:(\\S+)");
	regex reg3 = ("节点(\\w+),距离为(\\d+)，带宽为(\\d+)");
	smatch r1;
	smatch r2;
	smatch r3;
	std::stringstream ss;
	while (getline(topofile,line)){
		std::string text;
		Server node;
		if (regex_search(line,reg1,r1))
		{
			const std:string nodename = r1.str(1);
			ss << r1.str(2);
			ss >> const int cpunum;
			node = Server(nodename,cpunum);
			nodelist.push_back(node);
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
		node::setoutnodedict(outnodedict);
		for (int i = 0; i < count; ++i)
		{
			/* code */
		}
	}
}

int main(int argc, char const *argv[])
{
	/* code */
	return 0;
}