export let map = null;
export const setMap = (newMap) => {
    map = newMap;
};

export let waypoints=[]
export const setWaypoint = (newWaypoints) => {
    waypoints = newWaypoints;
};

export let center= [10.7388542,106.7319975];
export const setCenter= (lat,lon)=>{
    center=[lat,lon];
}

export let compassAngle=50;
export const setCompassAngel=(angel)=>{
    compassAngle=angel
}

export let mapMarkers=[];
export const setmapMarkers=(newMapMarkers)=>{
    mapMarkers=newMapMarkers
}

export let polyline = null;
export const setpolyline = (newPolyline) => {
  polyline = newPolyline;
}
