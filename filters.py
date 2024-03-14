import logging

from constants import CLNSIG, INFO_FIELDS
from variants import get_info_field

LOG = logging.getLogger(__name__)


def only_clnsg_pathogenic(vcf_row: str) -> bool:
    clnsg = get_info_field(vcf_row, INFO_FIELDS.CLINVAR_SIGNIFICANCE)

    return clnsg == CLNSIG.PATHOGENIC
