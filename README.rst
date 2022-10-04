pl-dcm2mha_cnvtr
================================

.. image:: https://img.shields.io/docker/v/fnndsc/pl-dcm2mha_cnvtr?sort=semver
    :target: https://hub.docker.com/r/fnndsc/pl-dcm2mha_cnvtr

.. image:: https://img.shields.io/github/license/fnndsc/pl-dcm2mha_cnvtr
    :target: https://github.com/FNNDSC/pl-dcm2mha_cnvtr/blob/master/LICENSE

.. image:: https://github.com/FNNDSC/pl-dcm2mha_cnvtr/workflows/ci/badge.svg
    :target: https://github.com/FNNDSC/pl-dcm2mha_cnvtr/actions


.. contents:: Table of Contents


Abstract
--------

An app  to convert dcm files to mha and vice-versa 


Description
-----------


``dcm2mha_cnvtr`` is a *ChRIS ds-type* application that takes in .mha/.dcm as input files
and produces .dcm/.mha files as output


Usage
-----

.. code::

    docker run --rm fnndsc/pl-dcm2mha_cnvtr dcm2mha_cnvtr
        [-f|--inputFileFilter <inputFileFilter>]
        [-s|--saveAsPng]                                           
        [-n|--imageName <pngFileName>]                             
        [-p|--filterPerc <filterPercentage>]                        
        [-h|--help]
        [--json] [--man] [--meta]
        [--savejson <DIR>]
        [-v|--verbosity <level>]
        [--version]
        <inputDir> <outputDir>


Arguments
~~~~~~~~~

.. code::
    [-f|--inputFileFilter <inputFileFilter>]
    A glob pattern string, default is "**/*.mha",
    representing the input file that we want to
    convert. You can choose either .mha or .dcm
    files
    
    [-s|--saveAsPng]  
    If specified, generate a resultant PNG image along with dicoms
                                                 
    [-n|--imageName <pngFileName>]
    The name of the resultant PNG file. Default is "composite.png"
                                               
    [-p|--filterPerc <filterPercentage>]
    An integer value that represents the lowest percentage of the
    maximum intensity of the PNG image that should be set to 0. 
    This field is particularly important if there is too much noise 
    in an image and we want to get a sharper resultant PNG. Default
    is 30               
        
    [-h] [--help]
    If specified, show help message and exit.
    
    [--json]
    If specified, show json representation of app and exit.
    
    [--man]
    If specified, print (this) man page and exit.

    [--meta]
    If specified, print plugin meta data and exit.
    
    [--savejson <DIR>] 
    If specified, save json representation file to DIR and exit. 
    
    [-v <level>] [--verbosity <level>]
    Verbosity level for app. Not used currently.
    
    [--version]
    If specified, print version number and exit. 


Getting inline help is:

.. code:: bash

    docker run --rm fnndsc/pl-dcm2mha_cnvtr dcm2mha_cnvtr --man

Run
~~~

You need to specify input and output directories using the `-v` flag to `docker run`.


.. code:: bash

    docker run --rm -u $(id -u)                             \
        -v $(pwd)/in:/incoming -v $(pwd)/out:/outgoing      \
        fnndsc/pl-dcm2mha_cnvtr dcm2mha_cnvtr               \
        /incoming /outgoing


Development
-----------

Build the Docker container:

.. code:: bash

    docker build -t local/pl-dcm2mha_cnvtr .

Run unit tests:

.. code:: bash

    docker run --rm local/pl-dcm2mha_cnvtr nosetests

Examples
--------

Put some examples here!


.. image:: https://raw.githubusercontent.com/FNNDSC/cookiecutter-chrisapp/master/doc/assets/badge/light.png
    :target: https://chrisstore.co
