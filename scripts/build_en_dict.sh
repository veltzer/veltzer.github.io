#!/bin/bash
# Compile the English spellcheck allowlist into an aspell dictionary.
#
# Mirrors scripts/build_he_dict.sh, and for the same two reasons: `aspell create
# master` resolves a relative output path against /usr/lib/aspell rather than
# the working directory, and the allowlist cannot be passed as a --personal
# wordlist. For Hebrew --personal segfaults; for English it is milder but still
# wrong -- aspell reads the personal file as Latin-1 whatever --encoding says,
# so "Bahá'í", "Pâques" and "élan" arrive mojibaked and are rejected. The
# compiled extra-dictionary path handles them correctly.

set -euo pipefail

root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
src="${root}/.aspell.en.txt"
out_dir="${root}/out/aspell"
# rsconstruct derives the expected output name from the source filename.
out="${out_dir}/.aspell.en.rws"

mkdir -p "${out_dir}"

# aspell warns and skips on characters its en_US charset cannot represent (see
# scripts/spellcheck_en.sh, which filters the same words out of the results).
# Those warnings are expected, so they are dropped here to keep builds quiet.
#
# LC_ALL=C for the same reason as the Hebrew list: a UTF-8 locale makes sort -u
# collate distinct strings as equal and silently drop entries.
# Build to a temp file and rename into place. The checkers build the dictionary
# themselves when it is missing (rsconstruct does not order generators before
# checkers), so under -j0 a reader can otherwise open a half-written file and
# fail with "is not in the proper format". rename(2) is atomic within a
# filesystem, so a reader sees either the old file or the complete new one.
tmp="${out}.$$"
LC_ALL=C sort -u "${src}" |
	aspell --lang=en --encoding=utf-8 create master "${tmp}" 2>/dev/null
mv -f "${tmp}" "${out}"

echo "built ${out} ($(LC_ALL=C sort -u "${src}" | wc -l) words)"
