<!-- Grab your social icons from https://github.com/carlsednaoui/gitsocial -->
[1.2]: http://i.imgur.com/wWzX9uB.png (me on Twitter)
[1]: http://www.twitter.com/franapoli
<!-- Grab your social icons from https://github.com/carlsednaoui/gitsocial -->
On Twitter: [![alt text][1.2]][1]

pyleaf README
=============

pyleaf is the Python implementation of the Leaf system. The Leaf
system is a pipeline (AKA data flow or data analysis protocol)
management system that allows to design the pipeline as an ASCII-art
diagram through a language called LGL (Leaf Graph Language, see
https://github.com/franapoli/lglc - also see INSTALL paragraph below).


Scientific publications
-----------------------

Please consider the reference below to cite Leaf if you are using
it. The paper is also a good introductory guide.

[Napolitano, F., Mariani-Costantini, R., Tagliaferri, R.,
2013. Bioinformatic pipelines in Python with Leaf. BMC Bioinformatics
14, 201.](https://bmcbioinformatics.biomedcentral.com/articles/10.1186/1471-2105-14-201)


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

    https://pythonhosted.org/pyleaf


INSTALL
=======

pyleaf *requires* lglc. Precompiled Windows and Linux binaries are
included in the lglc\_bin directory and must be in the system PATH.

    

C++ sources from:

    https://github.com/franapoli/lglc


To install pyleaf:

   > python setup.py install

You may require administrator rights.


Using pyleaf
============

Please check the "doc" directory (if this is part of a source
distribution you may need to build the documentation, see
"site_and_doc" directory). You may also want to start with the
tutorial "ex1_tut.txt" in the directory "samples".
