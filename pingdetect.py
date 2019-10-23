from pythonping import ping
import logging
from multiprocessing import Process, Queue
from time import sleep

# Khai bao thong so cho viec ghi log
logging.basicConfig(filename='result.log',
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
# logging.disable(logging.DEBUG)

# Khai bao log Handler de in ket qua ra ngoai man hinh
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)


def check_safestop_queue(queue):
    if not queue.empty():
        if queue.get():
            return True
    return False


def ping_job(name, ip, queue, safe_stop):
    prev_status = None

    while True:
        if check_safestop_queue(safe_stop) is True:
            print('Da hoan tat kiem tra {} ({}))'.format(name, ip))
            break
        else:
            status = ping(ip, count=1).success()
            if status != prev_status:
                queue.put('{} ({}) is {}'.format(
                    name, ip, 'UP' if status is True else 'DOWN'))
                prev_status = status

        sleep(1)


def print_and_log(queue, safe_stop):
    while True:
        if check_safestop_queue(safe_stop) is True:
            break
        else:
            while not queue.empty():
                log = queue.get()
                logging.info(log)

        sleep(0.1)


def host_list():
    import csv
    with open('hosts.csv') as hosts_file:
        csv_reader = csv.reader(hosts_file)

        hosts = []

        for row in csv_reader:
            hosts.append(tuple(row))

        return hosts


def main():
    procs = []
    logs = Queue()
    safe_stop = Queue()

    for name, ip in host_list():
        proc = Process(target=ping_job, args=(name, ip, logs, safe_stop))
        procs.append(proc)
        proc.start()

    log_writer = Process(target=print_and_log, args=(
        logs,
        safe_stop,
    ))
    procs.append(log_writer)
    log_writer.start()

    while True:
        stop = bool(input('Ky tu bat ky de ngung chuong trinh\n' or ''))
        if stop:
            break
        sleep(1)

    for i in range(len(procs)):
        safe_stop.put(True)

    logging.info('Dang cho cac tien trinh con hoan tat ...')

    for proc in procs:
        proc.join()
    print('Da thoat chuong trinh.')


if __name__ == '__main__':
    main()
