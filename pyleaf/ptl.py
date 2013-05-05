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
import pickle
import inspect
from pyleaf.log import send as dbgstr
from pyleaf.rrc import resource
import copy
import inspect
import time        
import sys    

class protocol():
    """Leaf Protocol
    
    Manages all protocol resources and provides user interface through
    Python command line. Protocols are created by the prj class: use
    it to obtain a protocol object.

    Pipeline nodes are executed through the run and provide
    methods. These methods will return the corresponding resource
    immediately if available in memory, load it from the disk if
    previously dumped, or run the appropriate nodes according to the
    protocol.

    If dumping is ON (method dumpOn) automatic caching is active and
    the output of all nodes is stored in the leaf_MODULENAME directory
    as the files NODENAME.res. The files NODENAME.mod within the same
    directory are used to store nodes source code. All the data in
    these files are wrapped in leaf.rrc.resource objects which dump
    themselves through the pickle.dump method. Other files in the
    directory are produced by the leaf.prj.project class.
    
    """    

    def __init__(self, graph, mods, folder, doc):
        untrustme1 = list()
        untrustme2 = list()
        dbgstr('Initializing protocol with root: ' + folder)
        self._metafolder = folder
        self._rootdir = os.getcwd()
        self._resmap = dict()
        self._doc = doc

        self._graphres = resource('graph', os.path.join(folder,'graph.grp'))
        untrustme1 = self._updateGraph(graph)

        for res in self._getResNames():
            newres = resource(res, folder+'/'+res+'.res')
            #print res, newres
            self._addResource(res, newres)

        for mod in self._getNodeNames():
            newres = resource(mod, folder+'/'+mod+'.mod')
            self._modules[mod] = newres

        untrustme2 = self._updateModules(mods)

        for mod in untrustme1:
            self.untrust(mod)
        for mod in untrustme2:
            self.untrust(mod)

