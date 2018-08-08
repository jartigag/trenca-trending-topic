#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# just a script to collect twitter's TTs
#
# usage: python3 trenca.py -cvf json dbFile.json

__author__ = "@jartigag"
__version__ = '0.1'

#TO-DO LIST
# - sqlite database

import tweepy
import argparse
import json
import sqlite3
from collections import OrderedDict
from datetime import datetime
from time import time,sleep

from secrets import secrets
s = 0 # counter of the actual secret: secrets[i]

SLEEP_INTERVAL = 5 # secs between reqs
woeids = json.load(open('woeids.json'))
results = {}
n=0 # number of api reqs

def main(verbose,format,file,nTop):
	global secrets,s,results,n
	try:

		init_time = time()
		auth = tweepy.OAuthHandler(secrets[s]['consumer_key'], secrets[s]['consumer_secret'])
		auth.set_access_token(secrets[s]['access_token'], secrets[s]['access_token_secret'])
		dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		api = tweepy.API(auth, compression=True)
		for place in woeids:
			tt = api.trends_place(woeids[place])
			n+=1
			if dt in results: #if this 'place' isn't the first consulted in this 'dt'
				results[dt] += [tt[0]] #append new results list
			else:
				results[dt] = [tt[0]] #create key 'dt' and add new results list
			if verbose:
				print('[*]',dt,place.upper())
				if nTop:
					end = nTop
				else:
					end = len(tt[0]['trends'])-1
				for t in tt[0]['trends'][:end]:
					print('	','%02d'%(tt[0]['trends'].index(t)+1),'-',t['name'],
						'(%s tweets)'%(t['tweet_volume']) if t['tweet_volume'] is not None else '')
		if format=='json':
			write_json(file)
		elif format=='sqlite':
			write_sqlite(file)

	except tweepy.error.RateLimitError as e:
		current_time = time()
		running_time = int(current_time - init_time)
		print("[\033[91m#\033[0m] api limit reached! \033[1m%i\033[0m api reqs were made (running time: %i secs,secrets%i)."
			% (n,running_time,s))
		# rotate secrets[s]
		if s < len(secrets)-1:
			s+=1
		else:
			s=0
	except tweepy.error.TweepError as e:
		print("[\033[91m!\033[0m] twitter error: %s" % e)
	except Exception as e:
		print("[\033[91m!\033[0m] error: %s" % e)

def write_json(outFile):
	"""
	write results as a json (an array of jsons, actually) to dbFile

	:param outFile: .json output file 
	"""
	with open(outFile,'w') as f:
		print("[",file=f)
		for dt in results:
			for loc in results[dt]:
				print("[",file=f)
				print(json.dumps(loc,indent=2,sort_keys=True),file=f)
				print("],",file=f) #TODO: avoid to remove last "," manually
		print("],",file=f) #TODO: avoid to remove last "," manually

def write_sqlite(outFile):
	#TODO:
	"""
	write results as a sqlite database to dbFile

	:param outFile: .db sqlite database file
	"""
	conn = sqlite3.connect(outFile)
	conn.execute('''CREATE TABLE IF NOT EXISTS trending_topics
			 (id			INT PRIMARY KEY,
			 dt				TEXT,
			 woeid			INT,
			 location		TEXT);''')
	for dt in results:
		for loc in results[dt]:
			conn.execute("INSERT INTO trending_topics (dt,woeid,location) \
				VALUES ('"+dt+"',"+str(loc['locations'][0]['woeid'])+",'"+loc['locations'][0]['name']+"');")
			conn.execute("CREATE TABLE IF NOT EXISTS '"+str(loc['locations'][0]['woeid'])+"_"+loc['locations'][0]['name']+"'\
					 (id			INT PRIMARY KEY,\
					 as_of			TEXT,\
					 created_at		TEXT,\
					 locations		TEXT);")
			conn.commit()
	conn.close()

if __name__ == '__main__':

	parser = argparse.ArgumentParser(
		description="just a script to collect twitter's TTs, v%s by @jartigag" % __version__,
		usage="%(prog)s [-cdfv]")
	parser.add_argument('-c','--continuum',action='store_true',
		help='run continuously')
	parser.add_argument('-v','--verbose',action='store_true')
	parser.add_argument('-f','--format',choices=['json','sqlite'],default='json',
		help='format to store data')
	parser.add_argument('-n','--nTopTTs', type=int, metavar='NUMBER',
		help='limit to NUMBER top TTs on every location')
	parser.add_argument('file',help='output file to store data')
	args = parser.parse_args()

	if args.continuum:
		while True:
			main(args.verbose,args.format,args.file,args.nTopTTs)
			sleep(SLEEP_INTERVAL)
	else:
		main(args.verbose,args.format,args.file,args.nTopTTs)
