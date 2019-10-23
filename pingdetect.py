from pythonping import ping
import logging
from multiprocessing import Process, Queue
from time import sleep

# Khai bao thong so cho viec ghi log
logging.basicConfig(filename='result.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logging.disable(logging.DEBUG)

# Global Var dung de dung an toan cac tien trinh
safe_stop = False


def produce_log(name, ip, queue):
    global safe_stop

    while True:
        if safe_stop is True:
            break
        else:
            if ping(ip, count=1).success():
                queue.put('{0} ({1}) is UP'.format(name, ip))
            else:
                queue.put('{0} ({1}) is DOWN'.format(name, ip))
        sleep(1)


def print_and_log(queue):
    global safe_stop

    while True:
        if safe_stop is True:
            break
        else:
            while not queue.empty():
                log = queue.get()
                print(log)
                logging.info(log)

        sleep(1)


def host_list():
    import csv
    with open('hosts.csv') as hosts_file:
        csv_reader = csv.reader(hosts_file)

        name = []
        ip = []

        for row in csv_reader:
            name.append(row[0])
            ip.append(row[1])

        return zip(name, ip)


def main():
    global safe_stop
    procs = []
    logs = Queue()

    for name, ip in host_list():
        proc = Process(target=produce_log, args=(name, ip, logs,))
        procs.append(proc)
        proc.start()

    log_writer = Process(target=print_and_log, args=(logs,))
    log_writer.start()

    while True:
        if safe_stop is True:
            for proc in procs:
                proc.join()
            log_writer.join()
            print('Da thoat chuong trinh.')
            break
        else:
            sleep(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        safe_stop = True
