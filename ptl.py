"""
Created on Fri Oct 22 15:59:38 2010

@author: ciccio
"""

import os
import cPickle
import leafinspect
from leaf.log import send as dbgstr
from leaf.rrc import resource
import copy
        
    

class protocol():
    def __init__(self, graph, mods, folder):
        dbgstr('Initializing protocol with root: ' + folder)
        self._metafolder = folder
        self._rootdir = os.getcwd()
        self._resmap = dict()

        self._graphres = resource('graph', folder+'/graph.grp')
        self._graphres.setValue(graph)
        if self._graphres.changed():
            self.manageGraphChange()
        self._graphres.update()

        for res in self.getResNames():
            newres = resource(res, folder+'/'+res+'.res')
            #print res, newres
            self.addResource(res, newres)
        
        for mod in self.getNodeNames():
            newres = resource(mod, folder+'/'+mod+'.mod')
            newres.setDump(True)
            self._modules[mod] = newres

        self.updateModules(mods)


    def updateModules(self, mods):
        for modname in mods:
            if modname in self._modules.keys():
                self._modules[modname].setValue(mods[modname])
                if self._modules[modname].changed():
                    self.untrustNode(self._modules[modname].name())
                self._modules[modname].update()
            else:
                dbgstr('New module: ' + modname)
                self._modules[modname] = resource(modname,
                    self._metafolder+'/'+modname+'.dmp' )
                self._modules[modname].setValue(mods[modname])
                self._modules[modname].update()                
                

    def manageGraphChange(self):
        dbgstr('Graph changed or not dumped, but I still can''t handle that, sorry.')
    
    def show(self):
        dbgstr('Protocol:',0)
        dbgstr(self._leafprot, 0)
        dbgstr('Node attributes:', 0)
        for node in self.getNodeNames():
            ostr = node +': '
            for attrib in self._nodeattribs.keys():
                if attrib[0]==node:
                    ostr += str(attrib[1])+'='+str(self._nodeattribs[attrib])+', '
            dbgstr(ostr[0:-2], 0)
        
    def clean(self):
        for res in self.getResNames():
            self.clearDump(res)

        if os.path.exists(self._metafolder):
            if os.listdir(self._metafolder) == []:
                os.rmdir(self._metafolder)
            
    def modSummary(self):
        pass
        #for mod in self.getNodeNames():
        #    dbgstr(mod + ', changed = ' + self.checkModChanged(modname,))
            
    def getContents(self, mod):
        try:
            leafinspect.getsource(mod)
            value = leafinspect.getsource(mod)
        except Exception:            
            value = mod
        return value
        
    def getInputs(self, mod):
        innodes = self.getInNodes(mod)
        ids = [self.getGraph().getAttrib(_node, 'id') for _node in innodes]
        nodeparams = [copy.deepcopy(self.getResource(innode).getValue()) for innode in innodes]
        nodeparams=[one for (one,two) in sorted(zip(nodeparams, ids), key = lambda x:x[1])]      
        return tuple(nodeparams)
        

        
    #def checkModChanged(self, modname, mod):                
        #return mod.checkChanged(), mod.getFingerprint()
        
