from common import mutex, event, containers
import database_io
import win32event
import win32service
import win32serviceutil


def get_data(file_mutex, filename):
    file_mutex.acquire()
    with open(filename, 'r') as f:
        raw_data = f.read()
    file_mutex.release()
    return raw_data


class DatabaseService(win32serviceutil.ServiceFramework):
    _svc_name_ = "Event Database Reader Service"
    _svc_display_name_ = "Event Database Reader Service"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        path = 'D:\\OneDrive\\WorkBox\\Python\\SeleniumProjectWithRAM\\JSON\\'
        filenames = (path + 'hrefs.json', path + 'texts.json', path + 'images.json')
        mutex_names = ('hrefs_mutex', 'texts_mutex', 'imgs_mutex')
        files = [containers.File(fn, mutex.NamedMutex(name=mtx)) for (fn, mtx) in zip(filenames, mutex_names)]
        stop = None
        start_reading_event = event.NamedEvent("StartSDB")
        while stop != win32event.WAIT_OBJECT_0:
            stop = win32event.WaitForSingleObject(self.hWaitStop, 5000)
            start_reading_event.waitOne(5000)
            if start_reading_event.signaled:
                database_io.write(*files)
                start_reading_event.clear()


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(DatabaseService)
