from distutils.core import setup

setup(
    name = "pyleaf",
    packages = ["pyleaf"],
    package_data={'pyleaf': ['resources/leaf.png','resources/style.css']},
    #data_files=[('pyleaf', ['resources/leaf.png','resources/style.css'])],
    version = "1.0.1",
    description = "ASCII-ART Data Analysis Pipeline Manager",
    author = "Francesco Napolitano",
    author_email = "franapoli@gmail.com",
    url = "www.francesconapolitano.it/leaf/downloads/pyleaf-1.0.1.tar.gz",
    download_url = "www.francesconapolitano.it/leaf/downloads/pyleaf-1.0.1.tar.gz",
    keywords = ["bioinformatics", "data", "pipeline"],
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Topic :: Scientific/Engineering :: Information Analysis",
        ],
    long_description = """\
pyleaf is the Python implementation of the Leaf system. The Leaf
system is a pipeline (AKA data flow or data analysis protocol)
management system that allows to design the pipeline as an ASCII-art
diagram through a language called LGL (Leaf Graph Language, see
https://github.com/franapoli/lglc).

Main Leaf features include:

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
"""
)
