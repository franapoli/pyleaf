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



""" Verbosity codes:
    -1: Shut up! Nothing is output (possibly dangerous).
    0: Show only errors and warnings.
    1: [Default] Show some run time info (like resource load/dump).
    2: Show debug info (can be very verbous).
    3: Show also resource contents (even more verbous).
    """

from datetime import datetime
import inspect

filopt = dict()
stdopt = dict()
    
filopt['verbosity'] = 2
filopt['showStackLevel'] = True
filopt['showIndent'] = True
filopt['showTime'] = True
filopt['showCaller'] = True
filopt['showCallerStack'] = False

stdopt['verbosity'] = 1
stdopt['showStackLevel'] = False
stdopt['showIndent'] = False
stdopt['showTime'] = False
stdopt['showCaller'] = False
stdopt['showCallerStack'] = False


base_stack_level = -1
lastmsg = None
termcolor = '32'
logfilename = 'autolog.log'
logfile = None

from inspect import stack

def colorize(txt):
    return txt
    #return '\033[' + termcolor +'m'+ txt + '\033[0m'
    
def insertBreak():
    global filopt
    if filopt['verbosity'] > -1:
        ostr = '\n'
        try:
            logfile.write(ostr+'\n')
        except:
            pass
    print('\n')
        
def makeLogString(string, logopt, caller, callerStack, curr_lev):
    outstr = '[L'
    if logopt['showStackLevel']:
        outstr += str(curr_lev)
    if logopt['showIndent']:
        outstr += '   ' * curr_lev
    if logopt['showCaller'] or logopt['showTime']:
        outstr += ' '
    if logopt['showTime']:
        outstr += str(datetime.today())[11:-7]
    if logopt['showCaller']:
        if logopt['showTime']:
            outstr += ', '
        if logopt['showCallerStack']:
            outstr += callerStack
        else:
            outstr += caller
    #if logopt['showCaller'] or logopt['showTime']:
    outstr += ']'



    if string == '':
        outstr += 'I''m working right now.'
    else:
        if outstr != '':
            outstr += ' ' + string
        else:
            outstr += string
        
    return outstr

def send(string='', verbosity=1):    
    global base_stack_level, lastmsg, stdopt, filopt
#    if string==lastmsg:
#       return
    
    if verbosity <= filopt['verbosity'] or verbosity <= stdopt['verbosity']:
        if stdopt['showCaller'] or filopt['showCaller']:
            if len(stack()) <= base_stack_level or base_stack_level == -1:
                base_stack_level = len(stack())
        
            curr_lev = len(stack()) - base_stack_level        
            caller = inspect.stack()[1][3]
        else:
            caller=''
            curr_lev=0

        if stdopt['showCallerStack'] or filopt['showCallerStack']:
            callerstack = getStackPath()[2:]
            if 'runcode' in callerstack:
                del(callerstack[callerstack.index('runcode'):])
            if 'runfile' in callerstack:
                del(callerstack[callerstack.index('runfile'):])
            callerstack = str(callerstack).strip('[]').replace(', ','.').replace('\'','')
        else:
            callerstack=''
        
        if verbosity <= filopt['verbosity']:
            try:
                outstr_file = makeLogString(string, filopt, caller, callerstack, curr_lev)
                logfile.write(outstr_file+'\n')
            except:
                pass

        if verbosity <= stdopt['verbosity']:
            outstr_std = makeLogString(string, stdopt, caller, callerstack, curr_lev)        
            print(colorize(outstr_std))

    lastmsg = string

def startline():
    global filopt, logfile, logfilename
    if filopt['verbosity'] > -1:
        ostr = '*** Starting log session on ' + str(datetime.today())[0:-7] + '. ***'
        logfile = open(logfilename, 'a')
        logfile.write(ostr+'\n')    
    
def endline():
    global filopt, logfile
    if filopt['verbosity'] > -1:
        ostr = '*** Ending log session on ' + str(datetime.today())[0:-7] + '. ***'
        logfile.write(ostr+'\n')
        logfile.close()
        
    
def getStackPath():
    path=list()
    for frame in inspect.stack():
        path.append(frame[3])

    return path
