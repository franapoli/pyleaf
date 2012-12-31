
##############################
## PREAMBLE                 ##
##############################

from pyleaf.prj import project

## The following is meant to make sure that pyLeaf can import this
## file. In case of problems, manually assign to "mydir" the absolute
## path of the directory containing this file.

import os, sys
mydir = os.path.abspath('.')
if not mydir in sys.path:
    sys.path.insert(0, mydir)

## Finally set the name of this module: it must be the same as the
## file name (without extension) containing this text. (Note that a
## few ways exist to determine it at runtime, but they are not robust
## enough).

module_name = 'ex1'


##############################
## THE PIPELINE             ##
##############################

## The LGL pipeline definition follows. The two lines just before it
## tell lglc where the LGL code starts in this file in order for it to
## correctly point out syntax errors.

import inspect
lglposition = inspect.currentframe().f_lineno
protocol = """
/*
   LEAF PROTOCOL

   This simple protocol is a basic example illustrating 
   the use of Leaf to drive a very simple experiment:
   we want to test the performance gain due to the use of
   the Python "sum" function as opposed to a for loop.
*/


         / testFor -> report
genData <
         \ testSum -> @report -> exportRes[F]
;
"""


##############################
## NODES IMPLEMENTATION     ##
##############################

## "Normal" Python code starts here.

import time
import random


def genData():
    """Generates some random numbers"""
    return [random.random() for i in range(1,1000)]

def testSum(data):
    """Times the sum function"""
    start = time.time()

    for i in range(1, 100000):
        x = sum(data)

    return time.time()-start

def testFor(data):
    """Times a for loop over its input"""
    start = time.time()

    x = 0
    for i in range(1, 100000):
        for i in range(0, len(data)):
            x = x + data[i]
        # i = 0
        # while i < len(data):
        #     x = x + data[i]
        #     i = i + 1

    return time.time()-start
    
def report(r1, r2):
    """Reports the ratio between the two timings"""
    return r2/r1

def exportRes(reportOut):
    """Exports results to the disk"""
    fname = 'reportOut.txt'
    f = open(fname, 'w')
    f.write(str(reportOut))
    f.close()
    return fname



############################
## PROJECT INITIALIZATION ##
############################

## This function will create a pyLeaf object and separately return
## references to the project object and to its first protocol (the
## only one included in this example).

def prj():
    global o
    pj = project(module_name, 'protocol', lglposition)
    p = pj.protocols['']
    o = p.provide
    return p, pj

