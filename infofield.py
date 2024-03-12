#!/usr/bin/env python3

import csv
import io

import click

from variants import get_info_field
from vcffile import VCF


@click.command(help="Get INFO field for specific variant")
@click.argument("vcf_file", type=click.Path(exists=True))
@click.argument("chrom_range", type=str)
@click.argument("info_key", type=str)
def get_info_fields(vcf_file, chrom_range, info_key):
    """
    Process VCF files with a given chromosomal range.

    Args:
    vcf_files: A list of VCF file paths
    chrom_range: A string specifying the chromosomal range in the format 'chrom:start-end'
    """

    vcf = VCF(vcf_file)

    # Example of how to split the chromosomal range
    chrom, range_part = chrom_range.split(":")
    start, end = range_part.split("-")

    records = vcf.get_range(chrom, int(start), int(end), _skip_progress=True)
    stdout = io.StringIO()

    fieldnames = ["FILE", "CHROM", "POS", "REF", "ALT", info_key]

    tsv_writer = csv.DictWriter(stdout, delimiter="\t", fieldnames=fieldnames)
    tsv_writer.writeheader()
    for record in records:
        info_val = get_info_field(record, info_key) or "NA"
        record = record.split("\t")
        row = {
            "FILE": vcf_file,
            "CHROM": record[0],
            "POS": record[1],
            "REF": record[3],
            "ALT": record[4],
        }
        row[info_key] = info_val
        tsv_writer.writerow(row)

    print(stdout.getvalue())


if __name__ == "__main__":
    get_info_fields()
