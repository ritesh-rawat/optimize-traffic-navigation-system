#include "TrafficSimulator.h"
#include <cstdlib>
void simulateTraffic(Graph &g){
for(int u=0;u<g.V;u++){
for(auto &e:g.adj[u]){
e.second += rand()%5;
}}}