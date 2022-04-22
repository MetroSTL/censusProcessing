import geopandas as gpd
import os
from datetime import datetime as dt
from dotenv import load_dotenv

# census data definitions (year, geographies, columns to pull, etc.)
from census_request import *

# the function used to combine the shapefile with the pulled census data
def build_geodata(census_df):
    print('loading census shapes...')
    geo_file = os.environ['census_geo_shp']
    census_geo = gpd.read_file(geo_file, epsg = 4326) # assume data is unprojected (degrees) 
    
    # keep cols we care about 
    census_geo = census_geo[['GEOID','ALAND','AWATER','geometry']]
    census_geo.columns = ['geo_id','land_area','water_area','geometry']

    # join with census data we've created
    print('joining shapes to demographic data...')
    census_gdf = census_df.merge(census_geo, on = 'geo_id')
    census_gdf = gpd.GeoDataFrame(census_gdf, epsg = 4326) # since the df is on the left, it comes out as a df; recast to gdf
    print(f'{len(census_gdf)} of {len(census_df)} successfully joined to geos ({100 * len(census_gdf) / len(census_df)}%)')

    return census_gdf

def main():
    load_dotenv()

    # load the census inputs config
    cr = census_request(os.environ['api_key'])
    
    # make the census api call and store the returned info in the format we desire
    census_df = cr.download_all()

    # create the census variables we want from our census input data
    census_df = cr.make_demog_vars(census_df)

    # load the census geographies and join
    census_gdf = build_geodata(census_df)
    
    # save the shapefile
    today = dt.now().strftime('%Y%m%d')
    census_gdf.to_file(f'output/census_{cr.type}_{cr.year}_{today}.shp')

main()