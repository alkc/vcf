#!/usr/bin/env python3
import csv
import io
import logging
import re

import click

from constants import INFO_FIELDS
from rankscore import _rankscore
from vcffile import VCF

RANK_SCORE_COL_NAME = "info_field_rank_score"
RANK_RESULT_SUM_COL_NAME = "rank_result_sum"
RANK_RESULT_PATTERN = rf"{INFO_FIELDS.RANK_RESULT}=([-\d|\|]+)"


@click.command(help="Output rankresults in TSV")
@click.argument("vcf_file1", type=click.Path(exists=True))
@click.option(
    "--positions_file",
    "-f",
    type=click.File("r"),
    default="-",
    help='File with chromosome positions (or "-" for stdin)',
)
@click.option(
    "--position",
    "-r",
    type=str,
    default=None,
    help="chrname:start-end",
)
def parse_rank_result(
    vcf_file1: str, positions_file: io.TextIOBase, position: str | None = None
) -> None:
    vcf = VCF(vcf_file1)
    rank_score_components = rank_keys(vcf)

    output_header = rank_score_components.copy()
    output_header.append(RANK_RESULT_SUM_COL_NAME)
    output_header.append(RANK_SCORE_COL_NAME)

    lines = []

    tsv_header = (
        ["CHROM", "POS", "REF", "ALT"]
        + rank_score_components
        + [RANK_RESULT_SUM_COL_NAME, RANK_SCORE_COL_NAME]
    )
    positions = []
    if position is not None:
        position = position.split(":")
        chr = position[0]

        position = position[1].split("-")
        position = [chr] + position
        positions.append("\t".join(position))
    else:
        for position in positions_file:
            position = position.split(":")
            chr = position[0]

            position = position[1].split("-")
            position = [chr] + position
            positions.append("\t".join(position))

    for line in positions:
        if line.startswith("#") or line.startswith("CHROM"):
            continue

        logging.warning(line)
        chromosome, start, end = line.split("\t")

        for variant in vcf.get_range(
            chromosome=chromosome, start=int(start), end=int(end), _skip_progress=True
        ):
            result = get_rankresult(variant)

            if not result:
                continue

            total_score = sum(int(score) for score in result)

            result.append(total_score)
            result.append(_rankscore(variant))

            result = dict(zip(output_header, result))
            id = get_id_fields(variant)

            id.update(result)
            lines.append(id)

    stdout = io.StringIO()
    writer = csv.DictWriter(stdout, fieldnames=tsv_header, delimiter="\t")
    writer.writeheader()
    writer.writerows(lines)

    print(stdout.getvalue())


def get_id_fields(vcf_row: str) -> dict:
    vcf_row = vcf_row.split("\t")
    return dict(CHROM=vcf_row[0], POS=vcf_row[1], REF=vcf_row[3], ALT=vcf_row[4])


def parse_range(chr_range: str):
    chr_range = chr_range.split(":")
    chromosome = chr_range[0]

    range = chr_range[1].split("-")
    start = int(range[0])
    end = int(range[1])

    return chromosome, start, end


def rank_keys(vcf):
    meta = vcf.get_info_meta(INFO_FIELDS.RANK_RESULT)
    desc = meta.get("Description")
    desc = desc.strip('""')
    return desc.split("|")


def get_rankresult(variant: str) -> int | None:
    match = re.search(RANK_RESULT_PATTERN, variant)

    if match:
        result = match.group(1)
        result = result.split("|")

    return result


if __name__ == "__main__":
    parse_rank_result()
