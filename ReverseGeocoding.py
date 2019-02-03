# Reverse Geo Coding

import pandas as pd
import requests
import logging
import time

logger = logging.getLogger("root")
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)


# ------------------ CONFIGURATION -------------------------------


API_KEY = 'Add your API Key'
BACKOFF_TIME = 30
RETURN_FULL_RESULTS = True


# ------------------ DATA LOADING --------------------------------
def reverseGeo(filname):
    output_filename = "output/"+"output_" + filname
    inputpath = 'upload/'+filname
    data = pd.read_csv(inputpath, encoding='utf8', usecols=['Lat', 'Lon'])
    latitude = 'Lat'
    longitude = 'Lon'
    if latitude not in data.columns:
        raise ValueError("Missing latitude column in input data")
    if longitude not in data.columns:
        raise ValueError("Missing longitude column")

    locations = []
    for i in range(len(data)):
        a = str(data.loc[i]['Lat'])
        b = str(data.loc[i]['Lon'])
        locations.append(f'{a},{b}')

    results = []

    for location in locations:
        geocoded = False
        while geocoded is not True:
            try:
                geocode_result = get_google_results(location, API_KEY, return_full_response=RETURN_FULL_RESULTS)
            except Exception as e:
                logger.exception(e)
                logger.error("Major error with {}".format(location))
                logger.error("Skipping!")
                geocoded = True

            if geocode_result['status'] == 'OVER_QUERY_LIMIT':
                logger.info("Hit Query Limit! Backing off for a bit.")
                time.sleep(BACKOFF_TIME * 60)  # sleep for 30 minutes
                geocoded = False
            else:
                if geocode_result['status'] != 'OK':
                    logger.warning("Error geocoding {}: {}".format(location, geocode_result['status']))
                logger.debug("Geocoded: {}: {}".format(location, geocode_result['status']))
                results.append(geocode_result)
                geocoded = True

        if len(results) % 20 == 0:
            logger.info("Completed {} of {} address".format(len(results), len(locations)))

        if len(results) % 30 == 0:
            pd.DataFrame(results).to_csv("{}_bak".format(output_filename))

    logger.info("Finished geocoding all locations")

    df = pd.DataFrame(results)
    filter_out = df[['formatted_address', 'latitude', 'longitude']]

    filter_out.to_csv(output_filename, encoding='utf8',index=False)

    return output_filename


def get_google_results(latlng, api_key, return_full_response=False):
    geocode_url = "https://maps.googleapis.com/maps/api/geocode/json?"
    if latlng is not None:
        geocode_url =geocode_url + "latlng={}".format(latlng)
  # Specifying the Malaysia in component change as per your needed country code.
  if api_key is not None:
        geocode_url = geocode_url + "&key={}".format(api_key)+ "&components=country:MY" 


    results = requests.get(geocode_url)
    results = results.json()

    if len(results['results']) == 0:
        output = {
            "formatted_address": None,
            "latitude": None,
            "longitude": None,
            "accuracy": None,
            "google_place_id": None,
            "type": None,
            "postcode": None
        }
    else:
        answer = results['results'][0]
        output = {
            "formatted_address": answer.get('formatted_address'),
            "latitude": answer.get('geometry').get('location').get('lat'),
            "longitude": answer.get('geometry').get('location').get('lng'),
            "accuracy": answer.get('geometry').get('location_type'),
            "google_place_id": answer.get("place_id"),
            "type": ",".join(answer.get('types')),
            "postcode": ",".join([x['long_name'] for x in answer.get('address_components')
                                  if 'postal_code' in x.get('types')])
        }
    output['input_string'] = latlng
    output['number_of_results'] = len(results['results'])
    output['status'] = results.get('status')
    if return_full_response is True:
        output['response'] = results

    return output