#    def show(self):
#        """Shows the Protocol Graph."""
#        dbgstr('Protocol:',0)
#        dbgstr(self._leafprot, 0)
#        dbgstr('Node attributes:', 0)
#        for node in self._getNodeNames():
#            ostr = node +': '
#            for attrib in self._nodeattribs.keys():
#                if attrib[0]==node:
#                    ostr += str(attrib[1])+'='+str(self._nodeattribs[attrib])+', '
#            dbgstr(ostr[0:-2], 0)
        
    def _updateGraph(self, graph):
        self._graphres.setValue(graph)
        untrustme1 = list()
        if self._graphres.changed():
            if self._graphres.isDumped():
                untrustme1 = self._manageGraphChange(self._graphres.getFingerprint())
        self._graphres.update()
        return untrustme1


    def _update(self, graph, mods):
        untrustme1 = list()
        untrustme2 = list()
        dbgstr('New graph is: ' + str(graph), 3)
        dbgstr('New mods are: ' + str(mods), 3)
        untrustme1 = self._updateGraph(graph)
        untrustme2 = self._updateModules(mods)
        for mod in untrustme1:
            self.untrust(mod)
        for mod in untrustme2:
            self.untrust(mod)

    def listinputs(self, node):
        """Lists the inputs for a node."""
        return self._getGraph().getInNodes(node)

    def listoutputs(self, node):
        """Lists the outputs for a node."""
        return self._getGraph().getOutNodes(node)       

    def resetall(self):
        """Clears and undumps all resources"""
        for res in self._getResNames():
            self.reset(res)

    def clearall(self):
        """Clears all resources from RAM"""
        for res in self._getResNames():
            self.clear(res)

    def undumpall(self):
        """Deletes all resources from the disk"""
        for res in self._getResNames():
            self.undump(res)

        if os.path.exists(self._metafolder):
            if os.listdir(self._metafolder) == []:
                os.rmdir(self._metafolder)

    def getinputs(self, mod):
        """Collects all input resources that are input to the given filter and returns a copy of them in a list."""
        if type(mod) != str:
            mod = mod.__name__

        innodes = self._getInNodes(mod)
        ids = [self._getGraph().getAttrib(_node, 'id') for _node in innodes]
        nodeparams = [copy.deepcopy(self._getResource(innode).getValue()) for innode in innodes]
        nodeparams=[one for (one,two) in sorted(zip(nodeparams, ids), key = lambda x:x[1])]      
        return tuple(nodeparams)

    def run(self, parallel = False):
        """Provides all leaf (final) resources."""
        res = None
        allok = True
        l = self._getLeaves()
        for leaf in l:
            resname = leaf
            if not self._isAvailable(resname)and not self._isDumped(resname):
                allok = False
        
        if allok:
            dbgstr('Nothing to be done. Zzz...')
        else:
            res = self.provide(l, parallel)
        return res
    
    def untrust(self, nodename):
        """Clears and undumps resource and all its dependent."""
        if type(nodename) != str:
            nodename = nodename.__name__

        self.reset(nodename)
                
        dependents = self._getOutNodesRecursive(nodename)
        for res in self._getResNames():
            if(res in dependents):
                self.reset(res)


    def clear(self, filtername, verbose = True):
        """Clears a resource.""" 
        if type(filtername) != str:
            filtername = filtername.__name__
        if self._isAvailable(filtername):
            if verbose:
                dbgstr('Clearing resource: ' + str(filtername))
            self._resmap[filtername].clear()

    def reset(self, filtername):
        """Clears and undump a resource"""
        if self._isAvailable(filtername) or self._isDumped(filtername):
            dbgstr('Resetting resource: ' + str(filtername))
        self.clear(filtername, False)
        self.undump(filtername, False)

    def undump(self, filtername, verbose = True):
        """Undumps a resource (removes cached version from disk)."""
        if type(filtername) != str:
            filtername = filtername.__name__
        if self._isDumped(filtername):
            if verbose:
                dbgstr('Undumping resource: ' + str(filtername))
            self._getResource(filtername).clearDump()

    def provideSerial(self, resname):
        """Provides a resource.
        
        This is a legacy method. Use provide with the serial flag,
        instead.
        """
        if type(resname) != str:
            resname = resname.__name__
        return self._provideResource(resname).getValue()

    def rebuild(self, resname):
        """Clears a resource, then provides it."""
        self.clear(resname)
        self.provide(resname)
            
    def dumpOn(self):
        """Switches dumping ON."""
        self._dodump = True

    def dumpOff(self):
        """Switches dumping OFF."""
        self._dodump = False
        
    def trust(self, who, what):
        """Assign a resource to a filter without invalidating dependent resources."""
        if type(who) != str:
            who = who.__name__

        if type(who) == str:
            self._setMod(who,what)
            dbgstr('I\'m assuming that using ' + str(what) + ' for ' + who + ' won\'t have consequences on other nodes.', 0)
        elif type(who) == tuple:
            self._addResource(who,what)        
            dbgstr('I\'m assuming that using your object of type ' + str(type(what)) + ' for ' + str(who) + ' won\'t have consequences on other nodes.', 0)

        
    def list(self):
        """Lists the state of all resources."""
        mystr = ''
        for res in self._getResNames():
            mystr+=str(res)+'\t '
            if self._isAvailable(res):
                mystr+='available\t'
            else:
                mystr+='NOT available\t'
            if self._isDumped(res):
                mystr+='dumped'
            else:
                mystr+='NOT dumped'
            mystr += '\n'
        print(mystr)

    def export(self, ofile, layout='LR'):
        """Exports the protocol to a pdf file."""
        import textwrap
        #ofile = self._metafolder+'/'+ofile
        ofile = ofile
        f=open(ofile, 'w')
        f.write('digraph G {'+
                'node [shape=box, style=rounded];'+
                'rankdir='+
                ('TB' if layout.lower()=='tb' else 'LR')+
                ';')
        for idx, node in enumerate(self._getGraph().getNodes()):

            if self._isFileMod(node):
                shape = 'note'
            else:
                shape = 'box'

            f.write(str(node))
            docstr = inspect.getdoc(self._modules[node].getValue()) if type(self._modules[node].getValue())==type(inspect.getdoc) else None
            f.write('[shape = ' + shape + ', label = <<table border="0"><tr><td><B>' +
                    self._getGraph().getAttrib(node, 'label') +
                    '</B></td></tr><tr><td align = "left"><font POINT-SIZE="10">'+
                   ('-' if docstr == None else  textwrap.fill(docstr, 30)).replace('\n','<br/>') +
                    '</font></td></tr></table>>]\n')
        for node in self._getGraph().keys():
            for onode in self._getGraph()[node]:
                f.write(node + ' -> ' + onode + '\n')
        f.write('}')
        f.close()
        t=os.system('dot -Tpdf -o' + ofile + '.pdf ' + ofile)
        if t!=0:
            raise NameError('Problems running dot: have you installed it?')

    def _readabletime(self, secs):
        mins, secs = divmod(secs, 60)
        hours, mins = divmod(mins, 60)
        return '%02d:%02d:%02.02f' % (hours, mins, secs)
        
    def publish(self, ofile, odir='', layout='LR'):
        """Publish the protocol to a HTML file."""
        import textwrap
        import os.path
        oname = ofile
        if odir == '':
            odir = 'html'
        if not os.path.exists(odir):
            os.mkdir(odir)
        fullname = os.path.join(odir, ofile)
        #ofile = os.path.join(self._metafolder, ofile)
        f=open(fullname+'.dot', 'w')
        f.write('digraph G {\n'+
                'graph [size="20, 20"];\n' +
                'node [shape=box, style=rounded];'+
                'rankdir='+
                ('TB' if layout.lower()=='tb' else 'LR')+
                ';\n')
        for idx, node in enumerate(self._getGraph().getNodes()):
            f.write(str(node))
            docstr = inspect.getdoc(self._modules[node].getValue()) if type(self._modules[node].getValue())==type(inspect.getdoc) else None

            if self._isFileMod(node):
                shape = 'note'
                if self._isAvailable(node):
                    content = self._getResource(node).getValue()
                    if isinstance(content, tuple) or isinstance(content, list):
                        output_line = '\t\t<td href="'+'(multiple)'+'"><font POINT-SIZE="8"><u>output</u></font></td>\n'
                    else:
                        output_line = '\t\t<td href="'+content+'"><font POINT-SIZE="8"><u>output</u></font></td>\n'
                else:
                    output_line = '\t\t<td><font POINT-SIZE="8"><u>not built</u></font></td>\n'                    
            else:
                output_line='\t\t<td></td>\n'
                shape = 'box'

            
            f.write('[shape = ' + shape + ', label = <<table border="0">\n'+
                    '\t<tr>\n'+
                    '\t\t<td colspan="2"><B>' +
                    self._getGraph().getAttrib(node, 'label') +
                    '</B></td>\n'+
                    '\t</tr>\n'+
                    '\t<tr>\n'+
                    '\t\t<td colspan="2" align = "left"><font POINT-SIZE="10">'+
                   ('-' if docstr == None else  textwrap.fill(docstr, 30)).replace('\n','<br/>') +
                    '</font></td>\n'+
                    '\t</tr>\n' +
                    '\t<tr>\n'+
                    '\t\t<td href="#'+node+'_details"><font POINT-SIZE="8"><u>details</u></font></td>\n'+
                    output_line +
                    '\t</tr>\n'+
                    '</table>>]\n')
        for node in self._getGraph().keys():
            for onode in self._getGraph()[node]:
                f.write(node + ' -> ' + onode + '\n')
        f.write('}')
        f.close()
        t=os.system('dot -s160 -Tcmapx -o' +
                    fullname + '.map -Tgif -o' + fullname + '.gif ' + fullname + '.dot')
        t=os.system('dot -Tpdf -o' + fullname + '.pdf ' + fullname + '.dot')

        if t!=0:
            raise NameError('Problems running dot: have you installed it?')





        html_header = """
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<title>""" + oname + """</title>
<meta http-equiv="Content-Language" content="English" />
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<link rel="stylesheet" type="text/css" href="style.css" media="screen" />
</head>
<body>

<div id="wrap">
<div id="top"></div>
<div id="content">

<div class="header">
<a href="index.html"><img src="leaf.png"></a>
<br><br><br><br><br>
</div>	

"""

        html_footer = """
</body>
</html>
"""


        f = open(fullname+'.html', 'w')
        f.write(html_header)
        f.write('<div class="breadcrumbs"><h1>' + oname + '</h1></div><div class="middle">')
        f.write('<h2>Project Summary</h2>')
        f.write('<div style="width: 90%">')
        if len(self._doc)>0:
            f.write('<b>Description:</b> ' + self._doc + '<br>')
        f.write('<b>Number of Modules:</b> ' + str(len(self._getGraph())) + '<br>')
        f.write('<b>Number of Output modules:</b> ' + str(sum([self._isFileMod(node) for node in self._getGraph().getNodes()]))+'<br>')
        f.write('<b>Total CPU time required:</b> '+ self._readabletime(sum([self._resmap[x]._buildtime for x in self._resmap]))+'<br>')
        f.write('</div><br>')
        f.write('<h2>Protocol map</h2>')
        f.write('<div align = "center">')
        f.write('<IMG SRC="' + oname + '.gif" USEMAP="#G" />\n')
        f.write('</div>')
        map = open(ofile + '.map').read()
        f.write(map)

        f.write('<h2>Modules'' details<h2>\n')

        for idx, node in enumerate(self._getGraph().getNodes()):
            f.write('<h3><a name="'+str(node)+'_details">'+str(node)+'</a></h3>\n')
            docstr = inspect.getdoc(self._modules[node].getValue()) if type(self._modules[node].getValue())==type(inspect.getdoc) else None
            if docstr == None:
                f.write('[documentation not available]')
            else:
                f.write(docstr)
                
            if not self._resmap[node]._timestamp == None:
                tstamp = self._resmap[node]._timestamp
                btime = self._resmap[node]._buildtime
            else:
                tstamp = 'never'
                btime = 'uknknown'

            f.write('<br><br>Last build was on ' + tstamp  + '.<br>')
            f.write('Time it took: ' + str(self._readabletime(btime))  + '.<br>')
        

            f.write('<div class="code"><pre>')
            srccode = inspect.getsource(self._modules[node].getValue()) if type(self._modules[node].getValue())==type(inspect.getdoc) else None
            f.write(srccode.replace('\n','<br>'))
            f.write('</pre></div>')
            f.write('<hr>')


        f.write('<div id="footer">')
        f.write('<br><br><i>Automatically generated on ' + time.asctime() +  ' using Leaf</i>')
        f.write('</div>')
        f.write(html_footer)
        f.close()

        try:
        ## copying external resources
            from pkg_resources import resource_filename
            stylef = resource_filename('pyleaf', 'resources/style.css')
            logof = resource_filename('pyleaf', 'resources/leaf.png')

        #stylef = os.path.join(sys.prefix, 'style.css')
        #logof = os.path.join(sys.prefix, 'leaf.png')

            import shutil
            shutil.copy(stylef, odir)
            shutil.copy(logof, odir)
        except:
            print('Couldn\'t copy resource files. HTML file will miss style and logo.')

    def _prettyPrint(self, x):
        return str(x).strip('[]').replace("'","")

    def provide(self, res, parallel=False):
        t = time.time()

        if not type(res) == list:
            temp = list()
            temp.append(res)
            res = temp

        for i,r in enumerate(res):
            if type(res[i]) != str:
                res[i] = res[i].__name__

        D = self._findDependancies(res)
        D.update(res)
        states = self._getBestStates(D)

        if len(states[1]) > 0:
            dbgstr('The following resources will be loaded from disk: '+
                   self._prettyPrint(states[1]))
            for node in states[1]:
                self._provideResource(node)

        if len(states[2]) > 0:
            dbgstr('The following resources will need production: '+
                   self._prettyPrint(states[2]))
        needbuild = states[2]

        while True:
            canrun = self._findRunnable(needbuild)
            if len(canrun) > 1 and parallel:
                dbgstr('The following nodes can run in parallel: '+
                       self._prettyPrint(canrun))

            self._runNodes(canrun, parallel)
            needbuild=[x for x in needbuild if not x in canrun]

            if len(canrun)==0:
                break

        builtres = list()
        for resname in res:
            builtres.append(self._resmap[resname].getValue())

        if len(states[1]) > 0 or len(states[2]) > 0:
            dbgstr('Done in: ' + self._readabletime(time.time() - t) + '.')

        if len(builtres) > 1:
            return builtres
        else:
            return builtres[0]

    def _runNodes(self, nodes, parallel = False):
        if parallel and len(nodes)>1:
            from multiprocessing import Process, Queue
            results = Queue()
            tasks = list()
            for node in nodes:
                nodeparams = self._getNodePar(node)
                tasks.append(
                    Process(target=self._callModPar, args=(node, nodeparams, results,))
                    )
            for task in tasks: task.start()
            for task in tasks: task.join()

            for task in tasks:
                taskres = results.get()
                resname = self._buildResName(taskres[0], None, taskres[1])
                dbgstr('Requesting add resource: ' + taskres[0], 2)
                t=taskres[2]
                self._newResource(resname, taskres[1], t)
        else:
            for node in nodes:
                nodeparams = self._getNodePar(node)
                taskres = self._callMod(node, nodeparams)
                resname = self._buildResName(taskres[1], None, taskres[0])
                dbgstr('Requesting add resource: ' + resname, 2)
                t=taskres[2]
                self._newResource(resname, taskres[0], t)

    def time(self, node):
        if type(node) != str:
            node = node.__name__
        return(self._resmap[node]._timestamp,
               self._resmap[node]._buildtime)

    def _findRunnable(self, nodes):
        #finds nodes whose inputs are available
        runnable = list()
        #import pdb; pdb.set_trace()
        for node in nodes:
            if all([self._isAvailable(n) for n in self._getInNodes(node)]):
                runnable.append(node)
        return runnable
        
    def _getBestStates(self, D):
        # categorizes resources to reflect best state. I.e., if a resource is
        # both available and dumped, it is returned in the set of available resources.
        ar = list()
        dr = list()
        nr = list()
        for d in D:
            if self._isAvailable(d):
                ar.append(d)
            elif self._isDumped(d):
                dr.append(d)
            else:
                nr.append(d)
                
        return ar,dr,nr

    def _findDependancies(self, nodes):
        # builds a list of all resources that are necessary
        # in order to build nodes
        nec = set()
        for n in nodes:
            nec.update(self._getGraph().getAncestors(n))
        return nec

    def _updateModules(self, mods):
        untrustme = list()
        for modname in mods:
            if modname in self._modules.keys():
                self._modules[modname].setValue(mods[modname])
                if self._modules[modname].changed():
                    untrustme.append(modname)
                    #self.untrust(self._modules[modname].name())
                    self._modhelp[modname] = inspect.getdoc(self._modules[modname].getValue())
                self._modules[modname].update()
            else:
                dbgstr('New module: ' + modname)
                self._modules[modname] = resource(modname,
                    self._metafolder+'/'+modname+'.dmp' )
                self._addResource(modname, self._modules[modname])
                self._modules[modname].setValue(mods[modname])
                self._modules[modname].update()
        return untrustme
                

    def _manageGraphChange(self, newGraph):
        if newGraph==None:
            return
        #checking for change in graph structure
        #a node is flagged as to-be-untrustest if its inputs have changed
        #not untrusted on the fly because of dependancies with untrusts
        #from source code changes
        oldg = self._graphres.getValue()
        untrustme = list()
