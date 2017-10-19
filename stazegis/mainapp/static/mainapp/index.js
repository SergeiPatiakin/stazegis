var ui_consts = {
    map_collapsed_styles: ["col-xs-12", "col-sm-12", "col-md-12"],
    map_expanded_styles: ["col-xs-6", "col-sm-7", "col-md-8"],
    merged_layer_names: {
        "PED":"staze_workspace:merged_ped",
        "CYC":"staze_workspace:merged_cyc",
        "ALL":"staze_workspace:merged_all"
    }
};
var ui_state = {
    track_desc_visible: false,
    individual_layer_visible: false,
    current_track_type_code: "ALL",
    article_json: null
};
var ui = {
    map: null,
    merged_layer_sources: {
        "PED":
            new ol.source.TileWMS({
                url: '/geoserver/wms',
                params: {'LAYERS': 'staze_workspace:merged_ped', 'TILED': true},
                serverType: 'geoserver',
                hidpi: true
            }),
        "CYC":
            new ol.source.TileWMS({
                url: '/geoserver/wms',
                params: {'LAYERS': 'staze_workspace:merged_cyc', 'TILED': true},
                serverType: 'geoserver',
                hidpi: true
            }),
        "ALL":
            new ol.source.TileWMS({
                url: '/geoserver/wms',
                params: {'LAYERS': 'staze_workspace:merged_all', 'TILED': true},
                serverType: 'geoserver',
                hidpi: true
            })
    },
    merged_layers: {},
    current_merged_source: null,
    elevation_marker: null,
    elevation_marker_layer: null,
    individual_layer: null,
    individual_layer_source: null
};

/** Expand track description panel */
function trackDescExpand() {
    ui_state.track_desc_visible = true;
    $("#trackdesc").show();

    for(var i=0; i<ui_consts.map_collapsed_styles.length; i++) $("#map").toggleClass(ui_consts.map_collapsed_styles[i], false);
    for(var i=0; i<ui_consts.map_expanded_styles.length; i++) $("#map").toggleClass(ui_consts.map_expanded_styles[i], true);

    $("#trackdesctoggle > span").toggleClass("glyphicon-chevron-left", false);
    $("#trackdesctoggle > span").toggleClass("glyphicon-chevron-right", true);

    ui.map.updateSize();
}

/** Contract track description panel */
function trackDescCollapse() {
    ui_state.track_desc_visible = false;
    $("#trackdesc").hide();

    for(var i=0; i<ui_consts.map_collapsed_styles.length; i++) $("#map").toggleClass(ui_consts.map_collapsed_styles[i], true);
    for(var i=0; i<ui_consts.map_expanded_styles.length; i++) $("#map").toggleClass(ui_consts.map_expanded_styles[i], false);

    $("#trackdesctoggle > span").toggleClass("glyphicon-chevron-right", false);
    $("#trackdesctoggle > span").toggleClass("glyphicon-chevron-left", true);

    ui.map.updateSize();
}

/** Toggle description panel state between contracted and expanded */
function trackDescToggle(){
    if(ui_state.track_desc_visible) trackDescCollapse();
    else trackDescExpand();
}

/** Convert a longitude-latitude extent to a map-CRS extent */
function extentFromLonLat(extent){
    var point1 = ol.proj.fromLonLat([extent[0], extent[1]]);
    var point2 = ol.proj.fromLonLat([extent[2], extent[3]]);
    return [point1[0], point1[1], point2[0], point2[1]]
}

/** Convert a latitude-longitude extent to a map-CRS extent */
function extentFromLatLon(extent){
    return extentFromLatLon([extent[1], extent[0], extent[3], extent[2]]);
}

/** Scale an extent by scale_factor, preserving center */
function scaleExtent(extent, scale_factor){
    var center_x = (extent[0]+extent[2])/2.0;
    var halfwidth_x= (extent[2]-extent[0])/2.0;
    var center_y=(extent[1]+extent[3])/2.0;
    var halfwidth_y = (extent[3]-extent[1])/2.0;
    return [
        center_x - halfwidth_x * scale_factor,
        center_y - halfwidth_y * scale_factor,
        center_x + halfwidth_x * scale_factor,
        center_y + halfwidth_y * scale_factor
    ];
}

