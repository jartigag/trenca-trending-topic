#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# just a script to collect twitter's TTs

__author__ = "@jartigag"
__version__ = '0.1'

#TO-DO LIST (09/07/2018)
#TODO: add options to store data: [-d] in sqlite database, [-f dbFile.json] in json file

import tweepy
import argparse
import json
from datetime import datetime
from time import time,sleep

from secrets import secrets
s = 0 # counter of the actual secret: secrets[i]

woeid = json.load(open('woeids.json'))
results = []

def main(verbose,outFile):
	global secrets,s,results
	five_mins = 300 # secs between reqs
	try:

		init_time = time()
		auth = tweepy.OAuthHandler(secrets[s]['consumer_key'], secrets[s]['consumer_secret'])
		auth.set_access_token(secrets[s]['access_token'], secrets[s]['access_token_secret'])
		api = tweepy.API(auth, compression=True)
		tt = api.trends_place(woeid['spain'])
		dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		print('[*]',dt)
		results.append([dt,tt[0]])
		for t in tt[0]['trends']:
			print('	','%02d'%(tt[0]['trends'].index(t)+1),'-',t['name'],
				'(%s tweets)'%(t['tweet_volume']) if t['tweet_volume'] is not None else '')
		write_data(outFile)
		sleep(five_mins)

	except tweepy.error.RateLimitError as e:
		current_time = time()
		running_time = int(current_time - init_time)
		print("[\033[91m#\033[0m] api limit reached! \033[1m%i\033[0m users analysed (running time: %i secs, pauses: %i secs, secrets%i)." % (n,running_time,t,s))
		# rotate secrets[s]
		if s < len(secrets)-1:
			s+=1
		else:
			s=0
	except tweepy.error.TweepError as e:
		print("[\033[91m!\033[0m] twitter error: %s" % e)
#	except Exception as e:
#		print("[\033[91m!\033[0m] error: %s" % e)

def write_data(outFile):
	# print results as a json (an array of jsons, actually) to dbFile
	with open(outFile,'a') as f:
		if not f.read(1): # if file is empty:
			#FIXME: io.UnsupportedOperation: not readable
			print("[",end="",file=f)
		else:
			print(",[",end="",file=f)
		for r in results:
			if not results.index(r)==len(results)-1:
				print(json.dumps(r.__dict__, indent=2, sort_keys=True),end=",\n",file=f)
			else:
				print(json.dumps(r.__dict__, indent=2, sort_keys=True),end="",file=f)
		print("]",file=f)

if __name__ == '__main__':

	parser = argparse.ArgumentParser(
		description="just a script to collect twitter's TTs, v%s by @jartigag" % __version__,
		usage="%(prog)s [-v]")
	parser.add_argument('-f','--file',help='-f dbFile.json')
	parser.add_argument('-v','--verbose',action='store_true')
	args = parser.parse_args()

	main(args.verbose,args.file)
