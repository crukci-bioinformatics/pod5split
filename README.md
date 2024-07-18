# Pod5 Split

This tool fills a hole in the [ONT Pod5 tools suite](https://github.com/nanoporetech/pod5-file-format)
to split a large Pod5 file into chunks of a given number of reads.

## Running the Tool

Assuming your environment is set up correctly (see below), the program is run on the command line thus:

```
usage: pod5split.py [-h] [-b <name>] [-o <dir>] [-r <int>] [-t <int>]
                    <pod5 file>

Split a Pod5 file into smaller files of a specified number of reads.

positional arguments:
  <pod5 file>           The Pod5 file to split.

optional arguments:
  -h, --help            show this help message and exit
  -b <name>, --base <name>
                        The base name for the output files.
  -o <dir>, --out <dir>
                        The directory to write the file's chunks to.
  -r <int>, --reads <int>
                        The number of reads in each chunk. Default 25000.
  -t <int>, --threads <int>
                        The number of parallel threads to use. Default is 4.

The default output directory is the current working directory. The default
name is the base name of the input file.
```


## Creating the Virtual Environment

This tool has dependencies on the ONT Pod5 Python package, which in turn has its own dependencies.
If you are using the tool outside of a container, you will probably want to create and activate
a Python virtual environment within which you can run the tool.

```BASH
% python3 -m venv venv
% source venv/bin/activate
% pip install -r requirements.txt
```

## Unit Tests

The unit test relies on `pytest`. This will be installed in the virtual environment with the
other dependencies. Running the test is simply typing at the top level:

```BASH
pytest
```
