#!/awips2/python/bin/python

####################################################################
#
# Script: importSingleShapefile.py
#
# Author: Darrel Kingfield (NOAA/GSL)
#
# Description: Python implementation of the following script:
# /awips2/database/sqlScripts/share/sql/maps/importShapeFile.sh
# that allows for both the dropping/rebuilding of a table from
# scratch (no -a flag) and the appending of information to an
# existing table (-a flag). This implementation allows for unique
# analysis geospatial datasets to be managed in separate shapefiles
# but imported into a single AWIPS database table.
#
####################################################################


import argparse
import os
import subprocess

# Configuration constants and commands
pgUser = "awipsadmin"
pgPort = 5432
pgBinDir = os.path.join(os.sep, "awips2", "postgresql", "bin")
psqlBinDir = os.path.join(os.sep, "awips2", "psql", "bin")
geometryLevels = ["0.064", "0.016", "0.004", "0.001"]
psqlCommand = f"a2dbauth {psqlBinDir}/psql"
vacuumDbCommand = f"a2dbauth {pgBinDir}/vacuumdb"


# Set environment variables
pgShareDir = os.path.join(os.sep, "awips2", "postgresql", "share")
gdalDataDir = os.path.join(pgShareDir, "gdal")
projDir = os.path.join(pgShareDir, "proj")
os.environ["GDAL_DATA"] = gdalDataDir
os.environ["PROJ_LIB"] = projDir

# Establish the parser arguments
parser = argparse.ArgumentParser()
parser.add_argument("-s", "--shapefile", dest = "shapefilePath", help="Path to shapefile", required=True)
parser.add_argument("-t", "--table", dest = "tableName", help="Table name", required=True)
parser.add_argument("-a", "--append", dest = "append", help="Append to existing table", default=False, const=True, nargs="?", type=bool)

# Parse the arguments
args = parser.parse_args()

argShapefilePath = args.shapefilePath
argTableName = args.tableName
if not argShapefilePath:
    print("ERROR: No shapefile path provided, please re-run with a shapefile path")
    exit()
if not argTableName:
    print("ERROR: No table name provided, please re-run with a table name")
    exit()

# Get the full path to the shapefile
shapefilePath = subprocess.Popen(f"readlink -f {args.shapefilePath}", stdout=subprocess.PIPE, shell=True).communicate()[0].strip().decode()

# Check that the shapefile exits
if not os.path.exists(shapefilePath):
    print(f"ERROR: File not found or is not readable: {shapefilePath}")
    exit()

# The path directory where the shapefile is found
shapefileDir = os.path.dirname(shapefilePath)
shapefileName = os.path.basename(shapefilePath)
shapefileBase = ".".join(os.path.basename(shapefilePath).split(".")[:-1])
shapefileExt = os.path.basename(shapefilePath).split(".")[-1]
projectionPath = os.path.join(shapefileDir, f"{shapefileBase}.prj")

srcSrid = ""
if not os.path.exists(projectionPath):
    print("WARNING: No projection file (.prj) found. Assuming a source projection of WGS84")
    srcSrid = "-s_srs EPSG:4326"

tableName = argTableName.lower()
psqlHeaderCommand = f"{psqlCommand} -d maps -U {pgUser} -q -p {pgPort} -c"
tableAppend = args.append


# Drop names if updating certain tables
syscmd = None
if tableName == "county":
    syscmd = f'''{psqlHeaderCommand} "DROP VIEW IF EXISTS mapdata.county_names;"'''
elif tableName == "marinezones" or tableName == "offshore":
    syscmd = f'''{psqlHeaderCommand} "DROP VIEW IF EXISTS mapdata.alaska_marine;"'''
if syscmd:
    os.system(syscmd)

if not tableAppend:
    # Drop the entry from public.geometry_columns and mapdata.map_version table
    command1 = f"""DELETE FROM public.geometry_columns WHERE f_table_schema = 'mapdata' AND f_table_name = '{tableName}'"""
    command2 = f"""DELETE FROM mapdata.map_version WHERE table_name='{tableName}'"""
    syscmd = f'''{psqlHeaderCommand} "{command1}; {command2}"'''
    os.system(syscmd)

# Drop the table completely if the -a or --append flag is not set
appendFlag = " -a"
if not tableAppend:
    appendFlag = ""
    syscmd = f'''{psqlHeaderCommand} "DROP TABLE IF EXISTS mapdata.{tableName}"'''
    os.system(syscmd)

# Create a temporary directory
tempDirectory = subprocess.Popen(f"mktemp --directory", stdout=subprocess.PIPE, shell=True).communicate()[0].strip().decode()

