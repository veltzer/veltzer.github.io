#!/bin/bash
# Spellcheck Hebrew posts against the compiled allowlist.
#
# This wraps aspell rather than calling it from rsconstruct.toml because every
# aspell path option resolves relative names against /usr/lib/aspell, not the
# working directory. --dict-dir has to be an absolute path, and hardcoding one
# in rsconstruct.toml would break on any other machine and in CI, so the repo
# root is resolved here instead.
#
# The allowlist reaches aspell as a compiled extra dictionary, not as a
# --personal wordlist: aspell's Hebrew support segfaults on any non-ASCII entry
# in a personal wordlist. See scripts/build_he_dict.sh.

set -euo pipefail

root=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)
dict_dir="${root}/out/aspell"

# Build the dictionary if it is missing. rsconstruct runs the generator and this
# checker in the same pass and does not order them, so on a cold cache the
# checker can start first -- which fails every time in CI. Depending on the
# compiled artifact rather than on scheduling keeps this correct either way.
if [ ! -f "${dict_dir}/.aspell.he.rws" ]; then
	"${root}/scripts/build_he_dict.sh" >/dev/null
fi

status=0
for file in "$@"; do
	# aspell appends .rws itself, but the compiled name already carries it.
	# The front matter's `slug = "..."` line is skipped: a slug is an
	# identifier (lowercase, no apostrophes), not prose, so "christianity"
	# there is not a misspelling. Titles and descriptions are still checked.
	misspelled=$(grep -v '^slug = ' "${file}" |
		aspell --lang=he --encoding=utf-8 \
		--dict-dir="${dict_dir}" \
		--add-extra-dicts=.aspell.he.rws \
		list | LC_ALL=C sort -u)
	if [ -n "${misspelled}" ]; then
		echo "Misspelled words in ${file}:"
		echo "${misspelled}"
		status=1
	fi
done

exit "${status}"
