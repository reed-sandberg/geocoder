#!/usr/bin/env python

import geocoder
import unittest
import tempfile

class GeocoderTestCase(unittest.TestCase):

    def setUp(self):
        geocoder.app.testing = True
        self.app = geocoder.app.test_client()

    def test_invalid_latlng_missing(self):
        rv = self.app.get('/addresses')
        assert b'Missing query parameters' in rv.data

    def test_invalid_latlng_invalid(self):
        rv = self.app.get('/addresses?latlng=41.88391,thirtyone')
        assert b'Invalid latlng parameter' in rv.data

    def test_invalid_latlng_precision(self):
        rv = self.app.get('/addresses?latlng=41.88391%2C-179.638')
        assert b'latlng precision must be' in rv.data

    def test_invalid_latlng_precision(self):
        rv = self.app.get('/addresses?latlng=41.88391%2C-190.63845')
        assert b'latlng out of range' in rv.data

if __name__ == '__main__':
    unittest.main()
