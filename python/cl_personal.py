import calendar
import re
import dateutil.parser
from urllib2 import urlopen
from bs4 import BeautifulSoup

def get_timestamp(str_datetime):
    d = dateutil.parser.parse(str_datetime)
    timestamp = calendar.timegm(d.utctimetuple())
    return int(timestamp)

def parse_url(url):
    url_pattern = r'http://(?P<city>\w*).craigslist.org/\w*/?\w*/(?P<id>\d*).html'
    match = re.match(url_pattern, url)
    return match.group('city', 'id')
   
def none_to_emptystr(var):
    if var is None:
        return ''
    return var
    
class CLPersonal: 
    def __init__(self, url):
        self.url = url 
        html = urlopen(url).read()
        cl_soup = BeautifulSoup(html, "lxml")
        
        # Get city and postid from url
        self.city, self.id = parse_url(url)
        self.id = int(self.id)
        
        # Get posted and updated times in unix timestamp
        timestamps = {}
        postinginfo = cl_soup.find_all(class_='postinginfo')
        for i in postinginfo:
            if i.time:
                timestamps[i.text.split(':')[0]] = get_timestamp(i.time['datetime'])
        self.posted = timestamps['posted']
        if 'updated' in timestamps.keys():
            self.updated = timestamps['updated']
        else:
            self.updated = None
         
        # Get title
        self.title = cl_soup.find(class_='postingtitle').text.strip()
        
        # Get posting text
        self.text = cl_soup.find(id='postingbody').text.strip().replace('\n', ' ')
        
        # Get attributes (physical, status)
        a = [at.text.split(':') for at in cl_soup.find_all(class_='personals_attrbubble')]
        attributes = { kv[0].strip() : kv[1].strip() for kv in a }
        if 'age' in attributes.keys():
            self.age = int(attributes['age'])
        else:
            self.age = None
        
        # Get location data
        if cl_soup.find(id='map'):
            self.latitude = float(cl_soup.find(id='map')['data-latitude'])
            self.longitude = float(cl_soup.find(id='map')['data-longitude'])
        else:
            self.latitude, self.longitude = None, None

    def get_tsv_string(self):
        #Compile string
        tsv_string = '{0}\t{1}\t{2}\t{3}\t{4}\t{5}\t{6}\t{7}\t{8}\t{9}'.format(
            self.url,
            self.city,
            self.id,
            self.posted,
            none_to_emptystr(self.updated),
            self.title,
            self.text.encode('ascii', 'ignore'),
            none_to_emptystr(self.age),
            none_to_emptystr(self.latitude),
            none_to_emptystr(self.longitude)
        )
        return tsv_string
        
if __name__ == "__main__":
    import sys
    cl_personal = CLPersonal(sys.argv[1])
    print cl_personal.get_tsv_string()