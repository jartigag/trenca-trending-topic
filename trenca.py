#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# just a script to collect twitter's TTs
#
# usage: python3 trenca.py -cvf dbFile.json

__author__ = "@jartigag"
__version__ = '0.1'

#TO-DO LIST (11/07/2018)
#TODO: add options to store data: [-d] in sqlite database, [-f dbFile.json] in json file

import tweepy
import argparse
import json
from datetime import datetime
from time import time,sleep

from secrets import secrets
s = 0 # counter of the actual secret: secrets[i]

woeids = json.load(open('woeids.json'))
results = {}
n=0 # number of api reqs

def main(verbose,outFile):
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
		if outFile:	
			write_data(outFile)

	except tweepy.error.RateLimitError as e:
		current_time = time()
		running_time = int(current_time - init_time)
		print("[\033[91m#\033[0m] api limit reached! \033[1m%i\033[0m api reqs were made (running time: %i secs, pauses: %i secs, secrets%i)." % (n,running_time,t,s))
		# rotate secrets[s]
		if s < len(secrets)-1:
			s+=1
		else:
			s=0
	except tweepy.error.TweepError as e:
		print("[\033[91m!\033[0m] twitter error: %s" % e)
	except Exception as e:
		print("[\033[91m!\033[0m] error: %s" % e)

def write_data(outFile):
	# print results as a json (an array of jsons, actually) to dbFile
	with open(outFile,'w') as f:
		print(json.dumps(results,indent=2,sort_keys=True),file=f)

if __name__ == '__main__':

	parser = argparse.ArgumentParser(
		description="just a script to collect twitter's TTs, v%s by @jartigag" % __version__,
		usage="%(prog)s [-v]")
	parser.add_argument('-c','--continuum',action='store_true',help='run continuously')
	parser.add_argument('-f','--file',help='store data in json file. e.g.: -f dbFile.json')
	parser.add_argument('-v','--verbose',action='store_true')
	args = parser.parse_args()

	if args.continuum:
		while True:
			main(args.verbose,args.file)
			five_mins = 300 # secs between reqs
			sleep(five_mins)
	else:
		main(args.verbose,args.file)

'''
extract info in console (example):
data = json.load(open('dbFile.json'))
for d in data:
	print('== %s =='%(d))
	for i in range(0,len(data[d])):
		print('*',data[d][i]['locations'][0]['name'])
		for j in range(0,3):
			print(' ',j+1,data[d][i]['trends'][j]['name'])
'''
