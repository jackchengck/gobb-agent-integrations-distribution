#!/bin/sh
# Run after cloning; Git Flow uses ordinary Git, with no extra package.
set -eu
root=$(git rev-parse --show-toplevel)
cd "$root"
common=$(git rev-parse --path-format=absolute --git-common-dir)
hooks=$(dirname "$common")/.githooks
[ -x "$hooks/pre-push" ] || { echo "Missing canonical Git Flow hook: $hooks/pre-push" >&2; exit 1; }
old=$(git config --get core.hooksPath || true)
[ -z "$old" ] || [ "$old" = "$hooks" ] || { echo "Existing hooksPath must be integrated first: $old" >&2; exit 1; }
[ ! -f "$common/hooks/pre-push" ] || { echo "Existing pre-push hook must be integrated first" >&2; exit 1; }
git rev-parse --verify refs/heads/main >/dev/null
if ! git show-ref --verify --quiet refs/heads/develop; then
  git branch develop main
fi
git config gitflow.branch.master main
git config gitflow.branch.develop develop
for prefix in feature release hotfix support; do
  git config "gitflow.prefix.$prefix" "$prefix/"
done
git config gitflow.prefix.versiontag ''
git config pull.ff only
git config merge.ff false
git config push.default simple
git config core.hooksPath "$hooks"
printf 'Git Flow enabled: main / develop; checkout remains %s\n' "$(git branch --show-current)"
