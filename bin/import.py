#! /usr/bin/python

import sys, getopt
import os
import re
import datetime

from models import *

startTime = datetime.datetime.now()

conf = {'test': False}

def import_folder():
	os.system('clear')
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
	
	# Start looping over recordings
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

		# Import events for this recording
		event_count = 0
		with open(conf['datadir'] + ddir['name'] + '/' + recording_data['id'] + '.events2', 'r') as f:
			events = f.read()

			#Split into events
			events = events.strip()[0:-1].split('}')

			for e in events:
				event_data = {'recording': recording}
				# Split into lines
				e = e.strip()[2:].split('\n')
				for line in e:
					# Split into tokens
					line = line.split('=')
					if len(line) == 2:
						line[0] = line[0].strip()
						line[1] = line[1].strip()
						if line[0] == 'offset_samp':
							event_data['offset'] = float(line[1])
						elif line[0] == 'dur_ms':
							event_data['duration_ms'] = float(line[1])
						elif line[0] == 'dur_samp':
							event_data['duration_sample'] = int(float(line[1]))
						elif line[0] == 'energy_ms':
							event_data['energy_ms'] = float(line[1])
						elif line[0] == 'f_min':
							event_data['f_min'] = float(line[1])
						elif line[0] == 'f_max':
							event_data['f_max'] = float(line[1])
						elif line[0] == 'bw':
							event_data['bw'] = float(line[1])
						elif line[0] == 'E_f':
							event_data['E_f'] = float(line[1])
						elif line[0] == 'std_f':
							event_data['std_f'] = float(line[1])
				
				try:
					event = Event.select().where(	Event.recording == event_data['recording'], 
													Event.offset == event_data['offset'], 
													Event.duration_ms == event_data['duration_ms'],
													Event.duration_sample == event_data['duration_sample']).get()
					print 'Existing event found.'
				except DoesNotExist:
					event = Event.create(	recording = event_data['recording'],
											offset = event_data['offset'],
											duration_ms = event_data['duration_ms'],
											duration_sample = event_data['duration_sample'],
											energy_ms = event_data['energy_ms'],
											f_min = event_data['f_min'],
											f_max = event_data['f_max'],
											bw = event_data['bw'],
											E_f = event_data['E_f'],
											std_f = event_data['std_f'])
					# print 'Created event.'
					event_count = event_count + 1

		print 'Created', event_count, 'events for this recording.'


	

 


def main(argv):
	try:
		opts, args = getopt.getopt(argv,"htd:s:p:",['test', 'datadir=', 'site=', 'place='])
	except getopt.GetoptError:
		print "import.py -d '/PATH/TO/DATA' -s 'SITE NAME' -p 'PLACE NAME'"
		sys.exit(2)

	for opt, arg in opts:
		if opt == '-h':
			print "import.py -d '/PATH/TO/DATA' -s 'SITE NAME' -p 'PLACE NAME'"
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

print(datetime.datetime.now()-startTime)
print 'Jobs done!'