[![](https://travis-ci.org/etetoolkit/ete.svg?branch=ete4)](https://travis-ci.org/etetoolkit/ete)
[![Join the chat at https://gitter.im/jhcepas/ete](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/jhcepas/ete?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)
![](https://coveralls.io/repos/jhcepas/ete/badge.png)
[![](http://img.shields.io/badge/stackoverflow-etetoolkit-blue.svg)](https://stackoverflow.com/questions/tagged/etetoolkit+or+ete4)
[![](http://img.shields.io/badge/biostars-etetoolkit-purple.svg)](https://www.biostars.org/t/etetoolkit,ete,ete2,ete3,ete4/)
[![](https://img.shields.io/badge/Contributor%20Covenant-2.0-4baaaa.svg)](CODE_OF_CONDUCT.md)


# Overview

ETE (Environment for Tree Exploration) is a toolkit that assists in
the automated manipulation, analysis and visualization of trees. It is
mainly written in Python, and includes many extra functionalities for
phylogenetic trees.

Its main features include:

- Read and write support for trees in Newick format
- Multiple functions for traversing, searching and manipulating tree topologies and node annotations
- Integration with NCBI Taxonomic database
- Integration with GTDB database
- Programmatic visualization framework
- Visualization of huge trees based on adaptive zooming
- Comparing trees
- Phylogenetic functions
  - orthology detection
  - phylogenetic distance?
- Command line tools
  - phylogenetic reconstruction protocols
  - tree comparison
  - tree diff

If you use ETE, please cite:

    Jaime Huerta-Cepas, François Serra and Peer Bork. "ETE 3: Reconstruction,
    analysis and visualization of phylogenomic data."  Mol Biol Evol (2016) doi:
    10.1093/molbev/msw046


# Installation and documentation

The official website of ETE is http://etetoolkit.org. You can find
downloading instructions and further documentation there, or in the
next subsection specifically for ETE v4.

News and announcements are usually posted on twitter:
http://twitter.com/etetoolkit


## Installation of ETE v4

To start
- Clone this repo to local computer with `git clone
  https://github.com/etetoolkit/ete.git` (or `git clone
  git@github.com:etetoolkit/ete.git` if you have the right
  permissions)
- Change to ete4 branch `git checkout ete4`
- Install dependecies
  - [Cython](https://cython.org/) (you can install it through
    [Conda](https://conda.io/) with `mamba install cython` or `conda
    install -c conda-forge cython`)
  - Additional dependencies: `flask flask-cors flask-httpauth
    flask-restful flask-compress numpy PyQt5` (you can
    install them with `pip install <list of dependencies>`)
- Build and install ete4 from repo's root directory: `pip install -e .`

(In Linux there may be some cases where the gcc library must be
installed, which can be done with `conda install -c conda-forge
gcc_linux-64`)


# Gallery of examples

![](https://raw.githubusercontent.com/jhcepas/ete/master/sdoc/gallery.png)


# Getting support

Rather than sending direct support-related emails to the developers,
it is better to keep the communication public.

For question on how to use ETE in the bioinformatics context, use
[Biostars](http://biostars.org) with the `etetoolkit` tag, or [stack
overflow](https://stackoverflow.com/questions/tagged/etetoolkit+or+ete4).

[![](http://img.shields.io/badge/biostars-etetoolkit-purple.svg)](https://www.biostars.org/post/search/?query=etetoolkit+or+ete+or+ete2+or+ete3+or+ete4)
[![](http://img.shields.io/badge/stackoverflow-etetoolkit-blue.svg)](https://stackoverflow.com/questions/tagged/etetoolkit+or+ete3+or+ete4)

For bug reports, feature requests and general discussion, use
https://github.com/etetoolkit/ete/issues

For more technical problems, you can also use the official ETE mailing
list at https://groups.google.com/d/forum/etetoolkit. To avoid spam,
messages from new users are moderated. Expect some delay until your
first message appears after your account is validated.

For any other inquiries (collaborations, sponsoring, etc), please
contact jhcepas@gmail.com.


# Contributing and bug reporting

https://github.com/etetoolkit/ete/wiki/Contributing


# Roadmap

https://github.com/etetoolkit/ete/wiki/ROADMAP
