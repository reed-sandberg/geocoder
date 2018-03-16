# Geocoder - simple geocoder API service

Geocoder is a RESTful service using authoritative sources to resolve and gecode location information. Use as a simplified API on top of these authoritative services. One of the authorities will be queried and the other(s) will be used as a backup in case of failure. A random order is used to load-balance among the authorities.

* Google Maps
* here.com Geocoder

### Requirements

* python 3.5
* for a full list of python dependencies, see requirements.txt (pip recommended)
```
$ pip install -r ./requirements.txt
```
* Accounts and API access keys for each of the authoritative sources. Create a file at the root level 'authority-keys.cfg' with the following definitions, replacing the values with actual access key values. Keys may be obtained by registering with the respective services:
```
HERE_GEOCODE_APP_ID = 'your_here_geocode_app_id'
HERE_GEOCODE_APP_CODE = 'your_here_geocode_app_code'

GOOGLE_MAPS_API_KEY = 'your_google_maps_api_key'
```

### Running the service

The service is a Python application using Flask.

* Verify access keys in 'authority-keys.cfg' (described above).

* Verify configuration in 'application.cfg' (port, log level, etc).

* Run the service

Output logging information to the terminal, useful for development:
```
$ ./geocoder-service.py
```

To capture output to a log file and run in the background
```
$ nohup ./geocoder-service.py >geocoder-service.log 2>&1 &
```

By default, the development configuration will be used, to use production settings, check configuration in 'prod.cfg' and set the enviroment EXEC_MODE=prod:
```
# Using bash, etc.
$ EXEC_MODE=prod ./geocoder-service.py
```


### Deployment

Most likely you'll use WSGI when running in full production mode, be sure to set the environment to pick up production config settings (EXEC_MODE=prod).


### API

Endpoints:

* /addresses (GET)

Reverse geocode lat/lng parameters and return a list of human-readable addresses.

Parameters:

* latlng

Comma-separated decimal representation of latitude and longitude.

The service responds with a JSON object in the following general form:
```
{
    "status": "STATUS",
    "status-msg": "Optional details of status",
    "results": [
        "address": "human-readable address",
        ...
    ]
}
```

Fields

 - status: one of
  - OK: success (note that the response may be empty, even if successful)
  - ERROR: service abuse or misuse
  - FAIL: attempts to query all authorities have failed
 
 - status-msg: optional details of status

 - results: list of human-readable addresses

Example

Request
```
http://localhost:8080/addresses?latlng=37.75691,-122.41064
```

Response
```
{
  "results": [
    "934 Florida St, San Francisco, CA 94110, USA"
  ], 
  "status": "OK"
}
```



### Development

To add authorities, subclass the geoauthority.GeoAuthority abstract base class and modify the `GEOCODER_AUTHORITY_CLASSES` list.

### Todo

* Before placing into full production, I would spend some more time on:

    - Automated testing
    - Instrumentation - post metrics to a monitoring system such as graphite, etc.
    - Monitoring endpoint and alert system

* here.com pages results with 100 results maximum. This should be ok for many use cases, but something to keep in mind - if more results are expected, need to properly support paging for this client API implementation. I didn't find any information on Google Maps paging results so assuming there are none, might want to verify.

* Results will vary among authorities. Some analysis should be done to see if one authority is preferred, or results combined, depending on specific use cases. Currently, the primary authority is chosen at random for each request.

* Results are returned in a human-readable format, one-line format. To be more useful, should structure and normalize the results depending on specific use cases.

* More flexible command-line options to override config for common options such as port and to run as a daemon.

* Currently everything is logged to stdout, would like to add more flexible logging options.

