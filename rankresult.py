#!/usr/bin/env python3
import csv
import re
from io import StringIO

import click

from constants import INFO_FIELDS
from vcffile import VCF

RANK_RESULT_PATTERN = rf"{INFO_FIELDS.RANK_RESULT}=([-\d|\|]+)"


@click.command(help="Output rankresults in TSV")
@click.argument("vcf_file1", type=click.Path(exists=True))
@click.argument("chr_range", type=str, required=False)
def compare_rank_score(vcf_file1: str, chr_range: str | None = None) -> None:
    vcf = VCF(vcf_file1)
    rank_score_components = rank_keys(vcf)

    chromosome, start, end = parse_range(chr_range)

    lines = []

    tsv_header = ["CHROM", "POS", "REF", "ALT"] + rank_score_components + ["total_score"]
    for variant in vcf.get_range(chromosome, start, end, _skip_progress=True):
        result = get_rankresult(variant)

        if not result:
            continue

        result = dict(zip(rank_score_components, result))
        id = get_id_fields(variant)

        id.update(result)
        lines.append(id)

    stdout = StringIO()
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
    compare_rank_score()
