from helpers import *

# census data definitions (year, geographies, columns to pull, etc.)
from definitions import *

# the functions used to process the census info
from func import *

def main():
    load_dotenv()

    # load the census inputs config
    census_config = census_inputs()
    
    # make the census api call and store the returned info in the format we desire
    census_df = pull_census_data(census_config)

    # create the census variables we want from our census input data
    census_df = make_demog_vars(census_df, census_config)
    print(census_df)

    # load the census geographies and join
        # ?? need to clip using the service area and compute the ratio of each geo left over
        # apply the ratio of geos leftover to the totals
    census_gdf = build_geodata(census_df)
    print(census_gdf.info(), census_gdf.head())
    
    # save the shapefile
        # Where? metroas08? W:/R&D? AGOL/Enterprise?

main()