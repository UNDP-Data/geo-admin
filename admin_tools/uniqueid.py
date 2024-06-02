from osgeo import gdal, ogr
gdal.UseExceptions()

'''
------------------------------------------------------------------------------------------------------------------------
decimal decimal     DMS              Object that can be unambiguously         N/S or E/W   E/W at      E/W at       E/W at 
places  degrees                       recognized at this scale                 at equator    23N/S      45N/S       67N/S
------------------------------------------------------------------------------------------------------------------------
0	    1.0	        1° 00′ 0″	        country or large region	                 111 km	    102 km	    78.7 km	    43.5 km
1	    0.1	        0° 06′ 0″	        large city or district	                 11.1 km	10.2 km	    7.87 km	    4.35 km
2	    0.01	    0° 00′ 36″	        town or village	                         1.11 km	1.02 km	    0.787 km	0.435 km
3	    0.001	    0° 00′ 3.6″	        neighborhood, street	                 111 m	    102 m	    78.7 m	    43.5 m
4	    0.0001	    0° 00′ 0.36″	    individual street, large buildings	     11.1 m	    10.2 m	    7.87 m	    4.35 m
5	    0.00001	    0° 00′ 0.036″	    individual trees, houses	             1.11 m	    1.02 m	    0.787 m	    0.435 m
6	    0.000001	0° 00′ 0.0036″	    individual humans	                     111 mm	    102 mm	    78.7 mm	    43.5 mm
7	    0.0000001	0° 00′ 0.00036″	    practical limit of commercial surveying	 11.1 mm	10.2 mm	    7.87 mm	    4.35 mm
8	    0.00000001	0° 00′ 0.000036″	specialized surveying	                 1.11 mm	1.02 mm	    0.787 mm	0.435 mm
-------------------------------------------------------------------------------------------------------------------------
'''

import math


def encode_base36(num):
    """Encode a number in base-36 with padding."""
    base36 = ''
    chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    while num > 0:
        num, rem = divmod(num, 36)
        base36 = chars[rem] + base36
    return base36.zfill(5)  # Pad to ensure at least 5 characters

def decode_base36(base36):
    """Decode a base-36 encoded number."""
    num = 0
    for char in base36:
        num = num * 36 + int(char, 36)
    return num


def admin0_iso32id(iso3_country_code=None):
    """
    Convert iso3 country code to integer admin0 id
    :param iso3_country_code:
    :return:
    """
    return int(''.join(map(str, map(ord, iso3_country_code))))

def admin0_id2iso3(admin0id=None):
    """
    Convert admin0 id to iso
    :param admin0id:
    :return:
    """
    strid = str(admin0id)
    idlen = len(strid)
    assert idlen == 6, f'admin0 id "{strid}" is not a 6 number value'
    chunk_size = idlen//3
    return ''.join(map(chr, map(int, (strid[idx: idx + chunk_size] for idx in range(0, idlen, chunk_size)))))

def scale_pos(number):
    """rescale tgo interval 10:99"""
    #return (number + 180) / 4.5 + 10
    return ((number + 180) * 89 / 360) + 10

def unscale_pos(number):
    """unscale from interval 10:90"""
    #return ((number - 10) * 4.5) - 180
    return ((number - 10) * 360 / 89) - 180
