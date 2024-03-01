import sys


def print_percent_done(index, total, bar_len=None, title="Please wait", suffix=""):
    """
    index is expected to be 0 based index.
    0 <= index < total

    Credit: https://stackoverflow.com/revisions/61433559/2
    """

    if bar_len is None:
        bar_len = 80

    percent_done = (index + 1) / total * 100
    percent_done = round(percent_done, 1)

    done = round(percent_done / (100 / bar_len))
    togo = bar_len - done

    done_str = "█" * int(done)
    togo_str = "░" * int(togo)

    print(
        f"\t⏳{title}: [{done_str}{togo_str}] {percent_done}% done. {suffix}",
        end="\r",
        file=sys.stderr,
    )

    if index == total:
        print("\t✅", file=sys.stderr)
