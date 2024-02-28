import gzip
import os
from typing import Callable, Generator


class VCF:
    def __init__(self, path: str | None = None):
        self.vcf_file = None
        self.tabix_index_file_exists = False

        self._active_filters = []
        self._open_func = open

        if path is not None:
            self.open_file(path)

    def open_file(self, vcf_file: str):
        self._open_func = open
        self.vcf_file = vcf_file
        if vcf_file.endswith(".gz"):
            self._open_func = gzip.open
            self.set_tabix(vcf_file)

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

    def get_rows(self) -> Generator:
        def _vcf_generator():
            with self._open_func(self.vcf_file, "rt") as vcf:
                for variant in vcf:
                    if variant.startswith("#"):
                        continue

                    if not self._passes_filters(variant):
                        continue

                    yield variant

        return _vcf_generator()

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
        print(info_meta)

        return {x[0]: x[1] for x in info_meta}

    def set_tabix(self, path_to_bgzipped_vcf: str):
        tbi_should_be_here = f"{path_to_bgzipped_vcf}.tbi"
        self.tabix_index_file_exists = os.path.isfile(tbi_should_be_here)


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
