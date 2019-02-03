import argparse
import csv
import logging

import alexa
import maxmind
import pt_wrapper


def setup_logger():
    logger = logging.getLogger('tracefinder')
    console_handler = logging.StreamHandler()
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)
    return logger


def get_as_path(hostname, maxmind_db):
    logger = logging.getLogger('tracefinder')
    logger.info('Finding route to %s', hostname)
    ip_hops = pt_wrapper.perform_pt(hostname)
    logger.info('paris-traceroute complete for %s', hostname)
    if not ip_hops:
        return None
    as_path = []
    for ip_hop in ip_hops:
        asn = maxmind_db.ip_to_asn(ip_hop)
        if not as_path or as_path[-1] != asn:
            as_path.append(asn)
    return as_path


def format_as_path(as_path):
    asns = []
    for asn in as_path:
        if asn:
            asns.append(str(asn))
        else:
            asns.append('Unknown AS')
    return ', '.join(asns)


def find_as_paths(hosts, maxmind_db, outfile):
    logger = logging.getLogger('tracefinder')
    csv_writer = csv.writer(outfile)
    for site in hosts:
        as_path = get_as_path(site, maxmind_db)
        if not as_path:
            logger.error('Failed to find AS path for %s', site)
	    continue
        print '%s: %s' % (site, format_as_path(as_path))
        row = [site]
        row.extend(as_path)
        csv_writer.writerow(row)


def main(args):
    logger = setup_logger()
    domains = ['.com', '.net', '.gov', '.edu', '.io', '.org']
    alexa_db = alexa.Alexa(domains, count=500)
    alexa_db.load()
    top_sites = alexa_db.get_sites()

    maxmind_db = maxmind.Maxmind()
    maxmind_db.load()

    #with open('alexa-pt-paths.csv', 'w') as outfile:
    #    find_as_paths(top_sites, maxmind_db, outfile)

    with open('mlab-pt-paths.csv', 'w') as outfile:
        mlab_hosts = []
        for i in range(1, 6):        
            mlab_hosts.append('ndt.iupui.mlab1.lga0%s.measurement-lab.org' %
                              i)
        find_as_paths(mlab_hosts, maxmind_db, outfile)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='Python NDT',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    # parser.add_argument('host', help='Target host')
    args = parser.parse_args()
    main(args)