#        import pdb; pdb.set_trace()

        for node in newGraph.getNodes():
            #check wether node is (not) new
            if node in oldg.getNodes():
                #check if node inputs have changed
                innodes1 = newGraph.getInNodes(node)
                innodes2 = oldg.getInNodes(node)
                for inNode in innodes1:
                    if not inNode in innodes2:
                        dbgstr('Inputs to ' + node + ' have changed, untrusting it.')
                        untrustme.append(node)
                #check if node properties have changed                
                #cycling through attrib names of node 'node'
                # for attrib in [a[1] for a in newGraph._nodeattribs if a[0]==node]:
                #     if newGraph.getAttrib(node, attrib) != oldg.getAttrib(node, attrib):
                #         dbgstr('Node attribs of ' + node +
                #                ' have changed, untrusting it.')
                #         untrustme.append(node)                        

        return untrustme
    
            
#    def modSummary(self):
#        pass
#        #for mod in self._getNodeNames():
#        #    dbgstr(mod + ', changed = ' + self.checkModChanged(modname,))
            
    def _getContents(self, mod):
        try:
            inspect.getsource(mod)
            value = inspect.getsource(mod)
        except Exception:            
            value = mod
        return value
        
        

        
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

    def _setMod(self, modname, mod):
        haschanged = self._modules[modname].changed()
        if haschanged:
            if type(mod) == File:
                mod.update()
            self._modules[modname].setValue(mod.getValue())
            self._modules[modname].updateFingerprint()
            self.untrust(modname)
            dependents = self._getOutNodesRecursive(modname)
            if dependents != []:
                dbgstr('These nodes are dependent: '+str(dependents), 0)
            #for dep in dependents:
            #    self._clearFilter(dep)

    def _setMods(self, mods):
        self._modules = mods
        for modname in mods.keys():
            self._setMod(modname, mods[modname])
        
        dbgstr('Modules are: ' + str(self._modules), 3)
        #dbgstr('with source: ' + str(self._modcontents), 3)
                
    # def _dumpResource(self, res):
    #     self._getResource(res).dump()
        
    def _newResource(self, resname, resval, t):
        dbgstr('Updating resource: ' + resname, 2)
        dbgstr('with contents: ' + str(resval), 3)
        self._getResource(resname).setValue(resval)
        self._getResource(resname).updateFingerprint()
        self._getResource(resname)._buildtime = t
        self._getResource(resname)._timestamp = time.asctime()
        dbgstr('Dumping resource: ' + resname)
        self._getResource(resname).dump()
        
        
    def _clearFilter(self, nodename):
        if self._isLeaf(nodename):
            self.clear(nodename)
        for node in self.getoutputs(nodename):
            self.clear(node)

  
            
    def _setWdir(self, wdir):
        self.wdir = wdir            
        
    def _isAvailable(self, resname):
        dbgstr('Checking resource: ' + str(resname), 3)
        if self._getResource(resname).isAvailable():
           dbgstr('Available: ' + str(resname), 3)
           return True
        dbgstr('Unavailable: ' + str(resname), 3)
        return False        

                
    def _getResource(self, resname):
        dbgstr('Getting resource: ' + str(resname), 3)        
        return self._resmap[resname]
        
    def _addResource(self, name, res):
        self._resmap[name]=res

    def _getNodeNames(self):
        return self._getGraph().getNodes()
        
    def _isResFile(self, res):
        isit = res.isFile()
        if isit : dbgstr(str(res) + ' is a file.')
        return isit
            
    def _provideResource(self, resname):
        dbgstr('Providing resource: ' + str(resname), 2)
        if self._isAvailable(resname):
            dbgstr('Found in RAM: ' + str(resname))
            dbgstr('Resource content is:\n' + str(self._getResource(resname)) ,4)
            return self._getResource(resname)
        elif self._isDumped(resname):
            dbgstr('Found on disk: ' + str(resname), 2)
            self._addResource(resname, self._loadResource(resname))
            dbgstr('Resource content is:\n' + str(self._getResource(resname)), 4)
            return self._resmap[resname]
        else:
            dbgstr('Resource not found. I need to run first: ' + str(resname))
            self._runNode(resname)
            return self._getResource(resname)

    def _runNode(self, node):
        dbgstr('Running node: ' + str(node))
        
        nodeparams = list()        
        input_nodes = self._getInNodes(node)
        for item in input_nodes:
            thisnode_inputs = list()
            neededres = item
            dbgstr('Retreiving resource: ' + neededres)
            this_params = self._provideResource(neededres)
            if type(this_params.getValue())==list:
                dbgstr('Resource type is: list.', 2)
                for this_param in this_params.getValue():
                    thisnode_inputs.append(this_param)
            elif self._isResFile(this_params):
                dbgstr('Resource type is: file.', 2)
                thisnode_inputs.append(this_params.getValue())
            else:
                dbgstr('Resource type is: ' + str(type(this_params.getValue())), 2)
                thisnode_inputs.append(this_params.getValue())
            if len(thisnode_inputs)==1:
                nodeparams.append(thisnode_inputs[0])
            else:
                nodeparams.append(thisnode_inputs)
        
        dbgstr('Ready to run: ' + node, 2)
        dbgstr('through ' + str(self._getModule(node).getValue()), 2)
        dbgstr('on input:\n\t' + str(nodeparams), 3)
        
        newres, newresname = self._callMod(node, nodeparams)
        dbgstr('Build took ' + str(self._resmap[newresname]._buildtime))

        return newres

    def _getNodePar(self, node):

        nodeparams = list()        
        input_nodes = self._getInNodes(node)
        for item in input_nodes:
            thisnode_inputs = list()
            neededres = item
            this_params = self._getResource(neededres)
            if type(this_params.getValue())==list:
                dbgstr('Resource type is: list.', 2)
                for this_param in this_params.getValue():
                    thisnode_inputs.append(this_param)
            elif self._isResFile(this_params):
                dbgstr('Resource type is: file.', 2)
                thisnode_inputs.append(this_params.getValue())
            else:
                dbgstr('Resource type is: ' + str(type(this_params.getValue())), 2)
                thisnode_inputs.append(this_params.getValue())
            if len(thisnode_inputs)==1:
                nodeparams.append(thisnode_inputs[0])
            else:
                nodeparams.append(thisnode_inputs)
        
        return nodeparams

    def _getModule(self, name):
        return self._modules[name]
        

    def _callMod(self, node, nodeparams):
        t = time.time()

        if not self._checkIsFunction(self._modules[node].getValue()):
            dbgstr('Node '+node+' is not a function: passing itself.', 2)            
            newres = self._modules[node].getValue()

            
        elif len(nodeparams)==0:
            dbgstr('No input for: ' + str(node), 2)
            dbgstr('Running node: ' + node)
            
            newres = self._modules[node].getValue()()


            dbgstr('Done.')
            dbgstr('Produced list:\n\t' + str(newres), 3)

    
        elif self._getGraph().getAttrib(node, 'hash'):
            dbgstr('Inputs are joined.', 2)
            dbgstr('Running node: ' + node)
            newres = self._modules[node].getValue()(*nodeparams)
            dbgstr('Done.', 0)
            dbgstr('Produced list:\n\t' + str(newres), 3)

            
        else:
            dbgstr('Inputs are hashed.', 2)
            for nodeparam in nodeparams:
                dbgstr('Running node: ' + node)
                newres = self._modules[node].getValue()(nodeparam)
                dbgstr('Done.')
                dbgstr('Produced list:\n\t' + str(newres), 3)

        newresname = self._buildResName(node, None, newres)
        dbgstr('Requesting add resource: ' + node, 2)
        t = time.time() - t
        #self._newResource(newresname, newres, t)
            
        return newres, newresname, t

    def _callModPar(self, node, nodeparams, queue):
           
        dbgstr('Running node: ' + node)
        funct = self._modules[node].getValue()
        if len(nodeparams)==0:
            dbgstr('No input for: ' + str(node), 2)
            t = time.time()
            newres = funct()
            t = time.time() - t    
        else:
            t = time.time()
            newres = funct(*nodeparams)
            t = time.time() - t

        dbgstr('Produced list:\n\t' + str(newres), 3)

            
        #the following is needed to correctly match node
        #and resource when going parallel
        queue.put((node, newres, t))
        #return newres

        
    def _checkIsFunction(self, x):
        #return hasattr(self._modules[node].getValue(), '_call_'):
        return type(lambda y:y)==type(x)
        
    def _placeFileRes(self, fname):
        if self._auto_place_files:
            os.system('mv -r"'+ fname + '" ' + self._metafolder)
            
    def _buildResName(self, inode, onode, rawres):
        if onode == None:
            return inode
        else:
            return inode
        

    def _isFileMod(self, node):
        flags = self._getGraph().getAttrib(node, 'LEAF_FLAGS')
        if flags == None:
            return False
        return 'f' in flags or 'F' in flags
        
    def _updateFilePath(self, path):
        parts = os.path.split(path)
        if parts[0] != self._metafolder:
            return self._metafolder + '/' + parts[1]
        return path

    def _processRawRes(self, node, rawres):
        

                        