def id2lonlat(intid=None):
    """
    Coverting an admin id derived using lonlat2id into its original lon and lat coodinates
    accounting for loss of precision
    The Number is converted to string, split into two equal parts corresponding to positive lon and lat
    . Next precision is extracted consdering that each of the positive coords contains 3 digist for integer part
    and the rest anre represented by precision. The positive lon/lat are divided by precision
    and unscaled from positive to ofriginla range that is -180:+180 for longitude
    and -90:+90 for latitude
    :param intid:
    :return:
    """
    sid = str(intid)
    sidlen = len(sid)
    assert sidlen % 2 == 0, f'Invalid intid={intid}. Needs to have an even number of digits '
    silon = sid[:sidlen//2]
    silat = sid[sidlen//2:]
    nzeros = len(silon)-2 # 3 because the integer part of positive lon/lat can take max 3 digits
    precision = 10**nzeros
    poslon = int(silon)/precision
    poslat = int(silat)/precision
    return unscale_pos(poslon), unscale_pos(poslat)

def lonlat2id(lon=None, lat=None, precision=3):
    """
    Create an id form 2 float lon&lat coordinates by scaling to
    positive (0-360) for lon and 0-180 for lat, multiplying by
    10 at the power of precision, converting to int using integer division
    , padding with three zeros to account for new scaled lon/lat values and
    combining lon and lat into a string and converting one more time to int

    Using integer division the coordinates are floored and rounded using the provided precision. This
    ensures that small change in the input coordinates will produce more or less same output.
    This is done to be able to join these ids to future version of admin units  whose geometry has been slightly altered




    :param lon: float, longitude of admin centroid
    :param lat: float, latitude of admin centroid
    :param precision: integer, the number of digits to be retained from teh lon and lat
    :return: admin id as int
    """
    poslon = scale_pos(lon)
    poslat = scale_pos(lat)
    # ilon = int(poslon//10**-precision)
    # ilat = int(poslat//10**-precision)
    ilon = int(poslon*10**precision)
    ilat = int(poslat*10**precision)
    return int(f'{ilon}{ilat}')





def get_admin2_id(
                  admin_entity_geom:ogr.Geometry=None,
                  precision=1e3):



    c = admin_entity_geom.Centroid()
    x = c.GetX()
    y = c.GetY()
    print(x, y)
    xrel = int(x // precision)
    yrel = int(y // precision)




def calculate_extent(layer):
    # Initialize min and max values
    minX, minY, maxX, maxY = float('inf'), float('inf'), float('-inf'), float('-inf')

    # Reset the reading to start from the first feature
    layer.ResetReading()

    # Iterate through the features
    for feature in layer:
        geom = feature.GetGeometryRef()
        if geom is not None:
            # Get the bounding box of the geometry
            geom_minX, geom_maxX, geom_minY, geom_maxY = geom.GetEnvelope()
            # Update the extent values
            minX = min(minX, geom_minX)
            maxX = max(maxX, geom_maxX)
            minY = min(minY, geom_minY)
            maxY = max(maxY, geom_maxY)

    return (minX, maxX, minY, maxY)
def read_adm1(src_path=None):
    thel = list()
    ds = gdal.OpenEx(src_path)
    l = ds.GetLayer(0)
    iso3_codes_l = [f.GetField('iso_3_grp') for f in l]
    iso3_codes = set(iso3_codes_l)
    #with open('/data/hreaibm/admfieldmaps/a1.csv', 'w') as srca1:
        #srca1.write(f'admin1_name,a1id\n' )
    for cc in sorted(iso3_codes):
        #convert iso3 code to int using ord functions

        a0id = admin0_iso32id(iso3_country_code=cc)
        l.SetAttributeFilter(f"iso_3_grp='{cc}'")
        print(f'{cc} : {a0id} {l.GetFeatureCount()}')
        for feature in l:
            olda1id = feature.GetField('adm1_id')
            a1name = feature.GetField('adm1_name')

            geom = feature.GetGeometryRef()

            if geom is not None:
                c = geom.Centroid()
                a1id = lonlat2id(
                                     lon=c.GetX(),
                                     lat=c.GetY(),
                                     precision=3
                                     )
                ea1id = encode_base36(a1id)
                ra1id = decode_base36(ea1id)
                assert a1id == ra1id
                aid = f'{cc}{ea1id}'
                print(f'adm1name {a1name} a1id {a1id}')
                thel.append(a1id)
                #srca1.write(f'{a1name},{aid}\n')

            #l.SetAttributeFilter(None)
            #l.ResetReading()
            #break
        break
    del ds
    return thel

def dissolve(lyr=None):

    multi = ogr.Geometry(ogr.wkbMultiPolygon)

    for feat in lyr:
        g = feat.GetGeometryRef()
        if g:
            g.CloseRings()  # this copies the first point to the end
            wkt = feat.geometry().ExportToWkt()
            multi.AddGeometryDirectly(ogr.CreateGeometryFromWkt(wkt))

    multi.UnionCascaded()
    return multi


def read_adm2(src_path=None, precision=4):

    #assert str(int(precision)).count("0")<7, 'precision is invalid'
    thel = list()
    ds = gdal.OpenEx(src_path)
    l = ds.GetLayer(0)
    iso3_codes_l = [f.GetField('iso_3_grp') for f in l]
    iso3_codes = set(iso3_codes_l)
    # with open('/data/hreaibm/admfieldmaps/a2.csv', 'w') as srca1:
    #     srca1.write(f'adm2_id,a2id\n' )
    for cc in sorted(iso3_codes):
        #convert iso3 code to int using ord functions
        if cc != 'AFG':continue
        a0id = admin0_iso32id(iso3_country_code=cc)
        l.SetAttributeFilter(f"iso_3_grp='{cc}'")

        adm1_ids = sorted(set([f.GetField('adm1_id') for f in l]))
        print(f'{cc} {a0id}')
        for admin1id in adm1_ids:
            l.SetAttributeFilter(f"adm1_id='{admin1id}'")

            adm1_geom = dissolve(lyr=l)
            adm1_centroid = adm1_geom.Centroid()

            a1id = lonlat2id(lon=adm1_centroid.GetX(), lat=adm1_centroid.GetY(), precision=precision)

            #thel.append(a1id)
            print(f'\t{admin1id} {a1id} ')
            for feature in l:

                olda2id = feature.GetField('adm2_id')
                a1name = feature.GetField('adm1_name')
                a2name = feature.GetField('adm2_name')

                geom = feature.GetGeometryRef()

                if geom is not None:
                    c = geom.Centroid()
                    a2id = lonlat2id(
                                         lon=c.GetX(),
                                         lat=c.GetY(),
                                         precision=precision
                                         )

                    fa2id = int(f'{a0id}{a1id}{a2id}')

                    #print(f'a1name: {a1name} a1id {a1id} a2name {a2name} a2id {a2id}')

                    print(f'\t\t{a2name} {fa2id}')

                    #srca1.write(f'{olda2id},{fa2id}\n')
                    #break
            l.SetAttributeFilter(None)
            l.ResetReading()

            #break
        #break

    del ds
    return thel


if __name__ == '__main__':

    adm1_path = '/data/hreaibm/admfieldmaps/adm1_simpl.shp'
    adm2_path = '/data/hreaibm/admfieldmaps/adm2_simpl.shp'

    #l1 = read_adm1(src_path=adm1_path)
    l2 = read_adm2(src_path=adm2_path)
    # for i in range(len(l1)):
    #     print(l1[i], l2[i], l1[i] == l2[i])
    #