# Convert shapefile and import shapefiles into the mapdata.table
syscmd = f'''a2dbauth -f {pgBinDir}/ogr2ogr -f "ESRI Shapefile" -overwrite {tempDirectory} {shapefilePath} {srcSrid} -t_srs EPSG:4326'''
os.system(syscmd)

# Import into an empty table or append to the existing table
syscmd = f'''a2dbauth -f {pgBinDir}/shp2pgsql -W LATIN1 -s 4326 -g the_geom{appendFlag} -I {tempDirectory}/{shapefileName} mapdata.{tableName} | {psqlCommand} -d maps -U {pgUser} -q -p {pgPort} -f -'''
os.system(syscmd)


command1 = f"""INSERT INTO mapdata.map_version (table_name, filename) values ('{tableName}','{shapefileName}')"""
command2 = f"""SELECT AddGeometryColumn('mapdata','{tableName}','the_geom_0','4326',(SELECT type FROM public.geometry_columns WHERE f_table_schema='mapdata' and f_table_name='{tableName}' and f_geometry_column='the_geom'),2)"""
command3 = f"""UPDATE mapdata.{tableName} SET the_geom_0=ST_Segmentize(the_geom,0.1)"""
command4 = f"""CREATE INDEX {tableName}_the_geom_0_gist ON mapdata.{tableName} USING gist(the_geom_0)"""

if tableAppend:
    command1 = ""
    command2 = ""
    command4 = ""

commandsString = ""
for c in [command1, command2, command3, command4]:
    if c:
        commandsString += f"{c}; "

syscmd = f'''{psqlHeaderCommand} "{commandsString}"'''
os.system(syscmd)

# Remove the temporary directory
if os.path.exists(tempDirectory):
    syscmd = "rm -rvf {tempDirectory}"
    os.system(syscmd)

# Create simplificaiton levels for non-point data
syscmd = f'''{psqlCommand} -d maps -U {pgUser} -qt -p {pgPort} -c "SELECT type FROM public.geometry_columns WHERE f_table_schema='mapdata' and f_table_name='{tableName}' and f_geometry_column='the_geom';"'''
geometryType = subprocess.Popen(syscmd, stdout=subprocess.PIPE, shell=True).communicate()[0].strip().decode()
if "POINT" not in geometryType:
    for level in geometryLevels:
        levelSuffix = level.replace(".", "_")
        command1 = f"""SELECT AddGeometryColumn('mapdata','{tableName}','the_geom_{levelSuffix}','4326',(SELECT type FROM public.geometry_columns WHERE f_table_schema='mapdata' and f_table_name='{tableName}' and f_geometry_column='the_geom'),2)"""
        command2 = f"""UPDATE mapdata.{tableName} SET the_geom_{levelSuffix}=ST_Segmentize(ST_Multi(ST_SimplifyPreserveTopology(the_geom,{level})),0.1)"""
        command3 = f"""CREATE INDEX {tableName}_the_geom_{levelSuffix}_gist ON mapdata.{tableName} USING gist(the_geom_{levelSuffix})"""
        commandsString = ""
        if tableAppend:
            command1 = "" ; command3 = ""
        for c in [command1, command2, command3]:
            if c:
                commandsString += f"{c}; "
        syscmd = f'''{psqlHeaderCommand} "{commandsString}"'''
        os.system(syscmd)

if tableName == "county":
    command1 = """CREATE OR REPLACE VIEW mapdata.county_names AS SELECT countyname as name, ST_SetSRID(ST_Point(lon,lat), 4326)::geometry(Point, 4326) as the_geom FROM mapdata.county;"""
    syscmd = f'''{psqlCommand} "{command1}"'''
    os.system(syscmd)
elif tableName == "marinezones" or tableName == "offshore":
    command1 = """CREATE OR REPLACE VIEW mapdata.alaska_marine AS
        SELECT CAST(ROW_NUMBER() OVER(ORDER BY id) AS INT) GID, * FROM (
            SELECT id, wfo, name, lat, lon,
                the_geom, the_geom_0, the_geom_0_064, the_geom_0_016, the_geom_0_004, the_geom_0_001
            FROM mapdata.marinezones WHERE wfo IN ('AFC', 'AFG', 'AJK')
            UNION
            SELECT id, wfo, name, lat, lon,
                the_geom, the_geom_0, the_geom_0_064, the_geom_0_016, the_geom_0_004, the_geom_0_001
            FROM mapdata.offshore WHERE wfo IN ('AFC', 'AFG', 'AJK')
        ) a;"""
    syscmd = f'''{psqlCommand} "{command1}"'''
    os.system(syscmd)

syscmd = f"""{vacuumDbCommand} -d maps -t mapdata.{tableName} -U {pgUser} -p {pgPort} -vfz"""
os.system(syscmd)
