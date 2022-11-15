//var hudstats = geojson_hud_county;
var pubstats = pubs;

console.log('pubs =')
console.log(pubs)

var cities = L.layerGroup();
var background = L.layerGroup();
var pubLayer = L.layerGroup();


//var mbAttr = 'Map data &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>';
var mbAttr = 'MapBox';
var mbUrl = 'https://api.mapbox.com/styles/v1/{id}/tiles/{z}/{x}/{y}?access_token=pk.eyJ1IjoibWFwYm94IiwiYSI6ImNpejY4NXVycTA2emYycXBndHRqcmZ3N3gifQ.rJcFIG214AriISLbB6B5aw';


var streets = L.tileLayer(mbUrl, {id: 'mapbox/streets-v11', tileSize: 512, zoomOffset: -1, attribution: mbAttr});

var osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
		maxZoom: 19,
		// attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
		attribution: ' '
	});


//var map = L.map('map').setView([37.8, -96], 4);
var map = L.map('map', {
		center: [0, 0],
		zoom: 2,
		minZoom: 2,
		maxZoom: 18,
		zoomSnap: 0.25,
		layers: [osm]
	});

	var baseLayers = {
		'OpenStreetMap': osm,
		'Streets': streets,
	};

	var overlays = {
		'Pubs': pubLayer,
		//'Background': background
	};

	var layerControl = L.control.layers(baseLayers, overlays).addTo(map);

	var satellite = L.tileLayer(mbUrl, {id: 'mapbox/satellite-v9', tileSize: 512, zoomOffset: -1, attribution: mbAttr});
	layerControl.addBaseLayer(satellite, 'Satellite');


	var tiles = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
		maxZoom: 19,
		//attribution: '&copy; <a href="http://www.openstreetmap.org/copyright" target="_blank" rel="noopener">OpenStreetMap</a>'
		//attribution: ''
	}).addTo(map);


// control that shows state info on hover
var info = L.control();


info.onAdd = function (map) {
		this._div = L.DomUtil.create('div', 'info');
		this.update();
		return this._div;
	};


info.update = function (props) {
	this._div.innerHTML = (props ? '<b>' + props.LSAD + ' ' + props.NAME + '</b>' +
	'<br>$' + props['Income Level']['value'].toLocaleString("en-US") + ' Income Level' +
	'<br>$' + props['FMR']['value'].toLocaleString("en-US") + ' Fair Market Rent - Efficiency' +
	'<br>' +  Math.round(props['ratio']['value']*100) + '% FMR/Income' +
	'<br>' +  Math.round(props['slope']['value']*100000) + '% Slope'
	 :'<br>Hover over a county');
	};


info.addTo(map);


function style(feature) {
		return {
			weight: 0,
			opacity: 1,
			color: 'white',
			dashArray: '3',
			fillOpacity: 0.7,
			fillColor: feature.properties['color']
		};
	}


function highlightFeature(e) {
		var layer = e.target;

		layer.setStyle({
			//weight: 5,
			//color: '#666',
			//dashArray: '',
			//fillOpacity: 0.7
		});

		if (!L.Browser.ie && !L.Browser.opera && !L.Browser.edge) {
			layer.bringToFront();
		}

		info.update(layer.feature.properties);
	}


function resetHighlight(e) {
		geojson_counties.resetStyle(e.target);
		info.update();
	}


function zoomToFeature(e) {
		map.fitBounds(e.target.getBounds());
	}


function onEachFeature(feature, layer) {
		layer.on({
			mouseover: highlightFeature,
			mouseout: resetHighlight,
			click: zoomToFeature
		});
	}


const polygon = L.polygon(
	[[180, 180], [-180, 180], [-180, -180], [180, -180], [180, 180]],
	{
		color: 'white',
		fillColor: 'white',
		fillOpacity: 0.4,
	}
).addTo(map).addTo(background);



function onEachTrial(feature, layer) {

			var aff = feature.properties.aff;
	    var url = feature.properties.url;
	    var title = feature.properties.title;

			map.createPane('popUpPane');
	    map.getPane('popUpPane').style.zIndex = 999;

	    var popupContent = '<p><b>'
	         + feature.properties.title
	         + '</b><br>'
	         + feature.properties.aff
	         + '<br>'
	         + '<a href="' + feature.properties.url + '" target="_blank" rel="noopener">'
	         + feature.properties.url + '</a>'
	         + '</p>';

	    if (feature.properties && feature.properties.popupContent) {
	            popupContent += feature.properties.popupContent;
	          }
	     layer.bindPopup(popupContent);
	  }


function trialStyle (feature) {
	    return feature.properties && feature.properties.style;
			}


function trialToLayer(feature, latlng) {

		var paneName = feature.properties.paneName;
		var zindex = feature.properties.zindex;
		console.log('paneName = ')
		console.log(paneName)
		console.log('zindex = ')
		console.log(zindex)

			map.createPane(paneName);
	    map.getPane(paneName).style.zIndex = zindex;
	    return L.circleMarker(latlng, {
	      radius: feature.properties.radius,
	      opacity:feature.properties.opacity,
	      fillOpacity: feature.properties.opacity,
	      fillColor: feature.properties.color,
	      color: 'black',
	      weight: 1,
	      pane: paneName,
	    });
	  }


var pubLayer = L.geoJson(pubstats, {
		style: trialStyle,
		onEachFeature: onEachTrial,
		pointToLayer: trialToLayer,
		}).addTo(map).addTo(pubLayer);


/* cite source of information */
map.attributionControl.addAttribution('| <a href="https://www.crossref.org/" target="_blank" rel="noopener">Crossref</a> | <a href="https://scholar.google.com/" target="_blank" rel="noopener"> Google Scholar </a> | <a href="https://www.openstreetmap.org" target="_blank" rel="noopener">OpenStreetMap</a>  | <a href="https://www.roosterbio.com/" target="_blank" rel="noopener">RoosterBio</a> ');
