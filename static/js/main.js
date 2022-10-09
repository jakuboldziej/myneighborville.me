function initMap(){
  const wrocław = {lat: 51.1079, lng: 17.0385};
  const rynek = {lat: 51.1104, lng: 17.0310};

  const map = new google.maps.Map(document.getElementById("map"), {
    zoom: 13,
    center: wrocław,
  });

  const marker = new google.maps.Marker({
    position: rynek,
    map,
    title: "Rynek",
  });
  const infowindow = new google.maps.InfoWindow({
    content: "<h1>Rynek</h1>",
  });
  
  marker.addListener('click', function(){
    infowindow.open(map, marker);
  });  
}
window.initMap = initMap;