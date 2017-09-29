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
                self.nodelist.clear()
                right_now_time = time.strftime('%m-%d_%H:%M', time.localtime(time.time()))
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
                self.topofile.write(routerdata)
            except:
                self.routerdate.append('添加错误，请重新添加！')
        def initTopo(self):
            self.topoinfdict = {}
            for node in self.nodelist:
                self.topoinfdict[str(node.nodename)] = {}
                for outnode,[distance,bandwitch] in node.outnodedict.items():
                    self.topoinfdict[str(node.nodename)][outnode] = [distance,bandwitch]
        def startButtonclicked(self):
            self.topofile.close()
            self.initTopo()
            for t in range(10,60,10):
                trafficsize = t
                self.Loadtrafficfile(trafficsize)
                self.run_cplex_electic(trafficsize)
        def loaddataButtonclicked(self):
            self.nodelist.clear()
            topofile = open('新建文本文档.txt')
            pattern1 = re.compile(r'添加了节点(\w+),cpu数量为(\d+),')
            pattern2 = re.compile(r'流入节点有:(\S+);流出')
            pattern3 = re.compile(r'流出节点有:(\S+)')
            for line in topofile:
                matchs1 = pattern1.search(line)
                if matchs1:
                    nodename = int(matchs1.group(1))
                    cpunum = int(matchs1.group(2))
                    node = Server(nodename, cpunum)
                    matchs2 = pattern2.search(line)
                    pattern4 = re.compile(r'节点(\w+),距离为(\d+)，带宽为(\d+)')
                    matchs3 = pattern4.findall(matchs2.group())
                    innodedict = {}
                    for match in matchs3:
                        innodedict[match[0]] = [int(match[1]), int(match[2])]
                    node.setinnodedict(innodedict)
                    matchs4 = pattern3.search(line)
                    matchs5 = pattern4.findall(matchs4.group())
                    outnodedict = {}
                    for match in matchs5:
                        outnodedict[match[0]] = [int(match[1]), int(match[2])]
                    node.setoutnodedict(outnodedict)
                    self.nodelist.append(node)
                    self.routerdate.append('读取日志成功！')
                    routerdata = '添加了节点{},cpu数量为{},流入节点有:'.format(node.nodename, node.cpunum)
                    for innode in node.innodedict.keys():
                        routerdata += '节点{},距离为{}，带宽为{};'.format(innode, node.innodedict[innode][0],
                                                                 node.innodedict[innode][1])
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
        def run_cplex_electic(self,trafficsize):
            self.Vnf2server()
            self.initlink()
            P = ['in','proxy','firewall','ids','out']
            W = [1550,1300]#光路可选用波长的集合
            B = 100000
            K_short_path = 2
            mdl = CpoModel()
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

            W_t_n1_n2_u_v = []
            try:
                for t,traffic in enumerate(self.trafficlist):
                    W_t_n1_n2_u_v.append([])
                    for n1,vnf in enumerate(traffic.vnfsec):
                        if vnf == 'out':
                            continue
                        W_t_n1_n2_u_v[t].append([])
                        for n2,n1_vnf in enumerate([traffic.vnfsec[n1+1]]):
                            W_t_n1_n2_u_v[t][n1].append([])
                            for u,node_u in enumerate(self.nodelist):
                                W_t_n1_n2_u_v[t][n1][n2].append({})
                                for v,node_v in enumerate(self.nodelist):
                                    if v == u:
                                        continue
                                    W_t_n1_n2_u_v[t][n1][n2][u][v] = mdl.integer_var(0,1,name='W_t_n1_n2_u_v_{}_{}_{}_{}_{}'.format(t,n1,n1+1,u,node_v.nodename))
            except Exception as e:
                print(e)
            # O_u_v = []
            # for u,node_u in enumerate(self.nodelist):
            #     O_u_v.append([mdl.integer_var(0,1,name='O_u_v_{}_{}'.format(u,v)) for v,node_v in enumerate(node_u.outnodedict.keys())])
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
            #
            C_u_v_k_w = []
            try:
                for u,node_u in enumerate(self.nodelist):
                    C_u_v_k_w.append({})
                    for v,node_v in enumerate(self.nodelist):
                        if v == u:
                            continue
                        C_u_v_k_w[u][v] = []
                        for k in range(K_short_path):
                            C_u_v_k_w[u][v].append([mdl.integer_var(0,1,name='C_u_v_k_w_{}_{}_{}_{}'.format(u,node_v.nodename,k,w)) for w,wave in enumerate(W)])
            except Exception as e:
                print(e)
        ###################################################
        #                     构建约束                     #
        ###################################################
        #约束式(1):
            try:
                M = 0
                for n,node in enumerate(self.nodelist):
                    cpu_constraints = [times(ym[M+m],vnf.cpu_required) for m,vnf in node.pesudoswitchdict.items()]
                    mdl.add(mdl.sum(cpu_constraints)<=node.cpunum)
                    M += len(node.pesudoswitchdict)
            except Exception as e:
                print(e)
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
                    Sum_4 = [x_t_n_m[t][n][m] for t,traffic in enumerate(self.trafficlist) for n, traffic_node in enumerate(traffic.vnfsec)]
                    mdl.add(ym[m]<=mdl.sum(Sum_4))
                    mdl.add(mdl.sum(Sum_4)<=ym[m]*9999999)
            except Exception as e:
                print(e)
        # 约束式(5):
        #     a = mdl.get_all_expressions()
        #     print(a)
            try:
                for t,traffic in enumerate(self.trafficlist):
                    for n, traffic_node in enumerate(traffic.vnfsec):
                        for m in range(self.getlenforvnf()):
                            Sum = [Amp[m][p]*g_t_n_p[t][n][p] for p,vnf_type in enumerate(P)]
                            mdl.add(x_t_n_m[t][n][m]<=sum(Sum))
            except Exception as e:
                print(e)
        # 约束式(6):
            try:
                for t,traffic in enumerate(self.trafficlist):
                    for n, traffic_node in enumerate(traffic.vnfsec):
                        M = 0
                        for s,node_s in enumerate(self.nodelist):
                            Sum = [x_t_n_m[t][n][m] for m in range(M,M+len(node_s.pesudoswitchdict))]
                            mdl.add(mdl.sum(Sum)==Z_t_n_s[t][n][s])
                            M += len(node_s.pesudoswitchdict)
            except Exception as e:
                print(e)
        # 约束式(7),(8):
            try:
                for t,traffic in enumerate(self.trafficlist):
                    for n1, vnf in enumerate(traffic.vnfsec):
                        if vnf =='out':
                            continue
                        for n2, n1_vnf in enumerate([traffic.vnfsec[n1 + 1]]):
                            Sum7 = []
                            for u,node_u in enumerate(self.nodelist):
                                for v, node_v in enumerate(self.nodelist):
                                    if v == u:
                                        continue
                                    Sum7.append(W_t_n1_n2_u_v[t][n1][n2][u][v])
                            mdl.add(mdl.sum(Sum7) <= 1)
            except Exception as e:
                print(e)
        #约束式(9):
            try:
                for t, traffic in enumerate(self.trafficlist):
                    for n1, vnf in enumerate(traffic.vnfsec):
                        if vnf =='out':
                            continue
                        for n2, n1_vnf in enumerate([traffic.vnfsec[n1 + 1]]):
                            for u, node_u in enumerate(self.nodelist):
                                Sum_9 = [minus(W_t_n1_n2_u_v[t][n1][n2][u][v],W_t_n1_n2_u_v[t][n1][n2][node_v.nodename][node_u.nodename]) for v, node_v in enumerate(self.nodelist) if v != u]
                                mdl.add(mdl.sum(Sum_9)==minus(Z_t_n_s[t][n1][u],Z_t_n_s[t][n1+1][u]))
            except Exception as e:
                print(e)
        # 约束式(10):
            try:
                for u, node_u in enumerate(self.nodelist):
                    for v, node_v in enumerate(self.nodelist):
                        if v == u:
                            continue
                        Sum_12 = []
                        for t, traffic in enumerate(self.trafficlist):
                            for n1, vnf in enumerate(traffic.vnfsec):
                                if vnf == 'out':
                                    continue
                                for n2, n1_vnf in enumerate([traffic.vnfsec[n1 + 1]]):
                                    Sum_12.append(times(W_t_n1_n2_u_v[t][n1][n2][u][v],int(traffic.bandwidth)))
                        mdl.add(mdl.sum(Sum_12)<= mdl.sum([C_u_v_k_w[u][v][k][w] for k in range(K_short_path) for w,wave in enumerate(W)])*B)
            except Exception as e:
                print(e)
        #约束式(11):
            try:
                for l,(u,v) in enumerate(self.link.values()):
                    for w,wave in enumerate(W):
                        Sum13 = []
                        for U,node_U in enumerate(self.nodelist):
                            for V,node_V in enumerate(self.nodelist):
                                if V == U:
                                    continue
                                if self.link_map_uv(str(U),str(V),str(u),str(v)):
                                    K = self.link_map_uv(str(U),str(V),str(u),str(v))
                                    for k in K:
                                        Sum13.append(C_u_v_k_w[U][V][k][w])
                        mdl.add(mdl.sum(Sum13) <= 1)
            except Exception as e:
                print(e)
            # try:
            #     for u, node_u in enumerate(self.nodelist):
            #         for v, node_v in enumerate(node_u.outnodedict.keys()):
            #             Sum_12 = []
            #             for t,traffic in enumerate(self.trafficlist):
            #                 for n1, vnf in enumerate(self.trafficlist[t].vnfsec):
            #                     if vnf == 'out':
            #                         continue
            #                     for n2, n1_vnf in enumerate([self.trafficlist[t].vnfsec[n1 + 1]]):
            #                         Sum11 = []
            #                         for U,node_U in enumerate(self.nodelist):
            #                             for V,node_V in enumerate(self.nodelist):
            #                                 if V == U:
            #                                     continue
            #                                 if self.link_map_uv(str(U),str(V),str(u),str(node_v)):
            #                                     K = self.link_map_uv(str(U),str(V),str(u),str(node_v))
            #                                     for k in K:
            #                                         Sum_12.append(W_t_n1_n2_u_v[t][n1][n2][U][V][k])
            #                                         Sum11.append(W_t_n1_n2_u_v[t][n1][n2][U][V][k])
            #                         mdl.add(mdl.sum([W_t_n1_n2_u_v_w[t][n1][n2][u][v][w] for w,wave in enumerate(W)]) <= mdl.sum(Sum11) <= mdl.sum([W_t_n1_n2_u_v_w[t][n1][n2][u][v][w] for w,wave in enumerate(W)])*9999999)
            #
            #             mdl.add(O_u_v[u][v]<=mdl.sum(Sum_12)<=O_u_v[u][v]*9999999)
            #
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
        #                                                         mdl.add(mdl.sum([W_t_n1_n2_U_V_u_v_w[t][n1][n2][U][V][int(path[i])][self.uv2vu(path[i],path[i+1])][w] for w,wave in enumerate(W)])==mdl.sum([W_t_n1_n2_u_v[t][n1][n2][U][V][K] for K in range(K_short_path)]))
        #                                                     else:
        #                                                         mdl.add(mdl.sum([W_t_n1_n2_U_V_u_v_w[t][n1][n2][U][V][int(path[i])][self.uv2vu(path[i],path[i+1])][w] for w,wave in enumerate(W)])==W_t_n1_n2_u_v[t][n1][n2][U][V][k])
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
            try:
                P_t = 35
                P_I = 0.00015
                P_O = 0.000015
                Sum_T = []
                for u,node_u in enumerate(self.nodelist):
                    for v,node_v in enumerate(self.nodelist):
                        if v == u:
                            continue
                        for k in range(K_short_path):
                            for w,wave in enumerate(W):
                                Sum_T.append(C_u_v_k_w[u][v][k][w])
                Sum_O = []
                for U, node_U in enumerate(self.nodelist):
                    for V, node_V in enumerate(self.nodelist):
                        if V == U:
                            continue
                        for k in range(K_short_path):
                            for w,wave in enumerate(W):
                                S = []
                                for l,(u,v) in enumerate(self.link.values()):
                                    if self.link_map_uv(str(U),str(V),str(u),str(v)):
                                        K = self.link_map_uv(str(U),str(V),str(u),str(v))
                                        if k in K:
                                            S.append(C_u_v_k_w[U][V][k][w])
                                Sum_O.append(C_u_v_k_w[U][V][k][w] + mdl.sum(S))
                Sum_I = []
                for t,traffic in enumerate(self.trafficlist):
                    beta_t = int(traffic.bandwidth)
                    for n1,vnf in enumerate(traffic.vnfsec):
                        if vnf == 'out':
                            continue
                        for n2,n1_vnf in enumerate([traffic.vnfsec[n1 + 1]]):
                            S = []
                            for u,node_u in enumerate(self.nodelist):
                                for v,node_v in enumerate(self.nodelist):
                                    if v == u:
                                        continue
                                    S.append(W_t_n1_n2_u_v[t][n1][n2][u][v])
                            Sum_I.append((mdl.sum(S) - 1) * beta_t)
                mdl.add(mdl.minimize(2*P_t*mdl.sum(Sum_T)+P_O*mdl.sum(Sum_O)+P_I*mdl.sum(Sum_I)))
            except Exception as e:
                print(e)
            ##############################################################################
            # Model solving
            ##############################################################################
            # Solve model
            resultfile = open('guang_result_{}.txt'.format(trafficsize),'w')
            try:
                cnt =1
                while True:
                    msol = mdl.solve(TimeLimit=500*cnt*len(self.trafficlist))
                    if msol.is_solution_optimal():
                        resultfile.write("Solving model....\r\n")
                        resultfile.write("Solution: \r\n")
                        resultfile.write('总能耗为{}\r\n'.format(msol.get_objective_values()[0]))
                        for t, traffic in enumerate(self.trafficlist):
                            for n, traffic_node in enumerate(traffic.vnfsec):
                                for s,node_s in enumerate(self.nodelist):
                                    Z = msol.get_value(Z_t_n_s[t][n][s])
                                    if Z == 1:
                                        resultfile.write('业务{}的第{}个服务链节点部署在服务器{}上\r\n'.format(t,n,s))
                                for m in range(self.getlenforvnf()):
                                    X = msol.get_value(x_t_n_m[t][n][m])
                                    if X == 1:
                                        resultfile.write('业务{}的第{}个服务链节点使用了{}号VNF\r\n'.format(t,n,m))
                        for m in range(self.getlenforvnf()):
                            Ym = msol.get_value(ym[m])
                            if Ym == 1:
                                resultfile.write('第{}号VNF处于激活状态\r\n'.format(m))
                        path_u_v = {}
                        for u,node_u in enumerate(self.nodelist):
                            for v,node_v in enumerate(self.nodelist):
                                if v == u:
                                    continue
                                path_u_v[(u,v)] = {}
                                C = {}
                                for k in range(K_short_path):
                                    for w,wave in enumerate(W):
                                        C[(k,w)] = (msol.get_value(C_u_v_k_w[u][v][k][w]))
                                for (k,w),c in C.items():
                                    if c == 1:
                                        path_u_v[(u,v)][(k,w)] = []
                                        paths = self.K_shortest_path(str(u),str(v))
                                        if paths:
                                            path = paths[k]
                                            for node in path:
                                                path_u_v[(u,v)][(k,w)].append(node)
                        for (u,v), path_k_w in path_u_v.items():
                            for (k,w),path in path_k_w.items():
                                resultfile.write('光路使用链路{}中的第{}条路径和波长{}映射的物理节点为{}\r\n'.format((u,v),k,W[w],[node for node in path]))
                        break
                    else:
                        cnt +=1
                resultfile.close()
                print('Sovling end')
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
                return 9999999
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
            return False

        def initlink(self):
            self.link = {}
            num = 0
            for u, node_u in enumerate(self.nodelist):
                for v, node_v in enumerate(node_u.outnodedict.keys()):
                    self.link[num] = (u, int(node_v))
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