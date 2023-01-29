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

`dcm2mha_cnvtr` is a *ChRIS ds-type* application that files of one type as input and converts to a reciprocal type as output. The reciprocating types of files are DICOM (dcm) and MetaImage Medical Foramt (mha).


Usage
-----

.. code::

    docker run --rm fnndsc/pl-dcm2mha_cnvtr dcm2mha_cnvtr
        [-f|--inputFileFilter <inputFileFilter>]
        [-s|--saveAsPng]
        [-n|--imageName <pngFileName>]
        [-p|--filterPerc <filterPercentage>]
        [-r| --rotate <rotateAngle>]
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
        A glob pattern string, default is "**/*.mha", representing the
        input file pattern to convert. Specify either "**/*mha" or
        "**/*dcm".

        [-s|--saveAsPng]
        If specified, generate a resultant PNG image along with dicoms.

        [-n|--imageName <pngFileName>]
        The name of the resultant PNG file. Default is "composite.png"

        [-p|--filterPerc <filterPercentage>]
        An integer value that represents the threshold for a high-pass
        filter on the image space. Image values less than this percentage
        are set to 0. This field is particularly important if image is
        noisy. Note that valid image data at intensities less than this
        cutoff are of course also filtered out! Default is 30.

        [-r| --rotate <rotateAngle>]
        An integer value in multiples of 90 that represents a rotation
        angle. The input image will be rotated anticlockwise for the
        provide angle.

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

Convert a set of DICOM files in a directory called `dicom` to MHA files in a directory called `mha`:

.. code:: bash

    docker run -v $PWD/dicom:/incoming -v $PWD/mha:/outgoing    \
                fnndsc/pl-dcm2mha_cnvtr dcm2mha_cnvtr           \
                --inputFileFilter "**/*.dcm"                    \
                /incoming /outgoing

and convert these back to DICOM again

.. code:: bash

    docker run -v $PWD/mha:/incoming -v $PWD/dicom:/outgoing    \
                fnndsc/pl-dcm2mha_cnvtr dcm2mha_cnvtr           \
                --inputFileFilter "**/*.mha"                    \
                /incoming /outgoing




.. image:: https://raw.githubusercontent.com/FNNDSC/cookiecutter-chrisapp/master/doc/assets/badge/light.png
    :target: https://chrisstore.co
