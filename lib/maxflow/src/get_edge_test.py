#!/usr/bin/python

import random

from maxflow import GraphDouble, GraphFloat, GraphInt


def main():
    print("GRAPHDOUBLE")
    test(GraphDouble, 100)
    print("GRAPHFLOAT")
    test(GraphFloat, 100)
    print("GRAPHINT")
    test(GraphInt, 100)


def test(graphtype, runs):
    print("#### FIRST ####")
    g = graphtype(2, 1)
    g.add_node(3)
    g.add_edge(0, 1, 2, 2)
    g.add_edge(0, 2, 4, 5)

    p(g, 0, 1, 2)
    p(g, 1, 0, 2)
    p(g, 0, 2, 4)
    p(g, 2, 0, 5)
    p(g, 1, 2, 0)
    p(g, 2, 1, 0)
    # p(g,1,3,1) # should raise error: node id out of bounds

    print("#### SECOND ####")
    g = graphtype(2, 1)
    g.add_node(2)
    g.add_edge(0, 1, 2, 3)
    p(g, 0, 1, 2)
    p(g, 1, 0, 3)
    # p(g,1,2,1) # should raise error: node id unknown, as add_node has not been often enough called

    print("#### THIRD: RANDOM ####")
    nodes = runs
    edges = nodes * (nodes - 1)
    g = graphtype(nodes, edges)
    g.add_node(nodes)
    connection = dict()
    for fr in range(nodes):
        for to in range(fr, nodes):
            if fr == to:
                continue
            connection[(fr, to)] = (random.randint(1, 10), random.randint(1, 10))
            g.add_edge(fr, to, connection[(fr, to)][0], connection[(fr, to)][1])
    print("Testing {} random edge weights...".format(edges))
    for fr in range(nodes):
        for to in range(fr, nodes):
            if fr == to:
                continue
            p2(g, fr, to, connection[(fr, to)][0])
            p2(g, to, fr, connection[(fr, to)][1])
    print("Finished.")


def p(g, f, t, exp):
    if exp != g.get_edge(f, t):
        print("!Failed:", end=" ")
    else:
        print("Passed:", end=" ")
    print("{}->{}:{} (expected: {})".format(f, t, g.get_edge(f, t), exp))


def p2(g, f, t, exp):
    if exp != g.get_edge(f, t):
        print("!Failed:", end=" ")
        print("{}->{}:{} (expected: {})".format(f, t, g.get_edge(f, t), exp))


if __name__ == "__main__":
    main()
