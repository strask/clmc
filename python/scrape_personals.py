import time
import pandas as pd
from output_city_personals import output_city_personals

output_file = 'data/clean/cl_missed_connections.tsv'
city_file = 'data/clean/clcity.csv'
section = 'mis'

def get_cl_cities():
    cities = pd.read_csv(city_file)
    return cities[cities['clcity'].notnull()]['clcity'].tolist()

cl_cities = get_cl_cities()
for city in cl_cities:
    print "Collecting {0} from {1}.craigslist".format(section, city)
    output_city_personals(output_file, city, section)