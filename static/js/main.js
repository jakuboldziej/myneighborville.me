  function initMap(){
    const wrocław = {lat: 51.1079, lng: 17.0385};
    const rynek = {lat: 51.1104, lng: 17.0310};

    map = new google.maps.Map(document.getElementById("map"), {
      zoom: 13,
      center: wrocław,
    });
    addMarker(rynek, "Rynek", "<h1>Rynek</h1>");
  }

  function addMarker(location, title, content){
    const infowindow = new google.maps.InfoWindow({
      content: content,
    });
    marker = new google.maps.Marker({
      position: location,
      map: map,
      title: title,
    });
    marker.addListener("click", () => {
      infowindow.open({
        anchor: marker,
        map,
        shouldFocus: false,
      });
    });
  }

  window.initMap = initMap;