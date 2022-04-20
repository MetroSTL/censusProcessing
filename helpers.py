import pandas as pd
import numpy as np
import censusdata as cd
import geopandas as gpd
import os
from dotenv import load_dotenv

# appends all the lists in a list of lists into one list. Get the gist?
# taken from https://stackoverflow.com/questions/952914/how-to-make-a-flat-list-out-of-a-list-of-lists
def flatten_lists(list_of_lists):
    return [item for cols in list_of_lists for item in cols]


# converts the index of the returned census dataframe into a dataframe row of geo information.
# used in the make_tidy function to clean up each row to get a nice census dataframe
def index_to_fips(cen_df,indx):
    temp = pd.DataFrame(cen_df.index[indx].params()).transpose() # convert tuple set to dataframe
    return temp.rename(columns = temp.iloc[0]).drop(temp.index[0]) # take the first row (geo labels) and make it column header


# Takes a censusdata download dataframe, and converts the index geocensus data into a dataframe where each
# column is the statecode, county code, etc. and combines that columnized data with the census output.
# Returns a dataframe of fips information with column headers for the geo
def make_tidy(dl_df):
    fips_set = pd.DataFrame() # empty df to collect all the rows

    # run index_to_fips on each index in the census download dataframe
    for indx in np.arange(len(dl_df)):
        row_fips = index_to_fips(dl_df, indx)  
        fips_set = fips_set.append(row_fips)

    # make & return the tidy data set: drop the census geo index from the dowload data,
    # then join the columnized fips data on the left side, making one nice data set
    return fips_set.reset_index(drop = True).join(dl_df.reset_index(drop = True))