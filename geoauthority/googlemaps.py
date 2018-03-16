"""Google Maps client API."""

from geoauthority import GeoAuthority, GeoAuthorityError

API_BASE_URL = 'https://maps.googleapis.com/maps/api/geocode/json'

API_BASE_PARAMS = {
    'location_type': 'ROOFTOP',
    'result_type': 'street_address',
    'key': ''
}


class GoogleMaps(GeoAuthority):
    """Represent a Google Maps API endpoint. Be sure to set_api_access_keys() before using."""

    def __init__(self):
        """Be sure to set_api_access_keys() before instantiating."""
        super().__init__()
        self._api_url = API_BASE_URL
        self._api_params = API_BASE_PARAMS.copy()

    @staticmethod
    def set_api_access_keys(**kwargs):
        """Set the access key as key=your_googlemaps_key. This must be called prior to contacting the API."""
        API_BASE_PARAMS['key'] = kwargs['key']

    @property
    def api_url(self):
        """API endpoint for this authority."""
        return self._api_url

    @property
    def api_params(self):
        """GET params for querying this authority."""
        return self._api_params

    def prep_latlng_params(self, lat, lng):
        """Prepare params for request processing."""
        self._api_params['latlng'] = '{},{}'.format(lat, lng)

    def parse_location_response(self, location_json):
        """Process response from authority API and return a list of human-readable addresses for any matches. Raise
        GeoAuthorityError with an appropriate message otherwise.
        """
        street_addresses = []
        try:
            if location_json['status'] == 'ZERO_RESULTS':
                return []
            elif location_json['status'] != 'OK':
                self.logger.error("Unexpected response status: %s", location_json['status'])
                raise GeoAuthorityError("Unexpected response body (status)")

            for result_json in location_json['results']:
                if 'formatted_address' in result_json:
                    street_addresses.append(result_json['formatted_address'])
        except (KeyError, TypeError):
            raise GeoAuthorityError("Unexpected response body (structure)")

        return street_addresses
