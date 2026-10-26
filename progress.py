#!/usr/bin/env python3
"""Show a GitHub user's profile achievements and progress toward the ones you can earn alone.

  python3 progress.py [USER]     USER defaults to the `gh` login

Python 3.9+ standard library only. Set GITHUB_TOKEN to raise the search-API rate limit.
"""
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request

PULL_SHARK_TIERS = [2, 16, 128, 1024]  # merged PRs for default, bronze, silver, gold
STARSTRUCK_TIERS = [16, 128, 512, 4096]  # stars on one repository you own
SOLO = {
    "Quickdraw": "close an issue or PR within 5 minutes of opening it",
    "YOLO": "merge one of your PRs without a review",
    "Pull Shark": "get PRs merged",
}


def get(url, api=False):
    headers = {"User-Agent": "badge-lab"}
    if api:
        headers["Accept"] = "application/vnd.github+json"
        if os.environ.get("GITHUB_TOKEN"):
            headers["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=20) as r:
        return r.read().decode("utf-8")


def earned(user):
    """Achievement name -> tier (1 = default, 2 = bronze, 3 = silver, 4 = gold), from the public profile."""
    page = get(f"https://github.com/{urllib.parse.quote(user)}?tab=achievements")
    tiers, current = {}, None
    for m in re.finditer(r'alt="Achievement: ([^"]+)"|achievement-tier-label--\w+[^>]*>x(\d+)', page):
        if m.group(1):
            current = m.group(1)
            tiers.setdefault(current, 1)
        elif current:
            tiers[current] = max(tiers[current], int(m.group(2)))
    return tiers


def merged_public_prs(user):
    q = urllib.parse.quote(f"type:pr author:{user} is:merged is:public")
    return json.loads(get(f"https://api.github.com/search/issues?q={q}&per_page=1", api=True))["total_count"]


def top_repo(user):
    """(full name, stars) of the user's most-starred non-fork repository, or None."""
    q = urllib.parse.quote(f"user:{user} fork:false")
    items = json.loads(get(f"https://api.github.com/search/repositories?q={q}&sort=stars&order=desc&per_page=1", api=True))["items"]
    return (items[0]["full_name"], items[0]["stargazers_count"]) if items else None


def next_tier(tiers, n):
    return next((t for t in tiers if t > n), None)


def main():
    user = sys.argv[1] if len(sys.argv) > 1 else subprocess.run(
        ["gh", "api", "user", "--jq", ".login"], capture_output=True, text=True, check=True).stdout.strip()
    have = earned(user)
    print(f"@{user}: {len(have)} achievement(s)")
    for name, tier in sorted(have.items()):
        print(f"  {name}" + (f" x{tier}" if tier > 1 else ""))

    print("\nSolo-earnable:")
    for name, how in SOLO.items():
        print(f"  [{'x' if name in have else ' '}] {name}: {how}")

    merged = merged_public_prs(user)
    nxt = next_tier(PULL_SHARK_TIERS, merged)
    print(f"\nPull Shark: {merged} merged PRs in public repos" +
          (f", {nxt - merged} more for the next tier ({nxt})" if nxt else ", top tier reached"))

    top = top_repo(user)
    if top:
        name, stars = top
        nxt = next_tier(STARSTRUCK_TIERS, stars)
        print(f"Starstruck: most-starred repo {name} has {stars} star(s)" +
              (f", {nxt - stars} more for the next tier ({nxt})" if nxt else ", top tier reached"))


if __name__ == "__main__":
    main()
