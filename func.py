
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
def make_demog_vars(df, config):
    print('now we doing the vars combo thing')
    
    # loop through vars and sum the columns associated with the vars
    for var in config['vars']:
        cols = config['vars'][var]
        print(f'Making {var} out of {cols}')
        df[var] = df[cols].sum(axis = 1) # name the column after the key, and sum the columns specified by the value list

    df.to_csv('check_census_totals.csv', index = False) # QA the totals

    # drop the component columns and keep only the totaled vars
    old_cols = flatten_lists(config['vars'].values()) # get one list of columns to drop
    df = df.drop(columns = old_cols)

    return df
