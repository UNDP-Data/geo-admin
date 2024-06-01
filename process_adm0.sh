#!/bin/bash

# cmd to extract the  update time of fieldmapsio

level="adm0"

cmd=`curl https://fieldmaps.io/data/adm0 | grep '<p>Updated:' | sed -n 's:.*<p>\(.*\)</p>.*:\1:p'`

res=${cmd}

update_date_str=${cmd#*, }
#echo $update_date_str


last_update=$(date -d "$update_date_str" +"%Y%m%d")
#echo $last_update
today=$(date +"%Y%m%d")
#echo $today
# Compare the dates

if [ "$last_update" -eq "$today" ]; then
  echo "Going to update"

elif [ "$last_update" -lt "$today" ]; then
  echo "No updates available"
fi


adm0_url="https://data.fieldmaps.io/adm0/osm/intl/adm0_polygons.gpkg.zip"
adm0_name="adm0_polygons.gpkg.zip"


if [ ! -e "$adm0_name" ]; then
  echo "File $file_name does not exist. Downloading..."
  curl  -L -C - -o "$adm0_name" "$adm0_url"
  echo "Download complete."
else
  echo "processing $admin0_name ..."
  gdald ogr2ogr -of GeoJSON -clipsrc -180 -85.06 180 85.06 -makevalid /data/hreaibm/admfieldmaps/script/adm0.geojson /vsizip//data/hreaibm/admfieldmaps/script/adm0_polygons.gpkg.zip/adm0_polygons.gpkg -progress -lco RFC7946=YES
  mapshaper mapshaper-xl /data/hreaibm/admfieldmaps/script/adm0.geojson -simplify visvalingam percentage=0.1 -filter-islands min-area=100km2 min-vertices=5 remove-empty -o /data/hreaibm/admfieldmaps/script/adm0_simpl.shp
  gdald ogr2ogr -of FlatGeobuf -t_srs EPSG:8857 /data/hreaibm/admfieldmaps/script/adm0_simpl_eqar.fgb /data/hreaibm/admfieldmaps/adm0_simpl.shp -progress -nlt PROMOTE_TO_MULTI
fi



