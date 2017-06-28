import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from haversine import haversine

#read Hospital General Information.csv
left = pd.read_csv('Hospital General Information.csv')
left1 = left.loc[:,['Provider ID','Hospital Name','Address','City','State','ZIP Code','Hospital overall rating']]
#change the name of columns
left1.columns = ['ccn','name','Street','City','State','zip_code','overall_rating']

#read Medicare Hospital Spending per Patient - Hospital.csv
right = pd.read_csv('Medicare Hospital Spending per Patient - Hospital.csv')
right1 = right.loc[:,['Provider ID','Score']]
right1.columns = ['ccn', 'spending_score']

#merge the two csv
result = pd.merge(left1, right1, on='ccn')

#read zipcodecentroids.csv
zipcode = pd.read_csv('zipcodecentroids.csv')
zipcode.columns = ['zip_code','lat','lng']
#combine the three csv as the original table
result = result.merge(zipcode, on='zip_code', how='left')

#combine street,city,state,zip_code as a new column address
address = []
for i in range(result.shape[0]):
    s = result[['Street','City','State','zip_code']].ix[i].values
    address.append(s)
#append the address as the last column
result['address'] = address

#simulating input

while True:
	zipcodein = float(raw_input('Please select the zip code you want to query. 0 to exit. '))
	if zipcodein == 0:
		print "Exit!"
		quit()
	if zipcodein not in set(result['zip_code']):
		print "Your input zipcode is not exist! Please change another input."

	else:		
		numberin = int(raw_input('Please input the number of hospital you want to show: '))
		ratingin = float(raw_input('What is the minimum rating (pleast input an int between 1 and 5)? '))
		print "Please wait for a few seconds..."
		#latitude and longitude of input zipcode
		x = zipcode[zipcode.zip_code == zipcodein]['lat']
		y = zipcode[zipcode.zip_code == zipcodein]['lng']
		start = [x,y]

		#distance between input zipcode and hospitals
		distance = []
		for i in range(result.shape[0]):
		    ending = result[['lat','lng']].ix[i].values
		    distance.append(haversine(start,ending))

		#append distance as the last column
		result1 = result.copy()
		result1['distance_miles'] = distance
		#convert the data type of 0verall_rating from string into int
		result1['overall_rating'] = pd.to_numeric(result1['overall_rating'],errors='coerce')
		#drop all overall_rating less than input
		result1 = result1[result1.overall_rating >= ratingin]
		#change the order of columns
		result2 = result1[['ccn','name','Street','City','State','zip_code','overall_rating','spending_score','lat','lng','distance_miles']]
		result1 = result1[['ccn','name','address','overall_rating','spending_score','lat','lng','distance_miles']]

		#sort the result and show the specific numbers
		result1 = result1.sort_values(['overall_rating','distance_miles','name'], ascending=[False,True,True]).head(numberin)
		result2 = result2.sort_values(['overall_rating','distance_miles','name'], ascending=[False,True,True]).head(numberin)
		print 'There are '+str(numberin)+' hospitals shown below, which minimum overall is '+str(ratingin)+':'
		print result1
		result2 = result2.to_json(orient='records')
		with open('data.json', 'w') as outfile:
			json.dump(result2, outfile)
