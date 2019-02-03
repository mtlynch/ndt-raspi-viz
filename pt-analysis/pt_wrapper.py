import re
import subprocess

def perform_pt(target_hostname):
    raw_output = subprocess.check_output(
        ['paris-traceroute', '-n', '-f','3', target_hostname],
        stderr=subprocess.STDOUT)
    return _parse_pt_output(raw_output)


def _parse_pt_output(pt_output):
    lines = pt_output.split('\n')
    cur_line = 0
    hops = []
    first_line = lines[cur_line]
    if first_line.startswith('[ERROR]'):
        return None
    while not first_line.startswith('traceroute [('):
        cur_line += 1
        first_line = lines[cur_line]
    dest_ip = re.findall(
        '\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', first_line)[1]
    cur_line += 1
    for line in lines[cur_line:]:
        m = re.search('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}',
                      line)
        if not m:
            continue
        hops.append(m.group())
    if not hops or hops[-1] != dest_ip:
        hops.append(dest_ip)
    return hops
