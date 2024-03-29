#!/usr/bin/env python3

import gzip
from collections import defaultdict
from typing import Callable, Generator

import click
from uniplot import plot

from constants import INFO_FIELDS
from filters import only_clnsg_pathogenic
from vcffile import VCF

RANK_SCORE_KEY_LEN = len(INFO_FIELDS.RANK_SCORE)


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
@click.option(
    "--output-type",
    default="tsv",
    type=str,
    help="Only print variants where scores diff between compared files.",
)
@click.option(
    "--only-pathogenic",
    is_flag=True,
    default=False,
    help="Only pathogenic variants.",
)
def rankscore(
    vcf_file1: str,
    vcf_file2: str | None = None,
    skip_identical: bool = False,
    output_difference: bool = False,
    only_scores_above: int | None = None,
    output_type: str = "tsv",
    only_pathogenic: bool = False,
) -> None:
    """
    Print comparison of rank scores for two VCF files

    Or just extract scores for one file, if you feel like it
    """

    filters = []

    if only_pathogenic:
        filters.append(only_clnsg_pathogenic)

    vcf = _setup_vcf(VCF(vcf_file1), filters)

    if vcf_file2 is not None:
        vcf2 = _setup_vcf(VCF(vcf_file2), filters)
        rank_score_data = compare_rank_scores(vcf, vcf2)

    unique_keys = sorted(rank_score_data.keys(), key=lambda x: (x[0], int(x[1]), x[2], x[3]))

    files = [vcf.vcf_file, vcf2.vcf_file]

    header = ["CHROM", "POS", "REF", "ALT"]
    header += files

    combined = rank_score_data

    if output_difference:
        header.append("diff_vcf1_to_vcf2")
        header.append("absolute_difference")

    print("\t".join(header))
    plot_data = defaultdict(list)

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

        if output_type == "plot":
            plot_data["x"].append(score1)
            plot_data["y"].append(score2)
            continue

        row.append(score1)
        row.append(score2)

        if output_difference:
            # TODO: convert back into ints? sure. for now.

            if any(x == "NA" for x in (score1, score2)):
                row.append("NA")
                row.append("NA")

            else:
                diff = score2 - score1
                row.append(diff)
                row.append(str(diff).lstrip("-"))

        print("\t".join(str(x) for x in row))

    if output_type == "plot":
        plot_data["x"] = [None if x == "NA" else x for x in plot_data["x"]]
        plot_data["y"] = [None if y == "NA" else y for y in plot_data["y"]]

        plot(
            xs=plot_data["x"],
            ys=plot_data["y"],
            title=files,
            lines=False,
            color=True,
            x_gridlines=[17],
            y_gridlines=[17],
            width=100,
            height=31,
        )


def compare_rank_scores(vcf: VCF, vcf2: VCF) -> dict[tuple, dict[str, int | None]]:
    scores_side_by_side = defaultdict(dict)

    for curr_vcf in [vcf, vcf2]:
        scores = reduce_vcf_to_rankscores(curr_vcf)
        for variant_id, rank_score in scores.items():
            scores_side_by_side[variant_id][curr_vcf.vcf_file] = rank_score

    return scores_side_by_side


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


def reduce_vcf_to_rankscores(vcf: VCF) -> dict[tuple, int]:
    scores = {}

    for line in vcf.variants():
        rank = _rankscore(line)
        key = get_id_fields(line)
        scores[key] = rank

    return scores


def _rankscore(line: str) -> int | None:
    rank_score_idx = line.find(INFO_FIELDS.RANK_SCORE)

    # TODO: should this return "missing"?
    #       instead of None/NA later on
    #       which would be synonymous w/
    #       variant not existing in one of
    #       compared files. dunno.
    if rank_score_idx < 0:
        return None

    score = (
        line[line.find(INFO_FIELDS.RANK_SCORE) + RANK_SCORE_KEY_LEN :].split(":")[1].split(";")[0]
    )
    return int(score)


def _setup_vcf(vcf: VCF, filters: list[Callable] | None = None):
    if filters:
        for f in filters:
            vcf.add_filter(f)

    return vcf


if __name__ == "__main__":
    rankscore()
