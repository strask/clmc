import os.path
import time
import re
from urllib2 import urlopen
from bs4 import BeautifulSoup
import pandas as pd

from cl_personal import CLPersonal

file = 'data/clean/cl_missed_connections.tsv'
output_file = open(file, 'a')
city = 'newyork'

def get_max_posted(city):
    max_posted = 0
    cl = pd.read_csv(file, sep='\t')    
    max_posted = cl[cl['city'] == city]['posted'].max()
    return max_posted

# If creating file, print header row
if os.stat(file).st_size == 0:
    header = 'url\tcity\tid\tposted\tupdated\ttitle\ttext\tage\tlatitude\tlongitude\n'
    output_file.write(header)

def get_cl_urls(city, section, index):
    base_url = 'http://{0}.craigslist.org'.format(city)
    search_url = '{0}/{1}/index{2}.html'.format(base_url, section, str(index))

    html = urlopen(search_url).read()
    search_results = BeautifulSoup(html, "lxml")

    postings = search_results.find_all(class_="i")
    links = ['{0}{1}'.format(base_url, a['href']) for a in postings]
    return links

section = 'mis'
cl_urls = []
for i in range(0, 1100, 100):
    l = get_cl_urls(city, section, i)
    cl_urls.extend(l)

#Get max postid (to know when to stop fetching)    
max_posted = get_max_posted(city)

# Get personal and print tsv_string to output file
# for index, u in enumerate(cl_urls):
#      cl_personal = CLPersonal(u)
#      tsv_string = cl_personal.get_tsv_string()
#      output_file.write('{0}\n'.format(tsv_string))
#      print 'Got {}'.format(index + 1)

print 'max_posted:{0}'.format(max_posted)
for index, u in enumerate(cl_urls):
    cl_personal = CLPersonal(u)
    print 'posted:{0}, updated:{1}'.format(cl_personal.posted, cl_personal.updated)
    if max(cl_personal.posted, cl_personal.updated) <= max_posted:
        print 'DONE!'
        print cl_personal.url
        break
    
# account for flagged for removal/expired
#e.g.http://newyork.craigslist.org/mnh/cas/4439423387.html