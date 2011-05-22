
import os
from leaf import log
import cPickle
import leafinspect



#class resfile(str):
#    def __init__(self, s):
#        if os.path.exists(s):
#            self.__lastmodified = os.path.getmtime(s)
#        
#    def hasChanged(self):
#        if not os.path.exists(self) and self.__lastmodified==-1:
#            #does not and did not exist            
#            return False
#        elif not os.path.exists(self):
#            #does not but did exist
#            return True
#        else:
#            #does and did exist
#            return self.__lastmodified != os.path.getmtime(self)
#            
#    def update(self):
#        if not self.hasChanged():
#            return
#        else:
#            if os.path.exists(self):
#                self.__lastmodified = os.path.getmtime(self)
#            else:
#                self.__lastmodified = -1
#                
#    def changeTime(self):
#        return self.__lastmodified
#    
#    __lastmodified = -1
#    __brandnew = True


class resource():
        
    def __init__(self, name, path):
        log.send('Initializing resource ' + name + ' with path ' + path, 3)
        self.__name=name
        self.__path = path
        if self.isDumped():
            self.load()
            
    def clear(self):
        self.__contents = None
        self.__fingerprint = None

            
    def name(self):
        return str(self)
        
    def update(self):
        if self.changed():
            log.send(self.name() + ' has changed: updating.')
            self.updateFingerprint()
            self.dump()
        else:
            log.send(self.name() + ' has not changed.', 2)

    def clearDump(self):
        if self.isDumped():
            os.remove(self.__path)
            
    def load(self):
        if self.isDumped():
            log.send(self.name() + ' is dumped in ' + self.__path + ': loading it.')
            res = cPickle.load(open(self.__path, 'r'))
            self.setDumpPath(res.getDumpPath())
            self.setIsFile(res.isFile())
            self.setValue(res.getValue())
            self.updateFingerprint()
        else:
            log.send(self.name() + ' is not dumped.', 2)
            
    def isDumped(self):        
        log.send('Checking ' + str(self) + ' in file: ' + self.__path, 3)
        if os.path.exists(self.__path):
            log.send('Available ' + str(self), 3)
            return True
        log.send('Unavailable: ' + str(self), 3)
        return False
        
    def dump(self):
        if not self.__dodump:        
            log.send('Dumping is switched off, so skipping.', 2)
            return
            
        log.send('Dumping resource: ' + str(self))
        log.send('with value: ' + str(self.__contents), 3)
        log.send('and fingerprint: ' + str(self.__fingerprint), 3)

        log.send('Dumping to file: ' + self.__path, 2)
        cPickle.dump(self, open(self.__path, 'w'))
        
    def isAvailable(self):
        return self.__contents != None
        
    def setValue(self, v):
        log.send('New value is: ' + str(v), 3)
        self.__contents = v
        
    def getValue(self):
        return self.__contents
        
    def setIsFile(self, isit = True):
        log.send('isFile value: ' + str(isit), 3)
        self.__isfile = isit

    def isFile(self):
        return self.__isfile
        
    def setDumpPath(self, path):
        log.send('Updating path: ' + str(path),2)
        self.__path = path
        
    def getDumpPath(self):
        return self.__path
        
    def changed(self):
        return self.__fingerprint != self.__makeFingerprint(self.__contents)
        
    def __makeFingerprint(self, obj):
        try:
            leafinspect.getsource(obj)
            log.send('Source got.', 3)
            return leafinspect.getsource(obj)
        except Exception:            
            log.send('No source: passing object', 3)
            return obj
            
    def getFingerprint(self):
        return self.__fingerprint
    
    def updateFingerprint(self):
        self.__fingerprint = self.__makeFingerprint(self.__contents)
        log.send('Fingerprint is: ' + str(self.__fingerprint), 3)


    def name(self):
        return self.__name

    __name = ''    
    __contents = None
    __dodump = False
    __fingerprint = None
    __path = None
    __isfile = False
    

        
