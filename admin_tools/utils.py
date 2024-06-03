import json

from osgeo import gdal, ogr
import requests
RESTCOUNTRIES_BASE_URL='https://restcountries.eu/v3.1/'
gdal.UseExceptions()
def get_field(src_path_or_ds=None, layer_name=None, field_name=None, unique=False, **kwargs):
    """
    Fetch all values from a geospatial vector dataset's layer field
    :param src_ds: path or gdal.Dataset instance
    :param layer_name: str
    :param field_name, str, name of the attr field to read
    :param unique: bool=False, return unique values only
    :return: iter holding values

    """


    if isinstance(src_path_or_ds, str):
        src_ds = gdal.OpenEx(src_path_or_ds, gdal.OF_READONLY|gdal.OF_VECTOR)
    else:
        src_ds = src_path_or_ds
    lnames = [src_ds.GetLayer(i).GetName() for i in range(src_ds.GetLayerCount())]
    assert layer_name not in ('', None) and layer_name in lnames, f'invalid layer_name={layer_name}. valid layer names are {",".join(lnames)}'

    layer = src_ds.GetLayerByName(layer_name)
    ldef = layer.GetLayerDefn()
    field_names = [ldef.GetFieldDefn(i).GetName() for i in range(ldef.GetFieldCount())]

    assert field_name not in ('', None) and field_name in field_names, f'invalid field_name={field_name}. Valid field names are {",".join(field_names)}'
    q = []
    for k, v in kwargs.items():
        if k in field_names:
            q.append(f"{k}='{v}'")

    query_text = ' AND '.join(q)
    layer.SetAttributeFilter(query_text)

    field_vals = (f.GetField(field_name) for f in layer)

    if unique:
        return set(field_vals)
    else:
        return list(field_vals)

def scale_pos(longitude):
    return (longitude + 180) / 4.5 + 10

def unscale_pos(new_longitude):
    return ((new_longitude - 10) * 4.5) - 180

def get_iso3_ccodes():
    pass
if __name__ == '__main__':
    src_path = '/data/hreaibm/admfieldmaps/adm0_simpl.shp'
    vals = get_field(src_path_or_ds=src_path, layer_name='adm0_simpl', field_name='iso_3', unique=True,
                     status_cd=1)

    get_iso3_ccodes()
    from admin_tools.uniqueid import lonlat2id, id2lonlat

    # Example usage
    lon, lat = -169.33259181615757, -34.55406470337032

    llid = lonlat2id(lon=lon, lat=lat, precision=2)
    print(f"Original: (lon: {lon}, lat: {lat})")
    print(llid, len(str(llid)))
    rlon, rlat = id2lonlat(llid)
    print(rlon, rlat)