#!/usr/bin/env python3

import gzip
import click
import tempfile
import os
from collections import defaultdict
from typing import Generator

RANK_SCORE_KEY = "RankScore="
RANK_SCORE_KEY_LEN = len(RANK_SCORE_KEY)


def open_vcf(path_to_vcf: str) -> Generator:
    """
    Open compressed/uncompressed vcf
    """

    def _vcf_file_generator():

        if path_to_vcf.endswith(".gz"):
            with gzip.open(path_to_vcf, "rt") as vcf_handle:
                for line in vcf_handle:
                    yield line
        else:
            with open(path_to_vcf, "rt") as vcf_handle:
                for line in vcf_handle:
                    yield line

    return _vcf_file_generator()


def get_id_fields(vcf_row):
    vcf_row = vcf_row.split("\t")
    return (vcf_row[0], vcf_row[1], vcf_row[3], vcf_row[4])


def process_vcf_into_scores(vcf) -> dict[tuple, int]:

    scores = {}

    for line in vcf:
        if line.startswith("#"):
            continue
        rank = _get_rankscore(line)
        key = get_id_fields(line)
        scores[key] = rank

    return scores


@click.command()
@click.argument("vcf_file1", type=click.Path(exists=True))
@click.argument("vcf_file2", type=click.Path(exists=True), required=False)
def compare_rank_score(vcf_file1: str, vcf_file2: str | None = None):
    """
    derp
    """
    vcf = open_vcf(vcf_file1)
    scores = process_vcf_into_scores(vcf)

    if vcf_file2 is not None:
        ...
        combined = defaultdict(dict)

        for key, score in scores.items():
            combined[key][vcf_file1] = score

        vcf2 = open_vcf(vcf_file2)
        scores2 = process_vcf_into_scores(vcf2)

        for key, score in scores2.items():
            combined[key][vcf_file2] = score

    for variant_ids, score in scores.items():
        row = list(variant_ids) + [str(score)]
        print("\t".join(row))


def _get_rankscore(line: str) -> int:

    score = (
        line[line.find(RANK_SCORE_KEY) + RANK_SCORE_KEY_LEN :]
        .split(":")[1]
        .split(";")[0]
    )
    return int(score)


if __name__ == "__main__":
    compare_rank_score()