#        isnew = False
#        if not self._modules.has_key(modname):
#            self._modules[modname].setValue(None)
#            isnew = True
#            haschanged = True
#            try:
#                leafinspect.getsource(mod)
#                fprint = leafinspect.getsource(mod)
#            except Exception:
#                dbgstr('No source code for \''+modname+'\': will store value.', 2)
#                fprint = mod
#                        
#        elif type(mod) == File:
#            haschanged = mod.hasChanged()
#            fprint = mod
#
#        else:
#            try:
#                haschanged = self._modules[modname].getFingerprint() != leafinspect.getsource(mod)
#                fprint = leafinspect.getsource(mod.getValue())
#            except Exception:
#                dbgstr('No source code for \''+modname+'\': will store value.', 2)
#                haschanged = self._modules[modname].get() != mod
#                fprint = mod
#            
#        if isnew: dbgstr('New module: ' + modname, 0)
#        elif haschanged:
#            dbgstr('Changed module: ' + modname, 0)
#        
#        return haschanged, fprint

    def setMod(self, modname, mod):
        haschanged = self._modules[modname].changed()
        if haschanged:
            if type(mod) == File:
                mod.update()
            self._modules[modname].setValue(mod.getValue())
            self._modules[modname].updateFingerprint()
            self.untrustNode(modname)
            dependents = self.getOutNodesRecursive(modname)
            if dependents != []:
                dbgstr('These nodes are dependent: '+str(dependents), 0)
            #for dep in dependents:
            #    self.clearNode(dep)

    def setMods(self, mods):
        self._modules = mods
        for modname in mods.keys():
            self.setMod(modname, mods[modname])
        
        dbgstr('Modules are: ' + str(self._modules), 3)
        #dbgstr('with source: ' + str(self._modcontents), 3)

        
    def update(self, graph, mods):
        dbgstr('New graph is: ' + str(graph), 3)
        dbgstr('New mods are: ' + str(mods), 3)
        self._graphres.setValue(graph)
        self._graphres.update()
        self.updateModules(mods)
        
        
    def dumpResource(self, res):
        self.getResource(res).dump()
        
    def newResource(self, resname, resval):
        dbgstr('Updating resource: ' + resname, 2)
        dbgstr('with contents: ' + str(resval), 3)
        self.getResource(resname).setValue(resval)
        self.getResource(resname).updateFingerprint()
        self.dumpResource(resname)
        
    def clearNode(self, nodename):
        if self.isLeaf(nodename):
            self.clearResource(nodename)
        for node in self.getOutNodes(nodename):
            self.clearResource(node)

    def untrustNode(self, nodename):
        if self.isLeaf(nodename):
            self.clearResource(nodename)
                
        dependents = self.getOutNodesRecursive(nodename)
        for res in self.getResNames():
            if(res in dependents):
                self.clearResource(res)

    def clearResource(self, resname):
        if self.isDumped(resname):
            dbgstr('Clearing dump: ' + str(resname), 2)
            self.getResource(resname).clearDump()
        if self.isAvailable(resname):
            dbgstr('Clearing resource: ' + str(resname))
            self._resmap[resname].clear()
            
    def setWdir(self, wdir):
        self.wdir = wdir
            
        
    def isAvailable(self, resname):
        dbgstr('Checking resource: ' + str(resname), 3)
        if self.getResource(resname).isAvailable():
           dbgstr('Available: ' + str(resname), 3)
           return True
        dbgstr('Unavailable: ' + str(resname), 3)
        return False        

    def provide(self, resname):
        return self.provideResource(resname).getValue()
                
    def getResource(self, resname):
        dbgstr('Getting resource: ' + str(resname), 3)        
        return self._resmap[resname]
        
    def addResource(self, name, res):
        self._resmap[name]=res
            
    def provideResource(self, resname):
        dbgstr('Providing resource: ' + str(resname), 2)
        if self.isAvailable(resname):
            dbgstr('Found in RAM: ' + str(resname))
            dbgstr('Resource content is:\n' + str(self.getResource(resname)) ,4)
            return self.getResource(resname)
        elif self.isDumped(resname):
            dbgstr('Found on disk: ' + str(resname))
            self.addResource(resname, self.loadResource(resname))
            dbgstr('Resource content is:\n' + str(self.getResource(resname)), 4)
            return self._resmap[-1]
        else:
            dbgstr('Resource not found. I need to run first: ' + str(resname))
            self.runNode(resname)
            return self.getResource(resname)

    def getNodeNames(self):
        return self.getGraph().getNodes()
        
    def isResFile(self, res):
        isit = res.isFile()
        if isit : dbgstr(str(res) + ' is a file.')
        return isit

    def runNode(self, node):
        dbgstr('Running node: ' + str(node))
        
        nodeparams = list()        
        input_nodes = self.getInNodes(node)
        for item in input_nodes:
            thisnode_inputs = list()
            neededres = item
            dbgstr('Retreiving resource: ' + neededres)
            this_params = self.provideResource(neededres)
            if type(this_params.getValue())==list:
                dbgstr('Resource type is: list.', 2)
                for this_param in this_params.getValue():
                    thisnode_inputs.append(this_param)
            elif self.isResFile(this_params):
                dbgstr('Resource type is: file.', 2)
                thisnode_inputs.append(this_params.getValue())
            else:
                dbgstr('Resource type is: ' + str(type(this_params.getValue())), 2)
                thisnode_inputs.append(this_params.getValue())
            if len(thisnode_inputs)==1:
                nodeparams.append(thisnode_inputs[0])
            else:
                nodeparams.append(thisnode_inputs)
        
        #sorting basing on ids        
        ids = [self.getGraph().getAttrib(_node, 'id') for _node in input_nodes]
        nodeparams=[one for (one,two) in sorted(zip(nodeparams, ids), key = lambda x:x[1])]

        dbgstr('Ready to run: ' + node, 2)
        dbgstr('through ' + str(self.getModule(node).getValue()), 2)
        dbgstr('on input:\n\t' + str(nodeparams), 3)
        
        return self.callMod(node, nodeparams)
        
    def getModule(self, name):
        return self._modules[name]
        
    def callMod(self, node, nodeparams):
        
        if not self._checkIsFunction(self._modules[node].getValue()):
            dbgstr('Node '+node+' is not a function: passing itself.', 2)            
            newres = self._modules[node].getValue()
            self._processRawRes(node, newres)
            
        elif len(nodeparams)==0:
            dbgstr('No input for: ' + str(node), 1)
            dbgstr('Running node: ' + node)
            newres = apply(self._modules[node].getValue(), [])
            dbgstr('Done.')
            dbgstr('Produced resources:\n\t' + str(newres), 3)
            self._processRawRes(node, newres)
    
        elif self.getGraph().getAttrib(node, 'hash'):
            dbgstr('Inputs are joined.', 2)
            dbgstr('Running node: ' + node)
            newres = apply(self._modules[node].getValue(), nodeparams)
            dbgstr('Done.', 0)
            dbgstr('Produced resources:\n\t' + str(newres), 3)
            self._processRawRes(node, newres)
            
        else:
            dbgstr('Inputs are hashed.', 2)
            for nodeparam in nodeparams:
                dbgstr('Running node: ' + node)
                newres = self._modules[node].getValue()(nodeparam)
                dbgstr('Done.')
                dbgstr('Produced resources:\n\t' + str(newres), 3)
                self._processRawRes(node, newres)
            
        return newres
        
    def _checkIsFunction(self, x):
        #return hasattr(self._modules[node].getValue(), '_call_'):
        return type(lambda y:y)==type(x)
        
    def placeFileRes(self, fname):
        os.system('mv -r"'+ fname + '" ' + self._metafolder)
            
    def buildResName(self, inode, onode, rawres):
        if onode == None:
            return inode
        else:
            return inode
        

    def isFileMod(self, node):
        flags = self.getGraph().getAttrib(node, 'LEAF_FLAGS')
        if flags == None:
            return False
        return 'f' in flags or 'F' in flags
        
    def updateFilePath(self, path):
        parts = os.path.split(path)
        if parts[0] != self._metafolder:
            return self._metafolder + '/' + parts[1]
        return path

    def _processRawRes(self, node, rawres):
        

                        
