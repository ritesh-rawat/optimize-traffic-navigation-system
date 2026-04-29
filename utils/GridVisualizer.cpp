#include "GridVisualizer.h"
#include <iostream>
#include <cmath>
using namespace std;

void drawGrid(int V,vector<int> path){
// Validate path nodes
for(int x:path) if(x<0||x>=V){cout<<"Invalid path nodes for grid.\n";return;}
int n=ceil(sqrt(V));
// Make grid big enough to hold all V nodes
vector<vector<string>> g(n,vector<string>(n," . "));
for(int i=0;i<V;i++)g[i/n][i%n]=" N ";
for(int x:path)g[x/n][x%n]=" * ";
cout<<"\nGRID (N=node, *=path, .=empty):\n";
for(int i=0;i<n;i++){
for(int j=0;j<n;j++)cout<<g[i][j];
cout<<endl;
}
cout<<"Path nodes: ";
for(int x:path)cout<<x<<" ";
cout<<endl;
}