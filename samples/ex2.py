

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

module_name = 'ex2'


##############################
## THE PIPELINE             ##
##############################

## The LGL pipeline definition follows. The two lines just before it
## tell lglc where the LGL code starts in this file in order for it to
## correctly point out syntax errors.


import inspect
lglposition = inspect.currentframe().f_lineno
protocol = """
/* This is a simple protocol whose aim is to drive an example of
   Python/R integration.  We just plot the R's <i>cars</i> dataset
   together with a linear regression using R's <i>lm</i> and a
   boxplot. The <i>[F]</i>-s in the protocol are <i>flags</i>
   indicating that the flagged node (rectangular in the graphical
   representation) produces a file on the disk. Such nodes must always
   return the name of the file they create (as a simple <i>str</i>),
   or a list of file names if they produce more than one file (as a
   <i>list</i> of <i>str</>). */


          / regression -> plots [F]
getData  <
          \  / @plots
           .<
             \ exportCSV [F]
;
"""


##############################
## NODES IMPLEMENTATION     ##
##############################

## "Normal" Python code starts here.

from rpy import r


def getData():
    """Calls R to get and normalize the cars dataset."""
    return r("scale(cars)")


def exportCSV(data):
    """Exports Car's data to a CSV file."""
    fname = 'carsdata.csv'
    f = open(fname, 'w')
    for point in data:
        f.write(str(point[0]) + ', ' +
                str(point[1]) + '\n')
    f.close()
    return fname


def regression(data):
    """Calls R's lm to make a linear regression on each of its inputs."""

    reg = r.lm(r('x ~ y'),
            data = r.data_frame(x=data[:,0], y=data[:,1])
            )['coefficients']

    return reg

def plots(regression_o, getData_o):
    """Plots the dataset with a regression line and a boxplot using R."""
    fname1 = 'car_regress.pdf'
    r.pdf(fname1)
    r.plot(getData_o, ylab='dist', xlab='speed')
    r.abline(regression_o['(Intercept)'], regression_o['y'], col='red')
    r.dev_off()

    fname2 = 'car_hist.pdf'
    r.pdf(fname2)
    r.boxplot(getData_o, names=['dist', 'speed'])
    r.dev_off()

    return fname1, fname2


############################
## PROJECT INITIALIZATION ##
############################

## This function will create a pyleaf project object and separately
## return references to the project object and to its first protocol
## (the only one included in this example).

def prj():
    global o
    pj = project(module_name, 'protocol', lglposition)
    p = pj.protocols['']
    o = p.provide
    return p, pj

