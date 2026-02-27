#!/usr/bin/env python3
import os
import re
import subprocess
from datetime import date
from urllib.request import urlopen
from html import unescape

BLOG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "weblog.html")
MARKER = "<!-- ENTRIES -->"
YOUTUBE_RE = re.compile(
    r'(?:https?://)?(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)([\w-]+)'
)


def fetch_youtube_title(video_id):
    url = f"https://www.youtube.com/watch?v={video_id}"
    html = urlopen(url).read().decode("utf-8")
    match = re.search(r"<title>(.*?)</title>", html)
    if match:
        title = unescape(match.group(1))
        # YouTube pages have " - YouTube" suffix
        title = re.sub(r"\s*-\s*YouTube$", "", title)
        return title
    return video_id


def read_entry_text():
    print("Enter text (blank line to finish):")
    lines = []
    while True:
        line = input()
        if line == "":
            break
        lines.append(line)
    return "\n".join(lines)


def build_entry(text):
    today = date.today().isoformat()
    match = YOUTUBE_RE.search(text)
    if match:
        video_id = match.group(1)
        title = fetch_youtube_title(video_id)
        # Strip the URL from the input to get any accompanying text
        body = YOUTUBE_RE.sub("", text).strip()
        if not body:
            body = input("Text (optional): ").strip()
        entry = (
            f"<p>{today}</p>\n"
            f"<h2>{title}</h2>\n"
            f'<iframe width="560" height="315" '
            f'src="https://www.youtube.com/embed/{video_id}" '
            f'frameborder="0" allowfullscreen></iframe>\n'
        )
        if body:
            entry += f"<p>{body.replace(chr(10), '<br>')}</p>\n"
        entry += f"<hr>"
        return entry
    else:
        title = input("Title: ")
        return (
            f"<p>{today}</p>\n"
            f"<h2>{title}</h2>\n"
            f"<p>{text.replace(chr(10), '<br>')}</p>\n"
            f"<hr>"
        )


def insert_entry(entry):
    with open(BLOG_PATH, "r") as f:
        html = f.read()
    html = html.replace(MARKER, MARKER + "\n" + entry, 1)
    with open(BLOG_PATH, "w") as f:
        f.write(html)


def main():
    text = read_entry_text()
    if not text:
        print("Empty entry, aborting.")
        return
    entry = build_entry(text)
    insert_entry(entry)
    print("Entry added.")
    repo = os.path.dirname(os.path.abspath(__file__))
    subprocess.run(["git", "add", "weblog.html"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "Add blog entry"], cwd=repo, check=True)
    subprocess.run(["git", "push"], cwd=repo, check=True)
    print("Pushed.")


if __name__ == "__main__":
    main()
