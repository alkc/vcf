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

    def set_tabix(self, path_to_bgzipped_vcf: str):
        tbi_should_be_here = f"{path_to_bgzipped_vcf}.tbi"
        self.tabix_index_file_exists = os.path.isfile(tbi_should_be_here)
