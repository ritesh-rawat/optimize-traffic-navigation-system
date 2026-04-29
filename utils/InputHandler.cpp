#include "InputHandler.h"
#include <cstdlib>
#include <algorithm>
#include <vector>
using namespace std;

Graph createSampleGraph(){
    Graph g(5);
    g.addEdge(0,1,2);
    g.addEdge(1,2,4);
    g.addEdge(0,3,1);
    g.addEdge(3,4,3);
    g.addEdge(4,2,1);
    return g;
}

Graph generateRandomGraph(int V,int E){
    Graph g(V);
    // Spanning tree first — all nodes guaranteed connected
    vector<int> nodes(V);
    for(int i=0;i<V;i++) nodes[i]=i;
    for(int i=V-1;i>0;i--){
        int j=rand()%(i+1);
        swap(nodes[i],nodes[j]);
    }
    for(int i=1;i<V;i++){
        int w=rand()%10+1;
        g.addEdge(nodes[i-1],nodes[i],w);
    }
    // Extra random edges
    int extra=E-(V-1);
    for(int i=0;i<extra;i++){
        int u=rand()%V;
        int v=rand()%V;
        int w=rand()%10+1;
        g.addEdge(u,v,w);
    }
    return g;
}
