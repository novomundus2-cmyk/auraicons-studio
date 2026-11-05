"""Export every registry version in a uv lock, including other platform markers."""

import argparse
import tomllib
from pathlib import Path


def export_locked_requirements(lock_path: Path, output_dir: Path) -> None:
    packages = tomllib.loads(lock_path.read_text())["package"]
    batches: list[dict[str, str]] = []
    count = 0
    for package in packages:
        source = package["source"]
        if source in ({"virtual": "."}, {"editable": "."}):
            print(f"Local project: {package['name']}")
            continue
        if source != {"registry": "https://pypi.org/simple"}:
            raise ValueError(f"Unsupported source for {package['name']}: {source}")
        artifacts = package.get("wheels", []) + [package.get("sdist", {})]
        hashes = sorted({item["hash"] for item in artifacts if "hash" in item})
        if not hashes:
            raise ValueError(f"Missing hashes for {package['name']}")
        requirement = f"{package['name']}=={package['version']} " + " ".join(
            f"--hash={value}" for value in hashes
        )
        # pip-audit rejects two versions of one name in a single input. Separate
        # batches preserve all variants without choosing a platform or version.
        batch = next((b for b in batches if package["name"] not in b), None)
        if batch is None:
            batch = {}
            batches.append(batch)
        batch[package["name"]] = requirement
        count += 1
    if not count:
        raise ValueError(f"No registry packages in {lock_path}")
    output_dir.mkdir(parents=True, exist_ok=False)
    for index, batch in enumerate(batches):
        (output_dir / f"{index}.txt").write_text("\n".join(batch.values()) + "\n")
    print(f"Exported {count} registry package versions from {lock_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("lock", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    export_locked_requirements(args.lock, args.output)
