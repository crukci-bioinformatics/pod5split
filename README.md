# Pod5 Split

This tool fills a hole in the [ONT Pod5 tools suite](https://github.com/nanoporetech/pod5-file-format)
to split a large Pod5 file into chunks of a given number of reads.

## Running the Tool

Assuming your environment is set up correctly (see below), the program is run on the command line thus:

```
python3 pod5split.py [-h] [-b <name>] [-o <dir>] [-r <int>] <pod5 file>
```

The required argument is the path to the Pod5 file you want to split. Other options are:

`-b`/`--base`: The base name for the output file chunks. If this is not provided, the base
name of the input pod5 file is used.

`-o`/`--out`: The directory to write the chunk files to. Defaults to the current working
directory if not given. The directory is created if it does not exist.

`-r`/`--reads`: The number of reads to put in each chunk. The default is 25,000.


## Creating the Virtual Environment

This tool has dependencies on the ONT Pod5 Python package, which in turn has its own dependencies.
If you are using the tool outside of a container, you will probably want to create and activate
a Python virtual environment within which you can run the tool.

```BASH
% python3 -m venv venv
% source venv/bin/activate
% pip install -r requirements.txt
```
