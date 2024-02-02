#!/usr/bin/env python3

import click
import sys


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
            print(line[0:7], _get_rank_score(info_field))


def _is_csq_format_field(line):
    return line.startswith("##INFO=<ID=CSQ")


def _get_rank_score(line):
    # TODO: move rankscore key to some constant something
    description_start = line.find("RankScore=") + len("RankScore=")
    line = line[description_start:].split(";")
    return line[0]


# TODO: nah
def _get_info_field_index(key, fields):
    for idx, field in enumerate(fields):
        if field.startswith(key):
            return idx


def _parse_csq(file):
    ...


if __name__ == "__main__":
    cli()
