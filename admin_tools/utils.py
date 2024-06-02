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

def float_to_fixed(val, precision=1e6):
    """Convert a floating point number to a fixed point integer."""
    return int(round(val * precision))

def fixed_to_float(val, precision=1e6):
    """Convert a fixed point integer back to a floating point number."""
    return val / precision
def encode(lat, lon, precision=1e6):
    """Encode latitude and longitude to a single positive integer."""
    # Define a bias to ensure all values are positive
    bias = 2 ** 31

    # Scale and convert to fixed point
    lat_fixed = float_to_fixed(lat, precision) + bias
    lon_fixed = float_to_fixed(lon, precision) + bias

    # Combine them into a single integer
    encoded = (lat_fixed << 32) | lon_fixed
    return encoded


def decode(encoded, precision=1e6):
    """Decode a single positive integer back to latitude and longitude."""
    # Define a bias to ensure all values are positive
    bias = 2 ** 31

    # Extract lat_fixed and lon_fixed from the encoded integer
    lat_fixed = (encoded >> 32) - bias
    lon_fixed = (encoded & 0xFFFFFFFF) - bias

    # Convert back to float
    lat = fixed_to_float(lat_fixed, precision)
    lon = fixed_to_float(lon_fixed, precision)
    return lat, lon

def get_iso3_ccodes():
    pass
if __name__ == '__main__':
    src_path = '/data/hreaibm/admfieldmaps/adm0_simpl.shp'
    vals = get_field(src_path_or_ds=src_path, layer_name='adm0_simpl', field_name='iso_3', unique=True,
                     status_cd=1)

    get_iso3_ccodes()
    from admin_tools.uniqueid import lonlat2id, id2lonlat

    # Example usage
    lon, lat = -.419452341, -.77495678

    llid = lonlat2id(lon=lon, lat=lat, precision=3)
    print(f"Original: (lon: {lon}, lat: {lat})")
    print(llid, len(str(llid)))
    rlon, rlat = id2lonlat(llid)
    print(rlon, rlat)