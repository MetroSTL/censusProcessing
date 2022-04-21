
from helpers import *

# make the API call to download census data for the geographies that we want,
# then assemble the data that is returned into a nice dataframe. return the dataframe.
def pull_census_data(config):

    # pull together the key inputs
    api_key = os.environ['api_key']
    yr = config['census_year']
    acs = config['census_type']
    census_cols = flatten_lists(config['vars'].values()) # gets all the census columns we need to pull in one list

    # Download data for each set of census geos
    census_df = pd.DataFrame()
    for geo_key in config['geos']:
        print(f'Downloading {yr} {acs} info for geos in {geo_key.upper()}')
        census_geos = cd.censusgeo(config['geos'][geo_key]) # the census geography set connected to the geo_key
        
        dl_df = cd.download(acs, yr, census_geos, census_cols, api_key)
        dl_df = make_tidy(dl_df)
        census_df = census_df.append(dl_df)

    # make a geo ID by concatenating the geo information
    census_df['geo_id'] = census_df['state'] + census_df['county'] + census_df['tract'] + census_df['block group']

    return census_df


# build demographic variables from the census dataframe. take the census input dictionary of vars,
# and create columns of demographic totals. Name the columns after the keys in the census input dictionary.
# Then, drop the component columns and return the completed demographic data sets 
def make_demog_vars(census_df, config):
    print('now we doing the vars combo thing')
    
    # loop through vars and sum the columns associated with the vars
    for var in config['vars']:
        cols = config['vars'][var]
        print(f'Making {var} out of {cols}')
        census_df[var] = census_df[cols].sum(axis = 1) # name the column after the key, and sum the columns specified by the value list

    census_df.to_csv('QA/check_census_totals.csv', index = False) # QA the totals

    # drop the component columns and keep only the totaled vars
    old_cols = flatten_lists(config['vars'].values()) # get one list of columns to drop
    census_df = census_df.drop(columns = old_cols)

    return census_df

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
    print(f'{len(census_gdf)} of {len(census_df)} successfully joined to geos ({100 * len(census_gdf) / len(census_df)}%)')

    return census_gdf