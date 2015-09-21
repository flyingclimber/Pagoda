#!/usr/local/bin/python
'''
pagoda - Given a CSV of rfgeneration games pull IGN review scores
'''

import csv
import requests
import time
import json
import ConfigParser

CONFIGFILE = '.config'
CSV = 'Collection-9-21-2015.csv'
MAX_RESULT = 5
API_URL = 'https://videogamesrating.p.mashape.com/get.php'

CONFIG = ConfigParser.ConfigParser()
CONFIG.readfp(open(CONFIGFILE))
MASHAPE_KEY = CONFIG.get('USER', 'KEY')

def send_request(name):
    '''
    send_reques - Retrieve game rating
    # GET https://videogamesrating.p.mashape.com/get.php
    '''

    try:
        response = requests.get(
            url=API_URL,
            params={
                "count": MAX_RESULT,
                "game": name,
            },
            headers={
                "X-Mashape-Key":MASHAPE_KEY,
                "Accept": "application/json",
            },
        )
        '''print('Response HTTP Status Code: {status_code}'.format(
            status_code = response.status_code))'''
        print('Response HTTP Response Body: {content}'.format(
            content = response.content))
        return response.content
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

with open(CSV) as csvfile:
    READER = csv.DictReader(csvfile)
    for row in READER:
        game_title = row['Title'].replace('[Game of the Year Edition]', '')
        resp = json.loads(send_request(game_title))
        print game_title, '{', resp[0]['score'], '}',  '[', row['Console'], ']'
        time.sleep(1)
