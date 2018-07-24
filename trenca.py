#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# just a script to collect twitter's TTs
#
# usage: python3 trenca.py -cvf dbFile.json

__author__ = "@jartigag"
__version__ = '0.1'

#TO-DO LIST (24/07/2018)
#WIP: add options to store data: [-d] in sqlite database

import tweepy
import argparse
import json
import sqlite3
from collections import OrderedDict
from datetime import datetime
from time import time,sleep

from secrets import secrets
s = 0 # counter of the actual secret: secrets[i]

woeids = json.load(open('woeids.json'))
results = {}
n=0 # number of api reqs

def main(verbose,outFileJSON,outFileDB):
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
				for t in tt[0]['trends']:
					print('	','%02d'%(tt[0]['trends'].index(t)+1),'-',t['name'],
						'(%s tweets)'%(t['tweet_volume']) if t['tweet_volume'] is not None else '')
		if outFileJSON:	
			write_json(outFileJSON)
		elif outFileDB:
			write_sqlite(outFileDB)

	except tweepy.error.RateLimitError as e:
		current_time = time()
		running_time = int(current_time - init_time)
		print("[\033[91m#\033[0m] api limit reached! \033[1m%i\033[0m api reqs were made (running time: %i secs,secrets%i)." % (n,running_time,s))
		# rotate secrets[s]
		if s < len(secrets)-1:
			s+=1
		else:
			s=0
	except tweepy.error.TweepError as e:
		print("[\033[91m!\033[0m] twitter error: %s" % e)
	#except Exception as e:
	#	print("[\033[91m!\033[0m] error: %s" % e)

def write_json(outFile):
	"""
	write results as a json (an array of jsons, actually) to dbFile

	:param outFile: .json output file 
	"""
	with open(outFile,'w') as f:
		print(json.dumps(results,indent=2,sort_keys=True),file=f)

def write_sqlite(outFile):
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

	'''
	conn.execute("UPDATE COMPANY set SALARY = 25000.00 where ID = 1")
	conn.commit
	print "Total number of rows updated :", conn.total_changes

	cursor = conn.execute("SELECT id, name, address, salary from COMPANY")
	for row in cursor:
	   print "ID = ", row[0]
	   print "NAME = ", row[1]
	   print "ADDRESS = ", row[2]
	   print "SALARY = ", row[3], "\n"

	print "Operation done successfully";
	'''

	conn.close()

if __name__ == '__main__':

	parser = argparse.ArgumentParser(
		description="just a script to collect twitter's TTs, v%s by @jartigag" % __version__,
		usage="%(prog)s [-cdfv]")
	parser.add_argument('-c','--continuum',action='store_true',help='run continuously')
	parser.add_argument('-d','--database',help='store data in sqlite database file. e.g.: -d sqliteFile.db')
	parser.add_argument('-f','--file',help='store data in json file. e.g.: -f dbFile.json')
	parser.add_argument('-v','--verbose',action='store_true')
	args = parser.parse_args()

	if args.continuum:
		while True:
			main(args.verbose,args.file,args.database)
			fifteen_mins = 60*15 # secs between reqs
			sleep(fifteen_mins)
	else:
		main(args.verbose,args.file,args.database)

'''
# extract info in console (example):
data = json.load(open('dbFile.json'))
for d in data:
	print('== %s =='%(d))
	for i in range(0,len(data[d])):
		print('*',data[d][i]['locations'][0]['name'])
		for j in range(0,3):
			print(' ',j+1,data[d][i]['trends'][j]['name'])
'''
'''
# let's see if TTs change significantly each 5 mins:
tts = json.load(open("dbFile.json"),object_pairs_hook=OrderedDict)
index_tts = list(tts)
for t in index_tts[0:5]:
	print('[*]',t)
	for i in range(0,len(tts[t])):
			print(tts[t][i]['locations'][0]['name'],'-',tts[t][i]['trends'][0]['name'])
	print()

# they're nearly the same -> probably it would be better if the script retrieved less data
'''
