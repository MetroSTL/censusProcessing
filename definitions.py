# define block groups in our area of interest

# define demographic information of interest; use a dict where key is title VI column and
# value is a list of census columns that feed into that title VI column
def census_inputs():
    return {
        'census_type':'acs5',
        'census_year':2019,
        'geos':{
            'mo':[('state','29'),('county','510,189'),('block group','*')], # all bg in STL City and STL County
            'il':[('state','17'),('county','163'),('block group','*')] # all bg in St. Clair County
        },
        'vars': {
            #'minority':,
            #'low_income':,
            #'lep':, # low English proficency
            'ada':['B22010_003E','B22010_006E']
        }
    }