/** Retrieve article info from the API, and drive UI changes to display the article */
function openArticle(track_id, pan_to_track, set_url_from_state){
    var url = "/tracks/"+track_id+"/";
    $.get(url, function (data) {
        ui_state.article_json = data;

        document.title = ui_state.article_json.title;

        showIndividualLayer(track_id);
        if(pan_to_track){
            // zoom out by 1.5 so that no part of the track is near the edge of the view
            var extent = scaleExtent(extentFromLonLat(ui_state.article_json.bbox), 1.5);
            map.getView().fit(extent, map.getSize());
        }
        // TODO: race condition if pan_to_track AND set_url_from_state
        if(set_url_from_state) setUrlFromState();

        trackDescExpand();
        $("#tracktitle").text(ui_state.article_json.title);
        $("#usercontent").html(ui_state.article_json.html_content);
    });
}
/** Handle a map click event */
function handleMapClick(feature_ids) {
    if(feature_ids.length==0) return;
    // pick first track
    var track_id = feature_ids[0];
    // open article, do not pan, set
    openArticle(track_id, false, true);
}


/** Update track type for the merged layer */
function switchMergedLayer(track_type_code){
    current_track_type_code = track_type_code;
    current_merged_source = ui.merged_layer_sources[current_track_type_code];
    for(key in ui.merged_layers){
        if(key == track_type_code) ui.merged_layers[key].setVisible(true);
        else ui.merged_layers[key].setVisible(false);
    }
}

/** Show individual track */
function showIndividualLayer(uid){
    ui_state.individual_layer_visible = true;
    ui_state.individual_layer_id = uid;
    ui.individual_layer_source = new ol.source.TileWMS({
        url: '/geoserver/wms',
        params: {'LAYERS': 'staze_workspace:individual', 'TILED': true, viewparams:'id:'+uid},
        serverType: 'geoserver',
        hidpi: true
    });
    ui.individual_layer.setSource(ui.individual_layer_source);
    ui.individual_layer.setVisible(true);

    $("#trackdescclose").show();
    $("#trackdesctoggle").show();
}

/** Hide individual track */
function hideIndividualLayer(){
    ui_state.individual_layer_visible = false;
    ui.individual_layer.setVisible(false);
    $("#trackdescclose").hide();
    $("#trackdesctoggle").hide();
}

/** Convert URL string to URL object */
function disassembleUrl(url){
    var url_obj = {};
    var param_index = url.indexOf("?");
    url_obj.path = url.slice(0,param_index+1);
    url_obj.params = {};
    var param_string_list = url.slice(param_index+1).split("&");

    for(var i=0; i<param_string_list.length; i++){
        var s = param_string_list[i].split("=");
        url_obj.params[decodeURIComponent(s[0])] = decodeURIComponent(s[1]);
    }
    return url_obj;
}

/** Lax version of encodeURIComponent that does not escape commas */
function encodeURILax(text){
    return encodeURIComponent(text).replace(/%2C/g,",");
}

/** Convert URL object to URL string */
function assembleUrl(url_obj){
    var url=url_obj.path;
    var first=true;
    for(var key in url_obj.params){
        if(!first){
            url+="&";
        }
        else{
            first=false;
        }
        url+=encodeURILax(key)+"="+encodeURILax(url_obj.params[key]);
    }
    return url;
}

