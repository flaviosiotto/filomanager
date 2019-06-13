#!/usr/bin/env python
# -*- coding: utf-8 -*-

#import urllib, urllib2
try:
	import json
except ImportError:
	import simplejson as json


def translate(text,src='', to='en'):
	api = "https://www.googleapis.com/language/translate/v2?"
	api_key = "AIzaSyBtlR1Zi3iDvCt2J25xQTRvNqf4BysHQmI"
	parameters = urllib.urlencode({
		'target': to,
		'key': api_key,
		'q': text
	})

	# response = urllib2.urlopen(api + parameters)
	# translations = json.loads(response.read())

	# translated_text = translations['data']['translations'][0]['translatedText']
	# return translated_text.encode('utf-8')
