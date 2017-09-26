#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2017/7/31 19:03
# @Author : YANGz1J
# @Site : 
# @File : test.py
# @Software: PyCharm
import random

INFINITY = float('inf')


def __shortest_distance(G, D, U):
    """
    Get the shortest path from node in D to node in U

    @:param G   graph
    @:param D   mapping of nodes to their dist from start
    @:param U   unexplored nodes

    @:return source vertex in D, target vertex in U, distance from source to target
    """
    distance = INFINITY
    source_vertex, target_vertex = None, None
    for source, dist_start in D.items():
        for v, d in G[source].items():
            if v in U and dist_start + d < distance:
                source_vertex, target_vertex, distance = source, v, dist_start + d
    return source_vertex, target_vertex, distance


def predecessor_to_path(pred, source, target):
    """
    generate a path from source to target by pred
    @:param pred    a dict mapping each node to its predecessor node on the
                    shortest path from the specified starting node:
                    e.g. pred == {'b': 'a', 'c': 'b', 'd': 'c'}

    @:return    a list of the vertices in order along the shortest path.
                e.g. path = ['a', 'b', 'c', 'd']
    """
    v = target
    path = [v]
    while v != source:
        v = pred[v]
        path.append(v)
    path.reverse()
    return path


def dijkstra(G, source, target=None):
    """
    Find shortest paths from the start vertex to all vertices nearer than or
    equal to the end.

    The input graph G is assumed to have the following representation:
    A vertex can be any object that can be used as an index into a dictionary.
    G is a dictionary, indexed by vertices. For any vertex v, G[v] is itself
    a dictionary, indexed by the neighbors of v. For any edge v->w, G[v][w]
    is the length of the edge from v to w.

    The output is a pair (D,P) where D[v] is the distance from start to v and
    P[v] is the predecessor of v along the shortest path from s to v.

    e.g

    graph = {'a': {'b': 1},
             'b': {'c': 2, 'b': 5},
             'c': {'d': 1},
             'd': {}}
    Returns two dicts, `dist` and `pred`:

        dist, pred = dijkstra(graph, start='a')

    `dist` is a dict mapping each node to its shortest distance from the
    specified starting node:
        assert dist == {'a': 0, 'c': 3, 'b': 1, 'd': 4}

    `pred` is a dict mapping each node to its predecessor node on the
    shortest path from the specified starting node:
        assert pred == {'b': 'a', 'c': 'b', 'd': 'c'}

    Dijkstra's algorithm is only guaranteed to work correctly when all edge
    lengths are positive.
    """
    # unexplored nodes
    U = set(G.keys())
    # mapping of nodes to their dist from start
    D = {source: 0}
    # mapping of nodes to their direct predecessors
    P = {}

    next_vertex = source
    U.remove(next_vertex)
    while U and not next_vertex == target:
        prev_vertex, next_vertex, distance = __shortest_distance(G, D, U)
        if next_vertex is None:
            break

        D[next_vertex] = distance
        P[next_vertex] = prev_vertex
        U.remove(next_vertex)
    return D, P


def dijkstra_shortest_path(G, source, target):
    """
    Find a single shortest path from the given start vertex to the given end vertex.

    The input has the same conventions as dijkstra().

    The output is a list of the vertices in order along the shortest path.
    e.g. path = ['a', 'b', 'c', 'd']
    """
    dist, pred = dijkstra(G, source, target)
    return (predecessor_to_path(pred, source, target),
            dist[target]) if target in pred else (None, INFINITY)


def yen_ksp(G, source, target, K=1):
    """
    Yen's algorithm computes single-source K-shortest loopless paths for a graph
    with non-negative edge cost.
    The algorithm was published by Jin Y. Yen in 1971 and employs any shortest
    path algorithm to find the best path, then proceeds to find K − 1 deviations
    of the best path.

    https://en.wikipedia.org/wiki/Yen's_algorithm

    @:param G   graph
    @:param source  source node
    @:param target  target node

    @:return a list of tuples that contains path and distance
    """

    # Determine the shortest path from the source to the target.
    # A = [(path[], dist[]), ...]
    A = []
    # Initialize the heap to store the potential kth shortest path.
    # B = [(path[], dist[]), ...]
    B = []

    dist, pred = dijkstra(G, source, target)
    if target in pred:
        A.append((predecessor_to_path(pred, source, target), dist))
    else:
        return None

    for k in range(1, K):
        # The previous k-shortest path
        last_path = A[-1][0]
        last_dist = A[-1][1]
        # The spur node ranges from the first node to the next to last node in
        # the previous k-shortest path.
        for i in range(0, len(last_path) - 1):
            spur_node = last_path[i]
            # The sequence of nodes from the source to the spur node of the
            # previous k-shortest path.
            root_path = last_path[:i + 1]
            root_distance = last_dist[spur_node]

            # Remove the links that are part of the previous shortest paths
            # which share the same root path.
            edges_removed = []
            for a in A:
                path = a[0]
                if (i + 1 < len(path) and path[:i + 1] == root_path and
                            path[i + 1] in G[spur_node]):
                    edges_removed.append(
                        (spur_node, path[i + 1], G[spur_node].pop(path[i + 1])))

            # NOT removed each node in root_path from Graph;

            # Calculate the spur path from the spur node to the target
            dist, pred = dijkstra(G, spur_node, target)
            # Add the potential k-shortest path to the heap.
            if target in pred:
                # Entire path is made up of the root path and spur path.
                total_path = root_path[:-1] + predecessor_to_path(pred,
                                                                  spur_node,
                                                                  target)
                total_dist = {node: last_dist[node] for node in root_path}
                for node in dist.keys():
                    total_dist[node] = dist[node] + root_distance

                if (total_path, total_dist) not in B:
                    B.append((total_path, total_dist))

            # Add back the edges and nodes that were removed from the graph.
            for edge in edges_removed:
                G[edge[0]][edge[1]] = edge[2]

        # Add the lowest cost path becomes the k-shortest path.
        if B:
            B.sort(key=lambda p: p[1][target])
            A.append(B.pop(0))
        else:
            break

    return A
