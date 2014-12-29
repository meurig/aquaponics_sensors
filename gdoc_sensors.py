#!/usr/bin/python

# Depends on the 'gspread' and 'oauth2client' packages being installed.  If you have pip installed
# execute:
#   sudo pip install gspread
#   sudo pip install oauth2client
# also depends on python-openssl for using the KEY_FILE
#   sudo apt-get install python-openssl

import datetime
import gspread
import os
import serial
import sys
import time

from oauth2client.client import SignedJwtAssertionCredentials
from threading import Thread

# Google Docs account email, password, and spreadsheet name.
GDOCS_SPREADSHEET_NAME = 'aquaponics_sensors'
CLIENT                 = '826241732043-bds91l28552blbtvj7vvq8dtjt81spru@developer.gserviceaccount.com'
KEY_FILE               = '/home/pi/.keys/gdoc sensors-5fd818da81fd.p12'
SCOPE                  = ['https://spreadsheets.google.com/feeds', 'https://docs.google.com/feeds']

# How long to wait (in seconds) between measurements.
FREQUENCY_SECONDS      = 30

ser = serial.Serial('/dev/ttyACM0', 9600)

def get_key():
	f = file(os.path.join(os.path.dirname(__file__), KEY_FILE), "r")
	key = f.read()
	f.close()
	return key

def receiving(ser):
	global last_received

	buffer = ''
	while True:
		buffer = buffer + ser.read(ser.inWaiting())
		if '\n' in buffer:
			lines = buffer.split('\n') # Guaranteed to have at least 2 entries
			last_received = lines[-2]
			#If the Arduino sends lots of empty lines, you'll lose the
			#last filled line, so you could make the above statement conditional
			#like so: if lines[-2]: last_received = lines[-2]
			buffer = lines[-1]

t = Thread(target=receiving, args=(ser,))
# This should cause the daemon thread to quit when the master is quit
t.daemon = True
t.start()

def get_sensor_values(ser):
	last_value = last_received
	for char in "[]":
		last_value = last_value.replace(char, "")
	return last_value.split(",")

def login_open_sheet(client, key, spreadsheet):
	"""Connect to Google Docs spreadsheet and return the first worksheet."""
	credentials = SignedJwtAssertionCredentials(client, key, SCOPE)
	gc = gspread.authorize(credentials)
	worksheet = gc.open(spreadsheet).sheet1
	return worksheet

print 'Logging sensor measurements to {0} every {1} seconds.'.format(GDOCS_SPREADSHEET_NAME, FREQUENCY_SECONDS)
print 'Press Ctrl-C to quit.'
worksheet = None
while True:
	# Login if necessary.
	if worksheet is None:
		worksheet = login_open_sheet(CLIENT, get_key(), GDOCS_SPREADSHEET_NAME)

	# Attempt to get sensor reading.
	#humidity, temp = Adafruit_DHT.read(DHT_TYPE, DHT_PIN)
	#temp1, temp2, temp3, humidity = get_sensor_data(/dev/

	# Skip to the next reading if a valid measurement couldn't be taken.
	#if humidity is None or temp is None:
		#time.sleep(2)
		#continue

	# Attempt to get sensor reading.
	temp1, temp2, temp3, humidity = get_sensor_values(ser)

	# Skip to the next reading if a valid measurement couldn't be taken.
	if temp1 is None or temp2 is None or temp3 is None or humidity is None:
		time.sleep(2)
		continue

	try:
		print 'Temp1: {0:0.1f} C'.format(float(temp1))
		print 'Temp2: {0:0.1f} C'.format(float(temp2))
		print 'Temp3: {0:0.1f} C'.format(float(temp3))
		print 'Humidity:    {0:0.1f} %'.format(float(humidity))
	except:
		# Error converting string to float, probably bad data
		print 'Parsing error, will rety'
		time.sleep(2)
		continue
 
	# Append the data in the spreadsheet, including a timestamp
	try:
		worksheet.append_row((datetime.datetime.now(), temp1, temp2, temp3, humidity))
	except:
		# Error appending data, most likely because credentials are stale.
		# Null out the worksheet so a login is performed at the top of the loop.
		print 'Append error, logging in again'
		worksheet = None
		time.sleep(FREQUENCY_SECONDS)
		continue

	# Wait 30 seconds before continuing
	print 'Wrote a row to {0}'.format(GDOCS_SPREADSHEET_NAME)
	time.sleep(FREQUENCY_SECONDS)
