import requests
import json
import os
from utils.config_utils import (GEOSERVER_REST_ENDPOINT, GEOSERVER_REST_USERNAME, GEOSERVER_REST_PASSWORD,
    DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD)

class GeoserverRestException(Exception):
    pass

def query(method, endpoint, **kwargs):
    kwargs["auth"]=(GEOSERVER_REST_USERNAME, GEOSERVER_REST_PASSWORD)
    return method(GEOSERVER_REST_ENDPOINT+endpoint, **kwargs)

def assert_status(r, *expected_statuses):
    try:
        assert r.status_code in expected_statuses
    except AssertionError:
        raise GeoserverRestException((r.status_code, r.content))

def get_conf_value(obj, key):
    return list(filter(lambda d: d["@key"] == key, obj))[0]["$"]

def set_conf_value(obj, key, value):
    list(filter(lambda d: d["@key"] == key, obj))[0]["$"] = value

def cleanup_server():
    headers={"Accept": "text/json", "Content-type": "text/json"}

    # Delete workspace
    r = query(requests.delete, 'workspaces/staze_workspace.json?recurse=true', headers=headers)
    assert_status(r, 200, 404)


def setup_server():
    generic_headers={"Accept": "text/json", "Content-type": "text/json"}

    # Create workspace
    payload={"workspace":{"name":"staze_workspace", }}
    r = query(requests.post, 'workspaces.json', headers=generic_headers, data=json.dumps(payload))
    assert_status(r, 201)

    # Create datastore
    DATASTORE_JSON_FILE = os.path.join(os.path.dirname(__file__), 'datastore_staze.json')
    with open(DATASTORE_JSON_FILE,'r') as f:
        datastore_json = json.loads(f.read())
        datastore_json["dataStore"]["name"] = "staze_datastore"
        connection_parameters_json = datastore_json["dataStore"]["connectionParameters"]["entry"]
        set_conf_value(connection_parameters_json, "host", DB_HOST)
        set_conf_value(connection_parameters_json, "port", DB_PORT)
        set_conf_value(connection_parameters_json, "database", DB_NAME)
        set_conf_value(connection_parameters_json, "user", DB_USER)
        set_conf_value(connection_parameters_json, "passwd", "plain:" + DB_PASSWORD)

        payload = json.dumps(datastore_json)
        r = query(requests.post, 'workspaces/staze_workspace/datastores.json', headers=generic_headers, data=payload)
        assert_status(r, 201)

    # Create featuretypes for merged layers
    layer_dict = {
        "merged_all": "SELECT a.id as name, a.track_type, a.geom FROM public.mainapp_article AS a",
        "merged_ped": "SELECT a.id as name, a.track_type, a.geom FROM public.mainapp_article AS a WHERE "
                      "a.track_type='PED'",
        "merged_cyc": "SELECT a.id as name, a.track_type, a.geom FROM public.mainapp_article AS a WHERE "
                      "a.track_type='CYC'",
    }
    for layer_name in layer_dict:
        layer_sql = layer_dict[layer_name]

        FEATURETYPE_JSON_FILE = os.path.join(os.path.dirname(__file__), 'featuretype_collection.json')
        with open(FEATURETYPE_JSON_FILE,'r') as f:
            featuretype_json = json.loads(f.read())

            featuretype_json["featureType"]["name"] = layer_name
            featuretype_json["featureType"]["title"] = layer_name
            featuretype_json["featureType"]["metadata"]["entry"]["virtualTable"]["sql"] = layer_sql

            payload = json.dumps(featuretype_json)
            r = query(requests.post, 'workspaces/staze_workspace/datastores/staze_datastore/featuretypes.json', headers=generic_headers, data=payload)
            assert_status(r, 201)

    # Create featuretype for individual layer
    FEATURETYPE_JSON_FILE = os.path.join(os.path.dirname(__file__), 'featuretype_individual.json')
    with open(FEATURETYPE_JSON_FILE,'r') as f:
        featuretype_json = json.loads(f.read())
        payload = json.dumps(featuretype_json)
        r = query(requests.post, 'workspaces/staze_workspace/datastores/staze_datastore/featuretypes.json', headers=generic_headers, data=payload)
        assert_status(r, 201)

    # Create style for individual layer
    styling_headers = {"Content-type": "application/vnd.ogc.sld+xml"}
    STYLING_SLD_FILE = os.path.join(os.path.dirname(__file__), 'style_individual.sld')
    with open(STYLING_SLD_FILE) as f:
        styling_sld = f.read()
        r = query(requests.post, 'workspaces/staze_workspace/styles.sld?name=individual_style', headers=styling_headers, data=styling_sld)
        assert_status(r, 201)

    # Patch individual layer to apply style
    LAYER_JSON_FILE = os.path.join(os.path.dirname(__file__), 'layer_individual.json')
    with open(LAYER_JSON_FILE) as f:
        layer_json = json.loads(f.read())
        payload = json.dumps(layer_json)
        r = query(requests.put, 'layers/individual.json', headers=generic_headers, data=payload)
        assert_status(r, 200)
