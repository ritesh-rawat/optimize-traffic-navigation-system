#include "AStar.h"
#include <queue>
#include <climits>
#include <algorithm>
#include <cmath>
using namespace std;

int heuristic(int u, int dest) {
    return abs(u - dest);
}

vector<int> aStar(Graph &g, int src, int dest) {
    vector<int> gCost(g.V, INT_MAX);
    vector<int> par(g.V, -1);
    priority_queue<pair<int,int>, vector<pair<int,int>>, greater<pair<int,int>>> pq;
    gCost[src] = 0;
    pq.push(make_pair(heuristic(src, dest), src));

    while (!pq.empty()) {
        int f = pq.top().first;
        int u = pq.top().second;
        pq.pop();

        if (u == dest) break;

        for (int i = 0; i < (int)g.adj[u].size(); i++) {
            int v = g.adj[u][i].first;
            int w = g.adj[u][i].second;
            int newG = gCost[u] + w;
            if (newG < gCost[v]) {
                gCost[v] = newG;
                par[v] = u;
                pq.push(make_pair(newG + heuristic(v, dest), v));
            }
        }
    }

    vector<int> path;
    for (int v = dest; v != -1; v = par[v])
        path.push_back(v);
    reverse(path.begin(), path.end());
    return path;
}
