#!/usr/bin/env python3

import click
import sys


class VCF_FIELDS:
    CHROM = 0
    POS = 1
    ID = 2
    REF = 3
    ALT = 4
    QUAL = 5
    FILTER = 6
    INFO = 7
    FORMAT = 8

class INFO_FIELDS:
    RANK_SCORE = "RankScore"
    CADD_SCORE = "CADD"


@click.group()
def cli():
    """A CLI tool for processing VCF files."""
    pass


@cli.command()
@click.argument("file", type=click.File("r"), default=sys.stdin)
def csq(file):
    """Process VEP CSQ annotations in a VCF file."""
    ...
    if file.name == "<stdin>":
        # Process from standard input
        for line in file:
            pass
    else:
        # Process from file
        with file as f:
            for line in f:
                if line.startswith("##INFO=<ID=CSQ"):
                    # Extract the description part
                    description_start = line.find("Format:") + len("Format: ")
                    description_end = line.rfind('"')
                    description = line[description_start:description_end]

                    # TODO:
                    fields = description.split("|")
                    print(fields)
                    break

    click.echo("VEP CSQ annotation processing complete.")


@cli.command()
@click.argument("file", type=click.File("r"), default=sys.stdin)
def rankscore(file):
    with file as f:
        rank_score_position = None

        for line in f:
            if line.startswith("#"):
                continue

            line = line.split("\t")
            info_field = line[7]

            # TODO: smth nicer:
            out = line[0:7]
            out.append(_get_rank_score(info_field))
            print("\t".join(out))


def _is_csq_format_field(line):
    return line.startswith("##INFO=<ID=CSQ")


def _get_rank_score(line):
    # TODO: move rankscore key to some constant something
    description_start = line.find(INFO_FIELDS.RANK_SCORE + "=") + len("RankScore=")
    line = line[description_start:].split(";")
    return line[0].split(":")[1]


# TODO: nah
def _get_info_field_index(key, fields):
    for idx, field in enumerate(fields):
        if field.startswith(key):
            return idx


def _parse_csq(file): ...


if __name__ == "__main__":
    cli()
