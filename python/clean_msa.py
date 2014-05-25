import pandas as pd
# Read in data frame
msa_raw = pd.read_csv('data/raw/PEP_2013_PEPANNGCT.US24PR_with_ann.csv')

# Create clean data frame
# Limit to only US metro area rows (exclude country total, headers and Puerto Rico)
s = 'United States - In metropolitan statistical area'
msa = msa_raw[msa_raw['GC.display-label'].str.startswith(s)].reset_index()
# Rename columns
msa.rename(columns={'GC.display-label.1' : 'msa', 'rescen42010' : 'pop2010'}
    , inplace=True)
# Recast pop2010 as int32
msa['pop2010'] = msa['pop2010'].astype('int32')
# Sort descending on population
msa = msa.sort('pop2010', ascending=False).reset_index()
# Keep only name and census 2010 pop fields
msa = msa[['msa','pop2010']]

#Export to csv
msa.to_csv('data/clean/msa.csv')

# Create craigslist cities dataset for top 50 MSAs
# Find clcity, where http://[clcity].craigslist.org/ is valid Craigslist URL

# Limit to top 50 MSAs
cl = msa.head(50)
# Extract first part of MSA (before '-', ',' or '/'), make lowercase and remove spaces/'.'
cl['clcity'] = cl['msa'].str.extract(r'([^-,/]*)').str.lower().str.replace(r'\s|\.','')
# Replace values for exceptions
remaps = {
          'washington':'washingtondc',
          'sanfrancisco':'sfbay',
          'riverside':'inlandempire',
          'virginiabeach':'norfolk',
          'birmingham':'bham',
          'sanjose':'' #part of sfbay
          }
def remap(city):
    if city in remaps.keys():
        return remaps[city]
    else:
        return city
cl['clcity'] = cl['clcity'].map(lambda x: remap(x))

# Export to csv
cl.to_csv('data/clean/clcity.csv')
