import gzip
import logging
import os
from typing import Callable, Generator

from util import print_percent_done

# import tabix


logging.basicConfig(level=logging.INFO)

LOG = logging.getLogger(__name__)


class VCF:
    def __init__(self, path: str | None = None):
        self.vcf_file = None
        self.tabix_index_file_exists = False

        self._active_filters = []
        self._open_func = open

        self._nbr_records = None
        self._header_stop = None

        if path is not None:
            self.open_file(path)

    def open_file(self, vcf_file: str):
        self._open_func = open
        self.vcf_file = vcf_file
        if vcf_file.endswith(".gz"):
            self._open_func = gzip.open
            self.set_tabix(vcf_file)
            self._total_nbr_records = sum(1 for _ in self._get_rows())

    def _get_rows(self) -> Generator:
        with self._open_func(self.vcf_file, "rt") as f:
            for line in f:
                if line.startswith("#"):
                    continue
                yield line

    def add_filter(self, filter_function: Callable[[str], bool]) -> None:
        self._active_filters.append(filter_function)

    def active_filters() -> list:
        ...

    def _passes_filters(self, row) -> bool:
        if not self._active_filters:
            return True

        for filter_func in self._active_filters:
            if not filter_func(row):
                return False

        return True

    def get_rows(self, skip_mito: bool = False, _skip_progress=False) -> Generator:
        def _vcf_generator():
            with self._open_func(self.vcf_file, "rt") as vcf:
                hits = 0
                for idx, variant in enumerate(vcf):
                    if not _skip_progress:
                        print_percent_done(
                            idx,
                            self._total_nbr_records,
                            title=" Processing records",
                        )

                    if variant.startswith("#"):
                        continue

                    if skip_mito and variant.startswith("M"):
                        continue

                    if not self._passes_filters(variant):
                        continue

                    hits += 1
                    yield variant

        return _vcf_generator()

    variants = get_rows

    def get_header(self):
        header = []

        with self._open_func(self.vcf_file, "rt") as vcf:
            for line in vcf:
                if not line.startswith("#"):
                    break
                header.append(line)

        return "\n".join(header)

    def get_info_meta(self, id: str):
        header = self.get_header()

        query = f"##INFO=<ID={id}"

        result_idx = header.find(query)
        header = header[result_idx:]
        header = header.split(">")[0]
        header = header.removeprefix("##INFO=<")
        header = header.split(",")

        info_meta = [x.split("=") for x in header]

        return {x[0]: x[1] for x in info_meta}

    def set_tabix(self, path_to_bgzipped_vcf: str):
        tbi_should_be_here = f"{path_to_bgzipped_vcf}.tbi"
        self.tabix_index_file_exists = os.path.isfile(tbi_should_be_here)

    def get_range(self, chromosome: str, start: int, end: int, _skip_progress=False):
        variants = self.get_rows(_skip_progress=_skip_progress)
        #         if self.tabix_index_file_exists:
        #             variants =
        #             LOG.info("Tabix!")
        #             tb = tabix.open(self.vcf_file)
        #             variants = tb.query(chromosome, start, end)
        # )
        #         else:
        #             variants = self.get_rows()

        for variant in variants:
            if not variant.split("\t")[0] == chromosome:
                continue

            position = int(variant.split("\t")[1])

            if position < start:
                continue

            if position > end:
                continue

            yield variant

    def nbr_variants(self, skip_mito: bool = False) -> int:
        return sum(1 for _ in self.get_rows(skip_mito=skip_mito))


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
