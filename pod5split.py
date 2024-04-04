#!/usr/bin/env python3

import os
import pod5
import sys

from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Collection

from tqdm.auto import tqdm
from pod5.repack import Repacker

from pod5.tools.utils import (
    DEFAULT_THREADS,
    PBAR_DEFAULTS,
    collect_inputs,
    init_logging,
    logged_all,
)

logger = init_logging()

class Pod5Split():

    def __init__(self):
        self.parser = ArgumentParser(
                            prog='pod5split',
                            description='Split a Pod5 file into smaller files of a specified number of reads.',
                            epilog='The default output directory is the current working directory.\nThe default name is the base name of the input file.')
        self.parser.add_argument('-r', '--reads', metavar = 'int', default = 25000, dest = 'chunkSize', type = int)
        self.parser.add_argument('-i', '--in', metavar = 'file', dest = 'inBam', required = True, type = Path)
        self.parser.add_argument('-o', '--out', metavar = 'dir', dest = 'outDir', type = Path)
        self.parser.add_argument('-b', '--base', metavar = 'name', dest = 'fileBase')
        # self.parser.add_argument('-t', '--threads', metavar = 'int', default = DEFAULT_THREADS, dest = 'threads', type = int)

    def parse(self, args = None):
        self.parser.parse_args(args, self)
        if not self.outDir:
            self.outDir = Path(os.getcwd())
        if not self.fileBase:
            self.fileBase = self.inBam.stem
        if self.chunkSize < 1:
            self.chunkSize = 1
        #if self.threads < 1:
        #    self.threads = 1

    def split(self):
        if not self.outDir.exists():
            self.outDir.mkdir(exist_ok = True)

        with pod5.Reader(self.inBam) as reader:
            expectedChunks = (reader.num_reads + self.chunkSize - 1) // self.chunkSize
            expectedKReads = (reader.num_reads + 999) // 1000

            pbar = tqdm(
                total = expectedKReads,
                desc="Splitting",
                unit="kRead",
                leave=True,
                position=0,
                **PBAR_DEFAULTS,
            )

            chunkReadIds = []
            chunkNumber = 0
            readNumber = 0

            for pod5Record in reader:
                chunkReadIds.append(pod5Record.read_id)

                readNumber += 1
                if readNumber % 1000 == 0:
                    pbar.update(readNumber // 1000)

                if len(chunkReadIds) >= self.chunkSize:

                    self._writeChunk(reader, chunkNumber, chunkReadIds)

                    chunkReadIds.clear()
                    chunkNumber += 1

                    #pbar.update(chunkNumber)

            if len(chunkReadIds) > 0:
                self._writeChunk(reader, chunkNumber, readIds)
                pbar.update(expectedKReads)

            pbar.close()

    def _writeChunk(self, reader: pod5.Reader, chunkNumber: int, readIds: Collection[str]):
        chunkName = f"{self.fileBase}_{chunkNumber:05d}.pod5"
        chunkPath = self.outDir / chunkName

        chunkPath.unlink(True)

        repacker = Repacker()

        with pod5.Writer(chunkPath) as writer:
            repackerOut = repacker.add_output(writer)

            repacker.add_selected_reads_to_output(repackerOut, reader, readIds)
            repacker.set_output_finished(repackerOut)

        repacker.finish()
        del repacker


if __name__ == "__main__":
    splitter = Pod5Split()
    splitter.parse()
    splitter.split()