#        elif type(rawres)==tuple:        
#            dbgstr('Raw resources are packed in a tuple.')
#            
#            if len(rawres != len(self.getGraph()[node])):
#                raise NameError('When a module returns a tuple, it''s length must be equal to the number of the module''s outputs.')
#                
#            for idx, outnode in enumerate(self.getGraph()[node]):
#                newresname = self.buildResName(node, outnode, rawres)                
#                dbgstr('Requesting add resource: ' + str(newresname))
#                if self.isFileMod(node):
#                    self.placeFileRes(rawres)
#                    self.newResource(newresname, self.updateFilePath(rawres[idx]))
#                else:
#                    self.newResource(newresname, rawres[idx])
#                
#        else:

        if self.isFileMod(node):
            import pdb; pdb.set_trace()
            if type(rawres)==tuple or type(rawres)==list:
                for rawresi in rawres:
                    newresname = self.buildResName(node, None, rawresi)
                    dbgstr('Requesting add resource: ' + node, 2)
                    self.placeFileRes(rawresi)
                    self.newResource(newresname, self.updateFilePath(rawresi))
            else:
                newresname = self.buildResName(node, None, rawres)
                dbgstr('Requesting add resource: ' + node, 2)
                self.placeFileRes(rawres)
                self.newResource(newresname, self.updateFilePath(rawres))
        else:
            newresname = self.buildResName(node, None, rawres)
            dbgstr('Requesting add resource: ' + node, 2)
            self.newResource(newresname, rawres)
                
                
                
    def setDumpFolder(self,f):
        self._metafolder=f

    def run(self):
        #dbgstr('Running project.', 0)
        res = dict()
        allok = True
        for leaf in self.getLeaves():
            resname = leaf
            if not self.isAvailable(resname)and not self.isDumped(resname):
                allok = False
            res[leaf]=self.provide(resname)
        if allok:
            dbgstr('Nothing to be done. Zzz...', 0)
        else:
            dbgstr('Done: all leaves available.', 0)
        return res
            
    def isDumped(self, resname):
        return self.getResource(resname).isDumped()

    def loadResource(self, res):
        dbgstr('Getting resource ' + str(res) + ' from disk.', 2)
        if self.isDumped(res):
            dbgstr('Resource ' + str(res) + ' found in: ' + res.getDumpPath() ,2)
            return cPickle.load(open(res.getDumpPath(), 'r'))
        else:
            dbgstr('Resource ' + str(res) + ' not found on disk! I\'ve been looking for: ' + res.getDumpPath())

    def ChangeME_resToPath(self, res):
        if self.getGraph().getAttrib(res[0], 'hashout'):
            if res[0] == None: first_part = ''
            else: first_part = res[0]
            if res[1] == None: second_part = ''
            else: second_part = res[1]
            if first_part != '' and second_part !='':
                mid_part = 'TO'
            else: mid_part = ''
        
            fname = first_part + mid_part + second_part + '.dmp'
        else:
            fname = res[0]
            
        dbgstr('Dump file for resource ' + str(res) + ' is ' + self._metafolder + '/' + fname, 2)
        return self._metafolder + '/' + fname


    def getInNodes(self, node):
        g = self._reverseGraph(self.getGraph())
        dbgstr('in-nodes of ' + str(node) + ' are: ' + str(g[node]), 2)
        return g[node]
        
    def getOutNodes(self, node):
        #dbgstr('out-nodes of ' + str(node) + ' are: ' + str(self._graph[node]), 2)
        return self.getGraph()[node]
        
    def isLeaf(self, node):
        return self.getGraph()[node]==[]
        
    def getOutNodesRecursive(self, node):
        alloutnodes = list()
        nodestack = list(self.getOutNodes(node))
        while nodestack!=[]:
            onode = nodestack.pop()
            nodestack.extend(self.getOutNodes(onode))
            alloutnodes.append(onode)
        return alloutnodes

    def getLeaves(self):
        leaves = list()
        for key in self.getGraph().keys():
            if self.getGraph()[key]==[]:
                leaves.append(key)
        return leaves

        
    def getResNames(self):
        return self.getGraph().getNodes()
