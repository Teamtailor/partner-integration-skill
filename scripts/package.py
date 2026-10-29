import argparse
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo


def package(output):
    root = Path(__file__).resolve().parents[1]
    skill = root / "skills" / "teamtailor-integration"
    paths = sorted(path for path in skill.rglob("*") if path.is_file())
    for path in paths:
        if path.suffix not in {".md", ".json"} or path.is_symlink():
            raise ValueError(f"Unexpected package file: {path.relative_to(skill)}")
    output.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(output, "w", compression=ZIP_DEFLATED) as archive:
        for path in paths:
            entry = ZipInfo(str(path.relative_to(skill.parent)), (2026, 1, 1, 0, 0, 0))
            entry.compress_type = ZIP_DEFLATED
            entry.external_attr = 0o100644 << 16
            archive.writestr(entry, path.read_bytes())
    print(f"Packaged {len(paths)} files: {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("dist/teamtailor-integration.zip"))
    package(parser.parse_args().output)
