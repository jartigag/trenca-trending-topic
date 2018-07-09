#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# just a script to collect twitter's TTs

__author__ = "@jartigag"
__version__ = '0.1'

#TO-DO LIST (09/07/2018)
#TODO: everything

import tweepy
import argparse

from secrets import secrets
s = 0 # counter of the actual secret: secrets[i]

def main(verbose):
	global secrets,s
	auth = tweepy.OAuthHandler(secrets[s]['consumer_key'], secrets[s]['consumer_secret'])
	auth.set_access_token(secrets[s]['access_token'], secrets[s]['access_token_secret'])
	api = tweepy.API(auth, compression=True)
	tt = api.trends_place(23424950)
	for t in tt[0]['trends']:
		print(tt[0]['trends'].index(t)+1,'-',t['name'])

if __name__ == '__main__':

	parser = argparse.ArgumentParser(
		description="just a script to collect twitter's TTs, v%s by @jartigag" % __version__,
		usage="%(prog)s [-v]")
	#parser.add_argument('arg',help='e.g.: first arg')
	parser.add_argument('-v','--verbose',action='store_true')
	args = parser.parse_args()

	try:
	    main(args.verbose)
	except tweepy.error.TweepError as e:
	    print("[\033[91m!\033[0m] twitter error: %s" % e)
	except Exception as e:
	    print("[\033[91m!\033[0m] error: %s" % e)
