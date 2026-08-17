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

# `aspell create master` needs the language data file, which ships in the
# aspell-<lang> package rather than with aspell itself. Without it the command
# fails with a bare non-zero exit, which is how this first broke CI: aspell and
# aspell-he installed, aspell-en did not, and nothing said so. Check explicitly
# and name the fix.
if [ ! -f /usr/lib/aspell/en.dat ]; then
	echo "error: /usr/lib/aspell/en.dat is missing -- install the aspell-en package" >&2
	exit 1
fi

# LC_ALL=C: a UTF-8 locale makes sort -u collate distinct strings as equal and
# silently drop entries.
#
# Build to a temp file and rename into place. The checkers build the dictionary
# themselves when it is missing (rsconstruct does not order generators before
# checkers), so under -j0 a reader can otherwise open a half-written file and
# fail with "is not in the proper format". rename(2) is atomic within a
# filesystem, so a reader sees either the old file or the complete new one.
tmp="${out}.$$"
trap 'rm -f "${tmp}"' EXIT

# stderr goes to a file rather than /dev/null so a real error survives. aspell
# warns and skips on characters its en_US charset cannot represent, which is
# expected (scripts/spellcheck_en.sh filters the same words out of the results);
# anything else is printed. Discarding all of stderr here is what left the first
# CI failure with a bare non-zero exit and no message.
err="${tmp}.err"
if ! LC_ALL=C sort -u "${src}" |
	aspell --lang=en --encoding=utf-8 create master "${tmp}" 2>"${err}"; then
	cat "${err}" >&2
	rm -f "${err}"
	exit 1
fi
grep -vE 'Warning: The string .* is invalid\. The Unicode code point' "${err}" >&2 || true
rm -f "${err}"

mv -f "${tmp}" "${out}"

echo "built ${out} ($(LC_ALL=C sort -u "${src}" | wc -l) words)"
