(() => {
  const years = [2019, 2021, 2023, 2025];
  const studyView = { center: [45.876, -64.244], zoom: 11 };

  const observations = {
    2019: {
      count: 18,
      flagged: 2,
      zones: [
        [[45.918,-64.316],[45.925,-64.293],[45.918,-64.270],[45.905,-64.273],[45.899,-64.294],[45.907,-64.314]],
        [[45.851,-64.286],[45.858,-64.266],[45.851,-64.244],[45.838,-64.248],[45.833,-64.269],[45.840,-64.285]],
        [[45.936,-64.236],[45.943,-64.218],[45.936,-64.199],[45.926,-64.201],[45.922,-64.221],[45.928,-64.235]],
        [[45.816,-64.214],[45.823,-64.197],[45.817,-64.180],[45.806,-64.183],[45.802,-64.200],[45.808,-64.213]]
      ]
    },
    2021: {
      count: 23,
      flagged: 3,
      zones: [
        [[45.920,-64.322],[45.930,-64.295],[45.921,-64.263],[45.902,-64.267],[45.894,-64.294],[45.905,-64.320]],
        [[45.856,-64.292],[45.864,-64.263],[45.852,-64.237],[45.835,-64.242],[45.827,-64.269],[45.839,-64.291]],
        [[45.939,-64.242],[45.948,-64.216],[45.937,-64.191],[45.921,-64.196],[45.916,-64.222],[45.927,-64.240]],
        [[45.820,-64.221],[45.829,-64.196],[45.818,-64.173],[45.801,-64.179],[45.797,-64.204],[45.808,-64.220]]
      ]
    },
    2023: {
      count: 29,
      flagged: 4,
      zones: [
        [[45.923,-64.329],[45.934,-64.299],[45.924,-64.256],[45.898,-64.260],[45.887,-64.293],[45.901,-64.325]],
        [[45.860,-64.300],[45.870,-64.264],[45.855,-64.229],[45.830,-64.236],[45.820,-64.270],[45.837,-64.298]],
        [[45.942,-64.249],[45.954,-64.216],[45.940,-64.181],[45.916,-64.189],[45.908,-64.225],[45.925,-64.247]],
        [[45.825,-64.229],[45.836,-64.195],[45.821,-64.164],[45.796,-64.173],[45.788,-64.208],[45.807,-64.227]],
        [[45.890,-64.195],[45.896,-64.178],[45.889,-64.163],[45.878,-64.168],[45.876,-64.184],[45.882,-64.194]]
      ]
    },
    2025: {
      count: 34,
      flagged: 5,
      zones: [
        [[45.926,-64.336],[45.939,-64.300],[45.927,-64.247],[45.893,-64.252],[45.880,-64.292],[45.898,-64.331]],
        [[45.864,-64.309],[45.876,-64.264],[45.858,-64.219],[45.824,-64.228],[45.810,-64.270],[45.835,-64.306]],
        [[45.946,-64.257],[45.960,-64.215],[45.943,-64.170],[45.909,-64.181],[45.898,-64.226],[45.923,-64.253]],
        [[45.830,-64.237],[45.844,-64.193],[45.824,-64.152],[45.790,-64.165],[45.779,-64.210],[45.805,-64.234]],
        [[45.895,-64.204],[45.904,-64.177],[45.893,-64.152],[45.874,-64.160],[45.869,-64.185],[45.881,-64.202]]
      ]
    }
  };

  const assets = [
    { id: 'tch-low', name: 'Trans-Canada Highway · Low Point', short: 'TCH Low Point', type: 'Transportation corridor', location: 'Aulac, New Brunswick', lat: 45.872, lng: -64.277, distance: '180 m', trend: '+31%', priority: 'high', status: 'Inspection recommended', series: [28,36,47,61] },
    { id: 'rail-crossing', name: 'CN Rail · Tantramar Crossing', short: 'CN Rail Crossing', type: 'Rail infrastructure', location: 'Tantramar Marshes', lat: 45.894, lng: -64.244, distance: '260 m', trend: '+23%', priority: 'high', status: 'Review drainage', series: [30,34,43,53] },
    { id: 'aboiteau-7', name: 'Aboiteau A-07', short: 'Aboiteau A-07', type: 'Water-control structure', location: 'LaPlanche River sector', lat: 45.842, lng: -64.236, distance: '90 m', trend: '+18%', priority: 'warning', status: 'Field check suggested', series: [35,42,45,53] },
    { id: 'dyke-north', name: 'Northern Dyke Segment', short: 'North Dyke Segment', type: 'Coastal protection', location: 'Upper Sackville sector', lat: 45.931, lng: -64.221, distance: '340 m', trend: '+12%', priority: 'normal', status: 'Monitor', series: [33,37,42,45] },
    { id: 'pump-east', name: 'East Marsh Pump Station', short: 'Pump Station', type: 'Municipal infrastructure', location: 'Amherst, Nova Scotia', lat: 45.818, lng: -64.184, distance: '210 m', trend: '+9%', priority: 'warning', status: 'Review maintenance history', series: [41,43,47,50] }
  ];

  const properties = [
    {name:'Sample parcel 101', value:'$318k', lat:45.864, lng:-64.250},
    {name:'Sample parcel 102', value:'$426k', lat:45.881, lng:-64.232},
    {name:'Sample parcel 103', value:'$287k', lat:45.849, lng:-64.207},
    {name:'Sample parcel 104', value:'$395k', lat:45.906, lng:-64.274},
    {name:'Sample parcel 105', value:'$352k', lat:45.828, lng:-64.222},
    {name:'Sample parcel 106', value:'$470k', lat:45.900, lng:-64.207}
  ];

  if (!window.L) {
    document.getElementById('map').innerHTML = '<div style="padding:100px 30px;text-align:center;color:#29445d"><h2>Map library unavailable</h2><p>Connect to the internet to load the OpenStreetMap demo.</p></div>';
    return;
  }

  const map = L.map('map', { zoomControl: false, attributionControl: true, minZoom: 8, maxZoom: 17 }).setView(studyView.center, studyView.zoom);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map);

  map.createPane('corridors'); map.getPane('corridors').style.zIndex = 410;
  map.createPane('water'); map.getPane('water').style.zIndex = 420;
  map.createPane('anomaly'); map.getPane('anomaly').style.zIndex = 430;
  map.createPane('assets'); map.getPane('assets').style.zIndex = 450;

  const waterGroup = L.layerGroup().addTo(map);
  const anomalyGroup = L.layerGroup().addTo(map);
  const assetGroup = L.layerGroup().addTo(map);
  const propertyGroup = L.layerGroup();
  const baselineGroup = L.layerGroup();
  let currentYearIndex = 3;
  let selectedAsset = assets[0];
  let playing = false;
  let playTimer = null;

  const corridorLine = L.polyline([
    [45.989,-64.280],[45.951,-64.254],[45.916,-64.272],[45.886,-64.292],[45.855,-64.261],[45.824,-64.218],[45.795,-64.196],[45.772,-64.166]
  ], { pane:'corridors', color:'#f4a522', weight:5, opacity:.88 }).addTo(map);
  corridorLine.bindTooltip('Trans-Canada Highway corridor', { sticky:true, className:'map-tooltip' });

  const railLine = L.polyline([
    [45.986,-64.303],[45.947,-64.286],[45.913,-64.264],[45.883,-64.247],[45.851,-64.219],[45.818,-64.191],[45.783,-64.177]
  ], { pane:'corridors', color:'#45596d', weight:3, opacity:.82, dashArray:'9 7' }).addTo(map);
  railLine.bindTooltip('CN rail corridor · schematic overlay', { sticky:true, className:'map-tooltip' });

  const dykeLine = L.polyline([
    [45.947,-64.310],[45.930,-64.290],[45.913,-64.284],[45.897,-64.264],[45.879,-64.252],[45.858,-64.229],[45.842,-64.206]
  ], { pane:'corridors', color:'#287d5d', weight:4, opacity:.85, dashArray:'2 8' }).addTo(map);
  dykeLine.bindTooltip('Existing dyke alignment · schematic', { sticky:true, className:'map-tooltip' });

  function markerIcon(asset) {
    const cls = asset.priority === 'high' ? 'high' : asset.priority === 'warning' ? 'warning' : '';
    return L.divIcon({ className:'', html:`<div class="asset-marker ${cls}">${asset.type.startsWith('Rail') ? 'R' : asset.type.startsWith('Water') ? 'A' : asset.type.startsWith('Coastal') ? 'D' : asset.type.startsWith('Municipal') ? 'P' : 'H'}</div>`, iconSize:[22,22], iconAnchor:[11,11] });
  }

  const assetMarkers = new Map();
  assets.forEach(asset => {
    const marker = L.marker([asset.lat, asset.lng], { pane:'assets', icon:markerIcon(asset), title:asset.name });
    marker.on('click', () => selectAsset(asset, true));
    marker.bindTooltip(asset.short, { direction:'top', offset:[0,-9], className:'map-tooltip' });
    marker.addTo(assetGroup);
    assetMarkers.set(asset.id, marker);
  });

  properties.forEach(property => {
    L.marker([property.lat, property.lng], {
      pane:'assets',
      icon:L.divIcon({className:'', html:'<div class="property-marker"></div>', iconSize:[13,13], iconAnchor:[7,7]})
    }).bindPopup(`<strong>${property.name}</strong><br>Illustrative assessed value: ${property.value}<br><small>Not linked to an actual parcel</small>`).addTo(propertyGroup);
  });

  function drawWater(year) {
    waterGroup.clearLayers();
    anomalyGroup.clearLayers();
    const zoneSet = observations[year].zones;
    zoneSet.forEach((coords, index) => {
      const polygon = L.polygon(coords, {
        pane:'water', color:'#1b86b1', weight:1.4, fillColor:'#26a7d0', fillOpacity:.27 + index * .018
      }).bindTooltip(`Illustrative water signal · Zone ${index + 1}`, { sticky:true, className:'map-tooltip' });
      polygon.addTo(waterGroup);

      if (year !== 2019 && index < Math.min(observations[year].flagged, zoneSet.length)) {
        L.polygon(coords, {
          pane:'anomaly', color:'#e56b4f', weight:2, dashArray:'6 5', fillColor:'#ef8a69', fillOpacity:.08, interactive:false
        }).addTo(anomalyGroup);
      }
    });
  }

  function drawBaseline(show) {
    baselineGroup.clearLayers();
    if (!show) { if (map.hasLayer(baselineGroup)) map.removeLayer(baselineGroup); return; }
    observations[2019].zones.forEach(coords => {
      L.polygon(coords, {pane:'anomaly', color:'#6a4eb4', weight:2, dashArray:'3 5', fillOpacity:0, interactive:false}).addTo(baselineGroup);
    });
    baselineGroup.addTo(map);
  }

  function updateYear(index) {
    currentYearIndex = Number(index);
    const year = years[currentYearIndex];
    document.getElementById('yearSlider').value = currentYearIndex;
    document.getElementById('yearLabel').textContent = year;
    document.getElementById('observationCount').textContent = observations[year].count;
    document.getElementById('flaggedCount').textContent = observations[year].flagged;
    document.querySelectorAll('.year-ticks button').forEach((button, i) => button.classList.toggle('active', i === currentYearIndex));
    drawWater(year);
    if (!document.getElementById('waterToggle').checked) map.removeLayer(waterGroup);
    if (!document.getElementById('anomalyToggle').checked) map.removeLayer(anomalyGroup);
    if (document.getElementById('compareButton').classList.contains('active')) drawBaseline(true);
    document.getElementById('detailObserved').textContent = year;
  }

  function selectAsset(asset, pan = false) {
    selectedAsset = asset;
    document.getElementById('detailType').textContent = asset.type.toUpperCase();
    document.getElementById('detailName').textContent = asset.name;
    document.getElementById('detailLocation').textContent = asset.location;
    document.getElementById('detailDistance').textContent = asset.distance;
    document.getElementById('detailTrend').textContent = asset.trend;
    document.getElementById('detailStatus').querySelector('strong').textContent = asset.status;
    document.getElementById('detailConfidence').textContent = 'Demo';
    document.getElementById('detailPanel').classList.remove('closed');
    document.getElementById('addInspection').textContent = 'Add to field inspection plan';
    document.getElementById('addInspection').classList.remove('added');
    document.querySelectorAll('.queue-item').forEach(item => item.classList.toggle('active', item.dataset.id === asset.id));
    drawSparkline(asset.series);
    if (pan) map.flyTo([asset.lat, asset.lng], 13, {duration:.65});
  }

  function drawSparkline(values) {
    const svg = document.getElementById('sparkline');
    const min = Math.min(...values) - 5;
    const max = Math.max(...values) + 5;
    const points = values.map((v,i) => `${10 + i * 83.3},${60 - ((v-min)/(max-min))*48}`).join(' ');
    const areaPoints = `10,62 ${points} 260,62`;
    svg.innerHTML = `<defs><linearGradient id="sparkFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a9cc8" stop-opacity=".28"/><stop offset="1" stop-color="#2a9cc8" stop-opacity="0"/></linearGradient></defs><line x1="10" y1="62" x2="260" y2="62" stroke="#dfe5e9" stroke-width="1"/><polygon points="${areaPoints}" fill="url(#sparkFill)" stroke="none"/><polyline points="${points}" fill="none" stroke="#258ab5" stroke-width="2.5"/>${points.split(' ').map(p => {const [x,y]=p.split(','); return `<circle cx="${x}" cy="${y}" r="3.5" fill="#fff" stroke="#258ab5" stroke-width="2"/>`;}).join('')}`;
  }

  function renderQueue() {
    const queue = assets.filter(a => a.priority !== 'normal').slice(0,3);
    document.getElementById('queueCount').textContent = `${queue.length} sites`;
    document.getElementById('inspectionQueue').innerHTML = queue.map(asset => `<button class="queue-item" data-id="${asset.id}"><i class="queue-severity ${asset.priority}"></i><span><strong>${asset.short}</strong><small>${asset.status}</small></span><em>${asset.distance}</em></button>`).join('');
    document.querySelectorAll('.queue-item').forEach(item => item.addEventListener('click', () => selectAsset(assets.find(a => a.id === item.dataset.id), true)));
  }

  function showToast(message) {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.hidden = false;
    clearTimeout(showToast.timer);
    showToast.timer = setTimeout(() => toast.hidden = true, 2600);
  }

  function toggleLayer(id, layer) {
    document.getElementById(id).addEventListener('change', e => e.target.checked ? layer.addTo(map) : map.removeLayer(layer));
  }

  toggleLayer('waterToggle', waterGroup);
  toggleLayer('anomalyToggle', anomalyGroup);
  toggleLayer('assetsToggle', assetGroup);
  toggleLayer('propertyToggle', propertyGroup);

  document.getElementById('resetLayers').addEventListener('click', () => {
    ['waterToggle','anomalyToggle','assetsToggle'].forEach(id => { document.getElementById(id).checked = true; });
    document.getElementById('propertyToggle').checked = false;
    [waterGroup, anomalyGroup, assetGroup].forEach(layer => layer.addTo(map));
    map.removeLayer(propertyGroup);
    showToast('Default monitoring layers restored');
  });

  document.getElementById('yearSlider').addEventListener('input', e => updateYear(e.target.value));
  document.querySelectorAll('.year-ticks button').forEach(button => button.addEventListener('click', () => updateYear(button.dataset.index)));

  document.getElementById('playButton').addEventListener('click', () => {
    playing = !playing;
    document.querySelector('.play-icon').hidden = playing;
    document.querySelector('.pause-icon').hidden = !playing;
    clearInterval(playTimer);
    if (playing) {
      if (currentYearIndex === years.length - 1) updateYear(0);
      playTimer = setInterval(() => {
        if (currentYearIndex >= years.length - 1) {
          playing = false; clearInterval(playTimer);
          document.querySelector('.play-icon').hidden = false;
          document.querySelector('.pause-icon').hidden = true;
        } else updateYear(currentYearIndex + 1);
      }, 1100);
    }
  });

  document.getElementById('compareButton').addEventListener('click', e => {
    const button = e.currentTarget;
    button.classList.toggle('active');
    drawBaseline(button.classList.contains('active'));
    showToast(button.classList.contains('active') ? '2019 baseline outlined in purple' : 'Baseline comparison hidden');
  });

  document.getElementById('collapseLeft').addEventListener('click', () => {
    document.querySelector('.left-panel').classList.add('collapsed');
    document.getElementById('reopenLeft').hidden = false;
  });
  document.getElementById('reopenLeft').addEventListener('click', () => {
    document.querySelector('.left-panel').classList.remove('collapsed');
    document.getElementById('reopenLeft').hidden = true;
  });
  document.getElementById('closeDetails').addEventListener('click', () => document.getElementById('detailPanel').classList.add('closed'));
  document.getElementById('homeButton').addEventListener('click', () => map.flyTo(studyView.center, studyView.zoom));
  document.getElementById('locateButton').addEventListener('click', () => map.flyTo(studyView.center, studyView.zoom));
  document.getElementById('zoomIn').addEventListener('click', () => map.zoomIn());
  document.getElementById('zoomOut').addEventListener('click', () => map.zoomOut());

  const aboutModal = document.getElementById('aboutModal');
  document.getElementById('infoButton').addEventListener('click', () => aboutModal.hidden = false);
  document.getElementById('closeAbout').addEventListener('click', () => aboutModal.hidden = true);
  aboutModal.addEventListener('click', e => { if (e.target === aboutModal) aboutModal.hidden = true; });

  document.getElementById('addInspection').addEventListener('click', e => {
    e.currentTarget.textContent = 'Added to inspection plan ✓';
    e.currentTarget.classList.add('added');
    showToast(`${selectedAsset.short} added to the sample field plan`);
  });
  document.getElementById('viewEvidence').addEventListener('click', () => showToast('Evidence panel would link to source RCM scenes and processing metadata'));

  const searchInput = document.getElementById('assetSearch');
  const searchResults = document.getElementById('searchResults');
  function runSearch() {
    const query = searchInput.value.trim().toLowerCase();
    if (!query) { searchResults.hidden = true; return; }
    const matches = assets.filter(a => `${a.name} ${a.type} ${a.location}`.toLowerCase().includes(query));
    searchResults.innerHTML = matches.length ? matches.map(a => `<button class="search-result" data-id="${a.id}"><span><strong>${a.short}</strong><small>${a.location}</small></span><em>View</em></button>`).join('') : '<div style="padding:12px;color:#6b7b8b;font-size:11px">No sample assets found</div>';
    searchResults.hidden = false;
    searchResults.querySelectorAll('.search-result').forEach(item => item.addEventListener('click', () => {
      selectAsset(assets.find(a => a.id === item.dataset.id), true);
      searchResults.hidden = true; searchInput.blur();
    }));
  }
  searchInput.addEventListener('input', runSearch);
  document.addEventListener('keydown', event => {
    if (event.key === '/' && document.activeElement !== searchInput) { event.preventDefault(); searchInput.focus(); }
    if (event.key === 'Escape') { searchResults.hidden = true; aboutModal.hidden = true; }
  });
  document.addEventListener('click', event => { if (!event.target.closest('.search-wrap')) searchResults.hidden = true; });

  renderQueue();
  updateYear(3);
  selectAsset(assets[0]);
  setTimeout(() => map.invalidateSize(), 120);
})();
