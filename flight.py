
#AUTHOR: SPENCER HARDER
#DEVELOPED IN PYTHON VERSION 2.7.11
#QPX API KEY: AIzaSyDsB6c3vOHxce4xnswDajVQVR0WcGCyDx8
#requests library used to send HTTPS requests: "http://docs.python-requests.org/en/v1.0.0/#"  Copyright 2012. A Kenneth Reitz Project.

import os
import json
import requests
import itertools
from datetime import datetime


#will clear windows command prompt
clear = lambda: os.system('cls')

#stores flight information for a single flight. Usage: Stores pertinent information parsed from QPX response
class Flight:
	def __init__(self, passName, flightNum, flightOrigin, flightDestination, flightDeparture, flightArrival, flightPrice):
		self.passName = passName
		self.flightNum = flightNum
		self.flightOrigin = flightOrigin
		self.flightDestination = flightDestination
		self.flightDeparture = flightDeparture
		self.flightArrival = flightArrival
		self.flightPrice = flightPrice

	def printFlight(self):
		print "\nFlight for " + self.passName + " from " + self.flightOrigin + " --> " + self.flightDestination
		print "\n\tFlight Number: " + self.flightNum
		print "\n\tDeparture time: "+ self.flightDeparture[1] + self.flightDeparture[2] +' '+ self.flightDeparture[0]
		print "\n\tArrival Time: "+ self.flightArrival[1] + self.flightArrival[2] +' '+ self.flightArrival[0]
		print "\n\tTotal Price: "+ self.flightPrice

#store passenger information for a single passenger. Usage: sending requests and storing received flight list
class Passenger:
	adultPassengers = 1
	def __init__(self, passengerName, departureDate, airportCodeDepart, airportCodeArrive, departAfter, arriveBefore, timeFrame):
		self.passengerName = passengerName
		self.departureDate = departureDate
		self.airportCodeDepart = airportCodeDepart
		self.airportCodeArrive = airportCodeArrive
		self.departAfter = departAfter
		self.arriveBefore = arriveBefore
		self.timeFrame = timeFrame
		self.responseDict = {}
		self.flightList = []

	def printAllFlights(self):
		for x in xrange(0, len(self.flightList) ):
			self.flightList[x].printFlight()

		
# requests passenger info, creates an object of class type Passenger then appends the object to passengerArray
def passengerArray_inputAppend():
	passengerName = raw_input("\nWhat is the name of the passenger? :")

	if planType.upper() == 'A':
		airportCodeArrive = groupAirportCode.upper()
		airportCodeDepart = raw_input("\nWhat airport will they be departing from?:").upper()
		newPassenger = Passenger(passengerName, departureDate, airportCodeDepart, airportCodeArrive, departAfter, arriveBefore, timeFrame)
		passengerArray.append(newPassenger)

	if planType.upper() == 'D':
		airportCodeDepart = groupAirportCode.upper()
		airportCodeArrive = raw_input("\nWhat airport will they be flying to?:").upper()
		newPassenger = Passenger(passengerName, departureDate, airportCodeDepart, airportCodeArrive, departAfter, arriveBefore, timeFrame)
		passengerArray.append(newPassenger)

#writes flight information to Json file in correct QPX format from Passenger member variables
def writeAndRequest(x, path, passengerArray): 
	data = {}
	data['request'] = {}
	data['request']['slice'] = []

	#pulls parameters from each Passenger object to create separate flight requests in request.json
	data['request']['slice'].append({
		'origin': passengerArray[x].airportCodeDepart ,
		'destination': passengerArray[x].airportCodeArrive ,
		'date': passengerArray[x].departureDate ,
		'maxStops': 0,
		'permittedDepartureTime': {
			'earliestTime': passengerArray[x].departAfter ,
			'latestTime': passengerArray[x].arriveBefore 
		}
	})

	data['request']['passengers'] = {
			'adultCount': Passenger.adultPassengers,
            'infantInLapCount': 0,
            'infantInSeatCount': 0,
            'childCount': 0,
            'seniorCount': 0
	}

	data['request']['solutions'] = 10
	data['request']['refundable'] = False

	#Writes to JSON file 
	filePathNameWExt = './' + './' + '/' + 'request' + '.json'
	with open(filePathNameWExt, 'w') as fp:
		json.dump(data, fp)

	passengerArray[x].responseDict = runQPXQuery()

#runs QPX request and returns json file with flight information, returns dict of responses
def runQPXQuery():
	url = "https://www.googleapis.com/qpxExpress/v1/trips/search?key=AIzaSyDsB6c3vOHxce4xnswDajVQVR0WcGCyDx8"
	jsonRequest = open('./request.json')
	headers = {'Content-Type' : 'application/json'}
	response = requests.post(url, data=jsonRequest, headers=headers)
	responseData = json.loads(response.text)
	jsonRequest.close()

	os.remove('./request.json')
	filePathNameWExt = './' + 'requestRESP' + '.json'
	with open(filePathNameWExt, 'w') as fp:
		json.dump(responseData, fp)


	return responseData

