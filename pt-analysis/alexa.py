import csv
import logging

import remote_zip

_ALEXA_ZIP_URL = 'http://s3.amazonaws.com/alexa-static/top-1m.csv.zip'
_TOP_SITES_FILENAME = 'top-1m.csv'


class Alexa(object):
    def __init__(self, domains, count):
        self.logger = logging.getLogger('tracefinder')
        self.domains=domains
        self.sites = []
        self.count = count

    def load(self):
        self.logger.info('loading top sites from %s', _ALEXA_ZIP_URL)
        with remote_zip.open_from_zipped_url(_ALEXA_ZIP_URL, _TOP_SITES_FILENAME) as top_sites_file:
            self.logger.info('loaded top sites, parsing...')
            self._parse_top_sites_file(top_sites_file)
        self.logger.info('parsing complete.')

    def get_sites(self):
        return self.sites

    def _parse_top_sites_file(self, top_sites_file):
        self.sites = []
        csv_reader = csv.reader(top_sites_file)
        for row in csv_reader:
            site = row[1]
            for domain in self.domains:
                if site.endswith(domain):
                    self.sites.append(site)
                    break
            if len(self.sites) >= self.count:
                return
