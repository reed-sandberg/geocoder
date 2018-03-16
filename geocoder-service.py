#!/usr/bin/env python

import logging
import os
import random

from flask import Flask, jsonify, request
from geoauthority import GeoAuthorityError
from geoauthority.googlemaps import GoogleMaps
from geoauthority.heregeocode import HereGeocode


# List of client API classes to use as authorities.
GEOCODER_AUTHORITY_CLASSES = (GoogleMaps, HereGeocode)


app = Flask(__name__)

# Application configuration, set environment EXEC_MODE=prod to run in production mode, default dev mode.
app.config.from_pyfile('application.cfg')
app.config.from_pyfile('authority-keys.cfg')
app.config['exec_mode'] = os.environ.get('EXEC_MODE', 'dev')
if app.config['exec_mode'] == 'prod':
    app.config.from_pyfile('prod.cfg')

logging.basicConfig(level=app.config.get('LOGLEVEL', logging.INFO))
logger = logging.getLogger(__name__)

# Initialize authority classes with access keys.
GoogleMaps.set_api_access_keys(key=app.config['GOOGLE_MAPS_API_KEY'])
HereGeocode.set_api_access_keys(app_id=app.config['HERE_GEOCODE_APP_ID'], app_code=app.config['HERE_GEOCODE_APP_CODE'])
HereGeocode.set_prod_endpoint(app.config['exec_mode'] == 'prod')

class InputParamError(Exception):
    """Invalid input from the client."""

def verify_coord_precision(coord):
    """Verify decimal places of coord given as a string. Return the same if valid, raise InputParamError otherwise, or
    ValueError for parsing or formatting errors.
    """
    _, mantissa = coord.split('.')
    if len(mantissa) < app.config['MIN_LATLNG_PRECISION']:
        raise InputParamError("latlng precision must be {} decimal places or more".format(
            app.config['MIN_LATLNG_PRECISION']))
    return coord

def parse_latlng_params(latlng):
    """Parse and verify latlng query param. Upon success, return a tuple of lat, lng as string values so as to maintain
    arbitrary precision. Otherwise, raise InputParamError if invalud or ValueError for parsing or formatting errors.
    """
    lat, lng = [verify_coord_precision(i.strip()) for i in latlng.split(',')]
    if not (-90 <= float(lat) <= 90 and -180 <= float(lng) <= 180):
        raise InputParamError("latlng out of range")
    return lat, lng

@app.route('/addresses')
def addresses():
    if 'latlng' not in request.args:
        return jsonify({'status': "ERROR", 'status-msg': "Missing query parameters (latlng)"}), 400

    try:
        lat, lng = parse_latlng_params(request.args['latlng'])
    except ValueError:
        return jsonify({
            'status': "ERROR",
            'status-msg': "Invalid latlng parameter, expected 'lat,lng' in decimal format"}), 400
    except InputParamError as param_err:
        return jsonify({'status': "ERROR", 'status-msg': str(param_err)}), 400

    # Balance requests evenly among authorities, at least until we can determine if one should be preferred.
    authority_classes = list(GEOCODER_AUTHORITY_CLASSES)
    random.shuffle(authority_classes)
    results = None
    for authority_class in authority_classes:
        try:
            authority = authority_class()
            results = authority.location_by_latlng(lat, lng)
        except GeoAuthorityError:
            logger.warning("Authority request error, using backup", exc_info=True)
            continue
        else:
            break

    if results is None:
        return jsonify({'status': "FAIL", 'status-msg': "No valid response from authorities"})

    return jsonify({'results': results, 'status': "OK"})

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=app.config.get('SERVICE_PORT', 8080), processes=app.config.get('FLASK_PROCESSES', 1))
