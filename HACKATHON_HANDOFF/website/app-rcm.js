(() => {
  const studyView = { center: [45.96, -64.18], zoom: 9 };
  const sceneOrder = ['dorian-before', 'dorian-after', 'fiona-before', 'fiona-after', 'july2023-before', 'july2023-during', 'lee-before', 'lee-after'];
  const measuredMeta = {
    dorian: {
      shortName: 'Dorian',
      title: 'Hurricane Dorian',
      firstRole: 'before',
      secondRole: 'after',
      newCategory: 'new_low_backscatter_after_dorian',
      newLabel: 'Appeared after Dorian',
      removedLabel: 'Seen only before Dorian',
      evidenceUrl: 'data/events/dorian-sentinel1-analysis.json',
      sensorLabel: 'Sentinel-1 · HV'
    },
    fiona: {
      shortName: 'Fiona',
      title: 'Hurricane Fiona',
      firstRole: 'before',
      secondRole: 'after',
      newCategory: 'new_low_backscatter_after_fiona',
      newLabel: 'Appeared after Fiona',
      removedLabel: 'Seen only before Fiona',
      evidenceUrl: 'data/fiona_analysis_summary.json',
      sensorLabel: 'RCM · VH'
    },
    july2023: {
      shortName: 'July 2023',
      title: 'July 2023 extreme rainfall',
      firstRole: 'before',
      secondRole: 'during',
      newCategory: 'new_low_backscatter_during_july2023',
      newLabel: 'Appeared by July 21',
      removedLabel: 'Seen only on July 17',
      evidenceUrl: 'data/events/july2023-analysis.json',
      sensorLabel: 'RCM · VH'
    },
    lee: {
      shortName: 'Lee',
      title: 'Hurricane Lee',
      firstRole: 'before',
      secondRole: 'after',
      newCategory: 'new_low_backscatter_after_lee',
      newLabel: 'Appeared after Lee',
      removedLabel: 'Seen only before Lee',
      evidenceUrl: 'data/events/lee-sentinel1-analysis.json',
      sensorLabel: 'Sentinel-1 · HV'
    }
  };

  let timeline = [];
  let currentIndex = 3;
  let playing = false;
  let playTimer = null;
  let selectedFeature = null;
  let footprints = null;
  let radarOverlay = null;
  const featureRecords = [];
  const historyRecords = [];

  if (!window.L) {
    document.getElementById('map').innerHTML = '<div style="padding:100px 30px;text-align:center"><h2>Map unavailable</h2><p>Connect to the internet to load the map.</p></div>';
    return;
  }

  const byId = id => document.getElementById(id);
  const map = L.map('map', { zoomControl: false, minZoom: 5, maxZoom: 17 }).setView(studyView.center, studyView.zoom);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
  }).addTo(map);

  map.createPane('radar');
  map.getPane('radar').style.zIndex = 350;
  map.getPane('radar').style.pointerEvents = 'none';
  ['persistent', 'removed', 'new', 'history', 'footprint'].forEach((name, i) => {
    map.createPane(name);
    map.getPane(name).style.zIndex = 420 + i * 10;
  });

  const makeChangeGroups = () => ({ persistent: L.layerGroup(), newAfter: L.layerGroup(), removed: L.layerGroup() });
  const groups = {
    radar: L.layerGroup(),
    changes: { dorian: makeChangeGroups(), fiona: makeChangeGroups(), july2023: makeChangeGroups(), lee: makeChangeGroups() },
    history: L.layerGroup(),
    footprint: L.layerGroup()
  };

  const classStyles = {
    persistent: { color: '#218bb2', fillColor: '#299fc9', fillOpacity: .42 },
    newAfter: { color: '#de5f42', fillColor: '#ef7654', fillOpacity: .62 },
    removed: { color: '#7651ad', fillColor: '#8a64be', fillOpacity: .48 }
  };

  const currentScene = () => timeline[currentIndex];
  const formatDate = iso => new Date(iso + 'T12:00:00Z').toLocaleDateString('en-CA', { month: 'short', day: 'numeric', year: 'numeric', timeZone: 'UTC' });
  const formatArea = value => Number(value).toLocaleString(undefined, { maximumFractionDigits: 2 });
  const classKey = category => category === 'persistent_low_backscatter' ? 'persistent' : category.startsWith('new_low_backscatter') ? 'newAfter' : 'removed';
  const classLabel = properties => {
    const key = classKey(properties.category);
    const meta = measuredMeta[properties.event_id];
    if (key === 'persistent') return 'Water-like on both dates';
    if (key === 'newAfter') return meta.newLabel;
    return meta.removedLabel;
  };
  const setMapLayer = (layer, visible) => {
    if (visible && !map.hasLayer(layer)) layer.addTo(map);
    if (!visible && map.hasLayer(layer)) map.removeLayer(layer);
  };
  const showToast = message => {
    byId('toast').textContent = message;
    byId('toast').hidden = false;
    clearTimeout(showToast.timer);
    showToast.timer = setTimeout(() => { byId('toast').hidden = true; }, 2800);
  };

  function addChangeData(collection, eventId) {
    collection.features.forEach(feature => {
      feature.properties.event_id = feature.properties.event_id || eventId;
      const key = classKey(feature.properties.category);
      const style = classStyles[key];
      featureRecords.push(feature);
      L.geoJSON(feature, {
        pane: key === 'newAfter' ? 'new' : key === 'persistent' ? 'persistent' : 'removed',
        style: { ...style, weight: 1.5 },
        onEachFeature: (item, layer) => {
          layer.bindTooltip(classLabel(item.properties) + '<br>' + formatArea(item.properties.area_ha) + ' hectares', { sticky: true, className: 'map-tooltip' });
          layer.on('click', () => selectCandidate(item));
        }
      }).addTo(groups.changes[eventId][key]);
    });
  }

  function addHistoryData(collection) {
    collection.features.forEach(feature => {
      historyRecords.push(feature);
      const p = feature.properties;
      L.geoJSON(feature, {
        pane: 'history',
        pointToLayer: (_item, latlng) => L.circleMarker(latlng, { radius: 4, color: '#7a6426', weight: 1.5, fillColor: '#f0cb55', fillOpacity: .9 }),
        onEachFeature: (_item, layer) => {
          const link = p.link_1 ? '<br><a href="' + p.link_1 + '" target="_blank" rel="noreferrer">Open source record ↗</a>' : '';
          layer.bindPopup('<strong>' + (p.locality || 'Historical flood report') + '</strong><br>' + (p.start_date || p.year || 'Date not recorded') + '<br>' + (p.flood_cause || 'Cause not recorded') + link + '<br><small>This point marks a reported location, not the full flooded area.</small>');
        }
      }).addTo(groups.history);
    });
  }

  function selectCandidate(feature, pan = false) {
    selectedFeature = feature;
    const p = feature.properties;
    const meta = measuredMeta[p.event_id];
    const observation = timeline.find(scene => scene.eventId === p.event_id && scene.role === meta.secondRole);
    byId('eventPreview').hidden = true;
    byId('detailType').textContent = meta.shortName.toUpperCase() + ' PLACE TO CHECK';
    byId('detailName').textContent = 'Area ' + p.feature_id;
    byId('detailLocation').textContent = p.center_lat.toFixed(4) + ', ' + p.center_lon.toFixed(4);
    byId('metricOneLabel').textContent = 'Approximate area';
    byId('detailDistance').textContent = formatArea(p.area_ha) + ' ha';
    byId('metricTwoLabel').textContent = 'What the radar saw';
    byId('detailTrend').textContent = classLabel(p);
    byId('detailObserved').textContent = observation ? formatDate(observation.date) : '—';
    byId('detailConfidence').textContent = meta.sensorLabel;
    byId('detailStatus').querySelector('strong').textContent = 'Needs a closer look';
    byId('detailStatus').querySelector('small').textContent = 'The radar signal alone does not prove flooding';
    byId('addInspection').hidden = false;
    byId('detailPanel').classList.remove('closed');
    if (pan) map.flyTo([p.center_lat, p.center_lon], 14);
  }

  function showScene() {
    const scene = currentScene();
    selectedFeature = null;
    byId('detailType').textContent = scene.analysis === 'measured' ? 'COMPARABLE RADAR OBSERVATION' : 'MAP-ALIGNED CONTEXT';
    byId('detailName').textContent = scene.eventName + ' · ' + scene.roleLabel;
    byId('detailLocation').textContent = scene.analysis === 'measured' ? 'Used in a measured candidate-change interval' : 'Real Sentinel-1 observation; contrast normalized per scene';
    byId('eventPreview').src = scene.preview;
    byId('eventPreview').alt = scene.sensor + ' preview for ' + formatDate(scene.date);
    byId('eventPreview').hidden = false;
    byId('metricOneLabel').textContent = 'Radar setting';
    byId('detailDistance').textContent = scene.polarization;
    byId('metricTwoLabel').textContent = 'Timeline position';
    byId('detailTrend').textContent = (currentIndex + 1) + ' of ' + timeline.length;
    byId('detailObserved').textContent = formatDate(scene.date);
    byId('detailConfidence').textContent = scene.sensor;
    byId('detailStatus').querySelector('strong').textContent = scene.analysis === 'measured' ? 'Comparable radar image' : 'Visual context only';
    byId('detailStatus').querySelector('small').textContent = scene.statusNote;
    byId('addInspection').hidden = true;
    byId('detailPanel').classList.remove('closed');
  }

  function renderRadar() {
    groups.radar.clearLayers();
    const scene = currentScene();
    radarOverlay = L.imageOverlay(scene.mapImage, scene.mapBounds, {
      pane: 'radar',
      opacity: Number(byId('imageOpacity').value) / 100,
      interactive: false,
      className: 'rcm-raster'
    });
    radarOverlay.on('error', () => showToast('The radar image could not be displayed'));
    radarOverlay.addTo(groups.radar);
    byId('sceneBadge').querySelector('strong').textContent = scene.eventName.replace('Hurricane ', '').toUpperCase() + ' · ' + scene.roleLabel.toUpperCase();
    byId('sceneBadge').querySelector('span').textContent = scene.sensor + ' · ' + scene.polarization + ' · ' + formatDate(scene.date) + (scene.analysis === 'measured' ? ' · measured interval' : ' · context only');
  }

  function renderFootprint() {
    groups.footprint.clearLayers();
    const scene = currentScene();
    if (scene.analysis === 'measured' || !footprints) return;
    const feature = footprints.features.find(item => item.id === scene.id);
    if (!feature) return;
    L.geoJSON(feature, {
      pane: 'footprint',
      style: { color: scene.role === 'after' ? '#e66b46' : '#267baa', weight: 3, dashArray: '8 5', fillOpacity: 0 }
    }).bindTooltip(scene.eventName + ' · ' + scene.roleLabel + ' image coverage', { sticky: true }).addTo(groups.footprint);
  }

  function syncLayers() {
    const scene = currentScene();
    const comparison = byId('compareButton').classList.contains('active');
    Object.entries(groups.changes).forEach(([eventId, changeGroups]) => {
      const active = scene.eventId === eventId && scene.analysis === 'measured';
      const first = scene.role === measuredMeta[eventId]?.firstRole;
      setMapLayer(changeGroups.persistent, active && byId('waterToggle').checked);
      setMapLayer(changeGroups.newAfter, active && byId('anomalyToggle').checked && (comparison || !first));
      setMapLayer(changeGroups.removed, active && byId('propertyToggle').checked && (comparison || first));
    });
    setMapLayer(groups.radar, byId('imageToggle').checked);
    setMapLayer(groups.history, byId('assetsToggle').checked);
    setMapLayer(groups.footprint, scene.analysis !== 'measured');
  }

  function renderQueue() {
    const scene = currentScene();
    if (scene.analysis !== 'measured') {
      const related = timeline.filter(item => item.eventId === scene.eventId);
      byId('queueTitle').textContent = scene.eventName.replace('Hurricane ', '') + ' observations';
      byId('queueCount').textContent = related.length + ' scenes';
      byId('inspectionQueue').innerHTML = related.map(item => {
        const index = timeline.indexOf(item);
        return '<button class="queue-item" data-scene="' + index + '"><i class="queue-severity ' + (item.role !== 'before' ? 'high' : '') + '"></i><span><strong>' + item.roleLabel + '</strong><small>' + item.sensor + ' · ' + item.polarization + '</small></span><em>' + formatDate(item.date).replace(', ', '<br>') + '</em></button>';
      }).join('');
      document.querySelectorAll('[data-scene]').forEach(button => button.addEventListener('click', () => setTimeline(Number(button.dataset.scene))));
      return;
    }
    const meta = measuredMeta[scene.eventId];
    const candidates = featureRecords.filter(f => f.properties.event_id === scene.eventId && f.properties.category === meta.newCategory).sort((a, b) => b.properties.area_ha - a.properties.area_ha).slice(0, 5);
    byId('queueTitle').textContent = 'Largest ' + meta.shortName + ' areas to check';
    byId('queueCount').textContent = candidates.length + ' shown';
    byId('inspectionQueue').innerHTML = candidates.map(f => '<button class="queue-item" data-id="' + f.properties.feature_id + '"><i class="queue-severity high"></i><span><strong>Area ' + f.properties.feature_id + '</strong><small>' + meta.newLabel + '</small></span><em>' + formatArea(f.properties.area_ha) + ' ha</em></button>').join('');
    document.querySelectorAll('[data-id]').forEach(button => button.addEventListener('click', () => selectCandidate(featureRecords.find(f => f.properties.feature_id === button.dataset.id), true)));
  }

  function setTimeline(index) {
    currentIndex = Math.max(0, Math.min(timeline.length - 1, Number(index)));
    const scene = currentScene();
    const measured = scene.analysis === 'measured';
    const meta = measured ? measuredMeta[scene.eventId] : null;
    byId('yearSlider').value = currentIndex;
    byId('yearLabel').textContent = formatDate(scene.date);
    document.querySelectorAll('.year-ticks button').forEach((button, i) => button.classList.toggle('active', i === currentIndex));
    byId('eventExplainer').textContent = scene.summary;
    byId('observationCount').textContent = timeline.length;
    byId('flaggedCount').textContent = measured ? scene.candidateCount : '—';
    byId('flaggedLabel').textContent = measured ? meta.shortName + ' areas to check' : 'visual context only';
    byId('eventYear').textContent = scene.date.slice(0, 4);
    byId('layerControls').classList.toggle('context-mode', !measured);
    byId('compareButton').hidden = !measured;
    byId('legend').hidden = !measured;
    if (measured) {
      byId('persistentLabel').textContent = 'Water-like on both dates';
      byId('newLabel').textContent = meta.newLabel;
      byId('removedLabel').textContent = meta.removedLabel;
      byId('legendTitle').textContent = meta.shortName + ' analysis';
    }
    byId('dataNote').textContent = scene.dataNote;
    renderRadar();
    renderFootprint();
    renderQueue();
    syncLayers();
    showScene();
  }

  ['imageToggle', 'waterToggle', 'anomalyToggle', 'assetsToggle', 'propertyToggle'].forEach(id => byId(id).addEventListener('change', syncLayers));
  byId('imageOpacity').addEventListener('input', event => { if (radarOverlay) radarOverlay.setOpacity(Number(event.target.value) / 100); });
  byId('resetLayers').addEventListener('click', () => {
    ['imageToggle', 'waterToggle', 'anomalyToggle', 'assetsToggle', 'propertyToggle'].forEach(id => { byId(id).checked = true; });
    syncLayers();
  });
  byId('yearSlider').addEventListener('input', event => setTimeline(event.target.value));
  document.querySelectorAll('.year-ticks button').forEach(button => button.addEventListener('click', () => setTimeline(button.dataset.index)));
  byId('playButton').addEventListener('click', () => {
    playing = !playing;
    document.querySelector('.play-icon').hidden = playing;
    document.querySelector('.pause-icon').hidden = !playing;
    clearInterval(playTimer);
    if (!playing) return;
    setTimeline(0);
    playTimer = setInterval(() => {
      if (currentIndex >= timeline.length - 1) {
        playing = false;
        clearInterval(playTimer);
        document.querySelector('.play-icon').hidden = false;
        document.querySelector('.pause-icon').hidden = true;
      } else setTimeline(currentIndex + 1);
    }, 1800);
  });
  byId('compareButton').addEventListener('click', event => { event.currentTarget.classList.toggle('active'); syncLayers(); });
  byId('collapseLeft').addEventListener('click', () => { document.querySelector('.left-panel').classList.add('collapsed'); byId('reopenLeft').hidden = false; });
  byId('reopenLeft').addEventListener('click', () => { document.querySelector('.left-panel').classList.remove('collapsed'); byId('reopenLeft').hidden = true; });
  byId('closeDetails').addEventListener('click', () => byId('detailPanel').classList.add('closed'));
  byId('homeButton').addEventListener('click', () => map.flyTo(studyView.center, studyView.zoom));
  byId('locateButton').addEventListener('click', () => map.flyTo(studyView.center, studyView.zoom));
  byId('zoomIn').addEventListener('click', () => map.zoomIn());
  byId('zoomOut').addEventListener('click', () => map.zoomOut());

  byId('infoButton').addEventListener('click', () => { byId('aboutModal').hidden = false; });
  byId('closeAbout').addEventListener('click', () => { byId('aboutModal').hidden = true; });
  byId('aboutModal').addEventListener('click', event => { if (event.target === byId('aboutModal')) byId('aboutModal').hidden = true; });
  const openHelp = () => { byId('helpModal').hidden = false; };
  byId('helpButton').addEventListener('click', openHelp);
  byId('helpButtonPanel').addEventListener('click', openHelp);
  byId('closeHelp').addEventListener('click', () => { byId('helpModal').hidden = true; });
  byId('helpModal').addEventListener('click', event => { if (event.target === byId('helpModal')) byId('helpModal').hidden = true; });
  byId('addInspection').addEventListener('click', event => {
    if (!selectedFeature) return showToast('Select a measured candidate first');
    event.currentTarget.textContent = 'Marked for review ✓';
    event.currentTarget.classList.add('added');
    showToast('Area marked locally for review');
  });
  byId('viewEvidence').addEventListener('click', () => window.open(currentScene().evidenceUrl, '_blank', 'noopener'));

  const searchInput = byId('assetSearch');
  const searchResults = byId('searchResults');
  searchInput.addEventListener('input', () => {
    const query = searchInput.value.trim().toLowerCase();
    if (!query) return searchResults.hidden = true;
    const matches = featureRecords.filter(f => f.properties.feature_id.toLowerCase().includes(query)).slice(0, 5);
    const records = historyRecords.filter(f => JSON.stringify(f.properties).toLowerCase().includes(query)).slice(0, 4);
    searchResults.innerHTML = matches.map(f => '<button class="search-result" data-search-id="' + f.properties.feature_id + '"><span><strong>' + f.properties.feature_id + '</strong><small>' + measuredMeta[f.properties.event_id].shortName + ' area to check</small></span><em>View</em></button>').join('') + records.map(f => '<button class="search-result" data-history-index="' + historyRecords.indexOf(f) + '"><span><strong>' + (f.properties.locality || 'Flood report') + '</strong><small>' + (f.properties.year || '') + '</small></span><em>View</em></button>').join('');
    if (!searchResults.innerHTML) searchResults.innerHTML = '<div style="padding:12px;font-size:11px">No match found</div>';
    searchResults.hidden = false;
    document.querySelectorAll('[data-search-id]').forEach(button => button.addEventListener('click', () => {
      const feature = featureRecords.find(f => f.properties.feature_id === button.dataset.searchId);
      const meta = measuredMeta[feature.properties.event_id];
      setTimeline(timeline.findIndex(scene => scene.eventId === feature.properties.event_id && scene.role === meta.secondRole));
      selectCandidate(feature, true);
      searchResults.hidden = true;
    }));
    document.querySelectorAll('[data-history-index]').forEach(button => button.addEventListener('click', () => {
      const coordinates = historyRecords[Number(button.dataset.historyIndex)].geometry.coordinates;
      map.flyTo([coordinates[1], coordinates[0]], 13);
      searchResults.hidden = true;
    }));
  });

  Promise.all([
    fetch('data/dorian_low_backscatter_change.geojson').then(r => r.json()),
    fetch('data/fiona_low_backscatter_change.geojson').then(r => r.json()),
    fetch('data/july2023_low_backscatter_change.geojson').then(r => r.json()),
    fetch('data/lee_low_backscatter_change.geojson').then(r => r.json()),
    fetch('data/historical_flood_context.geojson').then(r => r.json()),
    fetch('data/events/dorian-sentinel1-analysis.json').then(r => r.json()),
    fetch('data/fiona_analysis_summary.json').then(r => r.json()),
    fetch('data/events/july2023-analysis.json').then(r => r.json()),
    fetch('data/events/lee-sentinel1-analysis.json').then(r => r.json()),
    fetch('data/events/events.json').then(r => r.json()),
    fetch('data/events/event_footprints.geojson').then(r => r.json()),
    fetch('data/events/fiona-map-imagery.json').then(r => r.json()),
    fetch('data/events/sentinel1-matched-imagery.json').then(r => r.json())
  ]).then(([dorianChange, fionaChange, julyChange, leeChange, historyData, dorianSummary, fionaSummary, julySummary, leeSummary, eventData, footprintData, fionaImagery, sentinelImagery]) => {
    footprints = footprintData;
    addChangeData(dorianChange, 'dorian');
    addChangeData(fionaChange, 'fiona');
    addChangeData(julyChange, 'july2023');
    addChangeData(leeChange, 'lee');
    addHistoryData(historyData);

    const eventLookup = Object.fromEntries(eventData.events.map(event => [event.id, event]));
    const sentinelLookup = Object.fromEntries(sentinelImagery.scenes.map(scene => [scene.id, scene]));

    timeline = sceneOrder.map(id => {
      const split = id.lastIndexOf('-');
      const eventId = id.slice(0, split);
      const role = id.slice(split + 1);

      if (eventId === 'july2023') {
        const source = julySummary[role];
        const date = source.acquisition_utc.slice(0, 10);
        return {
          id, eventId, role,
          roleLabel: role === 'before' ? 'before rainfall' : 'during onset',
          eventName: 'July 2023 rainfall',
          date,
          sensor: source.satellite,
          polarization: 'VV/VH · VH analyzed',
          preview: julySummary.web_imagery.images[role],
          mapImage: julySummary.web_imagery.images[role],
          mapBounds: julySummary.web_imagery.bounds_wgs84,
          analysis: 'measured',
          candidateCount: julySummary.exported_polygon_counts.new_low_backscatter_during_july2023,
          evidenceUrl: measuredMeta.july2023.evidenceUrl,
          statusNote: role === 'during' ? 'Captured during event onset—not after the full rainfall event' : 'Comparable pre-event image',
          summary: 'This comparable RCM pair adds a second measured interval. The July 21 image was captured during the onset of the extreme rainfall, so the map shows early-event candidates rather than final flood extent.',
          dataNote: 'The July 17 and July 21 RCM images use matching settings. July 21 was during event onset; orange areas are early-event low-return candidates, not confirmed or final flood extent.'
        };
      }

      const event = eventLookup[eventId];
      const scene = event.scenes.find(item => item.role === role);
      const sentinel = sentinelLookup[id];
      const fiona = eventId === 'fiona';
      const sentinelMeasured = eventId === 'dorian' || eventId === 'lee';
      const measured = fiona || sentinelMeasured;
      const sentinelSummary = eventId === 'dorian' ? dorianSummary : leeSummary;
      return {
        id, eventId, role,
        roleLabel: role,
        eventName: event.name,
        date: scene.date,
        sensor: scene.sensor,
        polarization: scene.polarization,
        preview: scene.preview,
        mapImage: fiona ? fionaImagery.images[role] : sentinel.image,
        mapBounds: fiona ? fionaImagery.bounds_wgs84 : sentinel.bounds_wgs84,
        analysis: measured ? 'measured' : 'context',
        candidateCount: fiona
          ? fionaSummary.exported_polygon_counts.new_low_backscatter_after_fiona
          : sentinelSummary.exported_polygon_counts[measuredMeta[eventId].newCategory],
        evidenceUrl: measuredMeta[eventId].evidenceUrl,
        statusNote: fiona ? 'The matching Fiona RCM pair supports the candidate change layer' : 'Matched Sentinel-1 orbit, mode and polarization support this candidate layer',
        summary: fiona
          ? 'Fiona is a measured interval: its two RCM images use matching settings, allowing the orange candidate layer to be calculated.'
          : event.plain_summary,
        dataNote: fiona
          ? 'Fiona uses a comparable RCM pair. Dark radar areas can still be water, wet ground, roads or shadow—these are candidates, not confirmed floods.'
          : 'This matched Sentinel-1 pair uses the same platform, descending relative orbit 69, IW GRDH mode and HH/HV polarization. Orange areas are candidates—not confirmed flood boundaries.'
      };
    });

    const query = new URLSearchParams(window.location.search);
    let startIndex = sceneOrder.indexOf(query.get('scene'));
    if (startIndex < 0 && query.get('event')) {
      const requestedRole = query.get('date') === '0' ? 'before' : (query.get('event') === 'july2023' ? 'during' : 'after');
      startIndex = sceneOrder.indexOf(query.get('event') + '-' + requestedRole);
    }
    setTimeline(startIndex >= 0 ? startIndex : 3);
  }).catch(error => {
    console.error(error);
    byId('inspectionQueue').innerHTML = '<div style="padding:12px;color:#a64b3d;font-size:11px">The timeline data could not be loaded.</div>';
    showToast('Satellite timeline data could not be loaded');
  });

  setTimeout(() => map.invalidateSize(), 120);
})();
