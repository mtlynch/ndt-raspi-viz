import argparse
import csv
import datetime
import json
import logging
import os
import random
import re
import subprocess
import time
import urllib2

import pytz
import tzlocal


def setup_logger():
    logger = logging.getLogger('pyNDT')
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

    file_handler = logging.FileHandler('pyndt.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


logger = setup_logger()


class NDTResult(object):

    def __init__(self, hostname, test_end_time, upload_throughput, download_throughput):
        self.hostname = hostname
        self.test_end_time = test_end_time;
        self.upload_throughput = upload_throughput
        self.download_throughput = download_throughput



def mlab_site_from_ndt_hostname(hostname):
    return hostname.split('.')[3]


def get_ndt_hostname():
    response_raw = urllib2.urlopen('http://mlab-ns.appspot.com/ndt').read()
    response = json.loads(response_raw)
    return response['fqdn']


def get_ndt_hostnames(max_sites, max_queries):
    hostnames = []
    sites_discovered = set()
    queries = 0
    while (len(sites_discovered) < max_sites) and (queries < max_queries):
      logger.info('query #%u for NDT hosts', queries + 1)
      ndt_hostname = get_ndt_hostname()
      mlab_site = mlab_site_from_ndt_hostname(ndt_hostname)
      if mlab_site not in sites_discovered:
        logger.info('discovered new M-Lab site (%s): %s', mlab_site, ndt_hostname)
        hostnames.append(ndt_hostname)
        sites_discovered.add(mlab_site)
      queries += 1
    return hostnames


def parse_ndt_result(result_raw, hostname, end_time):
    upload_throughput = None
    download_throughput = None
    for line in result_raw:
        upload_match = re.search(r'client to server.+?(\d+\.\d+) Mb/s$', line)
        if upload_match:
            upload_throughput = float(upload_match.group(1))

        download_match = re.search(r'server to client.+?(\d+\.\d+) Mb/s$', line)
        if download_match:
            download_throughput = float(download_match.group(1))

    if not upload_throughput or not download_throughput:
        raise Exception('Unexpected NDT output: %s' % result_raw)

    return NDTResult(hostname, end_time, upload_throughput, download_throughput)


def do_ndt_test(ndt_binary, ndt_hostname):
    result_raw = subprocess.check_output(
        [ndt_binary, '-n', ndt_hostname, '--disablemid', '--disablesfw'])
    return parse_ndt_result(result_raw.split('\n'), ndt_hostname, datetime.datetime.utcnow())


def format_time(utc_time):
    utc_time_explicit = utc_time.replace(tzinfo=pytz.utc)
    localized = utc_time_explicit.astimezone(tzlocal.get_localzone())
    localized = localized.replace(microsecond=0)
    return localized.strftime('%Y-%m-%dT%H:%M:%S%z')


def save_test_result(output_filename, ndt_result):
  with open(output_filename, 'a+') as output_file:
    result_writer = csv.writer(output_file)
    result_writer.writerow([format_time(ndt_result.test_end_time),
                            ndt_result.hostname,
                            ndt_result.upload_throughput,
                            ndt_result.download_throughput])


def perform_test_loop(ndt_binary_path, output_path):
    while True:
        for ndt_hostname in get_ndt_hostnames(6, 50):
            try:
                ndt_result = do_ndt_test(ndt_binary_path, ndt_hostname)
                logger.info('%s: %.2f Mbps up, %.2f Mbps down',
                            ndt_hostname, ndt_result.upload_throughput,
                            ndt_result.download_throughput)
                save_test_result(output_path, ndt_result)
            except Exception as ex:
                logger.error('Error in NDT test: %s', ex)
        sleep_hours = random.randint(6, 10)
        resume_time = datetime.datetime.utcnow() + datetime.timedelta(hours=sleep_hours)
        logger.info('Sleeping for %u hours (until %s)', sleep_hours, format_time(resume_time))
        time.sleep(sleep_hours * 60 * 60)


def main(args):
    try:
        perform_test_loop(args.ndt_binary, args.output)
    except Exception as e:
        logger.error('Unhandled exception: %s', e)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Python NDT',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    parser.add_argument('ndt_binary',
                        help='Path to NDT client binary (web100clt)')
    parser.add_argument('-v', '--verbosity', action='count',
                        help="variable output verbosity (e.g., -vv is more than -v)")
    parser.add_argument('-o', '--output',
                        default='../dashboard/data/ndt-history.csv',
                        help='Output file path. If the folder does not exist, it will be created.')

    args = parser.parse_args()
    main(args)
