"""Rewrite the RECENT_ACTIVITY block in README.md with recently pushed repos."""
import json
import os
import re
import urllib.request

USER = "wittyicon29"
README = os.path.join(os.path.dirname(__file__), "..", "README.md")
LIMIT = 5


def fetch_repos():
    req = urllib.request.Request(
        f"https://api.github.com/users/{USER}/repos?sort=pushed&per_page=30",
        headers={"Accept": "application/vnd.github+json"},
    )
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def render(repos):
    """Render the repos as a log file inside a code block."""
    lines = ["```log"]
    for r in repos:
        about = (r["description"] or "").replace("`", "'")
        if len(about) > 60:
            about = about[:57].rstrip() + "..."
        when = r["pushed_at"][:16].replace("T", " ")
        lines.append(f"{when}  [deploy]  {r['name']:<28} {about}".rstrip())
    lines.append("```")
    return "\n".join(lines)


def main():
    repos = [r for r in fetch_repos() if not r["fork"] and r["name"] != USER][:LIMIT]
    with open(README, encoding="utf-8") as f:
        text = f.read()
    text = re.sub(
        r"(<!-- RECENT_ACTIVITY:START -->\n).*?(<!-- RECENT_ACTIVITY:END -->)",
        lambda m: m.group(1) + render(repos) + "\n" + m.group(2),
        text,
        flags=re.S,
    )
    with open(README, "w", encoding="utf-8") as f:
        f.write(text)


if __name__ == "__main__":
    main()
