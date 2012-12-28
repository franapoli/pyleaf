
=============
pyleaf README
=============


pyleaf is the Python implementation of the Leaf system. The Leaf
system is a pipeline (AKA data flow or data analysis protocol)
management system that allows to design the pipeline as an ASCII-art
diagram through a language called LGL (Leaf Graph Language, see
https://github.com/franapoli/lglc).


Features
--------

- Thin, lightweight, code-independent Abstraction Layer.
- Data flow graph embedded directly into Python source code.
- Automatic creation and management of variables associated with node
  outputs.
- Automatic persistent storage and retrieval of node outputs.
- Session persistence (i.e. run half project, reboot machine,
  automatically start again from the last processed node).
- Lazy builds (avoid running nodes that are not necessary for the
  build of a requested resource).
- Multiprocessing (independent nodes run in parallel).
- Enforcement of code version consistency between nodes
  (i.e. automatically reprocess all nodes deriving from node A if node
  A is found to be changed).
- Automatic time and space requirements statistics.
- Automatic publishing (producing hypertext with visual representation
  of the protocol, processing statistics, link to node outputs, node
  documentation and source code).


pipeline example
----------------


          / regression -> plots [F]
getData  <
          \  / @plots
           .<
             \ exportCSV [F]


Home Page
---------

       http://www.neuronelab.dmi.unisa.it/leaf


INSTALL
=======

pyleaf *requires* lglc. Get it from 

https://github.com/franapoli/lglc

To install pyleaf:

   > python setup.py install

You may require administrator rights.


Using pyleaf
============

Please check the "doc" directory.
