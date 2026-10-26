# badge-lab

Tracking GitHub profile achievements for @hexacron, and a small script that shows progress toward the ones you can earn alone.

## Usage

```sh
python3 progress.py            # the account `gh` is logged in as
python3 progress.py torvalds   # any public profile
```

Python 3.9+ standard library only. Set `GITHUB_TOKEN` to raise the search-API rate limit. It reads earned achievements and tiers from the public profile page (`?tab=achievements`) and counts merged PRs in public repos through the search API.

## Achievements

| Achievement | How | Tiers | Solo? |
|---|---|---|---|
| Quickdraw | Close an issue or PR within 5 minutes of opening it | one-time | yes |
| YOLO | Merge your own PR without a review | one-time | yes |
| Pull Shark | Get PRs merged | 2 · 16 · 128 · 1024 | yes |
| Pair Extraordinaire | Co-author commits in a merged PR | 1 · 10 · 24 · 48 | needs a real collaborator |
| Galaxy Brain | Answers accepted in Discussions Q&A | 2 · 8 · 16 · 32 | needs other people |
| Starstruck | A repository you own gets stars | 16 · 128 · 512 · 4096 | needs other people |
| Public Sponsor | Sponsor someone via GitHub Sponsors | one-time | costs money |

## Rules

Only real activity counts here: no second accounts, bought stars or bulk scripted PRs. GitHub's Acceptable Use Policies forbid inauthentic interactions and excessive automated bulk activity, and this account hosts public projects.
