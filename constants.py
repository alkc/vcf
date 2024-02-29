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
    RANK_RESULT = "RankResult"
    CADD_SCORE = "CADD"
    PHYLOP100WAY = "dbNSFP_phyloP100way_vertebrate"
    PHASTCONS100WAY = "dbNSFP_phastCons100way_vertebrate"
    CLINVAR_SIGNIFICANCE = "CLNSIG"
    CLINVAR_REVIEW_STATUS = "CLNREVSTAT"
    CLINVAR_ACCESSION = "CLNACC"
    zzz = "Annotation"
    GNOMADAF = "GNOMADAF"
    GNOMADAF_MAX = "GNOMADAF_MAX"
    GNOMADPOP_MAX = "GNOMADPOP_MAX"
    MOST_SEVERE_CONSEQUENCE = "most_severe_consequence"
    COMPOUNDS = "Compounds"
    GENETICMODELS = "GeneticModels"
