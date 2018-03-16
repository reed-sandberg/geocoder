"""here.com Geocoder client API."""


from geoauthority import GeoAuthority, GeoAuthorityError


API_BASE_URL_DEV = 'https://reverse.geocoder.cit.api.here.com/6.2/reversegeocode.json'
API_BASE_URL_PROD = 'https://reverse.geocoder.api.here.com/6.2/reversegeocode.json'
API_BASE_PARAMS = {
    'mode': 'retrieveAddresses',
    'maxresults': 100,
    'gen': 8,
    'app_id': '',
    'app_code': ''
}

# Minimum confidence score that the address matches.
MIN_ACCEPTABLE_RELEVANCE = 1

# Lat/lng search radius (meters)
API_LATLNG_RADIUS = 25


class HereGeocode(GeoAuthority):
    """Represent a here.com geocode API endpoint. Be sure to set_api_access_keys() before using."""

    api_base_url = API_BASE_URL_DEV

    def __init__(self):
        """Be sure to set_api_access_keys() before instantiating. Set prod=True to use the production endpoint."""
        super().__init__()
        self._api_url = self.api_base_url
        self._api_params = API_BASE_PARAMS.copy()

    @staticmethod
    def set_api_access_keys(**kwargs):
        """Set the app keys as (app_id=your_app_id, app_code=your_app_code). This must be called prior to contacting
        the API.
        """
        API_BASE_PARAMS['app_id'] = kwargs['app_id']
        API_BASE_PARAMS['app_code'] = kwargs['app_code']

    @classmethod
    def set_prod_endpoint(cls, is_prod):
        """Set True to use the production endpoint."""
        cls.api_base_url = API_BASE_URL_PROD if is_prod else API_BASE_URL_DEV

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
        self._api_params['prox'] = '{},{},{}'.format(lat, lng, API_LATLNG_RADIUS)

    def parse_location_response(self, location_json):
        """Process response from authority API and return a list of human-readable addresses for any matches. Raise
        GeoAuthorityError with an appropriate message otherwise.
        """
        street_addresses = []
        try:
            views = location_json['Response']['View']
            if not isinstance(views, list):
                raise GeoAuthorityError("Unexpected response body (structure)")
            elif len(views) == 0:
                return []
            elif len(views) > 1:
                self.logger.error("Not sure how to handle more than one view in the response: %s", location_json)
                raise GeoAuthorityError("Unexpected response body (structure)")

            for result_json in views[0]['Result']:
                try:
                    if (result_json['Relevance'] >= MIN_ACCEPTABLE_RELEVANCE and
                            result_json['Location']['LocationType'] == 'address'):
                        street_addresses.append(result_json['Location']['Address']['Label'])
                except (KeyError, TypeError):
                    # Placeholder for instrumentation.
                    self.logger.warning("Address is absent or possibly unrecognized result structure: %s", result_json)
        except (KeyError, TypeError):
            raise GeoAuthorityError("Unexpected response body (structure)")

        return street_addresses
