#! /usr/bin/python

import sys, getopt
import os
import re
import datetime

from models import *

startTime = datetime.datetime.now()

conf = {}

def main(argv):
	try:
		opts, args = getopt.getopt(argv,"hd:l:m:t:",['detected-events=', 'lines=', 'method-name=', 'type='])
	except getopt.GetoptError:
		print "classifier.py -d '/PATH/TO/detected_events2.rnd' -l '/PATH/TO/PREDICT.lines' -m 'METHOD NAME' -t 'TYPE'"
		sys.exit(2)

	for opt, arg in opts:
		if opt == '-h':
			print "classifier.py -d '/PATH/TO/detected_events2.rnd' -l '/PATH/TO/PREDICT.lines' -m 'METHOD NAME' -t 'TYPE'"
			sys.exit()
		elif opt in ('-d', '--detected-events'):
			conf['detected-events'] = arg.replace('\\', '')
		elif opt in ('-l', '--lines'):
			conf['lines'] = arg.replace('\\', '')
		elif opt in ('-m', '--method-name'):
			conf['method-name'] = arg
		elif opt in ('-t', '--type'):
			conf['type'] = True

	# Check arguments
	try:
		conf['detected-events']
	except KeyError:
  		print 'Path to detected_events.rnd file not given.'
		sys.exit(2)

	try:
		conf['lines']
	except KeyError:
  		print 'Path to predicted.lines file not given.'
		sys.exit(2)

	try:
		conf['method-name']
	except KeyError:
  		print 'Method name not given.'
		sys.exit(2)

	try:
		conf['type']
	except KeyError:
  		print 'Classification type name not given.'
		sys.exit(2)

	if not os.path.exists(conf['detected-events']):
		print 'The file', conf['detected-events'], 'could not be found.'
		sys.exit(2)

	if not os.path.exists(conf['lines']):
		print 'The file', conf['lines'], 'could not be found.'
		sys.exit(2)


if __name__ == "__main__":
	main(sys.argv[1:])

print(datetime.datetime.now()-startTime)
print 'Jobs done!'