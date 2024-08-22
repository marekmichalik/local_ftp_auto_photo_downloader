import socket
import os
import datetime
import traceback
from time import sleep
from ftplib import FTP, error_perm

IP_RANGE_START = '192.168.1.84'
IP_RANGE_END =   '192.168.1.84'

#PORTS_TO_SCAN = [2121, 2122]
PORTS_TO_SCAN = [2121, ]

TARGET_PATH_PREFIX = 'U:/fotky/'  # should end with /

VERBOSE = 0  # 1 for more output
CONVERT_FILES = 0  # not implemented, idea is to convert heic/heif and similar files to jpg for convenience

def ports_to_scan():
    for each in PORTS_TO_SCAN:
        yield each


def urls_to_scan():
    """

    :return: string: Generate every combination of protocol, ip address and port
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

            yield '.'.join(current_ip_num), port
        current_ip_num = inc_ip(current_ip_num)

    # yield also last IP of the range
    for port in ports_to_scan():
        yield '.'.join(current_ip_num), port


def get_target_path(file_name):

    today = datetime.date.today()
    this_month =  today.strftime("%Y%m")
    first = today.replace(day=1)
    last_month = first - datetime.timedelta(days=1)
    last_month =  last_month.strftime("%Y%m")

    #remove img prefix
    if file_name.lower().startswith('img'):
        file_name = file_name[3:]

    if file_name.lower().startswith('vid'):
        file_name = file_name[3:]

    file_name = file_name.replace('-', '')
    file_name = file_name.replace('_', '')  # huawei format

    #we will process only files for this and last month
    if not file_name.startswith(this_month) and not file_name.startswith(last_month):
        return None

    year = file_name[:4]
    month = file_name[4:6]

    # custom path generator
    #path = TARGET_PATH_PREFIX + year + month + '/'

    # something like: U:\fotky\2024\_raw\04_april2024
    months = ['januar', 'februar',  'marec', 'april', 'maj', 'jun', 'jul', 'august', 'september', 'oktober', 'november', 'december']
    try:
        path = f'{TARGET_PATH_PREFIX}{year}/_raw/{month}_{months[int(month)-1]}{year}/'
    except (ValueError, IndexError):  # can't detect month and year
        return None
    return path


def connect(url, port):
    ftp = FTP()
    ftp.connect(host=url, port=port, timeout=0.5)  # short timeout to fast pass through non existing ftp IPs
    try:
        print(f'Successfully connected.')
        ftp.login()  # anonymous
        print('CWD to camera dir...')
        try:
            ftp.cwd('0')
        except error_perm:
            pass
        ftp.cwd('DCIM')
        ftp.cwd('Camera')
        ftp.timeout = 3600  # following LIST/NLST command takes more time, also RETR
        print('Getting file list...')
        rows = ftp.nlst()
        print(f'Getting file list done {len(rows)} files, looking for new files...')
        for file_name in rows:
            target_file_path = get_target_path(file_name)
            if target_file_path:
                # make whole path if needed
                os.makedirs(target_file_path, mode=0o777, exist_ok=True)

                if not os.path.isfile(target_file_path + file_name):
                    try:
                        print(f'File copy to {target_file_path + file_name} ...')
                        # copy file from ftp as filename.ext.part
                        with open(target_file_path + file_name + '.part', 'wb') as fp:
                            ftp.retrbinary('RETR ' + file_name, fp.write)

                        # remove .part from file name only after copying is done
                        os.rename(target_file_path + file_name + '.part', target_file_path + file_name)
                    except OSError:
                        print(f'OSError occured on file {target_file_path + file_name}')
                else:
                    if VERBOSE:
                        print(f'File {target_file_path + file_name} already exists, skipping.')
            else:
                if VERBOSE:
                    print(f'File {file_name} too old or unrecognised, skipping.')
        print()
    finally:
        ftp.quit()

def main():

    for url, port in urls_to_scan():
        print(f'{url}:{port} ', end='')
        try:
            connect(url, port)

        except (socket.gaierror, TimeoutError) as e:
            # print('nothing here.')
            #traceback.print_exc()
            print(e)


if __name__ == "__main__":
    """ This is executed when run from the command line """
    while True:
        try:
            main()
        except Exception as e:
            traceback.print_exc()
            #print(e)
        print('waiting before next round...')
        sleep(10)