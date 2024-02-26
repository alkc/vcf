#!/usr/bin/env python3

import gzip
from collections import defaultdict
from typing import Generator

import click

RANK_SCORE_KEY = "RankScore"
RANK_SCORE_KEY_LEN = len(RANK_SCORE_KEY)


@click.command(help="Print nextflow_wgs rank scores for up to two VCF files")
@click.argument("vcf_file1", type=click.Path(exists=True))
@click.argument("vcf_file2", type=click.Path(exists=True), required=False)
@click.option(
    "--skip-identical",
    is_flag=True,
    default=False,
    help="Only print variants where scores diff between compared files.",
)
@click.option(
    "--output-difference",
    is_flag=True,
    default=False,
    help="Only print variants where scores diff between compared files.",
)
@click.option(
    "--only-scores-above",
    default=None,
    type=int,
    help="Only print variants where scores diff between compared files.",
)
def compare_rank_score(
    vcf_file1: str,
    vcf_file2: str | None = None,
    skip_identical: bool = False,
    output_difference: bool = False,
    only_scores_above: int | None = None,
) -> None:
    """
    Print comparison of rank scores for two VCF files

    Or just extract scores for one file, if you feel like it
    """
    vcf = open_vcf(vcf_file1)
    scores = process_vcf_into_scores(vcf)

    if vcf_file2 is not None:
        files = (vcf_file1, vcf_file2)

        combined = defaultdict(dict)

        for key, score in scores.items():
            combined[key][vcf_file1] = score

        vcf2 = open_vcf(vcf_file2)
        scores2 = process_vcf_into_scores(vcf2)

        for key, score in scores2.items():
            combined[key][vcf_file2] = score

        unique_keys = sorted(combined.keys(), key=lambda x: (x[0], int(x[1]), x[2], x[3]))

        header = ["CHROM", "POS", "REF", "ALT"]
        header += list(files)

        if output_difference:
            header.append("diff_vcf1_to_vcf2")
            header.append("absolute_difference")

        print("\t".join(header))

        for key in unique_keys:
            row = list(key)

            score1 = combined[key].get(files[0], "NA")
            score2 = combined[key].get(files[1], "NA")

            if skip_identical and (score1 == score2):
                continue

            if only_scores_above is not None and (
                score1 < only_scores_above and score2 < only_scores_above
            ):
                continue

            row.append(score1)
            row.append(score2)

            if output_difference:
                # TODO: convert back into ints? sure. for now.
                diff = score2 - score1
                row.append(diff)
                row.append(str(diff).lstrip("-"))

            print("\t".join(str(x) for x in row))

    else:
        for variant_ids, score in scores.items():
            row = list(variant_ids) + [str(score)]
            print("\t".join(row))


def open_vcf(path_to_vcf: str) -> Generator:
    """
    Open compressed/uncompressed vcf
    """

    def _vcf_file_generator():
        open_func = gzip.open if path_to_vcf.endswith(".gz") else open
        with open_func(path_to_vcf, "rt") as vcf_handle:
            for line in vcf_handle:
                yield line

    return _vcf_file_generator()


def get_id_fields(vcf_row: str) -> tuple[str]:
    """
    shrug emoji.

    use namedtuple. move out of this module.
    maybe convert pos to int already here.
    """
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


def _get_rankscore(line: str) -> int | None:
    rank_score_idx = line.find(RANK_SCORE_KEY)

    # TODO: should this return "missing"?
    #       instead of None/NA later on
    #       which would be synonymous w/
    #       variant not existing in one of
    #       compared files. dunno.
    if rank_score_idx < 0:
        return None

    score = line[line.find(RANK_SCORE_KEY) + RANK_SCORE_KEY_LEN :].split(":")[1].split(";")[0]
    return int(score)


if __name__ == "__main__":
    compare_rank_score()
