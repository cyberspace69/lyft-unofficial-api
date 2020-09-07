import requests
import json
import os

#
# Bearer token is required before getting auth
#

def create_bearer_token(data, user_agent,basic_token,user_device):
    url = "https://api.lyft.com/oauth2/access_token?user-agent=" + user_agent + "&user-device=" + user_device + "x-design-id=x&x-request-attempt=1&grant_type=client_credentials"
    payload = {'grant_type': 'client_credentials'}
    headers = {
        'user-agent': user_agent,
        'Authorization': 'Basic ' + basic_token
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    bearer_access = json.loads(response.text)
    print(bearer_access)
    #
    # Writing bearer token response to JSON file
    #
    with open(data, 'w+') as outfile:
        json.dump(bearer_access, outfile)
    return bearer_access

#
# After creating bearer token, request an authorization pin
#

def request_auth_pin(number, bearer_access_token):
    url = "https://api.lyft.com/v1/phoneauth"
    payload = "{\n    \"phone_number\": \"+1" + str(number) + "\",\n    \"voice_verification\": false\n}"
    headers = {
        'Authorization': 'Bearer ' + bearer_access_token,
        'Content-Type': 'application/json'
    }
    pin_response = requests.request("POST", url, headers=headers, data=payload)
    return pin_response

#
# After receiving authorization pin, request authorization token
#

def request_auth(number, email, pin_code, user_agent, basic_token, bearer_access_token, auth_json):
    url = "https://api.lyft.com/oauth2/access_token"

    payload = 'grant_type=urn%3Alyft%3Aoauth2%3Agrant_type%3Aphone&phone_number=+1' + str(
        number) + '&phone_code=' + str(
        pin_code) + '&email=' + str(email)
    headers = {
        'user-agent': user_agent,
        'Authorization': 'Basic ' + basic_token,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    auth_json_received = json.loads(response.text)

    #
    # Write authorization token to file
    #
    with open(auth_json, 'w+') as outfile:
        json.dump(auth_json_received, outfile)
    return auth_json_received
