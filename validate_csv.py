import csv
import json
from pathlib import Path

REQUIRED_COLS = ["id", "name", "age"]

def validate(path: str):
    errors = []
    warnings = []
    rows = []

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:
            raise ValueError("CSV has no header")

        missing_cols = [c for c in REQUIRED_COLS if c not in reader.fieldnames]
        if missing_cols:
            errors.append({"type": "MISSING_COLUMNS", "missing": missing_cols})

        for i, r in enumerate(reader, start=2):  # line number approx
            rows.append(r)
            # missing values
            for c in REQUIRED_COLS:
                if c in r and (r[c] is None or str(r[c]).strip() == ""):
                    errors.append({"type": "MISSING_VALUE", "line": i, "column": c})

            # simple age sanity
            if "age" in r and str(r.get("age", "")).strip() != "":
                try:
                    age = int(r["age"])
                    if age < 0 or age > 120:
                        warnings.append({"type": "AGE_OUT_OF_RANGE", "line": i, "age": age})
                except ValueError:
                    errors.append({"type": "AGE_NOT_INT", "line": i, "value": r["age"]})

    # duplicates by id
    seen = set()
    dup = 0
    for r in rows:
        if "id" in r:
            if r["id"] in seen:
                dup += 1
            seen.add(r["id"])
    if dup:
        warnings.append({"type": "DUPLICATE_ID", "count": dup})

    report = {
        "input": path,
        "errors": errors,
        "warnings": warnings,
        "summary": {"error_count": len(errors), "warning_count": len(warnings), "rows": len(rows)},
    }
    return report

def main():
    inp = "sample.csv"
    out = Path("out")
    out.mkdir(exist_ok=True)
    report = validate(inp)
    (out / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print("Wrote out/report.json")

if __name__ == "__main__":
    main()
