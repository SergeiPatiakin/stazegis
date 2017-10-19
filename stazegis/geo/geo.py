import ogr

def gpx_to_wkt(filepath):
    # Can't inline this due to gotcha: https://trac.osgeo.org/gdal/wiki/PythonGotchas
    ds = ogr.Open(filepath)
    layer = ds.GetLayerByName("tracks")
    assert layer.GetFeatureCount() == 1 # Assert we have a single track
    feature = layer.GetFeature(0)
    geom = feature.GetGeometryRef()
    wkt = geom.ExportToWkt()
    return wkt