# #        elif type(rawres)==tuple:        
# #            dbgstr('Raw list are packed in a tuple.')
# #            
# #            if len(rawres != len(self._getGraph()[node])):
# #                raise NameError('When a module returns a tuple, it''s length must be equal to the number of the module''s outputs.')
# #                
# #            for idx, outnode in enumerate(self._getGraph()[node]):
# #                newresname = self._buildResName(node, outnode, rawres)                
# #                dbgstr('Requesting add resource: ' + str(newresname))
# #                if self._isFileMod(node):
# #                    self._placeFileRes(rawres)
# #                    self._newResource(newresname, self._updateFilePath(rawres[idx]))
# #                else:
# #                    self._newResource(newresname, rawres[idx])
# #                
# #        else:

        # if self._isFileMod(node):
        #     if type(rawres)==tuple or type(rawres)==list:
        #         for rawresi in rawres:
        #             newresname = self._buildResName(node, None, rawresi)
        #             dbgstr('Requesting add resource: ' + node, 2)
        #             self._placeFileRes(rawresi)
        #             self._newResource(newresname, self._updateFilePath(rawresi))
        #     else:
        #         newresname = self._buildResName(node, None, rawres)
        #         dbgstr('Requesting add resource: ' + node, 2)
        #         self._placeFileRes(rawres)
        #         self._newResource(newresname, self._updateFilePath(rawres))
        # else:
        #     newresname = self._buildResName(node, None, rawres)
        #     dbgstr('Requesting add resource: ' + node, 2)
        #     self._newResource(newresname, rawres)
        newresname = self._buildResName(node, None, rawres)
        dbgstr('Requesting add resource: ' + node, 2)
        self._newResource(newresname, rawres)
                
                
                
    def _setDumpFolder(self,f):
        self._metafolder=f

 
            
    def _isDumped(self, resname):
        return self._getResource(resname).isDumped()

    def _loadResource(self, res):
        dbgstr('Getting resource ' + str(res) + ' from disk.', 2)
        if self._isDumped(res):
            dbgstr('Resource ' + str(self._resmap[res]) + ' found in: ' + self._resmap[res].getDumpPath() ,2)
            return pickle.load(open(self._resmap[res].getDumpPath(), 'r'))
        else:
            dbgstr('Resource ' + str(res) + ' not found on disk! I\'ve been looking for: ' + self._resmap[res].getDumpPath())

    def _ChangeME_resToPath(self, res):
        if self._getGraph().getAttrib(res[0], 'hashout'):
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


    def _getInNodes(self, node):
        return self._getGraph().getInNodes(node)
        # g = self._reverseGraph(self._getGraph())
        # dbgstr('in-nodes of ' + str(node) + ' are: ' + str(g[node]), 2)
        # return g[node]
        
    def getoutputs(self, node):
        #dbgstr('out-nodes of ' + str(node) + ' are: ' + str(self._graph[node]), 2)
        return self._getGraph().getOutNodes(node)
        
    def _isLeaf(self, node):
        return self._getGraph()[node]==[]
        
    def _getOutNodesRecursive(self, node):
        alloutnodes = list()
        nodestack = list(self.getoutputs(node))
        while nodestack!=[]:
            onode = nodestack.pop()
            nodestack.extend(self.getoutputs(onode))
            alloutnodes.append(onode)
        return alloutnodes

    def _getLeaves(self):
        leaves = list()
        for key in self._getGraph().keys():
            if self._getGraph()[key]==[]:
                leaves.append(key)
        return leaves

        
    def _getResNames(self):
        return self._getGraph().getNodes()
