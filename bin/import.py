#! /usr/bin/python

import sys, getopt
import os
import re
import datetime

from models import *

conf = {'test': False}

def import_folder():
	folders = os.listdir(conf['datadir'])
	datedirs = []

	# Find the directories with individual dates data.
	for item in folders:
		if os.path.isdir(conf['datadir'] + item):
			# Match datedirs: YEAR-MO-DA
			m = re.match(r'^([0-9]{4})-([0-1][0-9])-([0-3][0-9])$', item)
			if m != None:
				year = int(m.group(1))
				month = int(m.group(2))
				day = int(m.group(3))
				try:
					newDate = datetime.datetime(year, month, day)
				except ValueError:
					print 'The directory "' + item + '" does not match a valid date.'
					print 'Directories should be named: YEAR-MO-DA'
					sys.exit(2)

				datedirs.append({'name': item, 'year': year, 'month': month, 'day': day})

	print 'Found', len(datedirs), 'folders of data.'
	for ddir in datedirs:
		print 'Importing dir:', ddir['name']
		files = folders = os.listdir(conf['datadir'] + ddir['name'])
		identifiers = []
		for f in files:
			if os.path.isfile(conf['datadir'] + ddir['name'] + '/' + f):
				if f[-4:] == '.s16':
					if f[:-4] not in identifiers:
						identifiers.append(f[:-4])

	print 'Found', len(identifiers), 'recordings.'

	try:
		site = Site.select().where(Site.name == conf['site']).get()
		print 'Fetched site'
	except DoesNotExist:
		site = Site.create(name = conf['site'])
		print 'Created site'

	try:
		place = Place.select().where(Place.name == conf['place']).get()
		print 'Fetched place'
	except DoesNotExist:
		place = Place.create(name = conf['place'], site = site)
		print 'Created place'
	
	# Start recording loop
	# print 'Doing recording:', identifiers[0]

	for recording_id in identifiers:

		recording_data = {'id': recording_id}
	
		# Open data2 file, clean the tokens
		with open(conf['datadir'] + ddir['name'] + '/' + recording_data['id'] + '.data2', 'r') as f:
			for line in f:
				line = line.split(':', 1)
				for i in range(len(line)):
					line[i] = line[i].strip()
				
				if line[0] == 'File size (MiB)':
					recording_data['size'] = float(line[1])
				elif line[0] == 'Recorded at':
					recording_data['datetime'] = str(line[1])
				elif line[0] == 'Seconds since the epoch':
					recording_data['epoch'] = int(line[1])
				elif line[0] == 'Length (s)':
					recording_data['length'] = float(line[1])
				elif line[0] == 'Number of events':
					recording_data['number_events'] = int(float(line[1]))
				elif line[0] == 'Portion of total (%)':
					recording_data['portion'] = float(line[1])
				elif line[0] == 'Power rate (1/ms)':
					recording_data['power_rate'] = float(line[1])
				elif line[0] == 'Event power rate (1/ms)':
					recording_data['event_power_rate'] = float(line[1])
				elif line[0] == 'Background power rate (1/ms)':
					recording_data['background_power_rate'] = float(line[1])
	
	
		try:
			recording = Recording.select().where(Recording.place == place, Recording.epoch == recording_data['epoch'], Recording.filename == recording_data['id']).get()
			print 'Existing recording found:', recording_data['id']
		except DoesNotExist:
			recording = Recording.create(	place = place,
											epoch = recording_data['epoch'],
											filename = recording_data['id'],
											filesize = recording_data['size'],
											length = recording_data['length'],
											portion_of_total = recording_data['portion'],
											power_rate = recording_data['power_rate'],
											event_power_rate = recording_data['event_power_rate'],
											background_power_rate = recording_data['background_power_rate'])
			print 'Created recording:', recording_data['id']




	

 


def main(argv):
	os.system('clear')
	try:
		opts, args = getopt.getopt(argv,"htd:s:p:",['test', 'datadir=', 'site=', 'place='])
	except getopt.GetoptError:
		print 'import.py -i <inputfile> -o <outputfile>'
		sys.exit(2)

	for opt, arg in opts:
		if opt == '-h':
			print 'test.py -i <inputfile> -o <outputfile>'
			sys.exit()
		elif opt in ('-d', '--datadir'):
			conf['datadir'] = arg.replace('\\', '')
			if conf['datadir'][-1] != '/':
				conf['datadir'] = conf['datadir'] + '/'
		elif opt in ('-s', '--site'):
			conf['site'] = arg
		elif opt in ('-p', '--place'):
			conf['place'] = arg
		elif opt in ('-t', '--test'):
			conf['test'] = True

	if conf['test']:
		print 'Setup:'
		for opt in conf:
			print '\t' + str(opt) + ':\t' + str(conf[opt])
		sys.exit()

	# Check arguments
	if not os.path.isdir(conf['datadir']):
		print 'Data directory is not a directory.'
		sys.exit(2)

	if 'site' not in conf:
		print 'Please specify a site.'
		sys.exit(2)

	if 'place' not in conf:
		print 'Please specify a place.'
		sys.exit(2)

	import_folder()



			

	



if __name__ == "__main__":
	main(sys.argv[1:])

print 'Jobs done!'