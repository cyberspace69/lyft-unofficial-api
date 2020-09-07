import requests
import json
import os
from lyft_api import auth, lyft

#
# Basic variable definitions
#

user_agent = 'com.zimride.instant:iOS:13.2.3:6.32.3.96285429'
basic_token = 'Nko2OWJ6dExDS1FlOmZvYUdCeVRtODdXS2pkRzVfd0FFTC1xWnpWaEo0dVQ2'
user_device = 'iPhone8,1'
email = ' YOUR EMAIL GOES HERE '

auth_json = 'lyft_api/data/auth.json'
data_json = 'lyft_api/data/data.json'

# First, we're going to check if there's an established auth token. If not, we go through the steps to make one.

if os.path.isfile(auth_json):
    with open(auth_json) as authfile:
        access_file = json.load(authfile)
        access_token = access_file['access_token']
else:

    #
    # Check if bearer token exists, if not, fetch bearer access token, pincode, etc
    #

    if os.path.isfile(data_json):
        with open(data_json) as outfile:
            bearer_access = json.load(outfile)
            bearer_access_token = bearer_access['access_token']
    else:
        auth.create_bearer_token(data_json, user_agent, basic_token,user_device)
        with open(data_json) as outfile:
            bearer_access = json.load(outfile)
            bearer_access_token = bearer_access['access_token']
        print(bearer_access_token)

    #
    # Request the number to send pincode to
    #

    number = input('what is your number?: ')

    #
    # Try to send pincode, otherwise, request new bearer auth token and try again
    #
    try:
        pin_response = auth.request_auth_pin(str(number), bearer_access_token)
        pin_conf = json.loads(pin_response.text)
        if 'verification_code_length' in pin_conf:
            print('pin code sent')
    except:
        print('Rebuilding basic authentication token..')
        bearer_access_token, bearer_json = auth.create_bearer_token()
        pin_response = auth.request_auth_pin(str(number), bearer_access_token)
        pin_conf = json.loads(pin_response.text)
        if 'verification_code_length' in pin_conf:
            print('pin code sent')
        else:
            print('error .. check the phone number')

    #
    # Input authorization pincode
    #

    pin_code = input('what is the received pin? ')

    #
    # Request authorization token
    #

    auth_json_received = auth.request_auth(str(number), email, str(pin_code), user_agent, basic_token, bearer_access_token, auth_json)

    # Pull access token from received auth
    access_token = auth_json_received['access_token']
    print('auth token captured successfully')
    print('auth token: ' + access_token)

# Once here, we can do anything.
# The rest of this compiles data needed to request a ride
# The data is saved in a file, ride_request.json, and would be used by the function "request_a_ride" to make the request
# This example does not actually request the ride, just builds everything before sending!

print('===== You are now logged into lyft =====')

address = input('what is the address: ')
pickup_address, pickup_place_id = lyft.find_place_id(address, access_token)
pickup_ride_meta = lyft.access_spots(access_token, pickup_place_id, spot_type="pickup")
address = input('where is the dropoff: ')
dropoff_address, dropoff_place_id = lyft.find_place_id(address, access_token)
dropoff_ride_meta = lyft.access_spots(access_token, dropoff_place_id, spot_type="destination")

pickup_lat, pickup_lng, pickup_place_name, pickup_address = lyft.find_location(pickup_place_id, access_token)

print('the pickup lat is: ' + str(pickup_lat))
print('the pickup long is: ' + str(pickup_lng))
print('the pickup place id is: ' + str(pickup_place_id))
print('the pickup address is: ' + pickup_address)
dropoff_lat, dropoff_lng, dropoff_place_name, dropoff_address = lyft.find_location(dropoff_place_id, access_token)
print('the dropoff lat is: ' + str(dropoff_lat))
print('the dropoff lng is: ' + str(dropoff_lng))
print('the dropoff place id is: ' + str(dropoff_place_id))
print('the dropoff address is: ' + str(dropoff_address))

lyft_time = lyft.get_trip_time(access_token, str(pickup_lat * .000001), str(pickup_lng * .000001),str(dropoff_lat * .000001), str(dropoff_lng * .000001))

#cost_token = lyft.get_trip_price(access_token, pickup_lat, pickup_lng, dropoff_lat, dropoff_lng, ride_type)
offer_id, offer_token, cost_token, cost_estimate, time_estimate = lyft.ride_offerings_beta(access_token, str(dropoff_lat), str(dropoff_lng), str(pickup_lat), str(pickup_lng))
print('The offer id is: ' + str(offer_id))
print('The offer token is: ' + str(offer_token))
print('The cost token is: ' + str(cost_token))
print('The cost estimate is: ' + str(cost_estimate))
print('The trip will take: ' + str(time_estimate) + ' minutes.')
print('The current wait for a driver in your area is: ' + str(round(lyft_time - time_estimate, 2)) + ' minutes.')
lyft.ride_request_builder(cost_token, dropoff_address, dropoff_lat, dropoff_lng, dropoff_place_id, dropoff_place_name, pickup_address, pickup_lat, pickup_lng, pickup_place_id, pickup_place_name, offer_id, offer_token)
print('done! Ride request built in data/ride_request.json')