#parses response dict into FLight list to run an algorithm on
def responseParse(x):
	responseDict = passengerArray[x].responseDict
	passName = passengerArray[x].passengerName
	try:
		for item in responseDict['trips']['tripOption']:
			flightPrice = item['saleTotal']
			for s in item['slice']:
				for flight in s['segment']:
					flightNum = flight['flight']['carrier'] + ' ' + flight["flight"]["number"] 
					flightOrigin = flight['leg'][0]['origin']
					flightDestination = flight['leg'][0]['destination']
					flightDeparture = flight['leg'][0]['departureTime']
					flightArrival = flight['leg'][0]['arrivalTime']
					#0 in tuple is date, 1 in tuple is 24:00 time, 2 is time zone
					flightDeparture = (flightDeparture[:10], flightDeparture[11:-6], flightDeparture[-6:])
					flightArrival = (flightArrival[:10], flightArrival[11:-6], flightArrival[-6:] )

			newFlight = Flight(passName, flightNum, flightOrigin, flightDestination, flightDeparture, flightArrival, flightPrice)
			passengerArray[x].flightList.append(newFlight)
	except:
		print "No flights found for " + passName + ". Please make new entries."

#analyzes flights to find optimal flight matches based on input parameters (arrival / departure window, cheapest price)
def flightAnalyze(planType, passengerArray):

	allFlightSet = []
	victorySet = []
	bestPrice = 999999999

	for x in xrange(0, int(groupSize)):
		allFlightSet.append(passengerArray[x].flightList)

	#setList contains every popssible set combination of flights from each passenger. A list of tuples that contain Flight objects. 
	setList = list(itertools.product(*allFlightSet))

	#checks for timeframe and price
	for x in xrange(0, len(setList)):
		lowerTime = 1440 #24:00 in minutes
		upperTime = 0 #00:00 in minutes
		avgPrice = 0
		maxAltBound = 0

		for y in xrange(0, len(setList[x])):
			
			if planType == 'A':
				thisTime = setList[x][y].flightArrival
				altBound = setList[x][y].flightDeparture
				altBound = int(altBound[1][:2])*60 + int(altBound[1][-2:])
				maxAltBound = 1440
				if altBound < maxAltBound:
					maxAltBound = altBound

			if planType == 'D':
				thisTime = setList[x][y].flightDeparture
				altBound = setList[x][y].flightArrival
				altBound = int(altBound[1][:2])*60 + int(altBound[1][-2:])
				maxAltBound = 0
				if altBound > maxAltBound:
					maxAltBound = altBound

			thisTime = int(thisTime[1][:2])*60 + int(thisTime[1][-2:])
			avgPrice = avgPrice + float(setList[x][y].flightPrice[3:])

			if thisTime > upperTime:
				upperTime = thisTime
			if thisTime < lowerTime:
				lowerTime = thisTime

		avgPrice = ( avgPrice / (len(setList[x])) )
		
		if (upperTime - lowerTime) <= timeFrame*60 and (bestPrice > avgPrice):

			arriveBeforeMin = int(arriveBefore[:2])*60 + int(arriveBefore[-2:])
			departAfterMin = int(departAfter[:2])*60 + int(departAfter[-2:])

			if planType == 'A':
				if maxAltBound > departAfterMin and upperTime < arriveBeforeMin:
					bestPrice = avgPrice
					del victorySet[:]
					victorySet.append(setList[x])
			elif planType == 'D':
				if maxAltBound < arriveBeforeMin and lowerTime < departAfterMin:
					bestPrice = avgPrice
					del victorySet[:]
			else:
				pass
		else:
			pass
	if victorySet == []:
		return 0
	else:			
		return victorySet


#main runtime command line UI
#-------------------------------------
while True:
	print "\n\nWelcome to Flight Coordinator \n"
	planType = raw_input("Are you coordinating a group departure or arrival? Enter 'A' for arrival or 'D' for departure:").upper()
	groupSize = raw_input("\nHow many people are in your group?:")
	departureDate = raw_input("\nIn the format of 'YYYY-MM-DD', what date do you wish to fly?:")

	if planType == 'A':
		groupAirportCode = raw_input("\nWhat is the airport code of the airport you wish to coordinate your arrivals?:").upper()
	if planType == 'D':
		groupAirportCode = raw_input("\nWhat is the airport code of the airport from which you wish to coordinate your departures?:").upper()

	departAfter = raw_input("\nIn military time (24:00), what time would you like to depart after?:")
	arriveBefore = raw_input("\nIn military time (24:00), before what time would you like to arrive at your destination?:")

	timeFrame = raw_input("\nIn hours, what timeframe do you want to meet your party in? :")

	print("\nPlease enter passenger information. \n")

	#list of Passenger type objects. Main data structure
	passengerArray = []

	#Specific Passenger Input
	for x in xrange(0, int(groupSize)):
		clear()
		print ('\nEnter information for passenger ' + str(x+1) + '\n__________________________________')
		passengerArray_inputAppend()

	clear()

	print("Thank you, please wait while your request is processed...\n\n")

	#requests all flights, receives them, parses them into Flight class objects, stores them in lists in each passengers object
	for x in xrange(0, int(groupSize)):
			writeAndRequest(x, './', passengerArray)
			responseParse(x)

	if groupSize > 1: 
		print "\nThe optimal set of flights for your party:\n"
		try:
			finalFlightSets = flightAnalyze(planType, passengerArray)
			for x in xrange(0, len(finalFlightSets) ):
				for y in finalFlightSets[x]:
					y.printFlight()
		except: print "Not set of flights were found to match your criteria, sorry!"
	else:
		print "\nYou have only entered information for one passenger. There's nothing to calculate, so here is a list of your flights!"
		passengerArray[int(groupSize)-1].printAllFlights()
		
	


