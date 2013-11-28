#! /usr/bin/python

import sys, getopt
import os
import re
import datetime

from models import *

startTime = datetime.datetime.now()

conf = {}

def classify():
	os.system('clear')
	# Get or create method
	try:
		method = Detection_method.select().where(Detection_method.name == conf['method-name']).get()
		print 'Fetched Detection_method'
	except DoesNotExist:
		method = Detection_method.create(name = conf['method-name'])
		print 'Created Detection_method'

	# Get or create Event_type
	try:
		eventtype = Event_type.select().where(Event_type.name == conf['type']).get()
		print 'Fetched Event_type'
	except DoesNotExist:
		eventtype = Event_type.create(name = conf['type'])
		print 'Created Event_type'

	# Get linenumbers for positive events
	with open(conf['lines'], 'r') as f:
		positive_lines = map(int, f.readlines())

	# Walk the detected events
	linecount = 1
	recordings_not_found = 0
	events_not_found = 0
	classifications_saved = 0
	classifications_already_saved = 0
	with open(conf['detected-events'], 'r') as f:
		for line in f:
			if linecount in positive_lines:
				# print line
				ident = line.split('/')[-1].split('.events2')
				offset = ident[1].split('=')
				ident = ident[0]
				dur_sample = int(offset[-1])
				offset = int(offset[1].split(':')[0])
				# print ident, offset, dur_sample

				# Find recording
				try:
					recording = Recording.select().where( 
						Recording.filename == ident).get()
				except DoesNotExist:
					# print 'Recording not in DB. Skipping event.'
					recordings_not_found = recordings_not_found + 1
					continue

				try:
					event = Event.select().where(	Event.recording == recording, 
													Event.offset == offset, 
													Event.duration_sample == dur_sample).get()
				except DoesNotExist:
					# print 'Event not found in DB. Skipping event.'
					events_not_found = events_not_found + 1
					continue

				try:
					classif = Event_classification.select().where(
						Event_classification.event == event,
						Event_classification.detection_method == method,
						Event_classification.event_type == eventtype).get()
					print 'Classification already saved.'
					classifications_already_saved = classifications_already_saved + 1
				except DoesNotExist:
					classif = Event_classification.create(
						event = event,
						detection_method = method,
						event_type = eventtype
						)
					classifications_saved = classifications_saved + 1
					print 'Classification saved.'

			
			linecount = linecount + 1

		print (linecount - 1), 'lines processed.'
		print recordings_not_found, 'recordings not found.'
		print events_not_found, 'events not found.'
		print classifications_already_saved, 'classifications already in the DB.'
		print classifications_saved, 'new classifications saved.'

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
			conf['type'] = arg

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

	classify()


if __name__ == "__main__":
	main(sys.argv[1:])

print 'Jobs done in', datetime.datetime.now()-startTime