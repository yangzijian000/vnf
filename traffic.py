#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/7/26 15:58
# @Author : YANGz1J
# @Site : 
# @File : traffic.py
# @Software: PyCharm
import re
import docplex
import ksp
from DV import *
from PyQt5 import QtWidgets
from docplex.cp.model import *
class Traffic(object):
    def __init__(self,srcnode,dstnode,bandwidth,vnfsec):
        self.srcnode = srcnode
        self.dstnode = dstnode
        self.bandwidth = bandwidth
        self.vnfsec = vnfsec
class Server(object):
    def __init__(self,name,cpunum):
        self.nodename = name
        self.cpunum = cpunum
        self.pesudoswitchdict = {}
        self.setpesudoswitchdict()
    def setoutnodedict(self,outnodedict):
        self.outnodedict = outnodedict
    def setinnodedict(self,innodedict):
        self.innodedict = innodedict
    def setpesudoswitchdict(self):
        proxynum = int(self.cpunum/4)
        firewallnum = int(self.cpunum/4)
        idsnum = int(self.cpunum/8)
        self.pesudoswitchdict[len(self.pesudoswitchdict)] = Vnf('in')
        self.pesudoswitchdict[len(self.pesudoswitchdict)] = Vnf('out')
        for i in range(len(self.pesudoswitchdict),len(self.pesudoswitchdict)+proxynum):
            self.pesudoswitchdict[i] = Vnf('proxy')
        for i in range(len(self.pesudoswitchdict),len(self.pesudoswitchdict)+firewallnum):
            self.pesudoswitchdict[i] = Vnf('firewall')
        for i in range(len(self.pesudoswitchdict),len(self.pesudoswitchdict)+idsnum):
            self.pesudoswitchdict[i] = Vnf('ids')
class Vnf(object):
    def __init__(self,name):
        self.name = name
        self.id_dict = {'in':0,'proxy':1,'firewall':2,'ids':3,'out':4}
        self.cpu_dict = {'in':0,'proxy':4,'firewall':4,'ids':8,'out':0}
        self.band_dict = {'in':10000000000000000,'proxy':921600,'firewall':921600,'ids':614400,
                          'out':10000000000000000}
        self.id = self.id_dict[name]
        self.cpu_required = self.cpu_dict[name]
        self.pro_capacity = self.band_dict[name]

