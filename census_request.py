import pandas as pd
import numpy as np
import censusdata as cd


# Helper function for make_tidy
# converts the index of the returned census dataframe into a dataframe row of geo information.
# used in the make_tidy function to clean up each row to build a nice census dataframe
def index_to_fips(cen_df,indx):
    temp = pd.DataFrame(cen_df.index[indx].params()).transpose() # convert tuple set to dataframe
    return temp.rename(columns = temp.iloc[0]).drop(temp.index[0]) # take the first row (geo labels) and make it column header


# Helper function for the census download methods
# Takes a censusdata download dataframe, and converts the index geocensus data into a dataframe where each
# there is a column for each geography. Combines that columnized data with the census output and returns the df.
def make_tidy(dl_df):
    fips_set = pd.DataFrame() # empty df to collect all the rows

    # run index_to_fips on each index in the census download dataframe
    for indx in np.arange(len(dl_df)):
        row_fips = index_to_fips(dl_df, indx)  
        fips_set = fips_set.append(row_fips)

    # make a geo ID by concatenating the geo information
    fips_set['geo_id'] = fips_set.sum(axis = 1).astype('Int64').astype(str) # concatenate the fips numbers, recast to int to get rid of the ".0", and then cast to a string...

    # make & return the tidy data set: drop the census geo index from the download data,
    # then join the columnized fips data on the left side; return
    return fips_set.reset_index(drop = True).join(dl_df.reset_index(drop = True))


# a class containing all the info needed to make a census API call 
# and functions that make the call
class census_request:
    # define vars specific to an instance of census_request
    def __init__(self, api_key) -> None:
        self.api_key = api_key
        self.type = 'acs5'
        self.year = 2019
        self.geos = {
            'mo':[('state','29'),('county','510,189'),('block group','*')], # all bg in STL City and STL County
            'il':[('state','17'),('county','163'),('block group','*')] # all bg in St. Clair County
        }
        self.vars = {
            #'minority':,
            #'low_income':,
            #'lep':, # low English proficency
            #'senior':,
            'ada':['B22010_003E','B22010_006E']
        }

    # returns every census column variable listed in vars as a single list
    # https://stackoverflow.com/questions/952914/how-to-make-a-flat-list-out-of-a-list-of-lists
    def list_vars(self):
        return [v for sublist in self.vars.values() for v in sublist]


    # Make census API calls for each set of geos in the object instance. 
    # Append the results to create one output data frame.
    def download_all(self):
        census_df = pd.DataFrame()
        for geo in self.geos:
            print(f'Downloading {self.year} {self.type} info for geos in {geo.upper()}')
            
            c_geo = cd.censusgeo(self.geos[geo]) # the census geography set connected to the geo_key
            dl_df = cd.download(self.type, self.year, c_geo, self.list_vars(), self.api_key)
            dl_df = make_tidy(dl_df)
            census_df = census_df.append(dl_df)
        
        # make a geo ID by concatenating the geo information
        #census_df['geo_id'] = census_df['state'] + census_df['county'] + census_df['tract'] + census_df['block group']
        return census_df

    # make a census api call for one of the stored geos in the census_request object 
    def download_geo(self, geo):
        print(f'Downloading {self.year} {self.type} info for geos in {geo.upper()}')
        census_df = cd.download(self.type, self.year,self.geos['geo'],self.list_vars(),self.api_key)
        census_df = make_tidy(census_df)
        
        # make a geo ID by concatenating the geo information
        census_df['geo_id'] = census_df['state'] + census_df['county'] + census_df['tract'] + census_df['block group']

        return census_df

    # build demographic variables from the census dataframe. take the census input dictionary of vars,
    # and create columns of demographic totals. Name the columns after the keys in the census input dictionary.
    # Then, drop the component columns and return the completed demographic data sets 
    def make_demog_vars(self, census_df):
        
        # loop through vars and sum the columns associated with the vars
        for var in self.vars:
            cols = self.vars[var] # input cols to create the var
            print(f'Making {var} out of {cols}')
            census_df[var] = census_df[cols].sum(axis = 1) # name the column after the key, and sum the columns specified by the value list

        census_df.to_csv('QA/check_census_totals.csv', index = False) # QA the totals

        # drop the component columns and keep only the totaled vars
        old_cols = self.list_vars() # get one list of columns to drop
        census_df = census_df.drop(columns = old_cols)

        return census_df