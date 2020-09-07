import requests
import base64
import urllib
import json
import os

datajson = 'lyft_api/data/data.json'
authjson = 'lyft_api/data/auth.json'
ridepickupjson = 'lyft_api/data/ride_pickup.json'
ridedropoffjson = 'lyft_api/data/ride_est.json'
riderequestjson = 'lyft_api/data/ride_request.json'

def find_place_id(address, access_token):
    # Fetch Google Place ID
    url = "https://api.lyft.com/v1/place-autocomplete?query=" + address + "&skip_display_info=0&location_type=pickup"

    payload = {}
    headers = {
        'Authorization': 'Bearer ' + access_token
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    print(str(response))

    destinations = json.loads(response.text)

    full_address = destinations['place_predictions'][0]['description']
    place_id = destinations['place_predictions'][0]['place_id']
    print('The full address is: ' + str(full_address))
    print('The place_id is: ' + str(place_id))
    return full_address, place_id


def find_location(place_id, access_token):
    # Find Lat / Lon with Google Place ID
    url = "https://api.lyft.com/v1/access-spots?x-idl-source=pb.api.endpoints.v1.ridelocations.FetchRequest"

    payload = "{\n    \"place_search_location\": {\n        \"google_place_id\": \"" + str(
        place_id) + "\",\n        \"place_provider\": \"google\"\n    },\n    \"source\": 1\n}"
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    place_id_response = json.loads(response.text)

    place_id_lat = \
        place_id_response['raw_location']['portable_location_with_features']['portable_location']['location'][
            'lat_microdegrees']
    place_name = place_id_response['raw_location']['location_metadata']['static_metadata']['spot']['name']
    place_id_lng = \
        place_id_response['raw_location']['portable_location_with_features']['portable_location']['location'][
            'lng_microdegrees']
    place_address = place_id_response['raw_location']['location_metadata']['static_metadata']['spot']['routable_address']

    #print(str(place_id_lat))
    #print(str(place_id_lng))
    print(place_id_lat)
    print(place_id_lng)
    print(place_name)
    print(place_address)
    return place_id_lat, place_id_lng, place_name, place_address


def nearby_drivers(access_token, pickup_lat, pickup_lng, dropoff_lat, dropoff_lng):
    # Requesting Available Drivers
    url = "https://api.lyft.com/v1/nearby-drivers-pickup-etas?lng=" + pickup_lng + "&lat=" + pickup_lat + "&destination_lng=" + dropoff_lng + "&selected_ride_type=lyft&using_commuter_payment=0&destination_lat=" + dropoff_lat
    headers = {
        'Authorization': 'Bearer ' + access_token
    }
    response = requests.request("GET", url, headers=headers)

    nearby_drivers = json.loads(response.text)

    print(nearby_drivers)


def find_scooters(access_token, lat, lng):
    url = "https://api.lyft.com/v1/last-mile/nearby-rideables?result_types=stations&result_types=rideables&radius_km=1&request_purpose=magic_map_v1&origin_lat=" + lat + "&origin_lng=" + lng
    headers = {
        'x-idl-source': 'pb.api.endpoints.v1.last_mile.ReadLastMileNearbyRideablesRequest',
        'Authorization': 'Bearer ' + access_token
    }

    response = requests.request("GET", url, headers=headers)

    nearby_scooters = json.loads(response.text)


def get_trip_time(access_token, pickup_lat, pickup_lng, dropoff_lat, dropoff_lng):
    url = "https://api.lyft.com/v1/dropoff-times?destination_lat=" + dropoff_lat + "&lng=" + pickup_lng + "&using_commuter_payment=0&destination_lng=" + dropoff_lng + "&lat=" + pickup_lat

    headers = {
        'Authorization': 'Bearer ' + access_token
    }

    response = requests.request("GET", url, headers=headers)

    trip_time = json.loads(response.text)

    lyft_combo_time = trip_time['dropoff_times'][0]['dropoff_duration_range']['duration_ms']
    lyft_combo_time = (int(lyft_combo_time) / (1000 * 60) % 60)
    lyft_time = trip_time['dropoff_times'][1]['dropoff_duration_range']['duration_ms']
    lyft_time = (int(lyft_time) / (1000 * 60) % 60)
    return lyft_time


def get_trip_price(access_token, pickup_lat, pickup_lng, dropoff_lat, dropoff_lng, ride_type):
    url = "https://api.lyft.com/v1/cost?start_lat=" + str(pickup_lat * .000001) + "&start_lng=" + str(
        pickup_lng * .000001) + "&end_lat=" + str(dropoff_lat * .000001) + "&end_lng=" + str(
        dropoff_lng * .000001) + "&ride_type=lyft"

    payload = {}
    headers = {
        'user-agent': 'com.zimride.instant:iOS:13.2.3:6.32.3.96285429',
        'Authorization': 'Bearer ' + access_token,
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    price_data = json.loads(response.text)
    # print(price_data)

    cost_estimate = (price_data['cost_estimates'][0]['apple_pay_pre_auth_cents'] * .01)
    cost_token = price_data['cost_estimates'][0]['cost_token']
    print(price_data)
    # print(cost_estimate)
    # return cost_estimate
    return cost_token

def get_charge_accounts(access_token):
    url = "https://api.lyft.com/chargeaccounts"

    payload = {}
    headers = {
        'x-idl-source': 'pb.api.endpoints.charge_accounts.ReadChargeAccountsRequest',
        'Authorization': 'Bearer ' + access_token
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    payments = json.loads(response.text)
    first_card = payments['chargeAccounts'][0]['id']
    return first_card


def ride_offerings_beta(access_token, dest_micro_lat, dest_micro_lng, pickup_micro_lat, pickup_micro_lng):
    url = "https://api.lyft.com/v1/offerings"

    payload = '{\n    "destination": {\n        "latitude_e6": ' + dest_micro_lat + ',\n        "longitude_e6": ' + dest_micro_lng + '\n    },\n    "is_business_ride": false,\n    "is_shadow_request": false,\n    "offer_selector_type": 1,\n    "origin": {\n        "latitude_e6": ' + pickup_micro_lat + ',\n        "longitude_e6": ' + pickup_micro_lng + '\n    },\n    "request_source": 4,\n    "using_commuter_payment": false\n}'
    headers = {
        'user-agent': 'com.zimride.instant:iOS:13.2.3:6.36.3.98686917',
        'accept-language': 'en_US',
        'x-device-density': '2.0',
        'x-locale-region': 'US',
        'x-idl-source': 'pb.api.endpoints.v1.offers.OffersRequest',
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    cost_response = json.loads(response.text)
    offer_amount = len(cost_response['offers'])
    print('the amount of offers available are: ' + str(offer_amount))
    offer = 0
    if offer_amount > 0:
        for offer_type in cost_response['offers']:
            if 'standard' in cost_response['offers'][offer]['offer_product_id']:
                print('The offer ' + str(offer) + ' contains standard')
                offer_id = cost_response['offers'][offer]['id']
                offer_token = cost_response['offers'][offer]['offer_token']
                cost_token = cost_response['offers'][offer]['cost_estimate']['cost_token']
                cost_estimate = cost_response['offers'][offer]['cost_estimate']['estimated_cost_cents_max']
                time_estimate = cost_response['offers'][offer]['cost_estimate']['estimated_duration_seconds']
                cost_estimate = round(int(cost_estimate) * .01, 2)
                time_estimate = round(int(time_estimate) / 60, 2)
                break
            else:
                offer += 1
    return offer_id, offer_token, cost_token, cost_estimate, time_estimate


def ride_review(access_token, ride_id):
    url = "https://api.lyft.com/v1/feedback/passenger-to-driver"

    payload = "{\n    \"feedback\": \"\",\n    \"rating\": 5,\n    \"ride_id\": " + ride_id + "\n}"
    headers = {
        'x-idl-source': 'pb.api.endpoints.v1.feedback.CreatePassengerToDriverFeedbackRequest',
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    feedback = json.loads(response.text)


def ride_info(access_token, ride_id):
    url = "https://api.lyft.com/v1/rides/" + ride_id + "/paymentdetails?ride_id=" + ride_id

    payload = {}
    headers = {
        'user-agent': 'com.zimride.instant:iOS:13.2.3:6.32.3.96285429',
        'x-idl-source': 'pb.api.endpoints.v1.rides.ReadRidePaymentDetailsRequest',
        'Authorization': 'Bearer ' + access_token
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    ride_info = json.loads(response.text)

    ride_cost = ride_info['amount']

    return ride_cost


def access_spots(access_token, place_id, **kwargs):
    url = "https://api.lyft.com/v1/access-spots"

    payload = '{\n    "place_search_location": {\n        "google_place_id": \"' + str(
        place_id) + '\",\n        "place_provider": "google"\n    },\n    "source": 4\n}'
    headers = {
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    ride_meta = json.loads(response.text)
    ride_meta = ride_meta['raw_location']
    spot_type = kwargs.get('spot_type')
    if spot_type == 'pickup':
        print('this is for the pickup address')
        with open(ridepickupjson, 'w+') as outfile:
            json.dump(ride_meta, outfile)
    if spot_type == 'destination':
        print('this is for the destination address')
        with open(ridedropoffjson, 'w+') as outfile:
            json.dump(ride_meta, outfile)
    # print(ride_meta['raw_location'])
    return ride_meta


def ride_request_builder(cost_token, dest_address, dest_lat, dest_lng, dest_place_id, dest_place_name, pickup_address,
                         pickup_lat, pickup_lng, pickup_place_id, pickup_place_name, offer_id, offer_token, first_card):
    with open(ridepickupjson) as outfile:
        pickup_info = json.load(outfile)
    with open(ridedropoffjson) as outfile:
        dest_info = json.load(outfile)

    ride_request = {"cost_token": cost_token,
                    "destination": {"address": dest_address, "lat": dest_lat * .000001, "lng": dest_lng * .000001,
                                    "location_input_source": "placeSearch",
                                    "navigation_method": "coordinate",
                                    "place_id": dest_place_id, "place_name": dest_place_name,
                                    "routable_address": dest_address},
                    "destination_location_v2": dest_info,
                    "is_business_ride": False, "offer_id": offer_id, "offer_token": offer_token,
                    "origin": {"address": pickup_address, "lat": pickup_lat * .000001, "lng": pickup_lng * .000001,
                               "location_input_source": "placeSearch", "navigation_method": "address",
                               "place_id": pickup_place_id, "place_name": pickup_place_name,
                               "routable_address": pickup_address}, "party_size": 1,
                    "payment_account_id": first_card, "pickup_mode": "standard",
                    "request_location_v2": pickup_info, "ride_type": "lyft", "ride_type_features": ["is_display_default", "supports_plan_ahead", "supports_waypoints", "supports_scheduled_ride", "prompt_mandatory_passenger_queue"]}

    with open(riderequestjson, 'w+') as outfile:
        json.dump(ride_request, outfile)
    return ride_request


def request_a_ride(ride_request, access_token):
    url = "https://api.lyft.com/v1/rides"

    payload = json.dumps(ride_request)
    headers = {
        'x-idl-source': 'pb.api.endpoints.v1.rides.CreateRideRequest',
        'user-agent': 'com.zimride.instant:iOS:13.2.3:6.32.3.96285429',
        'Authorization': 'Bearer ' + access_token,
        'Content-Type': 'application/json'
    }
    print(ride_request)
    response = requests.request("POST", url, headers=headers, data=payload)

    print('Response is: ' + str(response))

    if response.status_code == '201' or '200':
        request_response = json.loads(response.text)
        print('=============divider===========')
        ride_id = request_response['ride_id']
        print('The rider ID is: ' + str(ride_id))
        wait_time = request_response['wait_estimate_seconds']
    else:
        print('Connection not successful')
        ride_id = 'null'
        wait_time = 'null'
    return ride_id, wait_time
