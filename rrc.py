
import os
from leaf import log
import cPickle
import leafinspect


class resource():
        
    def __init__(self, name, path):
        log.send('Initializing resource ' + name + ' with path ' + path, 3)
        self._name=name
        self._path = path
        if self.isDumped():
            self.load()
            
    def clear(self):
        self._contents = None
        self._fingerprint = None

            
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
            os.remove(self._path)
            
    def load(self):
        if self.isDumped():
            log.send(self.name() + ' is dumped in ' + self._path + ': loading it.')
            res = cPickle.load(open(self._path, 'r'))
            self.setDumpPath(res.getDumpPath())
            self.setIsFile(res.isFile())
            self.setValue(res.getValue())
            self.updateFingerprint()
        else:
            log.send(self.name() + ' is not dumped.', 2)
            
    def isDumped(self):        
        log.send('Checking ' + str(self) + ' in file: ' + self._path, 3)
        if os.path.exists(self._path):
            log.send('Available ' + str(self), 3)
            return True
        log.send('Unavailable: ' + str(self), 3)
        return False
        
    def dump(self):
        if not self._dodump:        
            log.send('Dumping is switched off, so skipping.', 2)
            return
            
        log.send('Dumping resource: ' + self._name)
        log.send('object: ' + str(self), 3)
        log.send('value: ' + str(self._contents), 3)
        log.send('fingerprint: ' + str(self._fingerprint), 3)

        log.send('Dumping to file: ' + self._path, 2)
        cPickle.dump(self, open(self._path, 'w'))
        
    def isAvailable(self):
        return self._contents != None
        
    def setValue(self, v):
        log.send('New value is: ' + str(v), 3)
        self._contents = v
        
    def getValue(self):
        return self._contents
        
    def setIsFile(self, isit = True):
        log.send('isFile value: ' + str(isit), 3)
        self._isfile = isit

    def isFile(self):
        return self._isfile
        
    def setDumpPath(self, path):
        log.send('Updating path: ' + str(path),2)
        self._path = path
        
    def getDumpPath(self):
        return self._path
        
    def changed(self):

        return self._fingerprint != self._makeFingerprint(self._contents)
        
    def _makeFingerprint(self, obj):
        try:
            leafinspect.getsource(obj)
            log.send('Source got.', 3)
            return leafinspect.getsource(obj)
        except Exception:            
            log.send('No source: passing object', 3)
            return obj
            
    def getFingerprint(self):
        return self._fingerprint
    
    def updateFingerprint(self):
        self._fingerprint = self._makeFingerprint(self._contents)
        log.send('Fingerprint is: ' + str(self._fingerprint), 3)


    def name(self):
        return self._name

    def setDump(self, d):
        self._dodump = d

    _name = ''    
    _contents = None
    _dodump = True
    _fingerprint = None
    _path = None
    _isfile = False
    

        
