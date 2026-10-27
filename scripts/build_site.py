#!/usr/bin/env python

"""
The site build steps around rssite, one subcommand per rsconstruct product.

rssite itself is run by rsconstruct's processor.mass_generator.generic.site:
`rssite plan` lists every file a build writes with its sources, and each
becomes a cached product. What rssite does not produce is done here, each
step declaring exactly what it reads and writes in rsconstruct.toml so
rsconstruct can order, cache and restore it:

  companies      _site/data/companies.json.gz and _site/logos/

companies is an explicit processor: rsconstruct appends `--inputs ...
--output-files ... --output-dirs ...`.

What used to be done here and no longer is:
  - the commit every footer names is rssite's `git` context variable;
  - the legacy-URL redirect stubs are `[[redirects]]` in rssite.toml and
    `pager_aliases` in content/blog/_index.en.md;
  - the English feed at /atom.xml is `feeds.root` in rssite.toml;
  - the shared-themes files are published by rssite itself ([[publish]] in
    rssite.toml); the language chooser at "/" is templates/root.html;
  - the archive stats and the tag translation table that gen_stats.py
    generated come from rssite (section.years, infer_translations);
  - import_teaching.py reads the sibling teaching-* repos and rewrites
    committed content, so it is run by hand, not by the build.

Posts are authored directly in content/blog/. The old blog/posts/ tree and
scripts/mkdocs_to_zola.py were the one-time migration path and have been
retired: the converter rebuilt content/blog from scratch on every run, which
silently destroyed anything added there by hand -- translations included.
"""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
COMPANIES_IMPORTER = REPO_ROOT / "scripts" / "import_companies.py"
ORGANIZATIONS_YAML = REPO_ROOT / "data" / "yaml" / "organizations.yaml"
LOGOS_SRC = REPO_ROOT / "data" / "logos"
IMAGES_DIR = REPO_ROOT / "static" / "images"


def die(message):
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


def write_companies(output_file, logos_dir):
    """Build the companies tab's data and logos straight into the output.

    The other media tabs read committed static/data/*.json.gz files that
    scripts/copy_data.py produces by hand, because half of their sources
    live in the private ../data repo that CI cannot see. organizations.yaml
    and the logos it names live in this repo, so there is nothing to commit:
    the JSON is generated and the SVGs copied into _site/ on every build,
    beside rssite's output. The logo paths inside the YAML are relative
    to data/ (logos/<slug>.svg), and data/logos/ lands at /logos/, so the
    plugin can use them as they are.
    """
    output_file.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [sys.executable, str(COMPANIES_IMPORTER), str(ORGANIZATIONS_YAML), str(output_file),
         "--images-dir", str(IMAGES_DIR)],
        check=True,
        cwd=REPO_ROOT,
    )
    if not LOGOS_SRC.is_dir():
        die(f"{LOGOS_SRC} missing")
    logos_dir.mkdir(parents=True, exist_ok=True)
    for source in sorted(LOGOS_SRC.glob("*.svg")):
        shutil.copyfile(source, logos_dir / source.name)


# The steps, in the order the bare command lists them, each with its line.
STEPS = {
    "companies": "write _site/data/companies.json.gz and _site/logos/",
}


def list_steps(prog):
    """What a bare invocation prints: the steps, nothing else."""
    width = max(len(name) for name in STEPS)
    print(f"{prog} needs a step:")
    for name, line in STEPS.items():
        print(f"  {name:<{width}}  {line}")
    print(f"Run '{prog} --help' for the options.")


def main():
    parser = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    sub = parser.add_subparsers(dest="step")
    for name, line in STEPS.items():
        step = sub.add_parser(name, help=line)
        # The arguments rsconstruct's explicit processor appends.
        step.add_argument("--inputs", nargs="*", type=Path, default=[])
        step.add_argument("--output-files", nargs="*", type=Path, default=[])
        step.add_argument("--output-dirs", nargs="*", type=Path, default=[])
    args = parser.parse_args()
    if args.step is None:
        list_steps(parser.prog)
        sys.exit(2)

    try:
        write_companies(*args.output_files, *args.output_dirs)
    except subprocess.CalledProcessError as error:
        sys.exit(error.returncode)


if __name__ == "__main__":
    main()
