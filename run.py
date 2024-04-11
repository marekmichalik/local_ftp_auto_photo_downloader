import socket
import traceback
from time import sleep
from ftplib import FTP

PROTOCOLS = ['ftp://', ]
PROTOCOLS = ['', ]

IP_RANGE_START = '192.168.1.84'
IP_RANGE_END = '192.168.1.85'

#PORTS_TO_SCAN = [2121, 2122]
PORTS_TO_SCAN = [2121, ]

TARGET_PATH = 'd:/pokus/'  # should end with /

def ports_to_scan():
    for each in PORTS_TO_SCAN:
        yield str(each)


def urls_to_scan():
    """

    :return: string: Every combination of protocol, ip address and port
    """
    ip_range_start_num = IP_RANGE_START.split('.')
    ip_range_end_num = IP_RANGE_END.split('.')

    def inc_ip(ip_num):
        ip_num[3] = str(int(ip_num[3]) + 1)
        if ip_num[3] == '255':
            ip_num[3] = '1'
            ip_num[2] = str(int(ip_num[2]) + 1)
        return ip_num

    current_ip_num = ip_range_start_num
    while current_ip_num != ip_range_end_num:
        for port in ports_to_scan():
            for protocol in PROTOCOLS:
                yield protocol + '.'.join(current_ip_num)# + ':' + port
        current_ip_num = inc_ip(current_ip_num)

    # yield also lst IP of the range
    for port in ports_to_scan():
        for protocol in PROTOCOLS:
            yield protocol + '.'.join(current_ip_num)# + ':' + port


def connect(url):
    #ftp = FTP(url)
    ftp = FTP()
    ftp.connect(host=url, port=2121, timeout=1)
    print('*** wow ***')
    ftp.login()  # anonymous
    ftp.cwd('0')
    ftp.cwd('DCIM')
    ftp.cwd('Camera')
    ftp.timeout = 200  # following LIST command takes more time
    print('Getting file list...')
    #rows = ftp.retrlines('LIST')
    #rows = ftp.retrlines('NLST')
    rows = ftp.nlst()
    print(len(rows))
    print(f'Getting file list done {len(rows)} files.')
    for file_name in rows:
        print(f'Creating {TARGET_PATH + file_name}')
        if not file
        with open(TARGET_PATH + file_name, 'wb') as fp:
            ftp.retrbinary('RETR ' + file_name, fp.write)

    ftp.quit()

def main():
    while True:
        for url in urls_to_scan():
            print(url + ' ', end='')
            try:
                connect(url)

            except (socket.gaierror, TimeoutError) as e:
                # print('nothing here.')
                #traceback.print_exc()
                print(e)
        print('waiting before next round...')
        sleep(10)


if __name__ == "__main__":
    """ This is executed when run from the command line """
    main()


