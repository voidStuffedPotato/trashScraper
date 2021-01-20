import clr
from System.Reflection import Assembly
from System.Threading import EventWaitHandle, EventResetMode
from System.Security.AccessControl import MutexAccessRule, MutexRights, AccessControlType, EventWaitHandleSecurity, EventWaitHandleRights, EventWaitHandleAccessRule
from System.Security.Principal import SecurityIdentifier, WellKnownSidType
from System import Environment


class NamedEvent:

    def __init__(self, name):
        self.eventId = "Global\\{0}".format(name)
        self.signaled = False
        user = Environment.UserDomainName + "\\" + Environment.UserName
        # rule = EventWaitHandleAccessRule(user,
        #         EventWaitHandleRights.ReadPermissions |
        #           EventWaitHandleRights.ChangePermissions,
        #         AccessControlType.Allow)
        self.rule = EventWaitHandleAccessRule(SecurityIdentifier(WellKnownSidType.WorldSid,None), EventWaitHandleRights.FullControl, AccessControlType.Allow)
        securitySettings = EventWaitHandleSecurity()
        securitySettings.AddAccessRule(self.rule)
        self.handle = EventWaitHandle(False, EventResetMode.ManualReset, self.eventId)
        self.handle.SetAccessControl(securitySettings)

    def is_set(self): return self.signaled

    def set(self):
        if self.signaled:
            return
        self.handle.Set()
        self.signaled = True

    def clear(self):
        self.handle.Reset()
        self.signaled = False

    def waitOne(self, time):
        self.signaled = self.handle.WaitOne(time)

    __del__ = clear


class NamedEventO:

    def __init__(self, name):
        self.eventId = "Global\\{0}".format(name)
        self.signaled = False
        self.rule = EventWaitHandleAccessRule(SecurityIdentifier(WellKnownSidType.WorldSid,None), EventWaitHandleRights.FullControl, AccessControlType.Allow)
        securitySettings = EventWaitHandleSecurity()
        securitySettings.AddAccessRule(self.rule)
        self.handle = EventWaitHandle.OpenExisting(self.eventId, EventWaitHandleRights.FullControl)

    def is_set(self): return self.signaled

    def set(self):
        if self.signaled:
            return
        self.handle.Set()
        self.signaled = True

    def clear(self):
        self.handle.Reset()
        self.signaled = False

    def waitOne(self, time):
        self.signaled = self.handle.WaitOne(time)


    # __del__ = clear
