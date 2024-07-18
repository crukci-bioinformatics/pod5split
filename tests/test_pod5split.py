#!/usr/bin/env python3
# coding: utf-8

import sys
import pytest
import unittest
import shutil
from unittest.mock import patch, MagicMock, create_autospec

import pod5

from pathlib import Path
from posixpath import devnull
from _ast import Try

from tempfile import TemporaryDirectory

sourceDir = Path(__file__).parent.parent
sys.path.insert(0, str(sourceDir))
from pod5split import process_chunk


# See https://stackoverflow.com/a/51234338
exec(open(str(sourceDir / "pod5split.py")).read())

data_file = sourceDir / "testdata" / "fourreads.pod5"
out_dir = sourceDir / "testout"


# The correct way to set up before and clean up after each test.
# This function needs to be passed as an argument to each test case.
@pytest.fixture
def setup():
    # Remove any dangling "out" directory from before.
    if out_dir.exists():
        shutil.rmtree(str(out_dir))

    # Make sure out_dir exists.
    out_dir.mkdir(exist_ok=False)

    # Run the test.
    yield

    # Clean up out_dir
    shutil.rmtree(str(out_dir))


def test_parse_defaults():
    args = [str(data_file)]

    splitter = Pod5Split()
    splitter.parse(args)

    assert splitter.fileBase == "fourreads"
    assert splitter.chunkSize == 25000
    assert splitter.outDir == Path.cwd()
    assert splitter.inPod5 == data_file
    assert splitter.threads == DEFAULT_THREADS


def test_parse_full():
    args = [
        "-b",
        "unittest",
        "-o",
        str(out_dir),
        "-r",
        "150",
        "-t",
        "4",
        str(data_file),
    ]

    splitter = Pod5Split()
    splitter.parse(args)

    assert splitter.fileBase == "unittest"
    assert splitter.chunkSize == 150
    assert splitter.outDir == out_dir
    assert splitter.inPod5 == data_file
    assert splitter.threads == 4


def test_split_into_chunks_of_two(setup):
    args = ["-b", "tworeads", "-o", str(out_dir), "-r", "2", "-t", "2", str(data_file)]

    splitter = Pod5Split()
    splitter.parse(args)

    assert splitter.fileBase == "tworeads"
    assert splitter.chunkSize == 2
    assert splitter.outDir == out_dir
    assert splitter.inPod5 == data_file
    assert splitter.threads == 2

    splitter.split()

    chunks = out_dir.glob("tworeads.*.pod5")
    names = [c.name for c in chunks]

    assert len(names) == 2, f"Wrong number of chunk files: {len(names)}"

    assert "tworeads.00000.pod5" in names, "Missing tworeads.00000.pod5"
    _check_read_count(out_dir / "tworeads.00000.pod5", 2)
    assert "tworeads.00001.pod5" in names, "Missing tworeads.00001.pod5"
    _check_read_count(out_dir / "tworeads.00001.pod5", 2)


def test_split_into_chunks_of_three(setup):
    args = [
        "-b",
        "threereads",
        "-o",
        str(out_dir),
        "-r",
        "3",
        "-t",
        "1",
        str(data_file),
    ]

    splitter = Pod5Split()
    splitter.parse(args)

    assert splitter.fileBase == "threereads"
    assert splitter.chunkSize == 3
    assert splitter.outDir == out_dir
    assert splitter.inPod5 == data_file
    assert splitter.threads == 1

    splitter.split()

    chunks = out_dir.glob("threereads.*.pod5")
    names = [c.name for c in chunks]

    assert len(names) == 2, f"Wrong number of chunk files: {len(names)}"

    assert "threereads.00000.pod5" in names, "Missing threereads.00000.pod5"
    _check_read_count(out_dir / "threereads.00000.pod5", 3)
    assert "threereads.00001.pod5" in names, "Missing threereads.00001.pod5"
    _check_read_count(out_dir / "threereads.00001.pod5", 1)

def _check_read_count(pod5file, expectedReads):
    with pod5.Reader(pod5file) as reader:
        assert (
            reader.num_reads == expectedReads
        ), f"Have {reader.num_reads} in {pod5file} when expecting {expectedReads}"

class TestProcessChunk(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for output
        self.temp_dir = TemporaryDirectory()
        self.outDir = Path(self.temp_dir.name)
        # Define the path to the input file
        self.inPod5 = Path(data_file)

    def tearDown(self):
        # Clean up the temporary directory
        self.temp_dir.cleanup()

    def test_process_chunk(self):
        # Define test data
        chunk_data = (
            1,
            [
                "25621b7d-c8c4-4571-9861-650be08d8a57",
                "1cf788e5-cb7b-45eb-a507-41e7d47985af",
            ],
            self.inPod5,
            self.outDir,
            "test_chunk",
        )
        # Process the chunk
        chunkPath, numReadIds = process_chunk(chunk_data)
        # Assertions
        self.assertTrue(chunkPath.exists(), "Chunk file does not exist.")
        self.assertEqual(numReadIds, 2, "Number of read IDs does not match.")
