import clr
from System.Threading import Mutex
from System.Security.AccessControl import MutexAccessRule, MutexRights, AccessControlType, MutexSecurity
from System.Security.Principal import SecurityIdentifier, WellKnownSidType


class NamedMutex():
    def __init__(self, name):
        mutexId = "Global\\{0}".format(name)
        allowEveryoneRule = MutexAccessRule(SecurityIdentifier(WellKnownSidType.WorldSid,None), MutexRights.FullControl, AccessControlType.Allow)
        securitySettings = MutexSecurity()
        securitySettings.AddAccessRule(allowEveryoneRule)
        self.mutex = Mutex(False, mutexId)
        self.mutex.SetAccessControl(securitySettings)

    def acquire(self):
        self.hashandle = self.mutex.WaitOne(5000, False)
        if not self.hashandle:
            raise Exception("error in WaitOne")

    def release(self):
        if self.hashandle: self.mutex.ReleaseMutex()

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()
