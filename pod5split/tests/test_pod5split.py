#!/usr/bin/env python3
# coding: utf-8

import os
import pytest
import shutil

import pod5

# See https://stackoverflow.com/a/8663557
from pathlib import Path
from posixpath import devnull
from _ast import Try
sourceDir = Path(__file__).parent.parent

# See https://stackoverflow.com/a/51234338
exec(open(str(sourceDir / 'pod5split.py')).read())

data_file = sourceDir / "testdata" / 'fourreads.pod5'
out_dir = sourceDir / "testout"

# The correct way to set up before and clean up after each test.
# This function needs to be passed as an argument to each test case.
@pytest.fixture
def setup():
    # Remove any dangling "out" directory from before.
    if out_dir.exists():
        shutil.rmtree(str(out_dir))

    # Make sure out_dir exists.
    out_dir.mkdir(exist_ok = False)

    # Run the test.
    yield

    # Clean up out_dir
    shutil.rmtree(str(out_dir))

def test_parse_defaults():
    args = [ str(data_file) ]

    splitter = Pod5Split()
    splitter.parse(args)

    assert splitter.fileBase == 'fourreads'
    assert splitter.chunkSize == 25000
    assert splitter.outDir == Path.cwd()
    assert splitter.inPod5 == data_file

def test_parse_full():
    args = [ '-b', 'unittest', '-o', str(out_dir), '-r', '150', str(data_file) ]

    splitter = Pod5Split()
    splitter.parse(args)

    assert splitter.fileBase == 'unittest'
    assert splitter.chunkSize == 150
    assert splitter.outDir == out_dir
    assert splitter.inPod5 == data_file

def test_split_into_chunks_of_two(setup):
    args = [ '-b', 'tworeads', '-o', str(out_dir), '-r', '2', str(data_file) ]

    splitter = Pod5Split()
    splitter.parse(args)

    assert splitter.fileBase == 'tworeads'
    assert splitter.chunkSize == 2
    assert splitter.outDir == out_dir
    assert splitter.inPod5 == data_file

    splitter.split()

    chunks = out_dir.glob("tworeads.*.pod5")
    names = [ c.name for c in chunks ]

    assert len(names) == 2, f"Wrong number of chunk files: {len(names)}"

    assert 'tworeads.00000.pod5' in names, "Missing tworeads.00000.pod5"
    _check_read_count(out_dir / 'tworeads.00000.pod5', 2)
    assert 'tworeads.00001.pod5' in names, "Missing tworeads.00001.pod5"
    _check_read_count(out_dir / 'tworeads.00001.pod5', 2)

def test_split_into_chunks_of_three(setup):
    args = [ '-b', 'threereads', '-o', str(out_dir), '-r', '3', str(data_file) ]

    splitter = Pod5Split()
    splitter.parse(args)

    assert splitter.fileBase == 'threereads'
    assert splitter.chunkSize == 3
    assert splitter.outDir == out_dir
    assert splitter.inPod5 == data_file

    splitter.split()

    chunks = out_dir.glob("threereads.*.pod5")
    names = [ c.name for c in chunks ]

    assert len(names) == 2, f"Wrong number of chunk files: {len(names)}"

    assert 'threereads.00000.pod5' in names, "Missing threereads.00000.pod5"
    _check_read_count(out_dir / 'threereads.00000.pod5', 3)
    assert 'threereads.00001.pod5' in names, "Missing threereads.00001.pod5"
    _check_read_count(out_dir / 'threereads.00001.pod5', 1)


def _check_read_count(pod5file, expectedReads):
    with pod5.Reader(pod5file) as reader:
        assert reader.num_reads == expectedReads, f"Have {reader.num_reads} in {pod5file} when expecting {expectedReads}"
