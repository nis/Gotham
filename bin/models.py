from peewee import *

mysql_db = MySQLDatabase('gotham_db', passwd = 'CakDydtaquelLa', user = 'gotham')

class MySQLModel(Model):
	"""A base model that will use our MySQL database"""
	class Meta:
		database = mysql_db

class Site(MySQLModel):
	name = CharField()
	latitude  = CharField(default = None, null=True)
	longitude  = CharField(default = None, null=True)

class Place(MySQLModel):
	site = ForeignKeyField(Site)
	name = CharField()
	latitude  = CharField(default = None, null=True)
	longitude  = CharField(default = None, null=True)

class Recording(MySQLModel):
	place = ForeignKeyField(Place)
	epoch = IntegerField()
	filename = CharField()
	filesize = IntegerField()
	length = FloatField()
	portion_of_total = FloatField()
	power_rate = FloatField()
	event_power_rate = FloatField()
	background_power_rate = FloatField()
	sample_rate = IntegerField(default = None, null=True)
	bit_depth = IntegerField(default = None, null=True)

class Event(MySQLModel):
	recording = ForeignKeyField(Recording)
	offset = FloatField()
	duration_ms = FloatField()
	duration_sample = IntegerField()
	energy_ms = FloatField()
	f_min = FloatField()
	f_max = FloatField()
	bw = FloatField()
	E_f = FloatField()
	std_f = FloatField()

class Detection_method(MySQLModel):
	name = CharField()
	notes = TextField(default = None, null=True)

class Event_type(MySQLModel):
	name = CharField()
	latin = CharField(default = None, null=True)
	notes = TextField(default = None, null=True)

class Event_classification(MySQLModel):
	event = ForeignKeyField(Event)
	detection_method = ForeignKeyField(Detection_method)
	event_type = ForeignKeyField(Event_type)

class Zoom_level(MySQLModel):
	level = IntegerField()
	name = CharField()
	width_s = FloatField()

class Audio_picture(MySQLModel):
	recording = ForeignKeyField(Recording)
	zoom_level = ForeignKeyField(Zoom_level)
	offset = FloatField()
	filename = CharField()

def create_tables():
	Site.create_table()
	Place.create_table()
	Recording.create_table()
	Event.create_table()
	Detection_method.create_table()
	Event_type.create_table()
	Event_classification.create_table()
	Zoom_level.create_table()
	Audio_picture.create_table()

def drop_tables():
	Audio_picture.drop_table()
	Zoom_level.drop_table()
	Event_classification.drop_table()
	Event_type.drop_table()
	Detection_method.drop_table()
	Event.drop_table()
	Recording.drop_table()
	Place.drop_table()
	Site.drop_table()


mysql_db.connect()