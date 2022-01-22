import UtilityModules
import BuiltInModules

"""
In order for the app to be able to handle custom modules for displaying, the code is structured as such;

Each module is started on it's own thread, allowing them to do whatever
From there, the modules can request screen time, allowing them to display bitmaps until they relinquish control
By default, the built-in keystroke module has control
There are utility modules that can be used to construct, modify, and display bitmaps, 
along with a multithreading module for simple working
"""

Posting = UtilityModules.Packet_posting()
Bitmapping = UtilityModules.Bitmaps()
Worker = UtilityModules.Working()
Modules = [UtilityModules.Packet_posting,BuiltInModules.Keystroke_logging,BuiltInModules.Afk]

def Start():
    B = UtilityModules.InstansiateCollection()
    for e in Modules:
        E = "%s.1" % e.__name__
        try:
            B.ClassInstance["E"]
            raise IndexError("Module %s tried to be started multiple times" % E)
        except:
            B.ClassInstance[E] = e(B)
            Worker.Work(B.ClassInstance[E].Start)
    B.StartCollection()

input("a")
Start()



