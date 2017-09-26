#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/7/26 15:58
# @Author : YANGz1J
# @Site : 
# @File : traffic.py
# @Software: PyCharm
import re
import docplex
import vnf.ksp as ksp
from vnf.DV import *
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
            self.topofile = open('topofile.txt', 'w')
        def setUI(self):
            self.addrouterButton.clicked.connect(self.addrouterButtonclicked)
            self.startButton.clicked.connect(self.startButtonclicked)
            self.loaddataButton.clicked.connect(self.loaddataButtonclicked)


        def addrouterButtonclicked(self):
            try:
                nodeinf = self.nodeinf.text()
                pattert = re.compile(r'(\w+):(\d+)')
                matchs = pattert.search(nodeinf)
                nodename = matchs.group(1)
                node_cpu_num = int(matchs.group(2))
                node = Server(nodename,node_cpu_num)
                outnodeinf = self.outnodeinf.text()
                pattert = re.compile(r'(\w+):(\d+):(\d+)')
                matchs = pattert.findall(outnodeinf)
                outnodedict = {}
                for match in matchs:
                    outnodedict[match[0]] = [int(match[1]),int(match[2])]
                node.setoutnodedict(outnodedict)
                self.nodelist.append(node)
                routerdata = '添加了节点{},cpu数量为{},'.format(node.nodename,node.cpunum)
                routerdata += '流出节点有:'
                for outnode in node.outnodedict.keys():
                    routerdata += '节点{},距离为{}，带宽为{};'.format(outnode,node.outnodedict[outnode][0],node.outnodedict[outnode][1])
                self.routerdate.append(routerdata)
                self.topofile.write(routerdata+'\r\n')
            except:
                self.routerdate.append('添加错误，请重新添加！')
        def initTopo(self):
            self.topoinfdict = {}
            for node in self.nodelist:
                self.topoinfdict[str(node.nodename)] = {}
                for outnode,[distance,bandwitch] in node.outnodedict.items():
                    self.topoinfdict[str(node.nodename)][outnode] = [distance,bandwitch]
        def startButtonclicked(self):
            try:
                self.topofile.close()
                self.initTopo()
                for t in range(10, 160, 10):
                    trafficsize = t
                    self.Loadtrafficfile(trafficsize)
                    self.run_cplex_electic()
            except Exception as e:
                print(e)
        def loaddataButtonclicked(self):
            self.nodelist.clear()
            topofile = open('新建文本文档.txt','r')
            pattern1 = re.compile(r'添加了节点(\w+),cpu数量为(\d+),')
            pattern3 = re.compile(r'流出节点有:(\S+)')
            for line in topofile:
                matchs1 = pattern1.search(line)
                if matchs1:
                    nodename = int(matchs1.group(1))
                    cpunum = int(matchs1.group(2))
                    node = Server(nodename, cpunum)
                    matchs2 = pattern3.search(line)
                    pattern4 = re.compile(r'节点(\w+),距离为(\d+),带宽为(\d+)')
                    matchs3 = pattern4.findall(matchs2.group())
                    outnodedict = {}
                    for match in matchs3:
                        outnodedict[match[0]] = [int(match[1]), int(match[2])]
                    node.setoutnodedict(outnodedict)
                    self.nodelist.append(node)
                    self.routerdate.append('读取日志成功！')
                    routerdata = '添加了节点{},cpu数量为{},'.format(node.nodename, node.cpunum)
                    routerdata += '流出节点有:'
                    for outnode in node.outnodedict.keys():
                        routerdata += '节点{},距离为{}，带宽为{};'.format(outnode, node.outnodedict[outnode][0],
                                                                 node.outnodedict[outnode][1])
                    self.routerdate.append(routerdata)
            topofile.close()




        def getlenforvnf(self):
            cnt = 0
            for node in self.nodelist:
                cnt += len(node.pesudoswitchdict)
            return cnt
        def run_cplex_electic(self):
            self.Vnf2server()
            self.initlink()
            P = ['in','proxy','firewall','ids','out']
            mdl = CpoModel(name='Step_one')
            ym = [mdl.integer_var(0,1,name='ym_{}'.format(m)) for m in range(self.getlenforvnf())]
            #若第 m 个 vnf 是被业务所使用，则 y m =1 ；否则 y m =0
            Z_t_n_s = []
            # 若第t个业务的第n个网络服务链节点是映射在s上，则为1，否则为0
            for t,traffic in enumerate(self.trafficlist):
                Z_t_n_s.append([])
                for n,vnf in enumerate(traffic.vnfsec):
                    Z_t_n_s[t].append([mdl.integer_var(0,1,name='Z_t_n_s_{}_{}_{}'.format(t,n,s)) for s in range(len(self.nodelist))])
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
                        if vnf == p:
                            g_t_n_p[t][n].append(1)
                        else:g_t_n_p[t][n].append(0)
            x_t_n_m = []
            for t,traffic in enumerate(self.trafficlist):
                x_t_n_m.append([])
                for n,vnf in enumerate(traffic.vnfsec):
                    x_t_n_m[t].append([mdl.integer_var(0,1,name='x_t_n_m_{}_{}_{}'.format(t,n,m)) for m in range(self.getlenforvnf())])


            # W_t_n1_n2_u_v_w = []
            # for t,traffic in enumerate(self.trafficlist):
            #     W_t_n1_n2_u_v_w.append([])
            #     for n1,vnf in enumerate(traffic.vnfsec):
            #         if vnf.name == 'out':
            #             continue
            #         W_t_n1_n2_u_v_w[t].append([])
            #         for n2,n1_vnf in enumerate(traffic.vnfsec[n1+1:n1+2]):
            #             W_t_n1_n2_u_v_w[t][n1].append([])
            #             for u,node_u in enumerate(self.nodelist):
            #                 W_t_n1_n2_u_v_w[t][n1][n2].append([])
            #                 W_t_n1_n2_u_v_w[t][n1][n2][u].append(mdl.integer_var_list(len(self.nodelist),0,1,'W_t_n1_n2_u_v_w'))

            # C_t_n1_n2_u_v = []
            # try:
            #     for t,traffic in enumerate(self.trafficlist):
            #         C_t_n1_n2_u_v.append([])
            #         for n1,vnf in enumerate(traffic.vnfsec):
            #             if vnf == 'out':
            #                 continue
            #             C_t_n1_n2_u_v[t].append([])
            #             for n2,n1_vnf in enumerate([traffic.vnfsec[n1+1]]):
            #                 C_t_n1_n2_u_v[t][n1].append([])
            #                 for u,node_u in enumerate(self.nodelist):
            #                     C_t_n1_n2_u_v[t][n1][n2].append([])
            #                     for v,node_v in enumerate(self.nodelist):
            #                         if v == u:
            #                             continue
            #                         C_t_n1_n2_u_v[t][n1][n2][u][v] = mdl.integer_var(0,1,name='C_t_n1_n2_u_v_{}_{}_{}_{}_{}'.format(t,n1,n2,u,v))
            # except Exception as e:
            #     print(e)
            # O_u_v = []
            # for u,node_u in enumerate(self.nodelist):
            #     O_u_v.append([mdl.integer_var(0,1,name='O_u_v_{}_{}'.format(u,node_v)) for v,node_v in enumerate(node_u.outnodedict.keys())])
            # W_t_n1_n2_U_V_u_v_w = []
            # try:
            #     for t,traffic in enumerate(self.trafficlist):
            #         W_t_n1_n2_U_V_u_v_w.append([])
            #         for n1,vnf in enumerate(traffic.vnfsec):
            #             if vnf == 'out':
            #                 continue
            #             W_t_n1_n2_U_V_u_v_w[t].append([])
            #             for n2,n1_vnf in enumerate([traffic.vnfsec[n1+1]]):
            #                 W_t_n1_n2_U_V_u_v_w[t][n1].append([])
            #                 for U,node_U in enumerate(self.nodelist):
            #                     W_t_n1_n2_U_V_u_v_w[t][n1][n2].append([])
            #                     for V, node_V in enumerate(self.nodelist):
            #                         W_t_n1_n2_U_V_u_v_w[t][n1][n2][U].append([])
            #                         for u,node_u in enumerate(self.nodelist):
            #                             W_t_n1_n2_U_V_u_v_w[t][n1][n2][U][V].append([])
            #                             for v,node_v in enumerate(node_u.outnodedict.keys()):
            #                                 W_t_n1_n2_U_V_u_v_w[t][n1][n2][U][V][u].append([mdl.integer_var(0,1,name='W_t_n1_n2_U_V_u_v_w_{}_{}_{}_{}_{}_{}_{}_{}'.format(t,n1,n1+1,U,V,u,node_v,w)) for w,wave in enumerate(W) ])
            # except Exception as e:
            #     print(e)

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
            try:
                for m in range(self.getlenforvnf()):
                    beta_vnf = [(times(x_t_n_m[t][n][m],int(traffic.bandwidth))) for t,traffic in enumerate(self.trafficlist) for n,traffic_node in enumerate(traffic.vnfsec)]
                    mdl.add(mdl.sum(beta_vnf)<=self.vnf2server[m].pro_capacity)
            except Exception as e:
                print(e)
        # 约束式(3):
            try:
                for t,traffic in enumerate(self.trafficlist):
                    for n, traffic_node in enumerate(traffic.vnfsec):
                        Sum_3 = [x_t_n_m[t][n][m] for m in range(self.getlenforvnf())]
                        mdl.add(mdl.sum(Sum_3)==1)
            except Exception as e:
                print(e)
        # 约束式(4):
            try:
                for m in range(self.getlenforvnf()):
                    Sum_4 = mdl.sum([x_t_n_m[t][n][m] for t,traffic in enumerate(self.trafficlist) for n, traffic_node in enumerate(traffic.vnfsec)])
                    mdl.add(ym[m] <= Sum_4)
                    mdl.add(Sum_4 <= ym[m] * 9999999)
            except Exception as e:
                print(e)
        # 约束式(5):
        #     a = mdl.get_all_expressions()
        #     print(a)
            try:
                for t,traffic in enumerate(self.trafficlist):
                    for n, traffic_node in enumerate(traffic.vnfsec):
                        for m in range(self.getlenforvnf()):
                            Sum5 = [Amp[m][p]*g_t_n_p[t][n][p] for p,vnf_type in enumerate(P)]
                            mdl.add(x_t_n_m[t][n][m]<=sum(Sum5))
            except Exception as e:
                print(e)
        # 约束式(6):
            try:
                for t,traffic in enumerate(self.trafficlist):
                    for n, traffic_node in enumerate(traffic.vnfsec):
                        M = 0
                        for s,node_s in enumerate(self.nodelist):
                            Sum6 = [x_t_n_m[t][n][m] for m in range(M,M+len(node_s.pesudoswitchdict))]
                            mdl.add(mdl.sum(Sum6)==Z_t_n_s[t][n][s])
                            M += len(node_s.pesudoswitchdict)
            except Exception as e:
                print(e)
        # 约束式(7),(8):
        #     try:
        #         for t,traffic in enumerate(self.trafficlist):
        #             for n1, vnf in enumerate(traffic.vnfsec):
        #                 if vnf =='out':
        #                     continue
        #                 for n2, n1_vnf in enumerate([traffic.vnfsec[n1 + 1]]):
        #                     Sum_7 = []
        #                     for u,node_u in enumerate(self.nodelist):
        #                         for v, node_v in enumerate(self.nodelist):
        #                             if v == u:
        #                                 continue
        #                             for k in range(K_short_path):
        #                                 for w,wave in enumerate(W):
        #                                     Sum_7.append(C_t_n1_n2_u_v_k[t][n1][n2][u][v][k][w])
        #                     mdl.add(mdl.sum(Sum_7) <= 1)
        #     except Exception as e:
        #         print(e)
        #约束式(9):
            # try:
            #     for t, traffic in enumerate(self.trafficlist):
            #         for n1, vnf in enumerate(traffic.vnfsec):
            #             if vnf =='out':
            #                 continue
            #             for n2, n1_vnf in enumerate([traffic.vnfsec[n1 + 1]]):
            #                 for u, node_u in enumerate(self.nodelist):
            #                     Sum_9 = [minus(C_t_n1_n2_u_v[t][n1][n2][u][v],C_t_n1_n2_u_v[t][n1][n2][node_v.nodename][node_u.nodename]) for v,node_v in enumerate(self.nodelist) if v != u]
            #                     mdl.add(mdl.sum(Sum_9)==minus(Z_t_n_s[t][n1][u],Z_t_n_s[t][n1+1][u]))
            #                     for v,node_v in enumerate(self.nodelist):
            #                         if v == u:
            #                             continue
            #                         Sum_10 = C_t_n1_n2_u_v[t][n1][n2][u][v]+C_t_n1_n2_u_v[t][n1][n2][v][u]
            #                         mdl.add(Sum_10 <= 1)
            # except Exception as e:
            #     print(e)
        # 约束式(10):
        #     try:
        #         for w,wave in enumerate(W):
        #             for u, node_u in enumerate(self.nodelist):
        #                 for v, node_v in enumerate(self.nodelist):
        #                     if v == u:
        #                         continue
        #                     for k in range(K_short_path):
        #                         Sum_10 = []
        #                         beta_u_v_k_w = self.compute_beta_u_v_k(u,v,k)
        #                         for t, traffic in enumerate(self.trafficlist):
        #                             for n1, vnf in enumerate(traffic.vnfsec):
        #                                 if vnf == 'out':
        #                                     continue
        #                                 for n2, n1_vnf in enumerate([traffic.vnfsec[n1 + 1]]):
        #                                     Sum_10.append(times(C_t_n1_n2_u_v_k[t][n1][n2][u][v][k][w],int(traffic.bandwidth)))
        #                         mdl.add(mdl.sum(Sum_10)<= beta_u_v_k_w)
        #     except Exception as e:
        #         print(e)
        #约束式(11):
            # try:
            #     for u, node_u in enumerate(self.nodelist):
            #         for v, node_v in enumerate(node_u.outnodedict.keys()):
            #             Sum_11 = []
            #             for U,node_U in enumerate(self.nodelist):
            #                 for V,node_V in enumerate(self.nodelist):
            #                     if V == U:
            #                         continue
            #                     if self.link_map_uv(str(U),str(V),str(u),str(node_v)):
            #                         t = 0
            #                         K = self.link_map_uv(str(U),str(V),str(u),str(node_v))
            #                         while t < len(self.trafficlist):
            #                             for n1, vnf in enumerate(self.trafficlist[t].vnfsec):
            #                                 if vnf == 'out':
            #                                     continue
            #                                 for n2, n1_vnf in enumerate([self.trafficlist[t].vnfsec[n1 + 1]]):
            #                                     for k in K:
            #                                         for w,wave in enumerate(W):
            #                                             Sum_11.append(C_t_n1_n2_u_v_k[t][n1][n2][U][V][k][w])
            #                             t += 1
            #             mdl.add(O_u_v[u][v]<=mdl.sum(Sum_11)<=O_u_v[u][v]*999999)
            # except Exception as e:
            #     print(e)
        # 约束式(12):
        #用于约束业务的入口与出口的位置
            try:
                for t,traffic in enumerate(self.trafficlist):
                    src = int(traffic.srcnode)
                    dst = int(traffic.dstnode)
                    ingress = 0
                    egress = len(traffic.vnfsec)-1
                    mdl.add(Z_t_n_s[t][ingress][src]==1)
                    mdl.add(Z_t_n_s[t][egress][dst]==1)
            except Exception as e:
                print(e)
        # 约束式(13):
        # 链路使用约束
        #     try:
        #         for t,traffic in enumerate(self.trafficlist):
        #             for n1, vnf in enumerate(traffic.vnfsec):
        #                 if vnf =='out':
        #                     continue
        #                 for n2, n1_vnf in enumerate([traffic.vnfsec[n1 + 1]]):
        #                     for U,node_U in enumerate(self.nodelist):
        #                         for V, node_V in enumerate(self.nodelist):
        #                             for k in range(K_short_path):
        #                                 for u, node_u in enumerate(self.nodelist):
        #                                     for v, node_v in enumerate(node_u.outnodedict.keys()):
        #                                         paths = self.K_shortest_path(str(node_U.nodename),str(node_V.nodename))
        #                                         if paths:
        #                                             path = paths[k]
        #                                             node_of_paths = self.node_of_paths(paths)
        #                                             if str(node_u.nodename) in node_of_paths and node_v in node_of_paths:
        #                                                 for i in range(len(path)-1):
        #                                                     if path[i] in paths[1-k] and path[i+1] in paths[1-k]:
        #                                                         mdl.add(mdl.sum([W_t_n1_n2_U_V_u_v_w[t][n1][n2][U][V][int(path[i])][self.uv2vu(path[i],path[i+1])][w] for w,wave in enumerate(W)])==mdl.sum([C_t_n1_n2_u_v_k[t][n1][n2][U][V][K] for K in range(K_short_path)]))
        #                                                     else:
        #                                                         mdl.add(mdl.sum([W_t_n1_n2_U_V_u_v_w[t][n1][n2][U][V][int(path[i])][self.uv2vu(path[i],path[i+1])][w] for w,wave in enumerate(W)])==C_t_n1_n2_u_v_k[t][n1][n2][U][V][k])
        #                                             else:
        #                                                 mdl.add(mdl.sum(
        #                                                     [W_t_n1_n2_U_V_u_v_w[t][n1][n2][U][V][u][v][w] for w, wave in
        #                                                      enumerate(W)]) == 0)
        #                                         else:
        #                                             mdl.add(mdl.sum([W_t_n1_n2_U_V_u_v_w[t][n1][n2][U][V][u][v][w] for w,wave in enumerate(W)])==0)
        #         for t, traffic in enumerate(self.trafficlist):
        #             for n1, vnf in enumerate(traffic.vnfsec):
        #                 if vnf == 'out':
        #                     continue
        #                 for n2, n1_vnf in enumerate([traffic.vnfsec[n1 + 1]]):
        #                     for U,node_U in enumerate(self.nodelist):
        #                         for V, node_V in enumerate(self.nodelist):
        #                             for u, node_u in enumerate(self.nodelist):
        #                                 for v,node_v in enumerate(node_u.outnodedict.keys()):
        #                                     Sum = [W_t_n1_n2_U_V_u_v_w[t][n1][n2][U][V][u][v][w] for w,wave in enumerate(W)]
        #                                     mdl.add(mdl.sum(Sum)<=1)
        #     except Exception as e:
        #         print(e)
    #目标函数:
        # P_t：路由器进行光-电-光转换的能耗
        # P_I：路由器转发1Gps流量的能耗
        # Sum_O：为承载业务所构建的光路使用的物理链路的总数
        # Sum_B：路由器转发的流量数的总和
        #     try:
        #         P_t = 35
        #         P_I = 0.000015
        #         Sum_B = []
        #         for t, traffic in enumerate(self.trafficlist):
        #             Sum_t_B = []
        #             beat_t = int(traffic.bandwidth)
        #             for n1, vnf in enumerate(traffic.vnfsec):
        #                 if vnf =='out':
        #                     continue
        #                 for n2, n1_vnf in enumerate([traffic.vnfsec[n1 + 1]]):
        #                     for U,node_U in enumerate(self.nodelist):
        #                         for V, node_V in enumerate(self.nodelist):
        #                             if V == U:
        #                                 continue
        #                             for k in range(K_short_path):
        #                                 for w,wave in enumerate(W):
        #                                     paths = self.K_shortest_path(str(U),str(V))
        #                                     if paths:
        #                                         link_num = len(paths[k])-1
        #                                         Sum_t_B.append(times(times(C_t_n1_n2_u_v_k[t][n1][n2][U][V][k][w],beat_t),link_num))
        #                                     else:
        #                                         link_num = 0
        #                                         Sum_t_B.append(times(times(C_t_n1_n2_u_v_k[t][n1][n2][U][V][k][w], beat_t),link_num))
        #             Sum_B.append(mdl.sum(Sum_t_B)-beat_t)
        #         Sum_O = []
        #         for u, node_u in enumerate(self.nodelist):
        #             for v, node_v in enumerate(node_u.outnodedict.keys()):
        #                 Sum_O.append(O_u_v[u][v])
        #         obj = 2*P_t*mdl.sum(Sum_O)+P_I*mdl.sum(Sum_B)
        #         mdl.add(mdl.minimize(obj))
        #     except Exception as e:
        #         print(e)
        #修改：分两步计算，第一步目标优化使得激活节点数最少：
            # y_t_s = [[mdl.integer_var(0, 1, name='y_t_s_{}_{}'.format(t,s)) for s, node_s in enumerate(self.nodelist)] for t,traffic in enumerate(self.trafficlist)]
            # try:
            #     for s,node_s in enumerate(self.nodelist):
            #         for t, traffic in enumerate(self.trafficlist):
            #             Sum_s = mdl.sum([Z_t_n_s[t][n][s]  for n in range(len(traffic.vnfsec))])
            #             mdl.add(y_t_s[t][s] <= Sum_s)
            #             mdl.add(Sum_s  <= y_t_s[t][s] * 9999999)



            # try:
            #     for u,node_u in enumerate(self.nodelist):
            #         for t,traffic in enumerate(self.trafficlist):
            #             for n,vnf in enumerate(traffic.vnfsec):
            #                 if vnf == 'out':
            #                     continue
            #                 for v, node_v in enumerate(self.nodelist):
            #                     if v == u:
            #                         continue
            #                     paths = self.K_shortest_path(str(u),str(v))
            #
            #                     obj.append(Z_t_n_s[t][n][u])

            obj = mdl.sum(ym[m] for m in range(self.getlenforvnf()))
            mdl.add(mdl.minimize(obj))
            # except Exception as e:
            #     print(e)

            ##############################################################################
            # Model solving
            ##############################################################################
            # Solve model

            try:
                resultfile = open('random_result_{}.txt'.format(len(self.trafficlist)), 'w')
                resultfile.write("Solving model....")
                resultfile.write('\r\n')
                msol = mdl.solve(TimeLimit = 600)
                resultfile.write("Solution: ")
                resultfile.write('\r\n')
                if msol:
                    resultfile.write('第一阶段优化完成:')
                    resultfile.write('\r\n')
                    active_node_num = []
                    for m in range(self.getlenforvnf()):
                        Ym = msol.get_value(ym[m])
                        if Ym == 1:
                            active_node_num.append(m)
                    resultfile.write('总激活vnf数为:{}'.format(len(active_node_num)))
                    resultfile.write('\r\n')
                    for m in active_node_num:
                        resultfile.write('第{}个vnf节点处于激活状态'.format(m))
                        resultfile.write('\r\n')
                # path_t = {}
                # for s,node_s in enumerate(self.nodelist):
                #     YS = msol.get_value(ys[s])
                #     print('ys[{}]={}'.format(s,YS))
                self.Z_t_n_s = []
                for t,traffic in enumerate(self.trafficlist):
                    self.Z_t_n_s.append({})
                    for n,vnf in enumerate(traffic.vnfsec):
                        for s,node in enumerate(self.nodelist):
                            Z = msol.get_value(Z_t_n_s[t][n][s])
                            if Z == 1:
                                self.Z_t_n_s[t][n] = s
                                resultfile.write('业务{}的第{}个vnf：{}部署在服务器{}上。'.format(t,n,vnf,s))
                                resultfile.write('\r\n')
                        for m in range(self.getlenforvnf()):
                            X = msol.get_value(x_t_n_m[t][n][m])
                            if X == 1:
                                resultfile.write('业务{}的第{}个vnf：{}使用了第{}个vnf节点'.format(t,n,vnf,m))
                                resultfile.write('\r\n')
                # for t, traffic in enumerate(self.trafficlist):
                #     path_t[t] = []
                #     for n1, vnf in enumerate(traffic.vnfsec):
                #         if vnf == 'out':
                #             continue
                #         for n2, n1_vnf in enumerate([traffic.vnfsec[n1 + 1]]):
                #             for u, node_u in enumerate(self.nodelist):
                #                 for v, node_v in enumerate(self.nodelist):
                #                     if v == u:
                #                         continue
                #                     for k in range(K_short_path):
                #                         for w,wave in enumerate(W):
                #                             C = msol.get_value(C_t_n1_n2_u_v_k[t][n1][n2][u][v][k][w])
                #                             if C != 1:
                #                                 continue
                #                             else:
                #                                 print('C_t_n1_n2_u_v_k_w_{}_{}_{}_{}_{}_{}_{}=1'.format(t,n1,n1+1,u,v,k,w))
                #                                 paths = self.K_shortest_path(str(u), str(v))
                #                                 path = paths[k]
                #                                 for node in path:
                #                                     path_t[t].append(node)
                #
                # for t,path in path_t.items():
                #     print('业务{}的路径路由为{}'.format(t,[node for node in path]))


                resultfile.write('Sovling end')
                resultfile.write('\r\n')
                self.run(resultfile)
                resultfile.close()
            except Exception as e:
                print(e)


        def run(self,resultfile):
            MDL = CpoModel(name='Step_two')
            W = [1550, 1300]  # 光路可选用波长的集合
            K_short_path = 2
            try:
                C_t_n1_n2_k = []
                for t,traffic in enumerate(self.trafficlist):
                    C_t_n1_n2_k.append([])
                    for n1,vnf in enumerate(traffic.vnfsec):
                        if vnf == 'out':
                            continue
                        C_t_n1_n2_k[t].append([])
                        for n2, n1_vnf in enumerate([traffic.vnfsec[n1 + 1]]):
                            C_t_n1_n2_k[t][n1].append([MDL.integer_var(0,1,name='C_t_n1_n2_k_{}_{}_{}_{}'.format(t,n1,n1+1,k)) for k in range(K_short_path)])
                O_l = [MDL.integer_var(0,1,name='O_l_{}'.format(l)) for l,link in enumerate(self.link.keys())]
                W_t_n1_n2_l_w = []
                for t,traffic in enumerate(self.trafficlist):
                    W_t_n1_n2_l_w.append([])
                    for n1,vnf in enumerate(traffic.vnfsec):
                        if vnf == 'out':
                            continue
                        W_t_n1_n2_l_w[t].append([])
                        for n2,n1_vnf in enumerate([traffic.vnfsec[n1 + 1]]):
                            W_t_n1_n2_l_w[t][n1].append([])
                            for l,link in enumerate(self.link):
                                W_t_n1_n2_l_w[t][n1][n2].append([MDL.integer_var(0,1,name='W_t_n1_n2_l_w_{}_{}_{}_{}_{}'.format(t,n1,n2,l,w)) for w,wave in enumerate(W)])
                                MDL.add(MDL.sum([W_t_n1_n2_l_w[t][n1][n2][l][w] for w,wave in enumerate(W)]) <= 1)
                for t,traffic in enumerate(self.trafficlist):
                    for n1,vnf in enumerate(traffic.vnfsec):
                        if vnf == 'out':
                            continue
                        for n2,n1_vnf in enumerate([traffic.vnfsec[n1 + 1]]):
                            for l,(u,v) in enumerate(self.link.values()):
                                if self.link_map_uv(str(self.Z_t_n_s[t][n1]),str(self.Z_t_n_s[t][n1+1]),str(u),str(v)):
                                    K = self.link_map_uv(str(self.Z_t_n_s[t][n1]),str(self.Z_t_n_s[t][n1+1]),str(u),str(v))
                                    MDL.add(MDL.sum([W_t_n1_n2_l_w[t][n1][n2][l][w] for w,wave in enumerate(W)]) == MDL.sum([C_t_n1_n2_k[t][n1][n2][k] for k in K]))
                                else:
                                    MDL.add(MDL.sum([W_t_n1_n2_l_w[t][n1][n2][l][w] for w,wave in enumerate(W)]) == 0)
                for t,traffic in enumerate(self.trafficlist):
                    for n1,vnf in enumerate(traffic.vnfsec):
                        if vnf == 'out':
                            continue
                        for n2,n1_vnf in enumerate([traffic.vnfsec[n1 + 1]]):
                            Sum = MDL.sum([C_t_n1_n2_k[t][n1][n2][k] for k in range(K_short_path)])
                            MDL.add(Sum == 1)

                for l,(u,v) in enumerate(self.link.values()):
                    Sum_o = []
                    for w,wave in enumerate(W):
                        beat_u_v = int(self.nodelist[u].outnodedict[str(v)][1])
                        Sum_b = []
                        for t,traffic in enumerate(self.trafficlist):
                            for n in range(len(traffic.vnfsec)-1):
                                n2 = 0
                                Sum_b.append(W_t_n1_n2_l_w[t][n][n2][l][w] *int(traffic.bandwidth))
                                Sum_o.append(W_t_n1_n2_l_w[t][n][n2][l][w])
                        if Sum_b:
                            MDL.add(MDL.sum(Sum_b) <= beat_u_v)
                    if Sum_o:
                        MDL.add(O_l[l] <= MDL.sum(Sum_o))
                        MDL.add(MDL.sum(Sum_o) <= O_l[l] * 9999999)


        # P_t：路由器进行光-电-光转换的能耗
        # P_I：路由器转发1Gps流量的能耗
        # Sum_O：为承载业务所构建的光路使用的物理链路的总数
        # Sum_B：路由器转发的流量数的总和

                P_t = 35
                P_I = 0.000015
                Sum_B = []
                for t, traffic in enumerate(self.trafficlist):
                    Sum_t_B = []
                    beat_t = int(traffic.bandwidth)
                    for n1, vnf in enumerate(traffic.vnfsec):
                        if vnf =='out':
                            continue
                        for n2, n1_vnf in enumerate([traffic.vnfsec[n1 + 1]]):
                            for l,link in enumerate(self.link):
                                for w,wave in enumerate(W):
                                    Sum_t_B.append(W_t_n1_n2_l_w[t][n1][n2][l][w])

                    Sum_B.append((MDL.sum(Sum_t_B) - 1)*beat_t)
                Sum_O = [O_l[l] for l,link in enumerate(self.link.keys())]
                obj = 2*P_t*MDL.sum(Sum_O)+P_I*MDL.sum(Sum_B)
                MDL.add(MDL.minimize(obj))


                path_t = {}
                resultfile.write("Solving model....")
                resultfile.write('\r\n')
                Msol = MDL.solve(TimeLimit=36*len(self.trafficlist))
                resultfile.write("Solution: ")
                resultfile.write('\r\n')
                if Msol:
                    resultfile.write('优化后的总能耗为{}W'.format(Msol.get_objective_values()[0]))
                    for t, traffic in enumerate(self.trafficlist):
                        path_t[t] = []
                        for n1,vnf in enumerate(traffic.vnfsec):
                            if vnf == 'out':
                                continue
                            for n2,n1_vnf in enumerate([traffic.vnfsec[n1 + 1]]):
                                for k in range(K_short_path):
                                    C = Msol.get_value(C_t_n1_n2_k[t][n1][n2][k])
                                    if C == 1:
                                        paths = self.K_shortest_path(str(self.Z_t_n_s[t][n1]), str(self.Z_t_n_s[t][n1+1]))
                                        if paths:
                                            path = paths[k]
                                            for node in path:
                                                path_t[t].append(node)
                for t, path in path_t.items():
                    resultfile.write('业务{}的路径路由为{}'.format(t,[node for node in path]))
                    resultfile.write('\r\n')
            except Exception as e:
                print(e)

        def Loadtrafficfile(self,trafficsize):
            self.trafficlist.clear()
            traffic_file = open('Traffic_{}.txt'.format(trafficsize))
            for line in traffic_file:
                if line == '\n':
                    continue
                trafficinf = line.split(',')
                trafficsrcnode = trafficinf[0]
                trafficdstnode = trafficinf[1]
                trafficbandwidth = trafficinf[2]
                trafficvnfsec = []
                trafficvnfsec.append('in')
                for i,vnc in enumerate(trafficinf[3:]):
                    if i == len(trafficinf[3:])-1:
                        trafficvnfsec.append(vnc.split('\n')[0])
                    else:
                        trafficvnfsec.append(vnc)
                trafficvnfsec.append('out')
                self.trafficlist.append(Traffic(trafficsrcnode,trafficdstnode,trafficbandwidth,trafficvnfsec))
            traffic_file.close()
        def Vnf2server(self):
            self.vnf2server ={}
            M = 0
            for n,node in enumerate(self.nodelist):
                for m in range(M,M + len(node.pesudoswitchdict)):
                    self.vnf2server[m] = node.pesudoswitchdict[m-M]
                M += len(node.pesudoswitchdict)
        def node_of_paths(self,paths):
            node_of_paths = set()
            for path in paths:
                for node in path:
                    node_of_paths.add(node)
            return node_of_paths
        def uv2vu(self,v,u):
            for node in self.nodelist:
                if str(node.nodename) == v:
                    for U,node_u in enumerate(node.outnodedict.keys()):
                        if node_u == str(u):
                            return U
                        else:
                            continue
                else:
                    continue
        def compute_beta_u_v_k(self,u,v,k):
            if u == int(v):
                return 999999
            else:
                Paths = self.K_shortest_path(str(u),str(v))
                if Paths:
                    path = Paths[k]
                    B = []
                    for i in range(len(path)-1):
                        node_u = self.nodelist[int(path[i])]
                        b = node_u.outnodedict[str(path[i+1])][1]
                        B.append(b)
                    beta_u_v_k = min(B)
                    return beta_u_v_k
        def link_map_uv(self,U,V,u,v):
            paths = self.K_shortest_path(U,V)
            K = []
            if paths:
                for k,path in enumerate(paths):
                    for i in range(len(path)-1):
                        if u == path[i] and v==path[i+1]:
                            K.append(k)
                        else:
                            continue
                return K
        def initlink(self):
            self.link = {}
            num = 0
            for u,node_u in enumerate(self.nodelist):
                for v,node_v in enumerate(node_u.outnodedict.keys()):
                    self.link[num] = (u,int(node_v))
                    num += 1

        def K_shortest_path(self,srcnode,dstnode):
            Paths = ksp.yen_ksp(self.topoinfdict,srcnode,dstnode,2)
            if Paths:
                paths = [path[0] for path in Paths]
                return paths
            else:
                return

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    mainwindow = MainWindow()
    mainwindow.show()
    sys.exit(app.exec_())