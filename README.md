# lyft-unofficial-api
Part of a larger, ongoing project at https://anon.sh
## Summary
This is a Python (3.6+) library for accessing Lyft's services.
A brief of these services are:
* Address to Google Place ID Conversion
* List of drivers from a location
* List of nearby Lime and Lyft e-scooters
* Price estimates for each available ride type (Lyft, Lyft Plus, etc)
* Estimated trip time and ETA
* And of course, **ordering a Lyft**
## Usage
For the purposes of better understanding the process, most lines are commented.

Included is an example file which goes through each step of building a **ride_request.json** file.
## Setup
The only dependency for this library is **Requests**. You can install this via pip:

> pip install requests

## Running the Example
To run the **example.py** be sure to edit the email variable (line 13) with the email of the Lyft account you're accessing.

After you've made the edit, run the file:

> python example.py

You'll be asked for your phone number. Enter it, and you'll receive a pincode from Lyft.

This will create a file called **data.json** within the data folder.

Once you receive the pincode, enter the pincode.

If successful, a file called **auth.json** will be created.

The next steps work through the process of returning price estimates, wait times, etc.

## Documentation
**Full documentation** is available here: https://anon.sh/projects/unofficial-lyft-api-for-python/rideshare-backporting-documentation.html
