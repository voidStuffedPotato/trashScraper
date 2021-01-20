import json
import threading

from common import netfile, mutex, event, containers
from playhouse.postgres_ext import *


connection = PostgresqlExtDatabase('testdb', user='postgres')


class BaseModel(Model):
    id = CharField(primary_key=True)
    data = JSONField()



class imgs_table(BaseModel):
    class Meta:
        database = connection
        db_table = 'imgs_table'


class hrefs_table(BaseModel):
    class Meta:
        database = connection
        db_table = 'hrefs_table'


class texts_table(BaseModel):
    class Meta:
        database = connection
        db_table = 'texts_table'


class DBThread(threading.Thread):
    def __init__(self, table, file, db_mutex):
        threading.Thread.__init__(self, target=self.target)
        self._file = file
        self.db_mutex = db_mutex
        self.table = table

    def target(self):
        self._file.mutex.acquire()
        f = netfile.NetFile(self._file.filename, 'r')
        raw_data = f.read()
        f.close()
        self._file.mutex.release()
        data = json.loads(raw_data)
        for el in data:
            with self.db_mutex:
                query = (self.table.insert(id=el['id'], data=json.dumps(el['data']))
                         .on_conflict(conflict_target=[self.table.id],
                                      update={self.table.data: EXCLUDED.data}))
                query.execute()


def write(f_h, f_t, f_i):
    hrefs_table.create_table()
    texts_table.create_table()
    imgs_table.create_table()

    mtx = threading.Lock()
    h_thr = DBThread(hrefs_table, f_h, mtx)
    t_thr = DBThread(texts_table, f_t, mtx)
    i_thr = DBThread(imgs_table, f_i, mtx)
    writers = [h_thr, t_thr, i_thr]
    for thread in writers:
        thread.start()
    for thread in writers:
        thread.join()

if __name__ == '__main__':
    path = 'D:\\OneDrive\\WorkBox\\Python\\SeleniumProject\\JSON\\'
    filenames = (path + 'hrefs.json', path + 'texts.json', path + 'images.json')
    mutex_names = ('hrefs_mutex', 'texts_mutex', 'imgs_mutex')
    files = [containers.File(fn, mutex.NamedMutex(name=mtx)) for (fn, mtx) in zip(filenames, mutex_names)]
    stop = None
    start_reading_event = event.NamedEvent("StartSDB")
    while True:
        start_reading_event.waitOne(5000)
        if start_reading_event.signaled:
            write(*files)
            start_reading_event.clear()
