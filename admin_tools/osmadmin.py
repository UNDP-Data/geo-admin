import json
import httpx
import requests
import asyncio

async def get_admin_level_bbox(iso3, admin_level=2):
    overpass_url = "http://overpass-api.de/api/interpreter"

    overpass_query = \
        f"""
        [out:json];
        area["ISO3166-1:alpha3"="{iso3}"][admin_level="{admin_level}"];
        rel(pivot)["boundary"="administrative"];
        out bb;

    """
    async with httpx.AsyncClient(timeout=100) as client:
        response = await client.post(overpass_url, data=overpass_query)
        data = response.json()
        bounds = data['elements'][0]['bounds']
        return bounds['minlon'], bounds['minlat'], bounds['maxlon'], bounds['maxlat']


async def get_admin_level_centroid(iso3, admin_level=2):
    overpass_url = "http://overpass-api.de/api/interpreter"

    overpass_query = f"""
    [out:json];
    area["ISO3166-1:alpha3"="{iso3}"][admin_level="{admin_level}"];
    rel(area)["boundary"="administrative"];
    out center;
    """



    async with httpx.AsyncClient() as client:
        response = await client.post(overpass_url, data=overpass_query)
        if response.status_code == 200:
            data = response.json()
            if 'elements' in data and len(data['elements']) > 0:
                for element in data['elements']:
                    if 'center' in element:
                        return element['center']
            return "Centroid not found"
        else:
            return f"Error: {response.status}"


async def get_admin1_unit_centroid(iso3, lat, lon):
    overpass_url = "http://overpass-api.de/api/interpreter"

    overpass_query = f"""
        [out:json];
            rel["ISO3166-2"~"^FR"]
            [admin_level=4]
            [type=boundary]
            [boundary=administrative];
        out center;
        """
    async with httpx.AsyncClient() as client:
        response = await client.post(overpass_url, data={"data": overpass_query})
        if response.status_code == 200:
            data = response.json()
            print(response.text)
            if 'elements' in data and len(data['elements']) > 0:
                for element in data['elements']:
                    if element['type'] == 'relation':
                        if 'tags' in element and 'admin_level' in element['tags'] and element['tags'][
                            'admin_level'] == '1':
                            for member in element['members']:
                                if member['type'] == 'node' and 'lat' in member and 'lon' in member:
                                    return {
                                        'id': element['id'],
                                        'lat': member['lat'],
                                        'lon': member['lon'],
                                        'name': element['tags'].get('name', 'Unknown')
                                    }
            return "Admin1 unit not found"
        else:
            return f"Error: {response.status}"


def fetch_admin1(iso3=None, lat=None, lon=None):
    overpass_url = "http://overpass-api.de/api/interpreter"

    overpass_query = f"""
    [out:json];
    is_in({lat},{lon});
    area._[admin_level=2];
    out body;
    """

    response = requests.post(overpass_url, data={"data": overpass_query})

    if response.status_code == 200:
        data = response.json()
        for element in data['elements']:
            print(json.dumps(element, indent=4))
            if element['type'] == 'area' and 'tags' in element and 'name' in element['tags']:
                return element['tags']['name']
        return "Admin1 unit not found"
    else:
        return f"Error: {response.status_code}"




# Example usage
lon, lat = 69.33260025567472, 34.55406901286477

admin1_unit = asyncio.run(get_admin1_unit_centroid(iso3='AFG', lat=lat, lon=lon))
print(f"The point ({lat}, {lon}) belongs to admin1 unit: {admin1_unit}")

# bb = asyncio.run(get_admin_level_bbox(iso3='AFG', admin_level=2))
# print(bb)
#
# c = asyncio.run(get_admin_level_centroid(iso3='AFG', admin_level=3))
# print(c)