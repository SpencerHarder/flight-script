ReadMe for flight.py use
Author: Spencer Harder

flight.py requires one non std library. 
Requests library used to send HTTPS requests: "http://docs.python-requests.org/en/v1.0.0/#"  Copyright 2012. A Kenneth Reitz Project.
You will need this library for the program to function, as it is used to send and receive HTTP requests.

Input is taken by command line user input. There is currently no format checking but correct format is indicated in the prompts. Program will loop if an exception is caught or the program finishes normally. Escape using CTL+C (normal cmd prompt escape shortcut).

I was not able to use the test stated in the instructions because that date is in the past. Instead I used:

		Arrival coordination
		2017-09-04
		Arriving at ATL airport
		3 people
		Departing after 00:00 (12:00am)
		Arriving before 22:00 (10:00pm) Had to use these hours and not 09:00 to get any flights, for some reason theres no 										nonstops after 9am to and from alot of places

		arriving within 2 hours of eachother

		Jon 
		Departs from BOS

		Korok
		Departs from IAD

		Josh 
		Departs from DEN

This produced a decent sized pool of flights for my program to process and choose from. Output from program stored in RESULTS.txt

Thanks for providing this challenge checking out my program, first full python program, it was a journey. 