#!/usr/bin/env python3

import logging
from collections import Counter

import click
import prettytable

from util import print_percent_done
from variants import get_info_field
from vcffile import VCF

logging.basicConfig(level=logging.INFO, format="[%(asctime)s][%(levelname)s]: %(message)s")

LOG = logging.getLogger(__name__)


@click.command(help="Checks if INFO fields are defined in variants")
@click.argument("vcf_file", type=click.Path(exists=True))
def check_vcf(vcf_file):
    LOG.info("HELLO.")
    LOG.info("Checking: %s", vcf_file)
    vcf = VCF(vcf_file)

    LOG.info("Calculating nbr variants.")
    n_variants = vcf.nbr_variants(skip_mito=True)

    LOG.info("Processing %s variants", n_variants)
    LOG.warning("Skipping mito variants!")

    table = get_completeness_table()

    header = vcf.get_header()
    header = [row for row in header.split("\n") if row.startswith("##INFO")]

    info_fields = [x.split("=")[2].split(",")[0] for x in header]
    counter = Counter()

    for info_key in info_fields:
        counter.setdefault(info_key, 0)

    for idx, variant in enumerate(vcf.get_rows(skip_mito=True)):
        print_percent_done(idx, n_variants - 1)

        for key in info_fields:
            counter[key] += info_field_defined_in_variant(variant, key)

    for k, v in counter.items():
        table.add_row([k, v, f"{v/n_variants * 100:.1f}%"])

    print(table)


def get_completeness_table():
    table = prettytable.PrettyTable(["info_field", "count", "pct_complete"])
    table.align["info_field"] = "l"
    table.align["count"] = "r"
    table.align["pct_complete"] = "r"
    table.sortby = "count"
    table.reversesort = True
    return table


def info_field_defined_in_variant(variant: str, info_key: str) -> bool:
    return get_info_field(variant, info_key) is not None


if __name__ == "__main__":
    check_vcf()
