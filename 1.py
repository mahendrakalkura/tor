# -*- coding: utf-8 -*-

from multiprocessing import Pool
from os import kill, makedirs
from os.path import isdir, join
from shutil import rmtree
from signal import SIGKILL
from subprocess import PIPE, Popen
from sys import argv

from human_curl import CurlError, get

from settings import HOSTNAME, NODES, POLIPO, TIMEOUT, TOR


def get_ip_addresses(type, port):
    pool = Pool(processes=NODES)
    ip_addresses = pool.map(get_ip_address, [(type, port + index, ) for index in range(1, NODES + 1)])
    pool.close()
    pool.join()
    return ip_addresses


def get_ip_address(arguments):
    try:
        return get(
            'http://ifconfig.co',
            proxy=(arguments[0], (HOSTNAME, arguments[1])),
            timeout=TIMEOUT,
            user_agent='curl/7.42.0',
        ).content.strip()
    except CurlError:
        pass
    except Exception:
        from traceback import print_exc
        print_exc()
    return 'N/A'


def get_output(command):
    try:
        handle = Popen(command, shell=True, stdin=PIPE, stdout=PIPE, stderr=PIPE, executable='/bin/bash')
        stdout, stderr = handle.communicate()
        return stdout.strip(), stderr.strip(), handle.returncode
    except ValueError:
        raise SystemExit
    except OSError:
        raise SystemExit


def reset():
    while True:
        pids = []
        stdout, stderr, returncode = get_output('ps -A')
        for line in stdout.splitlines():
            if 'polipo' in line or 'tor' in line:
                pids.append(int(line.split(None, 1)[0]))
        if not len(pids):
            break
        for pid in pids:
            kill(pid, SIGKILL)
    rmtree('files/')


def tor():

    def node(files_tor_data, contents, index):
        files_tor_data_index = join(files_tor_data, str(index))
        makedirs(files_tor_data_index, 0700)
        contents = contents.replace('{{ control_port }}', str(TOR['control'] + index))
        contents = contents.replace('{{ data_directory }}', files_tor_data_index)
        contents = contents.replace('{{ index }}', str(index))
        contents = contents.replace('{{ socks_bind_address }}', HOSTNAME)
        contents = contents.replace('{{ socks_port }}', str(TOR['socks'] + index))
        files_tor_data_index_torrc = join(files_tor_data_index, 'torrc')
        with open(files_tor_data_index_torrc, 'w') as resource:
            resource.write(contents)
        get_output(
            'tor -f {files_tor_data_index_torrc:s}'.format(files_tor_data_index_torrc=files_tor_data_index_torrc)
        )

    files_tor_data = 'files/tor/data'
    if not isdir(files_tor_data):
        makedirs(files_tor_data, 0755)
    torrc = ''
    with open('torrc', 'r') as resource:
        torrc = resource.read()
    for index in range(1, NODES + 1):
        node(files_tor_data, torrc, index)


def polipo():
    for index in range(1, NODES + 1):
        get_output(' '.join([
            'polipo',
            'allowedPorts=1-65535',
            'daemonise=true',
            'logSyslog=true',
            'proxyAddress={proxy_address:s}',
            'proxyPort={proxy_port:d}',
            'socksParentProxy={socks_parent_proxy_hostname}:{socks_parent_proxy_port:d}',
            'tunnelAllowedPorts=1-65535',
        ]).format(
            proxy_address=HOSTNAME,
            proxy_port=POLIPO + index,
            socks_parent_proxy_hostname=HOSTNAME,
            socks_parent_proxy_port=TOR['socks'] + index,
        ))


def report():
    print 'Tor'
    for index, ip_address in enumerate(get_ip_addresses('socks5', TOR['socks'])):
        print '    + {index:02d}: {ip_address:s}'.format(index=index + 1, ip_address=ip_address)
    print 'Polipo'
    for index, ip_address in enumerate(get_ip_addresses('http', POLIPO)):
        print '    + {index:02d}: {ip_address:s}'.format(index=index + 1, ip_address=ip_address)

if __name__ == '__main__':
    if len(argv) >= 2:
        locals()[argv[1]]()
