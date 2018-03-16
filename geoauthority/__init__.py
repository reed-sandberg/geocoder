"""An authoritive source for location data."""

from abc import ABC, abstractmethod
import logging
import requests


# Set client API connection and read timeout params in seconds.
REQUESTS_TIMEOUT = 6


class GeoAuthority(ABC):
    """Abstract class of an authoritative source for location data."""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @staticmethod
    @abstractmethod
    def set_api_access_keys(**kwargs):
        """Initialize the class with API access keys."""
        pass

    @abstractmethod
    def prep_latlng_params(self, lat, lng):
        """Prepare params for request processing."""
        pass

    @abstractmethod
    def parse_location_response(self, location_json):
        """Process response from authority API and return a list of human-readable addresses for any matches. Raise
        GeoAuthorityError with an appropriate message otherwise.
        """
        pass

    @property
    @abstractmethod
    def api_url(self):
        """API endpoint for this authority."""
        pass

    @property
    @abstractmethod
    def api_params(self):
        """GET params for querying this authority."""
        pass

    def location_by_latlng(self, lat, lng):
        """Query authority using reverse geocoding. lat/lng params given as strings in decimal format."""
        self.prep_latlng_params(lat, lng)
        location_json = self.send_request()
        return self.parse_location_response(location_json)

    def send_request(self):
        """Send HTTP request to the authority's API endpoint. Return the response body on success, or raise
        GeoAuthorityError with an appropriate message otherwise.
        """
        result_json = None
        try:
            res = requests.get(self.api_url, params=self.api_params, allow_redirects=False, timeout=REQUESTS_TIMEOUT)
            self.logger.info("Authority endpoint: %s", res.url)
            if res.status_code != 200:
                if res.status_code < 500:
                    self.logger.error("Possible API implementation flaw or change upstream with status %s: %s",
                                      res.status_code, res.text)
                raise GeoAuthorityError("Unexpected HTTP status")
            result_json = res.json()
        except requests.RequestException as req_ex:
            raise GeoAuthorityError("Trouble querying authoritative API") from req_ex
        except ValueError:
            raise GeoAuthorityError("Unexpected response: absent or invalid JSON")

        return result_json


class GeoAuthorityError(Exception):
    """Trouble querying the authoritative API or processing results."""
