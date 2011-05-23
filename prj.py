"""
Created on Fri Oct 22 15:59:38 2010

@author: ciccio
"""
import os
import leafinspect
from gph import graph
import log
from leaf.ptl import protocol
import copy


class project():
    def __init__(self, module, leafprot = ''):
        self.__modulename = module
        
        self.__metafolder = 'leaf_' + module        
        if not os.path.exists(self.__metafolder):
            os.mkdir(self.__metafolder)
        self.updateGraphs(leafprot)
            
            
            
    def updateGraphs(self, leafprot):
        if leafprot == '':
            leafprot = self.guessLeafProt()

        if leafprot != self.__leafprot:
            self.__graph.fromLeaf(leafprot)
            self.__leafprot=leafprot
        
        mods = self.seekforMods()

        altgraphs = self.generateAltGraphs()
        for gname in altgraphs.keys():
            if str(gname) != '[]':
                altfolder = self.__metafolder+'/'+str(gname).strip('[]').replace(', ','').replace('\'', '')
            else:
                altfolder = self.__metafolder.strip('[]').replace(', ','').replace('\'', '')
            if not os.path.exists(altfolder):
                os.mkdir(altfolder)
            self.__protocols[gname]=protocol(altgraphs[gname], mods, altfolder)
            self.__protocols[gname].getGraph().toPdf(altfolder+'/graph.dot')
            if not os.path.exists('wdir'):
                os.mkdir('wdir')
            if not os.path.exists('wdir/' + gname):
                os.mkdir('wdir/'+gname)
            self.__protocols[gname].setWdir('wdir/'+gname)

            
    def Name(self):
        return
                            
    def getNodeGroups(self):
        nodegroups = dict()
        for node in self.__graph.getNodes():
            gid = self.__graph.getAttrib(node, 'group')
            if gid:
                if gid in nodegroups.keys():
                    nodegroups[gid].append(node)
                else:
                    nodegroups[gid] = [node]
        return nodegroups
        

    def combinations(self, *iterables):
     if iterables:
       for head in iterables[0]:
         for remainder in self.combinations(*iterables[1:]):
           yield [head] + remainder
     else:
       yield []
       
    def altPathToName(self, path):
        return str(path)

    def generateAltGraphs(self):
        altpaths = self.generateAltPaths()
        groups = self.getNodeGroups().values()
        for path in altpaths:
            self.__altgraphs[self.altPathToName(path)] = copy.deepcopy(self.__graph)
            for group in groups:
                for node in group:
                    if node not in path:
                        self.__altgraphs[self.altPathToName(path)].delNode(node)
            log.send('Alternative protocol ' + self.altPathToName(path) +
                ' is: ' + str(self.__altgraphs[self.altPathToName(path)]), 2)
                        
        return self.__altgraphs

    def generateAltPaths(self):
        ngroups = self.getNodeGroups()
        temp = list()
        [temp.append(t) for t in self.combinations(*(ngroups.values()))]
        return temp
        
    def guessLeafProt(self):
        hislocals = self.getUserLocals()
        hisnames = hislocals.keys()
        
        if 'leafProtocol' in hisnames:
            leafprot = hislocals['leafProtocol']
            return leafprot
        else:
            raise NameError('I couldn''t find a variable called leafProtocol')


    def getUserLocals(self):
        import sys
        if self.__modulename in sys.modules.keys():
            self.__usermodule = sys.modules[self.__modulename]
        else:
            self.__usermodule = __import__(self.__modulename)
        if not self.__is_first_import:
            log.send('Reloading user module.', 2)
            reload(self.__usermodule)
        self.__is_first_import = False
        log.send('Your module is: ' + str(self.__usermodule), 2)
        hislocals = dict()

        for (name, value) in leafinspect.getmembers(self.__usermodule):
            hislocals[name] = value
        return hislocals
        
    def getModNames(self):
        names = self.__graph.getNodes()
        log.send('Mod names are: ' + str(names), 3)
        return names
                
        
    def seekforMods(self):
        log.send('Looking for mods in user module.', 3)
        hislocals=self.getUserLocals()

        mymods=dict()
        for modname in self.getModNames():
            if modname in hislocals.keys():
                mymods[modname] = hislocals[modname]
            else:
                raise NameError('I couldn''t bind '+modname+' to any of your defined objects.')

        resmods = dict()
        for mod in mymods.keys():
            resmods[mod]=mymods[mod]
                
        return resmods
        
    def update(self):
        self.updateGraphs(self.__leafprot)
        for prot in self.__protocols.values():
            prot.update(prot.getGraph(), self.seekforMods())
            
    def run(self):
        for protname in self.__protocols.keys():
            log.insertBreak()
            log.send('Running instance: ' + protname)
            self.__protocols[protname].run()

            
    def listAltProtocols(self):
        for protname in self.__protocols:
            log.send('- ' + protname, 0)            
            log.send('  ' + str(self.__protocols[protname].getGraph()))
            
    def getAltProtocol(self, protname):
        return self.__protocols[protname]
        
            
    def provide(self, what):
        if len(self.__protocols)==1:
            return self.__protocols[self.__protocols.keys()[0]].provide(what)
        else:
            resdict = dict()
            for protname in self.__protocols:
                resdict[protname] = self.__protocols[protname].provide(what)
            return resdict
            
    def getInputs(self, node):
        if len(self.__protocols)==1:
            return self.__protocols[self.__protocols.keys()[0]].getInputs(node)
        else:
            resdict = dict()
            for protname in self.__protocols:
                resdict[protname] = self.__protocols[protname].getInputs(node)
            return resdict
            
    def newFile(self, fname):
        return fname

    __protocols = dict()
    __graph = graph()
    __name = ''
    __metafolder = ''
    __leafprot = ''
    __altgraphs = dict()
    __is_first_import = True