if __name__ == '__main__':
    graph2 = {'c': {'d': 3, 'e': 2},
              'd': {'f': 4},
              'e': {'d': 1, 'f': 2, 'g': 3},
              'f': {'g': 2, 'h': 1},
              'g': {'h': 2},
              'h': {}
              }
    source, target = 'c', 'h'
    # paths = yen_ksp(graph2, source, target, 3)
    # paths = shortest_path.yen_ksp(self.graph2, source, target)
    # self.assertListEqual([path[0] for path in paths],
    #                      [['c', 'e', 'f', 'h']])

    paths = yen_ksp(graph2, source, target, 2)
    print(paths)
    print("TOP-10 shortest paths")
    # Random = [random.randint(0, 1000 * 10) for t in range(10-1)]
    # Random.sort()
    # print(Random)
    # B = Random[:1]
    # print(B)
    # for i in range(10-2):
    #     B.append(Random[i + 1] - Random[i])
    # B.append(1000*10 - Random[10-2])
    # print(B)
    # print(sum(B))
    # for t in range(10,160,10):
    #     trafficsize = t
    #     trafficfile = open('Traffic_{}.txt'.format(trafficsize),'w')
    #     Random = [random.randint(0,500*trafficsize)]
    #     for t in range(trafficsize-2):
    #         Random.append(random.randint(0,500*trafficsize))
    #         while Random[t+1] == Random[t]:
    #             Random.pop(t+1)
    #             Random.append(random.randint(0, 500 * trafficsize))
    #     Random.sort()
    #     B = Random[:1]
    #     for i in range(trafficsize - 2):
    #         B.append(Random[i + 1] - Random[i])
    #     B.append(500 * trafficsize - Random[trafficsize - 2])
    #     print(sum(B))
    #     for i in range(trafficsize):
    #         srcnode = random.randint(0,10)
    #         dstnode = random.randint(0,10)
    #         bandwidth = B[i]
    #         while srcnode == dstnode:
    #             dstnode = random.randint(0,10)
    #         vnfsec = ['ids','proxy','firewall']
    #         random.shuffle(vnfsec)
    #         trafficfile.write('{},{},{},{},{},{}\r\n'.format(srcnode,dstnode,bandwidth,vnfsec[0],vnfsec[1],vnfsec[2]))
    #     trafficfile.close()
    f = open('COST239.txt','w')
    a = {0:{1:1310,2:760,3:390,6:740},1:{0:1310,2:550,4:390,7:450},2:{0:760,1:550,3:660,4:210,5:390},3:{0:390,2:660,6:340,7:1090,9:660},4:{1:390,2:210,5:220,7:300,10:930},5:{2:390,4:220,6:730,7:400,8:350},6:{0:740,3:340,5:730,8:565,9:320},7:{1:450,4:300,5:400,8:600,10:820},8:{5:350,6:565,7:600,9:730,10:320},9:{3:660,6:320,8:730,10:820},10:{4:930,7:820,8:320,9:820}}
    for key,items in a.items():
        txt = '添加了节点{},cpu数量为16,流出节点有:'.format(key)
        for node,distance in items.items():
            txt += '节点{},距离为{},带宽为{};'.format(node,distance,distance*15)
        f.write(txt+'\r\n')
    # f = open('Traffic_10.txt','r')
    # a = f.readlines()
    # for size in range(2,16):
    #     f1 = open('Traffic_{}.txt'.format(size*10),'w')
    #     for i in range(size):
    #         for line in a:
    #             if line == '\n':
    #                 continue
    #             f1.write(line)



    # for size in range(20,160,10):

