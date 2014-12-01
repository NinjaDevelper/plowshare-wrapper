# Plowshare Wrapper
[![Build Status](https://travis-ci.org/Storj/plowshare-wrapper.svg)](https://travis-ci.org/Storj/plowshare-wrapper)
[![Coverage Status](https://coveralls.io/repos/Storj/plowshare-wrapper/badge.png?branch=master)](https://coveralls.io/r/Storj/plowshare-wrapper?branch=master)

Python wrapper for managing multi-host uploads and downloads using [plowshare](https://code.google.com/p/plowshare/). After uploading it returns an object with links to the file it uploaded. This wrapper contains both a Python module and a command line tool.

## Installation

Check [INSTALL.md](INSTALL.md) for installation instructions.

## Module Usage

### Upload

This module is composed of a single class, which can be used to upload a file to multiple hosts at once. Example:

    import plowshare

    p = plowshare.Plowshare()
    p.upload("/home/jessie/documents/README.md", 3)


The above example uploads the given file to three different hosts, chosen at random from a predefined list. This list is a subset of the available plowshare modules, limited to the ones that allow anonymous access. You can check it in plowshare/hosts.py

You can also specify a list of hosts (plowshare module names) to use:

    import plowshare

    p = plowshare.Plowshare(['turbobit', 'multiupload', 'exoshare', 'rghost', 'bayfiles'])
    p.upload("/home/jessie/documents/README.md", 3)


The upload method returns an array of objects with the hosts and URLs to which it uploaded the file. If some of the uploads fail, it doesn't return an URL, but an error flag instead.

Here's an example:

    [
        { "host_name": "mediafire",  "url":   "http://www.mediafire.com/?qorncpzfe74s9" },
        { "host_name": "rapidshare", "url":   "http://rapidshare.com/files/130403982" },
        { "host_name": "anonfiles",  "error": true }
    ]

### Download

You can also download uploaded files, by providing the object that the upload method generated, and the directory and filename where to download the file. This method returns an object that contains the path where the file was downloaded, or an object with the error message. Example:

    import plowshare

    uploads = [
        { "host_name": "mediafire",  "url":"http://www.mediafire.com/?qorncpzfe74s9" },
        { "host_name": "rapidshare", "url":"http://rapidshare.com/files/130403982" },
        { "host_name": "anonfiles",  "error":true }
    ]

    p = plowshare.Plowshare()
    p.download(info, "/tmp/", "readme_copy.md")


If multiple sources are provided, they are used as failovers for downloading the file. If at least one source is successful, the others won't be attempted and `download()` will return an object with the full path filename and the first host it successfuly downloaded it from:

    { "host_name": "mediafire", "filename": "/tmp/readme_copy.md" }


There are multiple errors that can occur. Here's a list of the currently supported errors:

    { "error": "no valid sources" }     # the provided object does not contain a valid source URL
    { "error": "<error message>" }      # something went wrong with invoking the plowshare commands


## Command Line Tool Usage

plowshare-wrapper comes with a command line tool to upload a single file to a given number of anonymous hosts. If you have installed it by just cloning this repository, you can run:

    $ bin/tool.py <file location> <number of hosts to upload to>


For example, the following uploads this project's README to five different hosts, chosen at random:

    $ bin/tool.py README.md 5

The command prints out a json representation of the result status object.
Details on the format of the json can be seen above.


## Testing

To run tests, ensure `plowshare-wrapper` is installed and execute the following command in the project root:

    $ python setup.py install
    $ python setup.py test -a "--doctest-modules --pep8 -v tests/"

To run tests with detailed coverage output, execute:
    
    $ coverage run setup.py test -a "--doctest-modules --pep8 -v tests/"
    $ coverage report -m --include="plowshare-wrapper/*"
