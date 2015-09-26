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
PARSER.add_argument('-f', metavar='filename', type=str,
                    help="csv to read")
PARSER.add_argument('-g', metavar='game_title', type=str,
                    help="single game lookup")
PARSER.add_argument('-c', metavar='console', type=str)
PARSER.add_argument('-d', action="store_true", help="debug")

ARGS = PARSER.parse_args()

CONFIGFILE = '.config'
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
        if ARGS.d:
            print('Response HTTP Response Body: {content}'.format(
                content = response.content))
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

def load_csv():
    '''
    load_csv - Load a passed in csv for lookup
    '''

    CSV = ARGS.f
    game_list = {}

    with open(CSV) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            title = row['Title']
            console = row['Console']

            game_title = cleanup_title(title)
            game_list[game_title] = console

    return game_list

def platform_equal(p1, p2):
    '''
    platform_equal - Check mapping table for console variant names
    '''
    for variant in mapping.IGN[p1]:
        if variant == p2:
            return True
    return False

if __name__ == "__main__":

    db.init_db()
    games = {}

    if ARGS.g:
        games[ARGS.g] = ARGS.c
    else:
        games = load_csv()

    for src_game, src_platform in games.iteritems():
        if not db.get_score(src_game):
            resp = json.loads(send_request(src_game))

            found = False
            score = None

            if resp:
                for res in resp:
                    if not res['score']:
                        print "No score ", res['title']
                        continue
                    else:
                        for res_platform in res['platforms'].itervalues():
                            if platform_equal(res_platform, src_platform):
                                score = res['score']
                                found = True
                                break
                    if found == True:
                        break
                if score:
                    print src_game, '{', score, '}',  '[', src_platform, ']'
                    if not ARGS.d:
                        db.update_score(src_game, src_platform, score)
            else:
                print "Couldn't find: ", src_game
            time.sleep(1)
        else:
            print "Skipping ", src_game
