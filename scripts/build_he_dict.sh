#!/bin/bash
# Compile the Hebrew spellcheck allowlist into an aspell dictionary.
#
# Two aspell quirks make this a script rather than a plain command in
# rsconstruct.toml:
#
# 1. `aspell create master` resolves a relative output path against
#    /usr/lib/aspell, not the working directory, and fails with "can not be
#    opened for writing". The output path must be absolute.
# 2. The allowlist cannot be fed to aspell as a --personal wordlist: aspell's
#    Hebrew support segfaults on any non-ASCII entry there. --add-extra-dicts
#    is the stable path, and it requires this compiled .rws.

set -euo pipefail

root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
src="${root}/.aspell.he.txt"
out_dir="${root}/out/aspell"
# rsconstruct derives the expected output name from the source filename
# (.aspell.he.txt -> .aspell.he.rws) and errors if it is not there, so this
# name is dictated by the build system rather than chosen.
out="${out_dir}/.aspell.he.rws"

mkdir -p "${out_dir}"

# The language data file ships in aspell-he, not with aspell itself; without it
# `create master` fails with a bare non-zero exit. See scripts/build_en_dict.sh.
if [ ! -f /usr/lib/aspell/he.dat ]; then
	echo "error: /usr/lib/aspell/he.dat is missing -- install the aspell-he package" >&2
	exit 1
fi

# LC_ALL=C is load-bearing. Under en_US.UTF-8, sort -u collates distinct Hebrew
# strings as equal and silently drops entries -- that is how four legitimate
# words went missing from an earlier build of this list.
# Build to a temp file and rename into place -- see scripts/build_en_dict.sh for
# why: under -j0 a checker can otherwise read a half-written dictionary.
tmp="${out}.$$"
LC_ALL=C sort -u "${src}" |
	aspell --lang=he --encoding=utf-8 create master "${tmp}"
mv -f "${tmp}" "${out}"

echo "built ${out} ($(LC_ALL=C sort -u "${src}" | wc -l) words)"