#        resnames = list()
#        for node in self._getGraph().keys():
#            if self.getoutputs(node) == []:
#                resname = (node, None)
#                if not resname in resnames:
#                    resnames.append(resname)
#            else:
#                for onode in self.getoutputs(node):
#                    resname = (node, onode)
#                    if not resname in resnames:
#                        resnames.append(resname)
#        dbgstr('Resource names: ' + str(resnames), 3)
#        return resnames
        
        
    def _setDumping(self, d):
        self._dodump = d
        
                
    def _getGraph(self):
        return self._graphres.getValue()
        
        
#    def updateFiles(self):
#        for res in self._modmap:
#            if res.isFile():
#                if res.Value().hasChanged():
#                    dbgstr('File resource '+str(res)+ ' has changed.')
                                    
    def _setMod(self, who, what):
        self._modcontents[who.getName()] = self._getContents(what)
        self.dumpMods()
        
#    def _setRes(self, who, what):
#        self._resmap[self._resmap.index(who)]=what
#        self._dumpResource(who)
                        
            
    def _loadMods(self):
        if os.path.exists(self.modsToPath()):
            mods = pickle.load(open(self.modsToPath(), 'r'))
        else:
            mods = dict()
        
        dbgstr('Found on disk: ' + str(mods.keys()), 2)
        return mods


        
    def _setMetaFolder(self, f):
        self._metafolder = f


    def _getresmap(self):
        return self._resmap
        
                    
    _resmap = dict()
    _graphres = None
    _metafolder = 'leafmeta'
    _dodump = True
    _modules = dict()
    _modhelp = dict()
    _auto_place_files = False
    _doc = ''
