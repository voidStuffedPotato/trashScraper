#  TODO: improve row selection in common.containers
from common import netfile, mutex, event, driverlogic, containers
from queue import Queue
import json
import time
import threading


def read_from_file(filenames, mutexnames, stdout_mutex, queue):
    flag = False
    threads_done = 0
    occasions = []
    for i in range(len(filenames)):
        occasions.append(0)
    mutexes = [mutex.NamedMutex(name) for name in mutexnames]
    while True:
        for (filename, _mutex, pos) in zip(filenames, mutexes, range(len(filenames))):
            _mutex.acquire()
            f = netfile.NetFile(filename, 'r')
            raw_data = f.read()
            f.close()
            _mutex.release()
            if raw_data == '':
                data = []
            else:
                data = json.loads(raw_data)
            tmp = len(data)
            with stdout_mutex:
                print('Read {0} new objects in {1}'.format(tmp - occasions[pos], filename))
            occasions[pos] = tmp
            time.sleep(0.25)
        if flag:
            break
        for i in range(3):
            if not queue.empty():
                threads_done += queue.get()
            time.sleep(0.1)
        if threads_done == 3:
            flag = True
    with stdout_mutex:
        print('Read {0} entries'.format(sum(occasions)))


def dump_to_file(row_dicts, filename, mutexname, stdout_mutex, queue):
    g_mutex = mutex.NamedMutex(mutexname)
    for row_dict in row_dicts:
        g_mutex.acquire()
        f = netfile.NetFile(filename, 'r')
        raw_data = f.read()
        if raw_data == '':
            data = []
        else:
            data = json.loads(raw_data)
        f.close()
        f = netfile.NetFile(filename, 'w')
        # Дозапись в файл
        flag = True
        i = 0
        while i < len(data):
            if row_dict['id'] == data[i]['id']:
                data[i]['data'] = list(set(data[i]['data']+row_dict['data']))
                flag = False
                break
            i += 1
        if flag:
            data.append(row_dict)
        f.write(json.dumps(data, indent=4))
        f.close()
        g_mutex.release()
        time.sleep(0.1)
    queue.put(1)
    with stdout_mutex:
        print("Finished dumping into {}".format(filename))
    event.NamedEventO("StartSDB").set()


def launch():
    driver = driverlogic.initialize()
    driver.get('http://vk.com/feed')
    feed_rows = driverlogic.get_rows(driver)
    hrefs = [containers.HrefRow(feed_row).dictionary for feed_row in feed_rows]
    texts = [containers.TextRow(feed_row).dictionary for feed_row in feed_rows]
    images = [containers.ImgRow(feed_row).dictionary for feed_row in feed_rows]
    driver.close()
    dicts = [hrefs, texts, images]

    mutexes = ('hrefs_mutex', 'texts_mutex', 'imgs_mutex')
    path = 'D:\\OneDrive\\WorkBox\\Python\\SeleniumProject\\JSON\\'
    filenames = (path + 'hrefs.json', path + 'texts.json', path + 'images.json')

    stdout_mutex = threading.Lock()
    queue = Queue()

    args_list = [(rows, filename, g_mutex, stdout_mutex, queue) for (rows, filename, g_mutex) in
                 zip(dicts, filenames, mutexes)]

    write_threads = [threading.Thread(target=dump_to_file, args=args) for args in args_list]
    read_thread = threading.Thread(target=read_from_file, args=(filenames, mutexes, stdout_mutex, queue))
    threads = write_threads + [read_thread]

    print('\n' + '-' * 50 + '\n')

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    print('\n' + '-' * 50 + '\n')


if __name__ == '__main__':
    launch()
