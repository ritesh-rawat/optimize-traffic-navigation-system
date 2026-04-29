#include "OutputHandler.h"
#include <iostream>
using namespace std;

void printPath(vector<int> p){
cout<<"Path: ";
for(int x:p)cout<<x<<"->";
cout<<"END\n";
}

void printBarChart(double a,double b){
// a,b already in nanoseconds (passed from main.cpp)
long long na = (long long)a;
long long nb = (long long)b;
long long mx = max(max(na,nb),1LL);
int barA = max(1,(int)(na * 40 / mx));
int barB = max(1,(int)(nb * 40 / mx));
cout<<"\n--- Algorithm Comparison ---\n";
cout<<"Dijkstra   ("<<na<<" ns): ";
for(int i=0;i<barA;i++)cout<<"#";
cout<<"\nBellmanFord("<<nb<<" ns): ";
for(int i=0;i<barB;i++)cout<<"#";
cout<<"\n";
if(na<nb)      cout<<">> Dijkstra faster by "<<(nb-na)<<" ns\n";
else if(nb<na) cout<<">> BellmanFord faster by "<<(na-nb)<<" ns\n";
else           cout<<">> Both took equal time!\n";
}