/** Initialize the OpenLayers map */
function initMap() {
    // set a style for the icon
    var iconStyle = new ol.style.Style({
        image: new ol.style.RegularShape({
            fill: new ol.style.Fill({
                color: '#F58026'
            }),
            stroke: new ol.style.Stroke({
                color: '#300',
                width: 2
            }),
            points: 4,
            radius: 10,
            radius2: 0,
            rotation: 0,//Math.PI / 4,
            angle: 0
        })
        ,text: new ol.style.Text({
         text: "",
         scale: 1.3,
         offsetX: 0,
         offsetY: 15,
         fill: new ol.style.Fill({
         color: '#F58026'
         }),
         stroke: new ol.style.Stroke({
         color: '#000',
         width: 4
         })
         })
    });
    var view = new ol.View({
        center: [2419464.8880813057, 5443860.4488202045],
        zoom: 10
    });
    ui.elevation_marker = new ol.Feature({
        type: 'elevation_marker',
        geometry: new ol.geom.Point(ol.proj.fromLonLat([0, 0]))
    });
    ui.elevation_marker_layer = new ol.layer.Vector({
            visible: false,
            source: new ol.source.Vector({
                features: [ui.elevation_marker]
            }),
            style: iconStyle,
            zIndex: 30
        });
    ui.individual_layer = new ol.layer.Tile({source: ui.individual_layer_source, visible: false, opacity: 1.0, zIndex:20});


    // Create geolocation object
    var geolocation = new ol.Geolocation({
        projection: view.getProjection(),
        tracking: true
    });

    // Create geolocation accuracy feature
    var accuracyFeature = new ol.Feature();
    geolocation.on('change:accuracyGeometry', function () {
        accuracyFeature.setGeometry(geolocation.getAccuracyGeometry());
    });

    // Create geolocation position feature
    var positionFeature = new ol.Feature();
    positionFeature.setStyle(new ol.style.Style({
        image: new ol.style.Circle({
            radius: 6,
            fill: new ol.style.Fill({
                color: '#FF6A32'
            }),
            stroke: new ol.style.Stroke({
                color: '#fff',
                width: 2
            })
        })
    }));
    geolocation.on('change:position', function () {
        var coordinates = geolocation.getPosition();
        positionFeature.setGeometry(coordinates ?
            new ol.geom.Point(coordinates) : null);
    });

    // add accuracy and position features to a layer
    geolocation_layer = new ol.layer.Vector({
        source: new ol.source.Vector({
          features: [accuracyFeature, positionFeature]
        })
    });

    // Array of all layers in map
    var map_layers = [
        new ol.layer.Tile({source: new ol.source.OSM()}),
        ui.elevation_marker_layer,
        ui.individual_layer,
        geolocation_layer
    ];
    for (var key in ui.merged_layer_sources) {
        var layer = new ol.layer.Tile({source: ui.merged_layer_sources[key], visible: false, opacity: 0.6});
        ui.merged_layers[key] = layer;
        map_layers.push(layer);
    }
    switchMergedLayer("ALL");

    ui.map = new ol.Map({
        layers: map_layers,
        target: 'map',
        view: view
    });

    ui.map.on('singleclick', function (evt) {
        var viewResolution = /** @type {number} */ (view.getResolution());
        var viewProjection = view.getProjection();
        var wms_url = current_merged_source.getGetFeatureInfoUrl(
                evt.coordinate, viewResolution, viewProjection,
                {'INFO_FORMAT': 'application/json'});
        if (wms_url) {
            // Oh no, we have to hack viewport parameters to get larger pixel tolerance.
            // Scale down I,J,WIDTH,HEIGHT

            /*var scale_parameters = function(str, name, scalefactor){
                var re = RegExp("&"+name+"=([0-9]+)&");
                var match_info = str.match(re);
                var match_string = match_info[0];
                var old_value = parseInt(match_info[1]);
                var new_value = Math.floor(old_value/scalefactor);
                return str.replace(match_string, "&"+name+"="+new_value+"&");
            };*/

            // var scale_factor = 4; // which fraction of the 256*256 tile should the new bounding box be?
            var pixel_margin = 5;
            var map_size = ui.map.getSize();
            var map_bbox = ui.map.getView().calculateExtent(ui.map.getSize());
            var x_range = (map_bbox[2] - map_bbox[0])/map_size[0]*pixel_margin;
            var y_range = (map_bbox[3] - map_bbox[1])/map_size[1]*pixel_margin;

            var click_x = evt.coordinate[0];
            var click_y = evt.coordinate[1];

            var new_bbox = ol.proj.transformExtent([click_x - 0.5*x_range,
                click_y - 0.5*x_range,
                click_x + 0.5 * x_range,
                click_y + 0.5 * y_range],
                "EPSG:3857", "EPSG:4326");

            var new_bbox_str = [
                new_bbox[0].toString(),
                new_bbox[1].toString(),
                new_bbox[2].toString(),
                new_bbox[3].toString()
            ].join(',');

            var url_obj = {
                path: "/trackquery/?",
                params: {
                    bbox: new_bbox_str,
                    layer_code: current_track_type_code
                }
            };

            // reconstruct URL
            url = assembleUrl(url_obj);

            $.get(url, function (data) {
                var featureIds = [];
                var featureCount = data.length;
                for (var i=0; i<featureCount; i++){
                    featureIds.push(data[i]);
                }
                handleMapClick(featureIds)
            });
        }
    });
    ui.map.on("moveend", function(e){
        setUrlFromState();
    });
    ui.map.on("zoomend", function(e){
        setUrlFromState();
    });
}

