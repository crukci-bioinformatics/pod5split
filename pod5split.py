#!/usr/bin/env python3
# coding: utf-8

import os
import pod5
import sys

from argparse import ArgumentParser, Namespace
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from time import sleep
from typing import Collection, List, Tuple

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


def process_chunk(chunk_data: Tuple[int, List[str], Path, Path]) -> Tuple[Path, int]:
    """
    Process a chunk of data.

    Args:
        chunk_data (Tuple[int, List[str], Path, Path, str]): A tuple containing the chunk data.
            - chunkNumber (int): The number of the chunk.
            - chunkReadIds (List[str]): The list of read IDs in the chunk.
            - inPod5 (Path): The input pod5 file path.
            - chunkPath (Path): The chunk's output file.

    Returns:
        Tuple[Path, int]: A tuple containing the chunk path and the number of read IDs in the chunk.
    """
    chunkNumber, chunkReadIds, inPod5, chunkPath = chunk_data

    chunkPath.unlink(missing_ok=True)

    with pod5.Reader(inPod5) as reader:
        with pod5.Writer(chunkPath) as writer:
            repacker = Repacker()
            repackerOut = repacker.add_output(writer)
            repacker.add_selected_reads_to_output(repackerOut, reader, chunkReadIds)
            repacker.set_output_finished(repackerOut)
            repacker.finish()

    return chunkPath, len(chunkReadIds)


class Pod5Split:
    def __init__(self):
        self.parser = ArgumentParser(
                            prog='pod5split.py',
                            description='Split a Pod5 file into smaller files of a specified number of reads.',
                            epilog='The default output directory is the current working directory. The default name is the base name of the input file.')
        self.parser.add_argument('-b', '--base', metavar = '<name>', dest = 'fileBase', help = "The base name for the output files.")
        self.parser.add_argument('-o', '--out', metavar = '<dir>', dest = 'outDir', type = Path, help = "The directory to write the file's chunks to.")
        self.parser.add_argument('-r', '--reads', metavar = '<int>', default = 25000, dest = 'chunkSize', type = int, help = "The number of reads in each chunk. Default 25000.")
        self.parser.add_argument('-t', '--threads', metavar='<int>', default = DEFAULT_THREADS, dest='threads', type = int, help=f"The number of parallel threads to use. Default {DEFAULT_THREADS}.")
        self.parser.add_argument('inPod5', metavar = '<pod5 file>', type = Path, help = "The Pod5 file to split.")

    def parse(self, args = None):
        self.parser.parse_args(args, self)
        if not self.outDir:
            self.outDir = Path.cwd()
        if not self.fileBase:
            self.fileBase = self.inPod5.stem
        if self.chunkSize < 1:
            self.chunkSize = 1

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

        totalChunks = (totalReads + self.chunkSize - 1) // self.chunkSize

        chunkList = []
        for chunkNumber in range(totalChunks):
            start = chunkNumber * self.chunkSize
            end = min((chunkNumber + 1) * self.chunkSize, totalReads)
            chunkReadIds = allReadIds[start:end]

            chunkPath = self.outDir / f"{self.fileBase}.{chunkNumber:05d}.pod5"

            chunkInfo = ( chunkNumber, chunkReadIds, self.inPod5, chunkPath )
            chunkList.append(chunkInfo)

        futures = {}
        with ProcessPoolExecutor(max_workers = self.threads) as executor:
            pbar = tqdm(
                total = totalReads,
                desc = "Splitting",
                unit = " reads",
                leave = True,
                colour = 'green',
                **PBAR_DEFAULTS,
            )

            for chunk in chunkList:
                futures[executor.submit(process_chunk, chunk)] = chunk[0]

            for future in as_completed(futures):
                chunkPath, chunk_size = future.result()
                pbar.update(chunk_size)

            pbar.close()

if __name__ == "__main__":
    splitter = Pod5Split()
    splitter.parse()
    splitter.split()
