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


import re
import os
from pyleaf import log
import sys

class graph(dict):
    def getNodes(self):
        nodes = self.keys()
        for value in self._reverseDict().keys():
            if not(value in nodes):
                nodes.append(value)
        return nodes

    def getInNodes(self, node):        
        # nodes are returned in edge-id order
        g = self._reverseDict()        
        ids = [self.getEdgeAttrib((x, node), 'id') for x in g[node]]
        return [x[1] for x in sorted(zip(ids, g[node]))]
        
    def getOutNodes(self, node):
        ids = [self.getEdgeAttrib((node, x), 'id') for x in self[node]]
        return [x[1] for x in sorted(zip(ids, self[node]))]
        
    def isLeaf(self, node):
        return self[node]==[]
        
    def toPdf(self, ofile='graph.pdf'):
        f=open(ofile, 'w')
        f.write(r"""digraph G {
node [shape=box, style=rounded];
rankdir=LR;
""")
        for idx, node in enumerate(self.getNodes()):
            f.write(str(node))
            f.write('[label = ' + node + ']\n')
        for node in self.keys():
            for onode in self[node]:
                f.write(node + ' -> ' + onode + '\n')
        f.write('}')
        f.close()
        os.system('dot -Tpdf -o' + ofile + '.pdf ' + ofile)

    def getAncestors(self, node):
        anc = set()
        g = self._reverseDict()
        stack = list()
        stack.append(node)

        while len(stack) != 0:
            n = stack.pop()
            for parent in g[n]:
                anc.add(parent)
                stack.append(parent)
        return anc            

    def _reverseDict(self):
        g = self
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

        #for key in rg.keys():
        #   rg[key]=sorted(rg[key])

        return rg

    def getAttrib(self, node, attr):
        if (node, attr) in self._nodeattribs:
            return self._nodeattribs[(node, attr)]
        return None

        
    def setAttrib(self, node, attr, value):
        log.send('Setting ' + 
            str(attr) + ' = ' + str(value) +
            ' for node: ' + str(node), 3)
        self._nodeattribs[(node, attr)] = value
        
    def delNode(self, node):
        del(self[node])
        for targets in self.values():
            if node in targets:
                del(targets[targets.index(node)])

    def lgl2dot(self, leafprot, erroffset):
        f=open('leafprot.lf', 'w')
        f.write(leafprot)
        f.close()

        ## Regression: the following will cause troubles in windows
        ## because of the "exe" extension.
        # def findLglcBin():
        #     for path in os.environ["PATH"].split(os.pathsep):
        #         lglcbin = os.path.join(path, 'lglc')
        #         if os.path.isfile(lglcbin):
        #             return lglcbin
        #         else:
        #             NameError('Error while searching for lglc binary. Is it in your PATH?')
        #     return lglcbin
            
        # lglcbin = findLglcBin()
        # if not os.access(lglcbin, os.X_OK):
        #     raise NameError('Error while running binary ' +\
        #                         lglcbin +
        #                     '. Please make sure that it is the correct LGL Compiler binary and that you have proper permissions to run it.')

        # t=os.system(os.path.join(lglcbin) +
        #             ' leafprot.lf -l' + str(erroffset))

        t=os.system('lglc' +
                    ' leafprot.lf -l' + str(erroffset))

        if t!=0:
            raise NameError('Error while running lglc. '+
                            'If I was able to run it, it produced an error message. ' +
                            'Otherwise make sure you can successfully run lglc from a system shell.')
        #t=os.system('dot -Tpdf leafprot.lf.dot -otemp.pdf')
        #if t!=0:
        #    raise NameError('Problems running dot: have you installed it?')
                                
        a = open('leafprot.lf.dot','r').read()
        return a

    def setEdgeAttrib(self, edge, key, value):
        self._edgeattribs[edge, key]=value

    def getEdgeAttrib(self, edge, key):
        return self._edgeattribs[edge, key]

    def load(self, language, source, erroffset):
        if language == 'lgl':
            self._fromLgl(source, erroffset)
        elif language == 'ldot':
            self._fromLdot(source, erroffset)

    def _fromLdot(self, source):
        for key in self.keys():
            del(self[key])

        a = source

        edges = re.findall(r'(\d+->\d+) \[(.*)\]', a)
        #edges = re.findall(r'\d+->\d+', a)
        nodelines = re.findall(r'(\d+) \[ (.*)\]', a)
        nodes = list()        

        ## Creating nodes
        for node in nodelines:
            nodeid = node[0]
            nodename = ''
            node_attribs = node[1].split(',')
            for node_attrib in node_attribs:
                key_val = node_attrib.split(' = ')
                if key_val[0]=='label':
                    nodename = key_val[1]
                    nodes.append([nodeid, nodename])
                    self.setAttrib(nodename, 'id', int(nodeid))
                self.setAttrib(nodename, key_val[0].strip(), key_val[1].strip())            
            if self.getAttrib(nodename, 'bind')==None:
                self.setAttrib(nodename, 'bind', nodename)
            
        names = dict()
        for node in nodes: names[node[0]]=node[1]
        
        ## Creating edges
        for edge in edges:
            thisnodes = re.findall('\d+', edge[0])
            key = names[thisnodes[0]]
            if key in self.keys():
                self[key].append(names[thisnodes[1]])
            else:
                self[key]=[names[thisnodes[1]]]
            eattrib = re.findall('(.*)=(.*)', edge[1])[0]

            ## IDs are converted to integer numbers
            if eattrib[0] == 'id':
                self.setEdgeAttrib((names[thisnodes[0]],
                                    names[thisnodes[1]]),
                                   eattrib[0], int(eattrib[1]))
            ## All the rest are left as strings
            else:
                self.setEdgeAttrib((names[thisnodes[0]],
                                    names[thisnodes[1]]),
                                   eattrib[0], eattrib[1])
    
        for value in names.values():
            if not(value in self.keys()):
                self[value]=[]
    
        for key in self.keys():
            self[key] = sorted(self[key])

        #os.remove('leafprot.lf.dot')
        log.send('Graph is: ' + str(self), 2)        

    def _fromLgl(self, leafprot, erroffset):
        self._nodeattribs=dict()
        self._edgeattribs=dict()

        a = self.lgl2dot(leafprot, erroffset)

        self._fromLdot(a)


        
    _nodeattribs = dict()
    _edgeattribs = dict()

