# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""Download the two Ken French source zips and extract their CSVs into data/raw/.

Public data from the Ken French Data Library:
  https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html

Both the zips and the extracted CSVs land under data/raw/, which is gitignored.
Re-running overwrites in place, so the build is reproducible from scratch.
"""

import urllib.request
import zipfile
from pathlib import Path

BASE = "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
FILES = [
    "F-F_Research_Data_Factors_CSV.zip",
    "25_Portfolios_5x5_CSV.zip",
]

RAW = Path(__file__).resolve().parent / "raw"


def main():
    RAW.mkdir(parents=True, exist_ok=True)
    for fname in FILES:
        url = BASE + fname
        zpath = RAW / fname
        print(f"Downloading {url}")
        urllib.request.urlretrieve(url, zpath)
        print(f"  -> {zpath} ({zpath.stat().st_size:,} bytes)")
        with zipfile.ZipFile(zpath) as zf:
            names = zf.namelist()
            zf.extractall(RAW)
            print(f"  extracted: {', '.join(names)}")
    print("Download complete.")


if __name__ == "__main__":
    main()
