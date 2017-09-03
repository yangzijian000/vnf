#ifdef VNF_H
#define VNF_H

#include <string>
#include <map>
#include <vector>
#include <iostream>
#include <utility>
class Traffic
{
public:
	Traffic(const std::string srcnode,const std::string dstnode,const int bandwidth,std::vector<string> vnfsec):
		srcnode(srcnode),dstnode(detnode),bandwidth(bandwidth),vnfsec(vnfsec) { }

private:
	const std::string srcnode;
	const std::string dstnode;
	const int bandwidth;
	std::vector<string> vnfsec;
};
class Server
{
public:
	Server(const string name,const int cpunum):
		nodename(name),cpunum(cpunum) { }
	void setoutnodedict(std::map<std::string, std::pair<std::string, int>> outnodedict) {
		this->outnodedict = outnodedict;
	}
	void setpesudoswitchlist() {
		proxynum = cpunum / 4;
		firewallnum = cpunum / 4;
		idsnum = cpunum / 8;
		pesudoswitchlist.push_back(VNF("in"));
		pesudoswitchlist.push_back(VNF("out"));
		for (int i = 0; i < proxynum; ++i)
		{
			pesudoswitchlist.push_back(VNF("proxy"))
		}
		for (int i = 0; i < firewallnum; ++i)
		{
			pesudoswitchlist.push_back(VNF("firewall"))
		}
		for (int i = 0; i < idsnum; ++i)
		{
			pesudoswitchlist.push_back(VNF("ids"))
		}

	}
private:
	const std::string nodename;
	const std::string cpunum;
	std::map<std::string, std::pair<std::string, int>> outnodedict;
	std::vector<VNF> pesudoswitchlist
				};
class VNF
{
public:
	VNF(const std::string name):
	name(name){
		cpu_dict = {{"in",0},{"proxy",4},{"firewall",4},{"ids",8},{"out",0}};
		band_dict = {{"in",1000000},{"proxy",921600},{"firewall",921600},{"ids",614400},{"out",10000000}};
		cpu_required = cpu_dict[name];
		pro_capacity = band_dict[name];
	}	
private:
	const std::string name;
	std::map<string,int> cpu_dict;
	std::map<str, int> band_dict;
	int cpu_required;
	int pro_capacity;	
};

#endif // VNF_H

