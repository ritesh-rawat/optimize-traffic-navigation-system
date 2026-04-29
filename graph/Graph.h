#ifndef GRAPH_H
#define GRAPH_H
#include <vector>
using namespace std;

class Graph {
public:
    int V;
    vector<vector<pair<int,int>>> adj;
    Graph(int V);
    void addEdge(int u,int v,int w);
};
#endif