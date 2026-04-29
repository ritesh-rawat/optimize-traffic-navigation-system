#include "BellmanFord.h"
#include <climits>
#include <algorithm>
using namespace std;

vector<int> bellmanFord(Graph &g,int src,int dest){
vector<int> dist(g.V,INT_MAX),par(g.V,-1);
dist[src]=0;
for(int i=0;i<g.V-1;i++){
for(int u=0;u<g.V;u++){
for(auto &e:g.adj[u]){
int v=e.first,w=e.second;
if(dist[u]!=INT_MAX && dist[v]>dist[u]+w){
dist[v]=dist[u]+w;
par[v]=u;
}}}}
vector<int> path;
for(int v=dest;v!=-1;v=par[v])path.push_back(v);
reverse(path.begin(),path.end());
return path;
}