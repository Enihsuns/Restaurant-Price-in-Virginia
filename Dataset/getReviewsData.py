# -*- coding: utf-8 -*-
"""
Created on Mon Nov 12 12:56:14 2018

@author: Xinyu Yang
"""
from __future__ import print_function

import argparse
import json
import requests
import sys
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
API_KEY= 'MhQZea0DKJRZjjL071jkYbZHRoF0wpVOXIDwhc2r4hdJycV1ZSd8yyR_gJxw8kXc1JSYenjmCSllL7ZU33-IIk5XeaiXRjnOCKY2XfiRBcYYHYOlZm32houBixq9W3Yx' 
#API_KEY = 'ALq0ppu2noIbUe-sAMW3nyJOKCIhiNjrEQPT64kpDQFeiT4vWSLJnPUKmXO0QSvhMGi9pkIMh-GVRBJCitO6PeUY4yuRdQVUnN8GnDFJXhMDLDsnvE1JqTFg-lfqW3Yx'


# API constants, you shouldn't have to change these.
API_HOST = 'https://api.yelp.com/v3'
REVIEW_PATH = '/businesses/{id}/reviews'


# Defaults for our simple example.
SEARCH_LIMIT = 50
DEFAULT_SET_FILE = './visited_biz_ids'
DEFAULT_BIZ_FILE = './biz_ids'
DEFAULT_DATA_FILE = 'reviews_VA.json'

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

def query_api(file, biz):
    """Queries the API by the input values from the user.

    Args:
        file (str): The file to save data.
        biz (str): The id of the business to be queried.
    """
    search_path = REVIEW_PATH.replace("{id}", biz)
    
    response = request(API_HOST, search_path, API_KEY)
    
    if response.get("error"):
        error = response.get("error")
        if(error.get("code") == "BUSINESS_UNAVAILABLE"): # A business with no review
            return
        raise Exception("Out of API limit!")
        return
    
    reviews = response
    
    reviews["id"] = biz
    with open(file, 'a', encoding='utf8') as outfile:
        json.dump(reviews, outfile, indent = 2, ensure_ascii = False)
        outfile.write(',\n')

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument('-f', '--reviewfile', dest='revfile', default=DEFAULT_DATA_FILE,
                        type=str, 
                        help='The file to save reviews data (default: %(default)s)')
    parser.add_argument('-bf', '--bizfile', dest='bizfile', default=DEFAULT_BIZ_FILE,
                        type=str,
                        help='The file contains bizs id (default: %(default)s)')
    parser.add_argument('-sf', '--setfile', dest='setfile', default=DEFAULT_SET_FILE,
                        type=str,
                        help='The file used to save useful variables (default: %(default)s)')

    input_values = parser.parse_args()
    
    try:
        # Obtain business id
        with open(input_values.bizfile, 'rb') as infile:
            biz_set, _, _ = pickle.load(infile) # Only biz_set is useful
        
        # Obtain visited business id
        if(os.path.exists(input_values.setfile)):
            with open(input_values.setfile, 'rb') as infile:
                visited_biz_set = pickle.load(infile)
        else:
            visited_biz_set = set()
        
        # Iterate business in set
        cnt = 0
        for biz in biz_set:
            # Counter
            if(cnt % 100 == 0):
                print("Querying {0} business...".format(cnt))
            cnt += 1
            
            if(biz in visited_biz_set): # Check whether already visited
                continue;
            query_api(input_values.revfile, biz)
            visited_biz_set.add(biz)
    
    except Exception as error:
        sys.exit(
            'Out of API limit!'
        )
    
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
            pickle.dump(visited_biz_set, outfile)

if __name__ == '__main__':
    main()
