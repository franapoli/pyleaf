# The MIT License (MIT)

# Copyright (c) 2012-2013 Francesco Napolitano, franapoli@gmail.com

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.


import os
import inspect
from pyleaf.gph import graph
from pyleaf import log
from pyleaf.ptl import protocol
import copy
from imp import reload

class project():
    """
    Leaf Project: creates Leaf protocols binding an LGL graph to
    Python functions.  This class creates Leaf projects by calling the
    LGL compiler to build a graph object, than binds node names to
    python functions. The python functions must be defined inside a
    module whose name is passed to the leaf.project constructor.

    This class is also responsible for resource consistency check. To
    this aim, nodes source code is stored within the directory
    leaf_USERMODULENAME as the files NODENAME.mod. The graph.grp file
    contains the pipeline structure as a pyleaf.gph.graph object.  All
    the data in these files are wrapped in leaf.rrc.resource objects
    which dump themselves through the pickle.dump method. Other files
    in the directory are produced by the leaf.ptl.protocol class.

    If the update method is called, pyleaf compares the current source
    code with the previously stored code (that produced the available
    resources) and invalidate all the resources dependent on code that
    is found changed. Note that currently Leaf just checks whether the
    source code is exactly the same or not, including blanks and
    comments. The consistency checks can be bypassed by using the
    trust method of leaf.ptl.protocol.

    Removing or renaming the directory leaf_USERMODULENAME or single
    files within it is safe. All resources associated with deleted
    files will need to be recomputed.
    
    """
    
    def __init__(self, modulename, leafprot, lglSrcOff=0, language='lgl'):
        self._lglSrcOff = lglSrcOff
        self._modulename = modulename        
        self._metafolder = 'leaf_' + modulename        
        if not os.path.exists(self._metafolder):
            os.mkdir(self._metafolder)
        self._updateUserModule()
        self._protName = leafprot
        self._leafProt = self._seekforProt(leafprot)
        self._language = language
        self._initGraphs(self._leafProt)

    def _extract_doc(self, lglprot):
        import re

        h = re.findall("/\*(.*)\*/", lglprot, re.DOTALL)

        if len(h)>0:
            return h[0]
        else:
            return ''


    def _seekforProt(self, gname):
        #extracts a variable with the given name from
        #the user module: it must contain the leaf protocol
        log.send('Looking for protocol in user module.', 3)
        hislocals=self._getUserLocals()

        if gname in hislocals.keys():
            return  hislocals[gname]
        else:
            raise NameError('I couldn''t bind "'+gname+
                            '" to any of your defined objects.')
        

    def _updateGraphs(self, leafprot):
        newGraph = graph()
        newGraph.load(self._language, leafprot, self._lglSrcOff)

            #TODO: the following includes stuff copy-pasted
            #from i_nitGraphs. Should be restructured.
        self._graph = newGraph

        altgraphs = self._generateAltGraphs()
        mods = self._seekforMods()
        
            #import pdb; pdb.set_trace()

        for gname in altgraphs.keys():
            if str(gname) != '':
                altfolder = os.path.join(self._metafolder,
                                         str(gname).strip('[]').\
                                             replace(', ','').replace('\'', ''))
            else:
                altfolder = self._metafolder.strip('[]').\
                    replace(', ','').replace('\'', '')

                if not os.path.exists(altfolder):
                    os.mkdir(altfolder)
                
                #self.protocols[gname]=protocol(altgraphs[gname], mods, altfolder)
                self.protocols[gname]._setMetaFolder(altfolder)
                #g = self.protocols[gname]._getGraph()                
                self.protocols[gname]._update(altgraphs[gname], mods)
                
            
    def _initGraphs(self, leafprot):
        if leafprot == '':
            leafprot = self._guessLeafProt()

        self._graph.load(self._language, leafprot, self._lglSrcOff)
        
        mods = self._seekforMods()

        altgraphs = self._generateAltGraphs()
        for gname in altgraphs.keys():
            if str(gname) != '':
                altfolder = os.path.join(self._metafolder,
                                         str(gname).strip('[]').\
                                             replace(', ','').replace('\'', ''))
            else:
                altfolder = self._metafolder.strip('[]').\
                    replace(', ','').replace('\'', '')
            if not os.path.exists(altfolder):
                os.mkdir(altfolder)
                
            self.protocols[gname]=protocol(altgraphs[gname], mods,\
                                               altfolder, self._extract_doc(leafprot))
            #self.protocols[gname]._getGraph().toPdf(altfolder+'/graph.dot')
            #if not os.path.exists('wdir'):
            #    os.mkdir('wdir')
            #if not os.path.exists('wdir/' + gname):
            #    os.mkdir('wdir/'+gname)
            #self.protocols[gname].setWdir('wdir/'+gname)

                                        
    def _getNodeGroups(self):
        nodegroups = dict()
        for node in self._graph.getNodes():
            gid = self._graph.getAttrib(node, 'group')
            if gid:
                if gid in nodegroups.keys():
                    nodegroups[gid].append(node)
                else:
                    nodegroups[gid] = [node]
        return nodegroups
        

    def _combinations(self, *iterables):
     if iterables:
       for head in iterables[0]:
         for remainder in self._combinations(*iterables[1:]):
           yield [head] + remainder
     else:
       yield []
       
    def _altPathToName(self, path):
        return str(path).strip('[]')

    def _generateAltGraphs(self):
        altpaths = self._generateAltPaths()
        groups = self._getNodeGroups().values()
        for path in altpaths:
            self._altgraphs[self._altPathToName(path)] = copy.deepcopy(self._graph)
            for group in groups:
                for node in group:
                    if node not in path:
                        self._altgraphs[self._altPathToName(path)].delNode(node)
            log.send('Alternative protocol ' + self._altPathToName(path) +
                ' is: ' + str(self._altgraphs[self._altPathToName(path)]), 2)
                        
        return self._altgraphs

    def _generateAltPaths(self):
        ngroups = self._getNodeGroups()
        temp = list()
        combs = self._combinations(*(ngroups.values()))
        # the following includes ugly patches because it's safer than
        # changing self._combinations, which is cryptic. Best solution
        # is still to change _combinations.
        for t in combs:
            if len(t)>0:
                temp.append(t[0])
            else:
                temp.append(t)
        return temp
        
    def _guessLeafProt(self):
        hislocals = self._getUserLocals()
        hisnames = hislocals.keys()
        
        if 'leafProtocol' in hisnames:
            leafprot = hislocals['leafProtocol']
            return leafprot
        else:
            raise NameError('I couldn''t find a variable called leafProtocol')

    def _updateUserModule(self):
        import sys

        #the following is needed to sync the inspect module
        #with actual disk content
        import linecache
        linecache.checkcache()

        if self._modulename in sys.modules.keys():
            log.send('Reloading user module.')
            self._usermodule = sys.modules[self._modulename]
            reload(self._usermodule)
        else:
            log.send('Loading user module.')
            self._usermodule = __import__(self._modulename)

        log.send('Your module is: ' + str(self._usermodule), 2)

        return self._usermodule

    def _getUserLocals(self):
        hislocals = dict()

        for (name, value) in inspect.getmembers(self._usermodule):
            hislocals[name] = value

        return hislocals
        
    #def _listFilters(self):
    #    names = self._graph.getNodes()
    #    log.send('Mod names are: ' + str(names), 3)
    #    return names
                
        
    def _seekforMods(self):
        log.send('Looking for mods in user module.', 3)
        hislocals = self._getUserLocals()

        mymods=dict()
        nodenames = self._graph.getNodes()
        for nodename in nodenames:
            modname = nodename #self._graph.getAttrib(nodename, 'bind')
            if modname in hislocals.keys():
                if not self._graph.getAttrib(nodename, 'bind') in hislocals:
                    NameError('There is no '+self._graph.getAttrib(nodename, 'bind')+
                              ' in your Python module.')
                mymods[modname] = hislocals[self._graph.getAttrib(nodename, 'bind')]
                #mymods[modname] = hislocals[modname]

            else:
                raise NameError('I couldn''t bind '+modname+' to any of your defined objects.')

        #resmods = dict()
        #for mod in mymods.keys():
        #    resmods[mod]=mymods[mod]
                
        return mymods
        
    def update(self):
        """Updates all protocols internals to keep coherency after changes.

        If the source code of a filter has changed, the new code is retrieved and the
        filter is untrusted.
        If the protocol graph has changed, all filters whose set of input filters has
        changed are untrusted.

        Function has no return value.
        """
        self._updateUserModule()
        g = self._seekforProt(self._protName)
        self._updateGraphs(g)
            
    def run(self):
        """Calls run on all protocols of the project."""
        for protname in self.protocols.keys():
            log.insertBreak()
            log.send('Running instance: ' + protname)
            self.protocols[protname].run()
            
    def listProtocols(self):
        """Lists the names of all the protocols of the project."""
        for protname in self.protocols:
            log.send('- ' + protname, 0)            
            log.send('  ' + str(self.protocols[protname]._getGraph()))
            
    # def getProtocol(self, protname):
    #     return self.protocols[protname]
        
            
    # def provide(self, what):
    #     if len(self.protocols)==1:
    #         return self.protocols[self.protocols.keys()[0]].provide(what)
    #     else:
    #         resdict = dict()
    #         for protname in self.protocols:
    #             resdict[protname] = self.protocols[protname].provide(what)
    #         return resdict
            
    # def getinputs(self, node):
    #     resdict = dict()
    #     for protname in self.protocols:
    #         resdict[protname] = self.protocols[protname].getinputs(node)
    #     return resdict
            
#    def newFile(self, fname):
#        return fname

    protocols = dict()
    _graph = graph()
    _name = ''
    _metafolder = ''
    _leafProt = ''
    _altgraphs = dict()
    _lglSrcOff = 0
    _protName = ''
