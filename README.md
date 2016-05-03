A-plus RST tools
================

Provides tools to publish RST course content for mooc-grader and a-plus.

* http://www.sphinx-doc.org/en/stable/
* http://matplotlib.org/sampledoc/
* http://docutils.sourceforge.net/rst.html


Creating a new course
---------------------

We recommend to start with a fork from the mooc-grader-rst-course repository
from Github.

    git clone --recursive https://github.com/Aalto-LeTech/mooc-grader-rst-course.git

To compile the RST source into HTML the Python sphinx module is required.

    pip install sphinx

The course is compiled with a make.

    make

The tools can be later upgraded.

    git submodule update


Adding tools to existing course
-------------------------------

The tools can be added into a repository as a submodule.

    git submodule add git@github.com:Aalto-LeTech/a-plus-rst-tools.git a-plus-rst-tools

Then installation of sphinx, creation of RST document root and configuring sphinx are required.

    pip install sphinx
    sphinx-quickstart
    cp a-plus-rst-tools/conf.py .
