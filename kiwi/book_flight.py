#!/usr/bin/env python

'''book_flight.py:'''

__author__ 		= 	'frantisekrehor.cz'
__email__		= 	'hi@frantisekrehor.cz'

#=========================================================================

import requests
import json
import sys
import time
from pprint import pprint
from datetime import datetime, timedelta

# APIs used
api_booking_url = 'http://37.139.6.125:8080/booking'
api_check_booking_url = 'https://booking-api.skypicker.com/api/v0.1/check_flights'
api_search_url = 'https://api.skypicker.com/flights'

def parse_argv(argv):
	'''
	Parse command line arguments
	@return - arguments & method for searching i.e. cheapest
	'''
	arguments = {
		'date_depart' : None,
		'date_return' : None, 
		'from' : None,
		'to' : None
		}

	if argv[1] == '--date':
		date_depart = datetime.strptime(argv[2], '%Y-%M-%d')
		arguments['date_depart'] = datetime.strftime(date_depart, '%d/%M/%Y')
	if argv[3] == '--from':
		arguments['from'] = argv[4]
	if argv[5] == '--to':
		arguments['to'] = argv[6]

	if len(argv) > 7:
		
		if argv[7] == '--return':
			date_return = date_depart + timedelta(days=int(argv[8]))
			arguments['date_return'] = datetime.strftime(date_return, '%d/%M/%Y')
		
		method =  argv[7].replace('--', '')
	else:
		method =  'one-way'

	print('Info: Configuration %r and with method %r' % (arguments,method))

	return arguments, method

def get_available_flights(arguments):
	'''
	Search for available flights and their combinations
	@return - list of flights
	'''
	params = {
		'flyFrom': arguments['from'],
		'to': arguments['to'],
		'dateFrom': arguments['date_depart'],
		'dateTo': arguments['date_depart'],
		'returnFrom': arguments['date_return'],
		'returnTo': arguments['date_return']
	}

	try:
		response = requests.get(api_search_url, params=params).json()
		print('Info: flights found: %r' % response['_results'])
		return response['data']
	except:
		raise Exception('Error: something happend when trying to get the flights from the API.')

def get_best_flight(flights, method):
	'''
	Get the best option based on the input and method 
	@return - the best flights
	'''
	def get_cheapest_flight():
		cheapest_flight = None

		for flight in flights:
			if cheapest_flight is None or flight['price'] < cheapest_flight['price']:
				cheapest_flight = flight
		return cheapest_flight

	def get_shortest_flight():
		shortest_flight = None

		for flight in flights:
			if shortest_flight is None or flight['duration']['total'] < shortest_flight['duration']['total']:
				shortest_flight = flight
		return shortest_flight


	if len(flights) == 0:
		raise Exception ('Error: no flights found.')

	if method == 'cheapest':
		print('Info: finding a best flight with a method %r.' % (method))
		return get_cheapest_flight()

	if method in ['shortest', 'return', 'one-way']:
		if method in ['return', 'one-way']:
			print('Info: finding a best fit with a method %r. I also pick the flight with a shortest duration.' % (method))
		if method == 'shortest':
			print('Info: finding a best fit with a method %r.' % (method))
		return get_shortest_flight()


def check_flights(booking):
	'''
	Check the price and if the flight can be booked
	@return - True/False for both 
	@link - http://docs.skypickerbookingapi1.apiary.io/#reference/check-flights/checkflights/check_flights?console=1
	'''
	print('Info: checking price and validity of the flight.')

	params = {	'v': 2,				 	# default
			 	'pnum': 1,				# passenger number
			  	'bnum': 0,				# number of bags
			  	'booking_token': booking['booking_token']
 	}
	try:
		response = requests.get(api_check_booking_url, params=params ).json()
		checked = response['flights_checked']
		invalid = response['flights_invalid']
		return checked, invalid
	except:
		raise Exception('Error: something happened when trying to check the flights.')

def save_booking(booking):
	'''
	Save booking
	@return - True if the booking process was successful
	@link - http://docs.skypickerbookingapi1.apiary.io/#reference/save-booking/savebooking/save_booking?console=1
	'''
	print('Info: trying to make a booking.')

	payload = {
		'lang':'en', # user language
		'bags':0, # number of bags
		'passengers':[ # array with passengers data
			{
				'lastName':'Rehor',
				'firstName':'Frantisek',
				'documentID':'123',
				'cardno':'123', # ID card/passport ID. In case, check flights will return document_options.document_need 2,
				#this needs to be filled in by the user togerther with the expiration field. Otherwise, those field can stay hidden from the booking form to increase conversion rate
				'phone':'+420 000000000', # needed only for the first passenger in the array
				'birthday':'1988-10-11', # passenger birth day, utc unix timestamp in seconds
				'nationality':'Czech Republic',
				'checkin':'', # DEPRECATED, leave an empty string here
				'issuer':'', # DEPRECATED, leave an empty string here
				'name':'test',
				'title':'Mr', # mr/ms/mrs
				'expiration':1598804820, # expiration date of the ID from the cardno field
				'email':'hi@frantisekrehor.cz'	# needed only for the first passenger in the array
			}
		],
		'locale':'en',
		'currency':'CZK',
		'customerLoginID':'unknown', # loginID for zooz payments
		'customerLoginName':'unknown', # login name for zooz payments
		'booking_token':booking['booking_token'],
		'affily':'affil_id', # affil id, can contain any subID string, max length 64
		'booked_at':'affil_id' # basic affil id, without any subIDs
	}
	headers = {'content-type': 'application/json'}

	try:
		response = requests.post(api_booking_url, data = json.dumps(payload), headers=headers)
		response_data = response.json()

		if response.status_code == 200:
			
			print('Info: booking is %r with booking number %r.' %(response_data['status'], response_data['pnr']))
			print('\nBooking information: ', response_data['pnr'])
			print('=========================================')
			for r in booking['route']:
				dTime = datetime.fromtimestamp(float(r['dTime'])).strftime('%c')
				aTime = datetime.fromtimestamp(float(r['aTime'])).strftime('%c')
				print ('%s -> %s \t %s -> %s' % (r['flyFrom'], r['flyTo'], dTime, aTime))
			print('\nDuration to destination: %dh' % (int(booking['duration']['departure'])/3600))
			print('Duration from destination: %dh' % (int(booking['duration']['return'])/3600))
			print('=========================================')

			return True
		else:
			print('Info: booking could not be booked, let\'s try again...')
			return False

	except:
		raise Exception('Error: something happend when trying to save the booking.')


def main():
	'''
	Main function
	'''
	arguments, method = parse_argv(sys.argv)
	
	for searching in range(10): # max 10 searching tries

		flights = get_available_flights(arguments)
		booking = get_best_flight(flights, method)

		for checking in range(10): # max 10 checking tries for the search

			checked, invalid = check_flights(booking)

			if checked and not invalid:
				book = save_booking(booking)
				if not book:
					time.sleep(5)
					continue	
				else:
					sys.exit()
		else:
			print('Info: This could not be booked, let\'s try another...')

	print('Try to change your request... The %r flight cannot be booked.' % method)
	sys.exit()


if __name__ == '__main__':
	main()