#        resnames = list()
#        for node in self.getGraph().keys():
#            if self.getOutNodes(node) == []:
#                resname = (node, None)
#                if not resname in resnames:
#                    resnames.append(resname)
#            else:
#                for onode in self.getOutNodes(node):
#                    resname = (node, onode)
#                    if not resname in resnames:
#                        resnames.append(resname)
#        dbgstr('Resource names: ' + str(resnames), 3)
#        return resnames


    def _reverseGraph(self, g):
        all_values = list()
        for item in g.values():
            for subitem in item:
                if not (subitem in all_values):
                    all_values.append(subitem)
        
        rg=dict.fromkeys(all_values)
        for key in rg:
            rg[key] = []
        for value in all_values:
            for key in g.keys():
                if value in g[key]:
                    rg[value].append(key)
        for value in g.keys():
            if not(value in rg.keys()):
                rg[value]=[]
        return rg
        
        
    def setDumping(self, d):
        self._dodump = d
                
    def getGraph(self):
        return self._graphres.getValue()
        
    def resSummary(self):
        dbgstr('Active resources:', -1)
        for res in self.getResNames():
            mystr = ''
            mystr+=str(res)+' '
            if self.isAvailable(res):
                mystr+='Available '
            if self.isDumped(res):
                mystr+='Dumped'
            dbgstr(mystr,-1)
        
#    def updateFiles(self):
#        for res in self._modmap:
#            if res.isFile():
#                if res.Value().hasChanged():
#                    dbgstr('File resource '+str(res)+ ' has changed.')
                                    
    def _setMod(self, who, what):
        self._modcontents[who.getName()] = self.getContents(what)
        self.dumpMods()
        
#    def _setRes(self, who, what):
#        self._resmap[self._resmap.index(who)]=what
#        self.dumpResource(who)
                        
    def trust(self, who, what):
        if type(who) == str:
            dbgstr('I\'m assuming that using ' + str(what) + ' for ' + who + ' won\'t have consequences on other nodes.', 0)
            self._setMod(who,what)
        elif type(who) == tuple:
            dbgstr('I\'m assuming that using your object of type ' + str(type(what)) + ' for ' + str(who) + ' won\'t have consequences on other nodes.', 0)
            self.addResource(who,what)
            
    def loadMods(self):
        if os.path.exists(self.modsToPath()):
            mods = cPickle.load(open(self.modsToPath(), 'r'))
        else:
            mods = dict()
        
        dbgstr('Found on disk: ' + str(mods.keys()), 2)
        return mods
        
    def setMetaFolder(self, f):
        self._metafolder = f


    def getresmap(self):
        return self._resmap
        
                    
    _resmap = dict()
    _graphres = None
    _metafolder = 'leafmeta'
    _leafprot = ''
    _dodump = True
    _modules = dict()




