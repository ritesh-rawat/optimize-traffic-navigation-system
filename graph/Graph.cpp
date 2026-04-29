#include "Graph.h"
Graph::Graph(int V){this->V=V;adj.resize(V);}
void Graph::addEdge(int u,int v,int w){adj[u].push_back({v,w});adj[v].push_back({u,w});}