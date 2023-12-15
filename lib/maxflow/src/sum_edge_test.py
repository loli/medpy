#!/usr/bin/python


from maxflow import GraphDouble, GraphFloat, GraphInt


def main():
    print("\nGRAPHINT")
    test(GraphInt)
    print("\nGRAPHFLOAT")
    test(GraphFloat)
    print("\nGRAPHDOUBLE")
    test(GraphDouble)
    print("\nADDITIONAL TESTS")
    test_sum(GraphDouble)
    test_multiple_arcs(GraphDouble)
    test_overflow(GraphDouble)


def test(graphtype):
    g = graphtype(4, 4)
    g.add_node(4)

    g.add_tweights(0, 99, 0)
    g.add_tweights(3, 0, 99)

    g.add_edge(0, 1, 1, 1)
    g.add_edge(0, 2, 1, 1)
    g.add_edge(1, 3, 2, 2)
    g.add_edge(2, 3, 2, 2)
    print("Flow: {}".format(g.maxflow()))
    print_cut(g, 4)

    g.add_edge(0, 1, 2, 2)
    g.add_edge(0, 2, 2, 2)
    print("Flow: {}".format(g.maxflow()))
    print_cut(g, 4)


def test_sum(graphtype):
    g = graphtype(2, 1)
    g.add_node(2)

    print(
        "Expected to go all the way to 20 without increasing the memory requirements..."
    )
    for i in range(20):
        print(i, end=" ")
        g.sum_edge(0, 1, 1, 2)

    v1 = g.get_edge(0, 1)
    v2 = g.get_edge(1, 0)
    print("\nFinal edge weight should be 20 resp. 40. Found {} resp. {}".format(v1, v2))


def test_multiple_arcs(graphtype):
    g = graphtype(2, 1)
    g.add_node(2)

    g.add_edge(0, 1, 1, 2)
    g.add_edge(0, 1, 1, 2)

    v1 = g.get_edge(0, 1)
    v2 = g.get_edge(1, 0)
    print("Final edge weight should be 1 resp. 2. Found {} resp. {}".format(v1, v2))


def test_overflow(graphtype):
    g = graphtype(2, 1)
    g.add_node(2)

    print("Memory expected to double after 15...")
    for i in range(20):
        g.add_edge(0, 1, 1, 2)
        print(i, end=" ")

    v1 = g.get_edge(0, 1)
    v2 = g.get_edge(1, 0)
    print("\nFinal edge weight should be 1 resp. 2. Found {} resp. {}".format(v1, v2))


def print_cut(g, nodes):
    for n in range(nodes):
        print("{} in {}".format(n, g.what_segment(n)))


if __name__ == "__main__":
    main()
