import csv
import logging
import socket
import struct

import remote_zip

_GEOLITE_ASN_URL = 'http://download.maxmind.com/download/geoip/database/asnum/GeoIPASNum2.zip'
_GEOLITE_ASN_FILENAME = 'GeoIPASNum2.csv'


def _ip_to_long(ip):
    packed_ip = socket.inet_aton(ip)
    return struct.unpack("!L", packed_ip)[0]


class Maxmind(object):

    def __init__(self):
        self.logger = logging.getLogger('tracefinder')
        self._db_rows = None

    def load(self):
        self.logger.info('loading Maxmind DB from %s', _GEOLITE_ASN_URL)
        with remote_zip.open_from_zipped_url(_GEOLITE_ASN_URL, _GEOLITE_ASN_FILENAME) as maxmind_file:
          self.logger.info('loaded Maxmind DB, parsing...')
          self._parse_maxmind_file(maxmind_file)
          self.logger.info('finished parsing Maxmind DB')

    def _parse_maxmind_file(self, maxmind_file):
      self._db_rows = []
      for row in csv.reader(maxmind_file):
          parsed = {}
          parsed['start'] = int(row[0])
          parsed['end'] = int(row[1])
          asn = row[2].split(' ')[0]
          asn = asn[2:]
          parsed['asn'] = int(asn)
          self._db_rows.append(parsed)

    def ip_to_asn(self, ip):
        ip_long = _ip_to_long(ip)
        for row in self._db_rows:
            if row['start'] <= ip_long <= row['end']:
                return row['asn']

        return None
