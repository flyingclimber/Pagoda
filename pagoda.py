#!/usr/local/bin/python
'''
pagoda - Given a CSV of rfgeneration games pull IGN review scores
'''

import csv
import requests
import time
import json
import ConfigParser
import database as db
import mapping
import re
import argparse

PARSER = argparse.ArgumentParser(description='Rank my games')
PARSER.add_argument('filename', metavar='filename', type=str,
                    help="csv to read")

ARGS = PARSER.parse_args()

CONFIGFILE = '.config'
CSV = ARGS.filename
MAX_RESULT = 3
API_URL = 'https://videogamesrating.p.mashape.com/get.php'

CONFIG = ConfigParser.ConfigParser()
CONFIG.readfp(open(CONFIGFILE))
MASHAPE_KEY = CONFIG.get('USER', 'KEY')

def send_request(name):
    '''
    send_request - Retrieve game rating
    '''

    try:
        response = requests.get(
            url=API_URL,
            params={
                "count": MAX_RESULT,
                "game": name,
            },
            headers={
                "X-Mashape-Key": MASHAPE_KEY,
                "Accept": "application/json",
            },
        )
        '''print('Response HTTP Status Code: {status_code}'.format(
            status_code = response.status_code))
        print('Response HTTP Response Body: {content}'.format(
            content = response.content))'''
        return response.content
    except requests.exceptions.RequestException:
        print('HTTP Request failed')

def cleanup_title(str):
    '''
    cleanup_title - Given a string remove all text inside brackets
    '''

    if str.find('[') == -1 and str.find(']') == -1:
        res = str
    else:
        res = re.sub(r'\[.*?\]', '', str)

    return res

if __name__ == "__main__":
    db.init_db()

    with open(CSV) as csvfile:
        READER = csv.DictReader(csvfile)
        for row in READER:
            title = row['Title']
            console = row['Console']

            game_title = cleanup_title(title)

            if not db.get_score(game_title):
                resp = json.loads(send_request(game_title))

                found = False
                score = None

                if resp:
                    for res in resp:
                        for key, platform in res['platforms'].iteritems():
                            if mapping.IGN[platform] == console:
                                score = res['score']
                                found = True
                                break
                        if found == True:
                            break

                    if score:
                        print game_title, '{', score, '}',  '[', console, ']'
                        db.update_score(game_title, console, score)
                    else:
                        print "No score found for: ", game_title
                else:
                    print "Couldn't find: ", game_title
                time.sleep(1)
            else:
                print "Skipping ", game_title
