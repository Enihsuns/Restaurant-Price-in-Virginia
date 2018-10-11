# -*- coding: utf-8 -*-
"""
Yelp Fusion API code sample.

This program demonstrates the capability of the Yelp Fusion API
by using the Search API to query for businesses by a search term and location,
and the Business API to query additional information about the top result
from the search query.

Please refer to http://www.yelp.com/developers/v3/documentation for the API
documentation.

This program requires the Python requests library, which you can install via:
`pip install -r requirements.txt`.

Sample usage of the program:
`python sample.py --term="bars" --location="San Francisco, CA"`
"""
from __future__ import print_function

import argparse
import json
import pprint
import requests
import sys
import urllib
import pickle
import os
import pylab as pl
import math


# This client code can run on Python 2.x or 3.x.  Your imports can be
# simpler if you only need one of those.
try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.parse import quote
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2 and urllib
    from urllib2 import HTTPError
    from urllib import quote
    from urllib import urlencode


# Yelp Fusion no longer uses OAuth as of December 7, 2017.
# You no longer need to provide Client ID to fetch Data
# It now uses private keys to authenticate requests (API Key)
# You can find it on
# https://www.yelp.com/developers/v3/manage_app
#API_KEY= 'MhQZea0DKJRZjjL071jkYbZHRoF0wpVOXIDwhc2r4hdJycV1ZSd8yyR_gJxw8kXc1JSYenjmCSllL7ZU33-IIk5XeaiXRjnOCKY2XfiRBcYYHYOlZm32houBixq9W3Yx' 
API_KEY = 'OvhnpRdwfScZM4QtkSK8EwwYOLr4qYoP08wEpyUbHQENlYNliOu4UJcXBdAD_3oeBlZgHbDm4gEaB5_a0hv0dSFI0TMeKriHmEPrieOig8WG8nrhsyhsrcoJe4-_W3Yx'

# API constants, you shouldn't have to change these.
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.


# Defaults for our simple example.
DEFAULT_TERM = 'restaurant'
#DEFAULT_LOCATION = ''
DEFAULT_DATA_FILE = 'restaurants_VA.json'
DEFAULT_SET_FILE = 'biz_ids'
MAX_LAT = 39.47
MAX_LONG = -75.24
SEARCH_LIMIT = 50


def request(host, path, api_key, url_params=None):
    """Given your API_KEY, send a GET request to the API.

    Args:
        host (str): The domain host of the API.
        path (str): The path of the API after the domain.
        API_KEY (str): Your API Key.
        url_params (dict): An optional set of query parameters in the request.

    Returns:
        dict: The JSON response from the request.

    Raises:
        HTTPError: An error occurs from the HTTP request.
    """
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % api_key,
    }

    # print(u'Querying {0} ...'.format(url))

    response = requests.request('GET', url, headers=headers, params=url_params)

    return response.json()


def search(api_key, term, lat, long):
    """Query the Search API by a search term and location.

    Args:
        term (str): The search term passed to the API.
        lat (int): The latitude.
        long (int): The longitude.

    Returns:
        dict: The JSON response from the request.
    """

    url_params = {
        'term': term.replace(' ', '+'),
        #'location': location.replace(' ', '+'),
        'limit': SEARCH_LIMIT,
        'latitude': lat,
        'longitude': long
    }
    return request(API_HOST, SEARCH_PATH, api_key, url_params=url_params)


def get_business(api_key, business_id):
    """Query the Business API by a business ID.

    Args:
        business_id (str): The ID of the business to query.

    Returns:
        dict: The JSON response from the request.
    """
    business_path = BUSINESS_PATH + business_id

    return request(API_HOST, business_path, api_key)


def query_api(file, term, offset, biz_set, lat, long):
    """Queries the API by the input values from the user.

    Args:
        file: The file to save data.
        term (str): The search term to query.
        offset (int): Offset the list of returned business results by this amount.
        biz_set (set): The set of saved businesses'id.
        lat: The latitude of location.
        long: The longitude of location.
    
    Returns:
        total: The total number of businesses.
    """
    response = search(API_KEY, term,  lat, long)

    total = response.get('total')
    businesses = response.get('businesses')

    if not businesses:
        print(u'No businesses for {0} found.'.format(term))
        return 0

    for biz in businesses:
        if(biz['id'] in biz_set):  # A repetition
            #print("repetition")
            continue
        if(biz.get('location') == None or biz['location']['state'] != 'VA'): # Not in VA
            continue
        biz_set.add(biz['id'])
        #response = get_business(API_KEY, biz_id)
        #if(response['location']['state'] != 'VA'):  # Not in VA
        #     print("Not in VA: in {0}".format(response['location']['state']))
        #    continue
        with open(file, 'a', encoding='utf8') as outfile:
            json.dump(biz, outfile, indent = 2, ensure_ascii = False)
            outfile.write('\n')
    
    return total

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-q', '--term', dest='term', default=DEFAULT_TERM,
                        type=str, help='Search term (default: %(default)s)')
    #parser.add_argument('-l', '--location', dest='location',
    #                    default=DEFAULT_LOCATION, type=str,
    #                    help='Search location (default: %(default)s)')
    parser.add_argument('-df', '--datafile', dest='datafile', default=DEFAULT_DATA_FILE,
                        type=str, 
                        help='The file to save restaurant data (default: %(default)s)')
    parser.add_argument('-sf', '--setfile', dest='setfile', default=DEFAULT_SET_FILE,
                        type=str,
                        help='The file to save set of useful variables (default: %(default)s)')

    input_values = parser.parse_args()
    
    # Load or Initialize biz_set, latitude, longitude variable
    if(os.path.exists(input_values.setfile)):
        with open(input_values.setfile, 'rb') as infile:
            biz_set, st_lat, st_long = pickle.load(infile)
    else:
        biz_set = set() # Save all the businesses' id to ensure no repetition
        st_lat = 36.57  # The start (min) of latitude
        st_long = -83.67 # The start (min) of longitude
    
    try:
        for lat in pl.frange(st_lat, MAX_LAT, 0.14):
            for long in pl.frange(st_long, MAX_LONG, 0.10):
                total = min(1000, query_api(input_values.datafile, 
                                            input_values.term, 
                                            0,
                                            biz_set, 
                                            lat, 
                                            long))
                for offset in range(SEARCH_LIMIT, total, SEARCH_LIMIT):
                    query_api(input_values.datafile, 
                              input_values.term, 
                              offset,
                              biz_set,
                              lat,
                              long)
                if(math.isclose(lat, st_lat, abs_tol=0.05)):
                    st_long = -83.67
                print("lat: {0}, long: {1}".format(lat, long));
                print("Current number of restaurants in VA: {0}".format(len(biz_set)))
            
    except HTTPError as error:
        sys.exit(
            'Encountered HTTP error {0} on {1}:\n {2}\nAbort program.'.format(
                error.code,
                error.url,
                error.read(),
            )
        )
            
    finally:
        with open(input_values.setfile, 'wb') as outfile:
            pickle.dump([biz_set, lat, long], outfile)


if __name__ == '__main__':
    main()
