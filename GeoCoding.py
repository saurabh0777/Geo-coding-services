# Sample code is python to geo code the addresses

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


API_KEY = '<Add Your Key Here>'
BACKOFF_TIME = 30
address_column_name = "address"
RETURN_FULL_RESULTS = True

# ------------------ DATA LOADING --------------------------------

def geocoder(file,filname):
    output_filename = "output/"+"output_"+filname
    df = pd.read_csv(file, encoding='utf8')
    df.columns = df.columns.str.lower()
   
    if address_column_name not in df.columns:
        raise ValueError("Missing Address column in input data")

    addresses = (df[address_column_name]).tolist()

    results = []
    for address in addresses:
        geocoded = False
        while geocoded is not True:
            try:
                geocode_result = get_google_results(address, API_KEY,
                                                                    return_full_response=RETURN_FULL_RESULTS)

            except Exception as e:
                logger.exception(e)
                logger.error("Major error with {}".format(address))
                logger.error("Skipping!")
                geocoded = True

            if geocode_result['status'] == 'OVER_QUERY_LIMIT':
                logger.info("Hit Query Limit! Backing off for a bit.")
                time.sleep(BACKOFF_TIME * 60)  # sleep for 30 minutes
                geocoded = False
            else:
            # Stroing the addresses having issues
                if geocode_result['status'] != 'OK':
                    with open('WrongAddress.txt', 'a') as fd:
                        fd.write("\n" + address)
                    logger.warning("Error geocoding {}: {}".format(address, geocode_result['status']))
                logger.debug("Geocoded: {}: {}".format(address, geocode_result['status']))
                results.append(geocode_result)
                geocoded = True


        if len(results) % 10 == 0:
            logger.info("Completed {} of {} address".format(len(results), len(addresses)))

        if len(results) % 20 == 0:
            pd.DataFrame(results).to_csv("{}_bak".format(output_filename))

    logger.info("Finished geocoding all addresses")

    df = pd.DataFrame(results)

    filter_out = df[['input_string','latitude','longitude']]

    for r in (("%23","#"), ("%20"," ",),("%2C",",")):
            filter_out['input_string']  = filter_out['input_string'] .replace(*r)

    filter_out.to_csv(output_filename, encoding='utf8', mode='w',index=False)


def get_google_results(address, api_key, return_full_response=False):
    
    for r in (("#", "%23"), (" ", "%20"),(",", "%2C")):
        address  = address .replace(*r)

    geocode_url = "https://maps.googleapis.com/maps/api/geocode/json?address={}".format(address)
   # Specifying for region malaysia change the component value as per your requirement
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

    output['input_string'] = address
    output['number_of_results'] = len(results['results'])
    output['status'] = results.get('status')

    if return_full_response is True:
        output['response'] = results

    return output