# class pesudoswitch(object):
#     def __init__(self,vnf):
#         self.vnf = vnf
# class Topo(object):
#     def __init__(self,nodelist,nodenum):
#         self.nodelist = nodelist
#         for i in range(0,nodenum):
#             servernode = Server(i,16)
#             self.nodelist[i] = servernode
#             servernode.setinnodelist()
class MainWindow(Ui_MainWindow,QtWidgets.QMainWindow):
        def __init__(self):
            super(MainWindow, self).__init__()
            self.setupUi(self)
            self.setUI()
            self.nodelist = []
            self.trafficlist = []
        def setUI(self):
            self.addrouterButton.clicked.connect(self.addrouterButtonclicked)
            # self.startButton.clicked.connect(self.startButtonclicked)
            # self.loaddataButton.clicked.connect(self.loaddataButtonclicked)


        def addrouterButtonclicked(self):
            try:
                nodeinf = self.nodeinf.text()
                pattert = re.compile(r'(\w+):(\d+)')
                matchs = pattert.search(nodeinf)
                nodename = matchs.group(1)
                node_cpu_num = int(matchs.group(2))
                node = Server(nodename,node_cpu_num)
                innodeinf = self.innodeinf.text()
                pattert = re.compile(r'(\w+):(\d+):(\d+)')
                matchs = pattert.findall(innodeinf)
                innodedict = {}
                for match in matchs:
                    innodedict[match[0]] = [int(match[1]),int(match[2])]
                node.setinnodedict(innodedict)
                outnodeinf = self.outnodeinf.text()
                pattert = re.compile(r'(\w+):(\d+):(\d+)')
                matchs = pattert.findall(outnodeinf)
                outnodedict = {}
                for match in matchs:
                    outnodedict[match[0]] = [int(match[1]),int(match[2])]
                node.setoutnodedict(outnodedict)
                self.nodelist.append(node)
                routerdata = '添加了节点{},cpu数量为{},流入节点有:'.format(node.nodename,node.cpunum)
                for innode in node.innodedict.keys():
                    routerdata += '节点{},距离为{}，带宽为{};'.format(innode,node.innodedict[innode][0],node.innodedict[innode][1])
                routerdata += '流出节点有:'
                for outnode in node.outnodedict.keys():
                    routerdata += '节点{},距离为{}，带宽为{};'.format(outnode,node.outnodedict[outnode][0],node.outnodedict[outnode][1])
                self.routerdate.append(routerdata)
            except:
                self.routerdate.append('添加错误，请重新添加！')
        def initTopo(self):
            self.topoinfdict = {}
            for node in self.nodelist:
                self.topoinfdict[node.nodename] = {}
                for outnode,[distance,bandwitch] in node.outnodedict.items():
                    self.topoinfdict[node.nodename][outnode] = [distance,bandwitch]


        def getlenforvnf(self):
            cnt = 0
            for node in self.nodelist:
                cnt += len(node.pesudoswitchdict)
            return cnt
        def run_cplex(self):
            self.Vnf2server()
            P = ['in','proxy','firewall','ids','out']
            W = [1550,1300]#光路可选用波长的集合
            mdl = CpoModel()
            ym = integer_var_list(self.getlenforvnf(),0,1,'ym')
            #若第 m 个 vnf 是被业务所使用，则 y m =1 ；否则 y m =0
            Z_t_n_s = []
            # 若第t个业务的第n个网络服务链节点是映射在s上，则为1，否则为0
            for i,t in enumerate(self.trafficlist):
                Z_t_n_s.append([])
                for vnf in t.vnfsec:
                    Z_t_n_s[i].append(integer_var_list(len(self.nodelist),0,1,'Z_t_n_s'))
            Amp = []
            # 若第m个vnf的类型还是属于p时,则为1，否则为0
            for m in range(self.getlenforvnf()):
                Amp.append([])
                for p in P:
                    if self.vnf2server[m].name == p:
                        Amp[m].append(1)
                    else:
                        Amp[m].append(0)
            g_t_n_p = []
            # 若第t个业务的第n个网络服务链节点所需的vnf类型为p时，则为1，否则为0
            for t,traffic in enumerate(self.trafficlist):
                g_t_n_p.append([])
                for n,vnf in enumerate(traffic.vnfsec):
                    g_t_n_p[t].append([])
                    for p in P:
                        if vnf.name == p:
                            g_t_n_p[t][n].append(1)
                        else:g_t_n_p[t][n].append(0)
            x_t_n_m = []
            for i,t in enumerate(self.trafficlist):
                x_t_n_m.append([])
                for vnf in t.vnfsec:
                    x_t_n_m[i].append(integer_var_list(self.getlenforvnf(),0,1,'x_t_n_m'))
            # w_t_n1_n2_u_v = []
            # for t,traffic in enumerate(self.trafficlist):
            #     w_t_n1_n2_u_v.append([])
            #     for n1,vnf in enumerate(traffic.vnfsec):
            #         if vnf.name == 'out':
            #             continue
            #         w_t_n1_n2_u_v[t].append([])
            #         for n2,n1_vnf in enumerate(traffic.vnfsec[n1+1:n1+2]):
            #             w_t_n1_n2_u_v[t][n1].append([])
            #             for u,node_u in enumerate(self.nodelist):
            #                 w_t_n1_n2_u_v[t][n1][n2].append([])
            #                 w_t_n1_n2_u_v[t][n1][n2][u].append(integer_var_list(len(self.nodelist),0,1,'w_t_n1_n2_u_v'))

            C_t_n1_n2_u_v_w = []
            for t,traffic in enumerate(self.trafficlist):
                C_t_n1_n2_u_v_w.append([])
                for n1,vnf in traffic.vnfsec:
                    if vnf.name == 'out':
                        continue
                    C_t_n1_n2_u_v_w[t].append([])
                    for n2,n1_vnf in enumerate(traffic.vnfsec[n1+1]):
                        C_t_n1_n2_u_v_w[t][n1].append([])
                        for u,node_u in enumerate(self.nodelist):
                            C_t_n1_n2_u_v_w[t][n1][n2].append([])
                            for v,node_v in enumerate(node_u.outnodedict.keys()):
                                C_t_n1_n2_u_v_w[t][n1][n2][u].append([])
                                C_t_n1_n2_u_v_w[t][n1][n2][u][v].append(integer_var_list(len(W),0,1,'C_t_n1_n2_u_v_w'))
            O_u_v = []
            for u,node_u in enumerate(self.nodelist):
                O_u_v.append([])
                O_u_v[u].append(integer_var_list(len(node_u.outnodedict),0,1,'O_u_v'))
        ###################################################
        #                     构建约束                     #
        ###################################################
        #约束式(1):
            M = 0
            for n,node in enumerate(self.nodelist):
                cpu_constraints = [times(ym[M+m],vnf.cpu_required) for m,vnf in node.pesudoswitchdict.items()]
                mdl.add(mdl.sum(cpu_constraints)<=node.cpunum)
                M += len(node.pesudoswitchdict)
        # 约束式(2):
            for m in range(self.getlenforvnf()):
                beta_vnf = []
                for t,traffic in self.trafficlist:
                    for n,traffic_node in enumerate(traffic.vnfsec):
                        beta_vnf.append(times(x_t_n_m[t][n][m],traffic.bandwidth))
                mdl.add(mdl.sum(beta_vnf)<=self.vnf2server[m].pro_capacity)
        # 约束式(3):
            for t,traffic in enumerate(self.trafficlist):
                for n, traffic_node in enumerate(traffic.vnfsec):
                    Sum = [x_t_n_m[t][n][m] for m in range(self.getlenforvnf())]
                    mdl.add(mdl.sum(Sum)==1)
        # 约束式(4):
            for m in range(self.getlenforvnf()):
                Sum = []
                for t,traffic in enumerate(self.trafficlist):
                    for n, traffic_node in enumerate(traffic.vnfsec):
                        Sum.append(x_t_n_m[t][n][m])
                mdl.add(ym[m]<=mdl.sum(Sum)<=ym[m]*INFINITY)
        # 约束式(5):
            for t,traffic in enumerate(self.trafficlist):
                for n, traffic_node in enumerate(traffic.vnfsec):
                    for m in range(self.getlenforvnf()):
                        Sum = [Amp[m][p]*g_t_n_p[t][n][p] for p,vnf_type in enumerate(P)]
                        mdl.add(x_t_n_m[t][n][m]<=mdl.sum(Sum))
        # 约束式(6):
            for t,traffic in enumerate(self.trafficlist):
                for n1, vnf in traffic.vnfsec:
                    for n2, n1_vnf in enumerate(traffic.vnfsec[n1 + 1]):
                        for u,node_u in enumerate(self.nodelist):
                            for v, node_v in enumerate(node_u.outnodedict.keys()):
                                Sum = [C_t_n1_n2_u_v_w[t][n1][n2][u][v][w] for w,wave in W]
                                mdl.add(mdl.sum(Sum)<=1)
        # 约束式(7):
            for w,wave in enumerate(W):
                for u, node_u in enumerate(self.nodelist):
                    for v, node_v in enumerate(node_u.outnodedict.keys()):
                        Sum = []
                        beta_u_v_w = int(node_u.outnodedict[node_v][1])
                        for t, traffic in enumerate(self.trafficlist):
                            for n1, vnf in traffic.vnfsec:
                                for n2, n1_vnf in enumerate(traffic.vnfsec[n1 + 1]):
                                    Sum.append(times(C_t_n1_n2_u_v_w[t][n1][n2][u][v][w],traffic.bandwidth))
                        mdl.add(mdl.sum(Sum)<= beta_u_v_w)
        #约束式(8):
            for u, node_u in enumerate(self.nodelist):
                for v, node_v in enumerate(node_u.outnodedict.keys()):
                    Sum = []
                    for t,traffic in enumerate(self.trafficlist):
                        for n1, vnf in traffic.vnfsec:
                            for n2, n1_vnf in enumerate(traffic.vnfsec[n1 + 1]):
                                for w,wave in enumerate(W):
                                    Sum.append(C_t_n1_n2_u_v_w[t][n1][n2][u][v][w])
                    mdl.add(O_u_v[u][v]<=mdl.sum(Sum)<=O_u_v[u][v]*INFINITY)
        # 约束式(9):
            
        def Vnf2server(self):
            self.vnf2server ={}
            M = 0
            for n,node in enumerate(self.nodelist):
                for m in range(M,M + len(node.pesudoswitchdict)):
                    self.vnf2server[m] = node.pesudoswitchdict[m-M]
                M += len(node.pesudoswitchdict)
        def K_shortest_path(self,srcnode,dstnode):
            paths = ksp.yen_ksp(self.topoinfdict,srcnode,dstnode,2)

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec_())