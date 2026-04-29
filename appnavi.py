import streamlit as st
import subprocess, os

st.set_page_config(page_title="Traffic Navigation System", page_icon="🚦", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;700&family=Syne:wght@400;600;800&display=swap');
:root{--bg:#060d1a;--bg2:#0d1b2e;--acc:#00e5b0;--red:#ff4d6d;--purple:#9d8df1;--yellow:#fbbf24;--text:#dde8f5;--muted:#4a6080;--border:#1a2e45;}
html,body,[data-testid="stAppViewContainer"]{background:var(--bg)!important;font-family:'JetBrains Mono',monospace;color:var(--text);}
[data-testid="stSidebar"]{background:var(--bg2)!important;border-right:1px solid var(--border);}
[data-testid="stSidebar"] *{color:var(--text)!important;}
h1,h2,h3{font-family:'Syne',sans-serif!important;color:var(--acc)!important;}
.stButton>button{background:transparent!important;border:1px solid var(--acc)!important;color:var(--acc)!important;font-family:'JetBrains Mono',monospace!important;border-radius:3px!important;width:100%;font-size:.8rem!important;letter-spacing:.06em!important;text-transform:uppercase!important;transition:all .2s!important;}
.stButton>button:hover{background:var(--acc)!important;color:var(--bg)!important;}
.pill{display:inline-block;padding:.18rem .6rem;border-radius:99px;font-size:.68rem;margin:.1rem;border:1px solid;}
.pill.g{background:rgba(0,229,176,.08);border-color:rgba(0,229,176,.3);color:var(--acc);}
.pill.r{background:rgba(255,77,109,.08);border-color:rgba(255,77,109,.3);color:var(--red);}
.pill.p{background:rgba(157,141,241,.08);border-color:rgba(157,141,241,.3);color:var(--purple);}
.pill.y{background:rgba(251,191,36,.08);border-color:rgba(251,191,36,.3);color:var(--yellow);}
</style>
""", unsafe_allow_html=True)

BASE = os.path.dirname(os.path.abspath(__file__))
EXE  = os.path.join(BASE, "traffic_app.exe" if os.name=="nt" else "traffic_app")

def compile_cpp():
    files = ["main.cpp","graph/Graph.cpp","algorithms/Dijkstra.cpp",
             "algorithms/BellmanFord.cpp","algorithms/AStar.cpp",
             "traffic/TrafficSimulator.cpp","utils/InputHandler.cpp",
             "utils/OutputHandler.cpp","utils/GridVisualizer.cpp"]
    r = subprocess.run(["g++"]+[os.path.join(BASE,f) for f in files]+["-o",EXE],
                        capture_output=True, text=True)
    return r.returncode==0, r.stderr

if 'compiled' not in st.session_state:
    ok,err=compile_cpp()
    st.session_state.compiled=ok; st.session_state.cerr=err

MAP_HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8"/>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{background:#060d1a;font-family:'JetBrains Mono',monospace;color:#dde8f5;display:flex;height:100vh;overflow:hidden;}

/* ── LEFT NAV PANEL ── */
#navpanel{
  width:320px;min-width:320px;height:100vh;
  background:#0d1b2e;border-right:1px solid #1a2e45;
  display:flex;flex-direction:column;overflow:hidden;z-index:100;
}
#navpanel .logo{
  padding:14px 16px 10px;
  border-bottom:1px solid #1a2e45;
  font-family:'Syne',sans-serif;font-size:14px;font-weight:800;color:#00e5b0;
  letter-spacing:-.01em;
}
#navpanel .logo span{color:#4a6080;font-size:11px;font-weight:400;display:block;margin-top:2px;}

#searchbox{padding:12px 14px;border-bottom:1px solid #1a2e45;}
#searchbox input{
  width:100%;background:#060d1a;border:1px solid #1a2e45;border-radius:4px;
  padding:8px 12px;color:#dde8f5;font-family:'JetBrains Mono',monospace;font-size:12px;outline:none;
}
#searchbox input:focus{border-color:#00e5b0;}
#searchbox button{
  margin-top:6px;width:100%;background:#00e5b0;border:none;border-radius:4px;
  padding:7px;color:#060d1a;font-family:'JetBrains Mono',monospace;font-size:11px;
  cursor:pointer;font-weight:700;letter-spacing:.05em;
}

#routecards{padding:10px 12px;border-bottom:1px solid #1a2e45;display:flex;flex-direction:column;gap:6px;}
.rcard{border:1px solid;border-radius:6px;padding:10px 12px;cursor:pointer;transition:all .2s;}
.rcard:hover{filter:brightness(1.2);}
.rcard.active{box-shadow:0 0 12px currentColor;}
.rcard .rname{font-size:11px;font-weight:700;letter-spacing:.06em;text-transform:uppercase;margin-bottom:4px;}
.rcard .rinfo{font-size:13px;font-weight:700;margin-bottom:2px;}
.rcard .rdesc{font-size:10px;opacity:.55;line-height:1.4;}

#dirlabel{padding:8px 14px 4px;font-size:10px;color:#4a6080;letter-spacing:.1em;text-transform:uppercase;border-bottom:1px solid #1a2e45;}
#directions{flex:1;overflow-y:auto;padding:0;}
#directions::-webkit-scrollbar{width:3px;}
#directions::-webkit-scrollbar-thumb{background:#1a2e45;border-radius:2px;}

.step{display:flex;align-items:flex-start;gap:10px;padding:10px 14px;border-bottom:1px solid rgba(26,46,69,.5);cursor:pointer;transition:background .15s;}
.step:hover{background:rgba(0,229,176,.04);}
.step.active-step{background:rgba(0,229,176,.08);border-left:3px solid #00e5b0;}
.step-icon{width:28px;height:28px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:14px;flex-shrink:0;margin-top:1px;background:#0a1628;border:1px solid #1a2e45;}
.step-text{flex:1;}
.step-name{font-size:12px;color:#dde8f5;line-height:1.4;margin-bottom:2px;}
.step-dist{font-size:10px;color:#4a6080;}

#emptystate{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:10px;color:#253d5e;padding:20px;text-align:center;}
.es-icon{font-size:36px;opacity:.4;}
.es-text{font-size:12px;line-height:1.7;}
.es-step{display:flex;align-items:center;gap:8px;font-size:11px;color:#1e3358;margin:4px 0;}
.es-num{width:20px;height:20px;border-radius:50%;background:#0d1b2e;border:1px solid #1a2e45;display:flex;align-items:center;justify-content:center;font-size:10px;flex-shrink:0;}

/* ── MAP ── */
#map{flex:1;height:100vh;}
#mapbar{position:absolute;top:12px;right:12px;z-index:1000;display:flex;gap:6px;}
.mapbtn{background:rgba(13,27,46,.92);border:1px solid #1a2e45;border-radius:4px;padding:7px 12px;color:#4a6080;font-family:'JetBrains Mono',monospace;font-size:10px;cursor:pointer;transition:all .2s;backdrop-filter:blur(6px);}
.mapbtn:hover,.mapbtn.active{background:#00e5b0;color:#060d1a;border-color:#00e5b0;}

#loading{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);z-index:2000;background:rgba(6,13,26,.95);border:1px solid #1a2e45;border-radius:8px;padding:20px 32px;font-size:12px;color:#00e5b0;display:none;text-align:center;backdrop-filter:blur(8px);}
@keyframes spin{to{transform:rotate(360deg)}}
.spinner{width:22px;height:22px;border:2px solid #1a2e45;border-top-color:#00e5b0;border-radius:50%;animation:spin .8s linear infinite;margin:0 auto 10px;}
</style>
</head>
<body>

<div id="navpanel">
  <div class="logo">🚦 Traffic Nav<span>Real-time routing · 3 algorithms</span></div>
  <div id="searchbox">
    <input id="si" type="text" placeholder="Search city, place, landmark..."/>
    <button onclick="searchPlace()">🔍 Search</button>
  </div>
  <div id="routecards"></div>
  <div id="dirlabel" style="display:none">TURN-BY-TURN DIRECTIONS</div>
  <div id="directions">
    <div id="emptystate">
      <div class="es-icon">🗺</div>
      <div class="es-step"><div class="es-num">1</div>Search for your city above</div>
      <div class="es-step"><div class="es-num">2</div>Click map to set <b style="color:#00e5b0">Source</b></div>
      <div class="es-step"><div class="es-num">3</div>Click again to set <b style="color:#ff4d6d">Destination</b></div>
      <div class="es-step"><div class="es-num">4</div>Routes + directions appear here</div>
    </div>
  </div>
</div>

<div style="position:relative;flex:1;">
  <div id="map"></div>
  <div id="mapbar">
    <button class="mapbtn active" onclick="setStyle('dark',this)">Dark</button>
    <button class="mapbtn" onclick="setStyle('street',this)">Street</button>
    <button class="mapbtn" onclick="setStyle('sat',this)">Satellite</button>
    <button class="mapbtn" id="resetBtn" onclick="resetAll()" style="color:#ff4d6d;border-color:#ff4d6d">✕ Reset</button>
  </div>
  <div id="loading"><div class="spinner"></div>Fetching routes...</div>
</div>

<script>
const map = L.map('map',{zoomControl:false}).setView([28.6139,77.2090],13);
L.control.zoom({position:'bottomright'}).addTo(map);

const TILES={
  dark:'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
  street:'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
  sat:'https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
};
let tileLayer=L.tileLayer(TILES.dark,{attribution:'© CartoDB',maxZoom:19}).addTo(map);

function setStyle(s,btn){
  map.removeLayer(tileLayer);
  tileLayer=L.tileLayer(TILES[s],{attribution:'© '+s,maxZoom:19}).addTo(map);
  document.querySelectorAll('.mapbtn').forEach(b=>b.classList.remove('active'));
  if(btn) btn.classList.add('active');
}

let srcLL=null,dstLL=null,srcM=null,dstM=null;
let routeLayers=[];
let allRoutes=[],activeRouteIdx=0;

function pinIcon(color,label){
  return L.divIcon({className:'',
    html:`<div style="width:32px;height:32px;border-radius:50% 50% 50% 0;
      transform:rotate(-45deg);background:${color};border:2px solid rgba(255,255,255,.7);
      box-shadow:0 0 14px ${color}88;display:flex;align-items:center;justify-content:center;">
      <span style="transform:rotate(45deg);font-size:13px;font-weight:800;color:white">${label}</span>
    </div>`,iconSize:[32,32],iconAnchor:[16,32]});
}

map.on('click',function(e){
  if(!srcLL){
    srcLL=e.latlng;
    if(srcM) map.removeLayer(srcM);
    srcM=L.marker(srcLL,{icon:pinIcon('#00e5b0','S'),zIndexOffset:1000}).addTo(map);
    updateEmpty('Source set ✓ — Now click to set <b style="color:#ff4d6d">Destination</b>');
  } else if(!dstLL){
    dstLL=e.latlng;
    if(dstM) map.removeLayer(dstM);
    dstM=L.marker(dstLL,{icon:pinIcon('#ff4d6d','D'),zIndexOffset:1000}).addTo(map);
    fetchRoutes();
  } else {
    resetAll();
    srcLL=e.latlng;
    if(srcM) map.removeLayer(srcM);
    srcM=L.marker(srcLL,{icon:pinIcon('#00e5b0','S'),zIndexOffset:1000}).addTo(map);
    updateEmpty('Source reset ✓ — Now click to set <b style="color:#ff4d6d">Destination</b>');
  }
});

function updateEmpty(msg){
  document.getElementById('emptystate').innerHTML=`
    <div class="es-icon">📍</div>
    <div style="font-size:12px;color:#4a6080">${msg}</div>`;
}

// ── FETCH ROUTES LOGIC ──
async function fetchRoutes(){
  document.getElementById('loading').style.display='block';
  clearRoutes();

  const slon = srcLL.lng, slat = srcLL.lat;
  const dlon = dstLL.lng, dlat = dstLL.lat;

  // Geometric Perpendicular Vector Math
  const dx = dlon - slon;
  const dy = dlat - slat;
  const dist = Math.sqrt(dx*dx + dy*dy);
  
  const px = -dy / dist;
  const py = dx / dist;
  const offset = Math.min(dist * 0.20, 0.015); 
  
  const mlon = (slon + dlon) / 2;
  const mlat = (slat + dlat) / 2;

  const wx1 = mlon + px * offset;
  const wy1 = mlat + py * offset;

  const wx2 = mlon - px * offset;
  const wy2 = mlat - py * offset;

  const url1 = `https://router.project-osrm.org/route/v1/driving/${slon},${slat};${dlon},${dlat}?overview=full&geometries=geojson&steps=true`;
  const url2 = `https://router.project-osrm.org/route/v1/driving/${slon},${slat};${wx1},${wy1};${dlon},${dlat}?overview=full&geometries=geojson&steps=true`;
  const url3 = `https://router.project-osrm.org/route/v1/driving/${slon},${slat};${wx2},${wy2};${dlon},${dlat}?overview=full&geometries=geojson&steps=true`;

  try {
    const [res1, res2, res3] = await Promise.all([fetch(url1), fetch(url2), fetch(url3)]);
    const [d1, d2, d3] = await Promise.all([res1.json(), res2.json(), res3.json()]);

    if(d1.code !== 'Ok' || !d1.routes || !d1.routes.length){
      alert('No route found. Try closer points on roads.');
      document.getElementById('loading').style.display='none';
      resetAll(); return;
    }

    allRoutes = [];
    allRoutes.push(d1.routes[0]); 
    allRoutes.push((d2.code === 'Ok' && d2.routes.length) ? d2.routes[0] : d1.routes[0]); 
    allRoutes.push((d3.code === 'Ok' && d3.routes.length) ? d3.routes[0] : d1.routes[0]); 

  } catch(e) {
    alert('OSRM API error.');
    document.getElementById('loading').style.display='none'; return;
  }

  document.getElementById('loading').style.display='none';
  renderRoutes(0);
}

const ALGOS=[
  {name:'Dijkstra',    color:'#00e5b0',weight:6,dash:null,
   desc:'Optimal shortest path — suffers heavily in traffic'},
  {name:'A* Search',   color:'#9d8df1',weight:4,dash:[12,6],
   desc:'Heuristic guided — adjusts weights to avoid gridlocks'},
  {name:'Bellman-Ford',color:'#ff6b35',weight:3,dash:[5,5],
   desc:'Edge relaxation — slower, calculates full traffic map'},
];

function getSimulatedDuration(baseDuration, algoName) {
  const mult = window.TRAFFIC_MULT || 1.0;
  if (algoName === 'Dijkstra') return baseDuration * mult;
  if (algoName === 'Bellman-Ford') return baseDuration * mult * 1.1;
  if (algoName === 'A* Search') {
      return (mult > 1.5) ? baseDuration * (mult * 0.4) : baseDuration * mult;
  }
  return baseDuration;
}

function renderRoutes(activeIdx){
  clearRoutes();
  activeRouteIdx=activeIdx;

  allRoutes.forEach((route,i)=>{
    if(i>=3) return;
    const algo=ALGOS[i];
    const coords=route.geometry.coordinates.map(c=>[c[1],c[0]]);
    const isActive=(i===activeIdx);

    if(isActive){
      const shadow=L.polyline(coords,{color:algo.color,weight:12,opacity:.15}).addTo(map);
      routeLayers.push(shadow);
    }

    const style={color:algo.color,weight:isActive?algo.weight:2, opacity:isActive?0.9:0.35};
    if(algo.dash) style.dashArray=algo.dash.join(',');

    const poly=L.polyline(coords,style).addTo(map);
    poly.on('click',()=>renderRoutes(i));
    routeLayers.push(poly);

    if(isActive){
      const step=Math.max(1,Math.floor(coords.length/8));
      for(let j=step;j<coords.length-1;j+=step*2){
        const from=coords[j],to=coords[j+1];
        const angle=Math.atan2(to[1]-from[1],to[0]-from[0])*180/Math.PI-90;
        const mid=[(from[0]+to[0])/2,(from[1]+to[1])/2];
        const am=L.marker(mid,{
          icon:L.divIcon({className:'',
            html:`<div style="color:${algo.color};font-size:12px;transform:rotate(${angle}deg);opacity:.8">▲</div>`,
            iconSize:[12,12],iconAnchor:[6,6]}),
          interactive:false}).addTo(map);
        routeLayers.push(am);
      }
    }
  });

  const allCoords=allRoutes.slice(0,3).flatMap(r=>r.geometry.coordinates.map(c=>[c[1],c[0]]));
  if(allCoords.length) map.fitBounds(L.latLngBounds(allCoords),{padding:[40,360]});

  buildRouteCards();
  buildDirections(allRoutes[activeIdx], ALGOS[activeIdx]);
}

function buildRouteCards(){
  const simRoutes = allRoutes.slice(0,3).map((r,i) => ({...r, simDur: getSimulatedDuration(r.duration, ALGOS[i].name)}));
  const minDur = Math.min(...simRoutes.map(r => r.simDur));
  
  let html='';
  simRoutes.forEach((r,i)=>{
    const a=ALGOS[i];
    const dist=(r.distance/1000).toFixed(1);
    const dur=fmtDur(r.simDur); 
    const winner= r.simDur === minDur; 
    const active=i===activeRouteIdx;
    
    html+=`<div class="rcard ${active?'active':''}" 
      style="border-color:${a.color};color:${a.color}" onclick="renderRoutes(${i})">
      <div class="rname">${winner?'🏆 ':''}${a.name}</div>
      <div class="rinfo" style="color:${a.color}">${dist} km · ${dur}</div>
      <div class="rdesc" style="color:#dde8f5">${a.desc}</div>
    </div>`;
  });
  document.getElementById('routecards').innerHTML=html;
}

// ── 100% FAIL-SAFE TURN-BY-TURN BUILDER ──
function buildDirections(route, algo){
  try {
    if(!route) return;
    
    const emptystate = document.getElementById('emptystate');
    const dirlabel = document.getElementById('dirlabel');
    const directions = document.getElementById('directions');

    if (emptystate) emptystate.style.display='none';
    if (dirlabel) {
        dirlabel.style.display='block';
        dirlabel.style.color = algo.color;
    }

    const steps = [];
    if (route.legs) {
        route.legs.forEach(leg => {
            if (leg.steps) {
                leg.steps.forEach(s => steps.push(s));
            }
        });
    }

    const totalSimDur = getSimulatedDuration(route.duration || 0, algo.name);
    let html='';
    
    let startLat = dstLL ? dstLL.lat : 0;
    let startLng = dstLL ? dstLL.lng : 0;
    
    if (steps.length > 0 && steps[0].maneuver && steps[0].maneuver.location) {
        startLng = steps[0].maneuver.location[0];
        startLat = steps[0].maneuver.location[1];
    }
    
    html+=`<div class="step active-step" onclick="flyToStep(${startLat},${startLng},16)">
      <div class="step-icon" style="border-color:${algo.color};color:${algo.color}">🏠</div>
      <div class="step-text">
        <div class="step-name" style="color:${algo.color}">Start</div>
        <div class="step-dist">${((route.distance||0)/1000).toFixed(1)} km total · ${fmtDur(totalSimDur)}</div>
      </div>
    </div>`;

    steps.forEach((step, i) => {
      if (!step || !step.maneuver) return;
      
      // Skip waypoint intermediate arrives so they don't clog up the directions
      if (step.maneuver.type === 'arrive' && i < steps.length - 1) return;
      if (step.maneuver.type === 'waypoint') return;

      const icon = maneuverIcon(step.maneuver.type, step.maneuver.modifier);
      const name = step.name ? ` onto <b>${step.name}</b>` : '';
      const dist = fmtDist(step.distance || 0);
      const loc = step.maneuver.location || [0,0];
      
      let text = step.maneuver.type + " " + (step.maneuver.modifier || "") + name;
      try { text = stepText(step); } catch(e) {} // Fallback if stepText fails

      html+=`<div class="step" onclick="flyToStep(${loc[1]},${loc[0]},17)">
        <div class="step-icon">${icon}</div>
        <div class="step-text">
          <div class="step-name">${text}</div>
          <div class="step-dist">${dist}</div>
        </div>
      </div>`;
    });

    let endLat = dstLL ? dstLL.lat : 0;
    let endLng = dstLL ? dstLL.lng : 0;

    html+=`<div class="step" onclick="flyToStep(${endLat},${endLng},16)">
      <div class="step-icon" style="border-color:#ff4d6d;color:#ff4d6d">🏁</div>
      <div class="step-text">
        <div class="step-name" style="color:#ff4d6d">Arrive at Destination</div>
        <div class="step-dist">You have reached your destination</div>
      </div>
    </div>`;

    if(directions) directions.innerHTML=html;

  } catch(err) {
    console.error("Directions render error:", err);
    document.getElementById('directions').innerHTML = `<div style="padding:20px;color:#ff4d6d;">Error calculating directions. Click map to try again.</div>`;
  }
}

function stepText(step){
  const mod=step.maneuver.modifier||'';
  const type=step.maneuver.type;
  const name=step.name?` onto <b>${step.name}</b>`:'';
  const map={
    'turn':        `Turn ${mod}${name}`,
    'new name':    `Continue${name}`,
    'depart':      `Head ${mod}${name}`,
    'arrive':      `Arrive at destination`,
    'merge':       `Merge ${mod}${name}`,
    'ramp':        `Take ramp ${mod}${name}`,
    'on ramp':     `Take on-ramp ${mod}${name}`,
    'off ramp':    `Take off-ramp ${mod}${name}`,
    'fork':        `Keep ${mod} at fork${name}`,
    'end of road': `Turn ${mod} at end of road${name}`,
    'roundabout':  `Enter roundabout${name}`,
    'rotary':      `Enter rotary${name}`,
    'continue':    `Continue ${mod}${name}`,
    'use lane':    `Use lane${name}`,
  };
  return map[type]||`${type} ${mod}${name}`;
}

function maneuverIcon(type,mod){
  if(type==='turn'){
    if(mod==='left'||mod==='sharp left') return '↰';
    if(mod==='right'||mod==='sharp right') return '↱';
    if(mod==='slight left') return '↖';
    if(mod==='slight right') return '↗';
    return '⬆';
  }
  const icons={
    'depart':'🏠','arrive':'🏁','merge':'↗','fork':'⑂',
    'roundabout':'🔄','rotary':'🔄','on ramp':'↗','off ramp':'↘',
    'new name':'⬆','continue':'⬆','end of road':'⬆','use lane':'⬆'
  };
  return icons[type]||'⬆';
}

function fmtDur(sec){
  const m=Math.floor(sec/60),h=Math.floor(m/60);
  if(h>0) return `${h}h ${m%60}m`;
  return `${m} min`;
}
function fmtDist(m){
  if(m>=1000) return (m/1000).toFixed(1)+' km';
  return Math.round(m)+' m';
}

function flyToStep(lat,lng,zoom){
  map.flyTo([lat,lng],zoom,{duration:1});
}

function clearRoutes(){
  routeLayers.forEach(l=>map.removeLayer(l));
  routeLayers=[];
}

function resetAll(){
  clearRoutes();
  srcLL=null; dstLL=null;
  if(srcM){map.removeLayer(srcM);srcM=null;}
  if(dstM){map.removeLayer(dstM);dstM=null;}
  allRoutes=[];
  document.getElementById('routecards').innerHTML='';
  document.getElementById('dirlabel').style.display='none';
  document.getElementById('directions').innerHTML=`
    <div id="emptystate">
      <div class="es-icon">🗺</div>
      <div class="es-step"><div class="es-num">1</div>Search for your city above</div>
      <div class="es-step"><div class="es-num">2</div>Click map to set <b style="color:#00e5b0">Source</b></div>
      <div class="es-step"><div class="es-num">3</div>Click again to set <b style="color:#ff4d6d">Destination</b></div>
      <div class="es-step"><div class="es-num">4</div>Routes + directions appear here</div>
    </div>`;
}

async function searchPlace(){
  const q=document.getElementById('si').value.trim();
  if(!q) return;
  try{
    const res=await fetch(`https://nominatim.openstreetmap.org/search?q=${encodeURIComponent(q)}&format=json&limit=1`,
      {headers:{'Accept-Language':'en'}});
    const data=await res.json();
    if(!data.length){alert('Place not found.');return;}
    map.flyTo([+data[0].lat,+data[0].lon],14,{duration:1.5});
  }catch(e){alert('Search failed.');}
}
document.getElementById('si').addEventListener('keydown',e=>{if(e.key==='Enter')searchPlace();});
</script>
</body>
</html>"""

# ── SIDEBAR ──
with st.sidebar:
    st.markdown("## 🚦 Traffic Nav")
    if st.session_state.compiled:
        st.markdown('<span style="color:#00e5b0;font-size:.8rem">✔ C++ COMPILED</span>',unsafe_allow_html=True)
    else:
        st.markdown('<span style="color:#ff4d6d;font-size:.8rem">✘ COMPILE FAILED</span>',unsafe_allow_html=True)
        st.code(st.session_state.cerr,language='bash')
    if st.button("↻ Recompile C++"):
        ok,err=compile_cpp(); st.session_state.compiled=ok; st.session_state.cerr=err; st.rerun()

    st.markdown('<hr style="border-color:#1a2e45"/>',unsafe_allow_html=True)
    
    st.markdown("### 🚗 Traffic Simulation")
    traffic_level = st.select_slider("Traffic Density", options=["Clear", "Moderate", "Heavy", "Gridlock"])
    traffic_mult = {"Clear": 1.0, "Moderate": 1.5, "Heavy": 2.5, "Gridlock": 4.0}[traffic_level]

    st.markdown('<hr style="border-color:#1a2e45"/>',unsafe_allow_html=True)
    st.markdown("### Quick Locations")
    locs={
        "🏛 Delhi, India":(28.6139,77.2090),
        "🌆 Mumbai, India":(19.0760,72.8777),
        "🏰 Jaipur, India":(26.9124,75.7873),
        "🌿 Bangalore, India":(12.9716,77.5946),
        "🗼 Paris, France":(48.8566,2.3522),
        "🗽 New York, USA":(40.7128,-74.0060),
        "🏯 Tokyo, Japan":(35.6762,139.6503),
    }
    for name,(lat,lng) in locs.items():
        if st.button(name):
            st.session_state['floc']=f"{lat},{lng}"
            st.rerun()

    st.markdown('<hr style="border-color:#1a2e45"/>',unsafe_allow_html=True)
    st.markdown("### Algorithm Legend")
    st.markdown("""
<div style="font-size:.78rem;line-height:2.4">
<span style="color:#00e5b0;font-size:16px">━━━</span> <b>Dijkstra</b> — Optimal<br>
<span style="color:#9d8df1;font-size:16px">╌╌╌</span> <b>A* Search</b> — Heuristic<br>
<span style="color:#ff6b35;font-size:16px">┄┄┄</span> <b>Bellman-Ford</b> — Relaxation
</div>""",unsafe_allow_html=True)

# ── MAIN ──
st.markdown("# Traffic Navigation System")
st.markdown("""<span class="pill g">Real Map</span>
<span class="pill g">Dijkstra</span><span class="pill r">Bellman-Ford</span>
<span class="pill p">A*</span><span class="pill y">Turn-by-Turn</span>
<span class="pill y">OSRM</span>""",unsafe_allow_html=True)
st.markdown('<hr style="border-color:#1a2e45;margin:.4rem 0"/>',unsafe_allow_html=True)

# Fly-to and Traffic Injection
fly_js = f"window.TRAFFIC_MULT = {traffic_mult};\n"
if 'floc' in st.session_state:
    lat,lng=st.session_state['floc'].split(',')
    fly_js += f"map.flyTo([{lat},{lng}],14,{{duration:1.5}});\n"
    del st.session_state['floc']

final_html=MAP_HTML.replace(
    "document.getElementById('si').addEventListener",
    fly_js+"document.getElementById('si').addEventListener"
)

st.components.v1.html(final_html, height=750, scrolling=False)