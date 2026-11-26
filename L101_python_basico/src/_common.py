import csv
import gzip
from pathlib import Path


def read_rows():
    data_path = Path(__file__).resolve().parents[1] / "data" / "data.csv.gz"
    with gzip.open(data_path, "rt", encoding="utf-8", newline="") as data_file:
        return [tuple(row) for row in csv.reader(data_file, delimiter="\t")]


def split_codes(text):
    return [code for code in text.split(",") if code]


def split_metrics(text):
    pairs = []
    for item in text.split(","):
        if item:
            key, value = item.split(":", 1)
            pairs.append((key, int(value)))
    return pairs
