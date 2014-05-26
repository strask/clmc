import time
import re
import os.path
from urllib2 import urlopen
from bs4 import BeautifulSoup
import pandas as pd

from cl_personal import CLPersonal
from cl_personal import PostRemovedError

def get_latest_timestamp(file, city, section):
    timestamp = 0
    file = 'data/clean/cl_missed_connections.tsv'
    cl = pd.read_csv(file, sep='\t')
    
    p = r'http://(?P<c>\w*).craigslist.org/(?P<sub>\w{3})?/?(?P<s>\w*)/(?P<id>\d*).html'
    if not cl.empty:
        cl[['city', 'sub', 'section', 'id']] = cl['url'].str.extract(p)
        timestamp = cl[(cl['city'] == city) & (cl['section'] == section)]['updated'].max()
    return timestamp

def get_cl_urls(city, section, index):
    base_url = 'http://{0}.craigslist.org'.format(city)
    search_url = '{0}/{1}/index{2}.html'.format(base_url, section, str(index))

    html = urlopen(search_url).read()
    search_results = BeautifulSoup(html, "lxml")

    postings = search_results.find_all(class_="i")
    links = ['{0}{1}'.format(base_url, a['href']) for a in postings]
    return links

def output_city_personals(file, city, section):

    # If creating file, print header row
    if not os.path.isfile(file):
        header = 'url\tposted\tupdated\ttitle\ttext\tlatitude\tlongitude\n'
        output_file = open(file, 'w+')
        output_file.write(header)
        output_file.close()
    
    # Get max postid to know when to stop fetching
    latest_timestamp = get_latest_timestamp(file, city, section)
    
    # Compile list of current URLs for city
    cl_urls = []
    for i in range(0, 1100, 100):
        l = get_cl_urls(city, section, i)
        cl_urls.extend(l)

    # Get personal and print tsv_string to output file for all new posts
    with open(file, 'a') as output_file:
        for i, u in enumerate(cl_urls):
            try:
                cl_personal = CLPersonal(u)
                # Stop if reach post older than most recent post previously collected
                if cl_personal.updated <= latest_timestamp:
                    print 'Done with new posts for {0}'.format(city)
                    break    
                tsv_string = cl_personal.get_tsv_string()
                output_file.write('{0}\n'.format(tsv_string))
                print '{0}: Got post ({1})'.format(i, u)
            except PostRemovedError:
                print '{0}: Post removed ({1})'.format(i, u)

if __name__ == "__main__":
    import sys
    file = 'data/clean/cl_missed_connections.tsv'
    output_city_personals(file, city=sys.argv[1], section=sys.argv[2])