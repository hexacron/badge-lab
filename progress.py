#!/usr/bin/env python3
"""Show a GitHub user's profile achievements and progress toward the ones you can earn alone.

  python3 progress.py [USER]     USER defaults to the `gh` login

Python 3.9+ standard library only. Set GITHUB_TOKEN to raise the search-API rate limit.
"""
import argparse
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


def collect_progress(user):
    achievements = earned(user)
    merged = merged_public_prs(user)
    pull_shark_next = next_tier(PULL_SHARK_TIERS, merged)
    repository = top_repo(user)
    starstruck = None
    if repository:
        name, stars = repository
        starstruck_next = next_tier(STARSTRUCK_TIERS, stars)
        starstruck = {
            "repository": name,
            "stars": stars,
            "next_tier": starstruck_next,
            "remaining": starstruck_next - stars if starstruck_next else 0,
        }

    return {
        "user": user,
        "achievements": achievements,
        "solo": {
            name: {"earned": name in achievements, "how": how}
            for name, how in SOLO.items()
        },
        "pull_shark": {
            "merged_public_prs": merged,
            "next_tier": pull_shark_next,
            "remaining": pull_shark_next - merged if pull_shark_next else 0,
        },
        "starstruck": starstruck,
    }


def print_human(progress):
    user = progress["user"]
    achievements = progress["achievements"]
    print(f"@{user}: {len(achievements)} achievement(s)")
    for name, tier in sorted(achievements.items()):
        print(f"  {name}" + (f" x{tier}" if tier > 1 else ""))

    print("\nSolo-earnable:")
    for name, status in progress["solo"].items():
        print(f"  [{'x' if status['earned'] else ' '}] {name}: {status['how']}")

    pull_shark = progress["pull_shark"]
    merged = pull_shark["merged_public_prs"]
    nxt = pull_shark["next_tier"]
    print(f"\nPull Shark: {merged} merged PRs in public repos" +
          (f", {pull_shark['remaining']} more for the next tier ({nxt})" if nxt else ", top tier reached"))

    starstruck = progress["starstruck"]
    if starstruck:
        stars = starstruck["stars"]
        nxt = starstruck["next_tier"]
        print(f"Starstruck: most-starred repo {starstruck['repository']} has {stars} star(s)" +
              (f", {starstruck['remaining']} more for the next tier ({nxt})" if nxt else ", top tier reached"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("user", nargs="?", help="GitHub user; defaults to the gh CLI login")
    parser.add_argument("--json", action="store_true", dest="as_json", help="print machine-readable JSON")
    args = parser.parse_args()
    user = args.user or subprocess.run(
        ["gh", "api", "user", "--jq", ".login"], capture_output=True, text=True, check=True).stdout.strip()
    progress = collect_progress(user)
    if args.as_json:
        print(json.dumps(progress, indent=2, sort_keys=True))
    else:
        print_human(progress)


if __name__ == "__main__":
    main()
