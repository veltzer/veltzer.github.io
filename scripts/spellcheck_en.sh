#!/bin/bash
# Spellcheck English posts against the compiled allowlist.
#
# Mirrors scripts/spellcheck_he.sh; see that script and scripts/build_en_dict.sh
# for why the allowlist is a compiled extra-dictionary and why the paths are
# resolved here rather than in rsconstruct.toml.

set -euo pipefail

root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
dict_dir="${root}/out/aspell"

# Build the dictionary if it is missing. rsconstruct runs the generator and this
# checker in the same pass and does not order them, so on a cold cache the
# checker can start first.
if [ ! -f "${dict_dir}/.aspell.en.rws" ]; then
	"${root}/scripts/build_en_dict.sh" >/dev/null
fi

status=0
for file in "$@"; do
	# Words containing characters outside aspell's en_US charset cannot be
	# added to its dictionary at all -- it rejects the code point outright
	# (U+0112 in Bede's "Ēosturmōnaþ", U+1E62 in "YHWH Ṣebaʾot"). They are
	# correctly spelled, so they are dropped from the results here rather
	# than misreported. This filter is deliberately narrow: it only removes
	# words aspell is incapable of judging, not words it judged wrong.
	# `|| true` on the grep: under pipefail, a grep that filters out every
	# line exits 1 and would fail the whole check with no output at all.
	misspelled=$(aspell --lang=en --encoding=utf-8 \
		--dict-dir="${dict_dir}" \
		--add-extra-dicts=.aspell.en.rws \
		list <"${file}" |
		{ grep -Pv '[^\x00-\xFF]' || true; } |
		LC_ALL=C sort -u)
	if [ -n "${misspelled}" ]; then
		echo "Misspelled words in ${file}:"
		echo "${misspelled}"
		status=1
	fi
done

exit "${status}"
