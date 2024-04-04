#!/usr/bin/env python3

import os
import pod5
import sys

from argparse import ArgumentParser, Namespace
from pathlib import Path
from time import sleep
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
                            prog='pod5split.py',
                            description='Split a Pod5 file into smaller files of a specified number of reads.',
                            epilog='The default output directory is the current working directory. The default name is the base name of the input file.')
        self.parser.add_argument('-b', '--base', metavar = '<name>', dest = 'fileBase', help = "The base name for the output files.")
        self.parser.add_argument('-o', '--out', metavar = '<dir>', dest = 'outDir', type = Path, help = "The directory to write the file's chunks to.")
        self.parser.add_argument('-r', '--reads', metavar = '<int>', default = 25000, dest = 'chunkSize', type = int, help = "The number of reads in each chunk. Default 25000.")
        self.parser.add_argument('inPod5', metavar = '<pod5 file>', type = Path, help = "The Pod5 file to split.")
        # self.parser.add_argument('-t', '--threads', metavar = 'int', default = DEFAULT_THREADS, dest = 'threads', type = int)

    def parse(self, args = None):
        self.parser.parse_args(args, self)
        if not self.outDir:
            self.outDir = Path(os.getcwd())
        if not self.fileBase:
            self.fileBase = self.inPod5.stem
        if self.chunkSize < 1:
            self.chunkSize = 1
        #if self.threads < 1:
        #    self.threads = 1

    @logged_all
    def split(self):
        if not self.outDir.exists():
            self.outDir.mkdir(exist_ok = True)

        allReadIds = []
        totalReads = 0

        with pod5.Reader(self.inPod5) as reader:
            totalReads = reader.num_reads
            for pod5Record in reader:
                allReadIds.append(pod5Record.read_id)

        totalChunks = (totalReads + self.chunkSize - 1) / self.chunkSize

        pbar = tqdm(
            total = totalReads,
            desc = "Splitting",
            unit = " reads",
            leave = True,
            colour = 'green',
            **PBAR_DEFAULTS,
        )

        chunkNumber = 0
        while chunkNumber < totalChunks:
            start = chunkNumber * self.chunkSize
            end = min((chunkNumber + 1) * self.chunkSize, totalReads)

            chunkReadIds = allReadIds[start:end]

            chunkName = f"{self.fileBase}.{chunkNumber:05d}.pod5"
            chunkPath = self.outDir / chunkName

            chunkPath.unlink(True)

            with pod5.Reader(self.inPod5) as reader:
                with pod5.Writer(chunkPath) as writer:
                    repacker = Repacker()
                    repackerOut = repacker.add_output(writer)
                    repacker.add_selected_reads_to_output(repackerOut, reader, chunkReadIds)
                    repacker.set_output_finished(repackerOut)
                    repacker.finish()

            pbar.update(len(chunkReadIds))

            chunkNumber += 1

        pbar.close()

if __name__ == "__main__":
    splitter = Pod5Split()
    splitter.parse()
    splitter.split()