/** Update page URL based on page state */
function setUrlFromState(){
    var center_coordinates = ol.proj.toLonLat(ui.map.getView().getCenter());
    var zoom_level = ui.map.getView().getZoom();

    var url_obj = {
        path: "/view/?",
        params: {
            pos: center_coordinates[0].toFixed(7)+','+center_coordinates[1].toFixed(7),
            z: zoom_level
        }
    };
    if(ui_state.individual_layer_visible){
        url_obj.params.track=ui_state.individual_layer_id;
    }
    window.history.replaceState("", "Staze Balkana", assembleUrl(url_obj))
}

/** Update page state based on page URL */
function setStateFromUrl() {
    var url_obj = disassembleUrl(location.href);
    if('pos' in url_obj.params){
        var coordinate_strs = url_obj.params.pos.split(',');
        // assert length of coordinates_strs is 2
        var center_position = ol.proj.fromLonLat([parseFloat(coordinate_strs[0]), parseFloat(coordinate_strs[1])]);
        ui.map.getView().setCenter(center_position);
    }
    if('z' in url_obj.params){
        var z = parseFloat(url_obj.params.z);
        ui.map.getView().setZoom(z);
    }
    if('track' in url_obj.params){
        if((!ui_state.individual_layer_visible) || ui_state.individual_layer_id != url_obj.params.track) {
            // open article, pan to track if no 'pos' or 'z' parameter, do not change URL
            openArticle(url_obj.params.track, !(('pos' in url_obj.params) && ('z' in url_obj.params)), false);
        }
    }
}

/** Set up event bindings */
function setupBindings() {
    $("#trackdesctoggle").on('click', function () {
        trackDescToggle();
    });

    $("#trackdescclose").on('click', function () {
        trackDescCollapse();
        hideIndividualLayer();
    });

    $("#btn-all > a").on('click', function () {
        switchMergedLayer("ALL");
        // Remove active style from all track type buttons
        $("#btn-tracktype-container > li").removeClass("active");
        $("#btn-all").addClass("active");
    });
    $("#btn-ped > a").on('click', function () {
        switchMergedLayer("PED");
        // Remove active style from all track type buttons
        $("#btn-tracktype-container > li").removeClass("active");
        $("#btn-ped").addClass("active");
    });
    $("#btn-cyc > a").on('click', function () {
        switchMergedLayer("CYC");
        // Remove active style from all track type buttons
        $("#btn-tracktype-container > li").removeClass("active");
        $("#btn-cyc").addClass("active");
    });
    window.onresize = function() {
        setTimeout( function() { ui.map.updateSize();}, 200);
    };
}

setupBindings();
initMap();
setStateFromUrl();