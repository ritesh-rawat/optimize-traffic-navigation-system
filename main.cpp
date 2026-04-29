#include <iostream>
#include <chrono>
#include "graph/Graph.h"
#include "algorithms/Dijkstra.h"
#include "algorithms/BellmanFord.h"
#include "algorithms/AStar.h"
#include "traffic/TrafficSimulator.h"
#include "utils/InputHandler.h"
#include "utils/OutputHandler.h"
#include "utils/GridVisualizer.h"
using namespace std;
using namespace chrono;

void menu(){
    cout<<"\n===== TRAFFIC NAVIGATION SYSTEM =====\n";
    cout<<"1. Use Sample Graph\n2. Generate Random Graph\n3. Run Dijkstra\n";
    cout<<"4. Run Bellman-Ford\n5. Compare Algorithms\n6. Simulate Traffic\n";
    cout<<"7. Show ASCII Grid\n8. Run A* Algorithm\n0. Exit\nEnter choice: ";
}

int main(){
    srand(42);
    Graph g=createSampleGraph();
    vector<int> lastPath;
    int src=0,dest=2;
    const int RUNS=1000;
    int choice;
    do{
        menu(); cin>>choice;
        switch(choice){
            case 1: g=createSampleGraph(); cout<<"Sample graph loaded.\n"; break;
            case 2:{int V,E; cout<<"Enter vertices and edges: "; cin>>V>>E; g=generateRandomGraph(V,E); cout<<"Random graph generated.\n"; break;}
            case 3:{
                cout<<"Enter source and destination: "; cin>>src>>dest;
                auto s=high_resolution_clock::now();
                for(int i=0;i<RUNS;i++) lastPath=dijkstra(g,src,dest);
                auto e=high_resolution_clock::now();
                printPath(lastPath);
                cout<<"Time: "<<duration_cast<nanoseconds>(e-s).count()/RUNS<<" ns (avg of "<<RUNS<<" runs)\n";
                break;}
            case 4:{
                cout<<"Enter source and destination: "; cin>>src>>dest;
                auto s=high_resolution_clock::now();
                for(int i=0;i<RUNS;i++) lastPath=bellmanFord(g,src,dest);
                auto e=high_resolution_clock::now();
                printPath(lastPath);
                cout<<"Time: "<<duration_cast<nanoseconds>(e-s).count()/RUNS<<" ns (avg of "<<RUNS<<" runs)\n";
                break;}
            case 5:{
                cout<<"Enter source and destination: "; cin>>src>>dest;
                auto s1=high_resolution_clock::now();
                for(int i=0;i<RUNS;i++) dijkstra(g,src,dest);
                auto e1=high_resolution_clock::now();
                auto s2=high_resolution_clock::now();
                for(int i=0;i<RUNS;i++) bellmanFord(g,src,dest);
                auto e2=high_resolution_clock::now();
                auto s3=high_resolution_clock::now();
                for(int i=0;i<RUNS;i++) aStar(g,src,dest);
                auto e3=high_resolution_clock::now();
                double t1=(double)duration_cast<nanoseconds>(e1-s1).count()/RUNS;
                double t2=(double)duration_cast<nanoseconds>(e2-s2).count()/RUNS;
                double t3=(double)duration_cast<nanoseconds>(e3-s3).count()/RUNS;
                printBarChart(t1,t2);
                cout<<"AStar: ("<<(long long)t3<<" ns)\n";
                break;}
            case 6: simulateTraffic(g); cout<<"Traffic simulated.\n"; break;
            case 7: if(!lastPath.empty()) drawGrid(g.V,lastPath); else cout<<"Run an algorithm first.\n"; break;
            case 8:{
                cout<<"Enter source and destination: "; cin>>src>>dest;
                auto s=high_resolution_clock::now();
                for(int i=0;i<RUNS;i++) lastPath=aStar(g,src,dest);
                auto e=high_resolution_clock::now();
                printPath(lastPath);
                cout<<"Time: "<<duration_cast<nanoseconds>(e-s).count()/RUNS<<" ns (avg of "<<RUNS<<" runs)\n";
                break;}
        }
    }while(choice!=0);
    return 0;
}
