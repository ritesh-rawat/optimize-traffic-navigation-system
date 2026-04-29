#include "Dijkstra.h"
#include <queue>
#include <climits>
#include <algorithm>
using namespace std;

vector<int> dijkstra(Graph &g,int src,int dest){
vector<int> dist(g.V,INT_MAX),par(g.V,-1);
priority_queue<pair<int,int>,vector<pair<int,int>>,greater<>> pq;
dist[src]=0;pq.push({0,src});

while(!pq.empty()){
auto top=pq.top();pq.pop();
int d=top.first,u=top.second;
for(auto &e:g.adj[u]){
int v=e.first,w=e.second;
if(dist[v]>dist[u]+w){
dist[v]=dist[u]+w;
par[v]=u;
pq.push({dist[v],v});
}}}

vector<int> path;
for(int v=dest;v!=-1;v=par[v])path.push_back(v);
reverse(path.begin(),path.end());
return path;
}