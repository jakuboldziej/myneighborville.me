const key = 'pk.eyJ1IjoiYmJrdWJlayIsImEiOiJjbDkwYmp4djcwMW8xM3Rtd2VyZG9za24zIn0.qhY72HdrmGVV6nEznDl2sQ';
const x = 51.108359435221300 
const y = 17.033173734577653
const map = L.map('map').setView([x , y], 13);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    accessToken: key
}).addTo(map);

const marker = L.marker([51.11035599061707, 17.031017734094917]).addTo(map);
marker.bindPopup('Wyprowadź psa');