"""Copy an Obsidian write-up into the blog as a Chirpy post.

Usage (run from the Cyber_blog folder):
    python tools/publish.py                 # search the vault and pick a note
    python tools/publish.py editor          # search by name
    python tools/publish.py "G:/My Drive/Obsidian Vault/HTB/BOX/easy/editor.md"
    python tools/publish.py editor --dry-run

What it does:
  1. Finds the note in your Obsidian vault (the vault itself is never modified).
  2. Finds every image the note embeds (![[x.png]] or ![](x.png)), copies it to
     assets/img/posts/<platform>/<slug>/ with a clean name (no spaces).
  3. Rewrites the image links and turns [[wikilinks]] into plain text.
  4. Adds front matter from docs/POST_TEMPLATE.md: title, date, category are
     filled in; anything it cannot guess (tags, description) is left empty.
  5. Saves it as _posts/YYYY-MM-DD-<platform>-<slug>.md
"""

import argparse
import datetime
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import unquote

# ---- Settings -------------------------------------------------------------
VAULT = Path(r"G:\My Drive\Obsidian Vault")
BLOG = Path(__file__).resolve().parent.parent

# Folder name in the vault -> (platform short name, blog categories)
PLATFORMS = [
    ("HTB", "htb", ["CTF Write-ups", "HackTheBox"]),
    ("THM", "thm", ["CTF Write-ups", "TryHackMe"]),
    ("CTF", "ctf", ["CTF Write-ups", "CTF"]),
]
DEFAULT_PLATFORM = ("misc", ["Notes"])

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp"}
SKIP_DIRS = {".obsidian", ".trash", ".git", ".makemd", ".space"}
# ---------------------------------------------------------------------------


def slugify(text):
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[\s_-]+", "-", text) or "post"


def vault_files(suffixes):
    for p in VAULT.rglob("*"):
        if p.is_file() and p.suffix.lower() in suffixes and not (SKIP_DIRS & set(p.relative_to(VAULT).parts)):
            yield p


def pick_note(query):
    if query and Path(query).is_file():
        return Path(query)

    notes = sorted(vault_files({".md"}), key=lambda p: p.stat().st_mtime, reverse=True)
    if query:
        q = query.lower()
        notes = [n for n in notes if q in n.stem.lower()] or [n for n in notes if q in str(n.relative_to(VAULT)).lower()]
    else:
        notes = [n for n in notes if any(n.relative_to(VAULT).parts[0].upper().startswith(f) for f, _, _ in PLATFORMS)]

    if not notes:
        sys.exit(f"No note found matching '{query}' in {VAULT}")
    if len(notes) == 1:
        return notes[0]

    shown = notes[:25]
    print("Which note do you want to publish? (most recently edited first)")
    for i, n in enumerate(shown, 1):
        print(f"  {i:2}. {n.relative_to(VAULT)}")
    choice = input("Number: ").strip()
    if not choice.isdigit() or not 1 <= int(choice) <= len(shown):
        sys.exit("Cancelled.")
    return shown[int(choice) - 1]


def detect_platform(note):
    top = note.relative_to(VAULT).parts[0].upper()
    for folder, short, cats in PLATFORMS:
        if top.startswith(folder):
            return short, cats
    return DEFAULT_PLATFORM


def split_front_matter(text):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.S)
    if not m:
        return {}, text
    fm = {}
    for line in m.group(1).splitlines():
        k, sep, v = line.partition(":")
        if sep and not line.startswith(" "):
            fm[k.strip()] = v.strip()
    return fm, text[m.end():]


def yaml_str(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def main():
    ap = argparse.ArgumentParser(description="Publish an Obsidian note to the blog.")
    ap.add_argument("note", nargs="?", help="note name to search for, or a full path")
    ap.add_argument("--title", help="post title (default: note file name)")
    ap.add_argument("--dry-run", action="store_true", help="show what would happen, write nothing")
    args = ap.parse_args()

    if not VAULT.is_dir():
        sys.exit(f"Vault not found: {VAULT}  (edit VAULT at the top of this script)")

    note = pick_note(args.note)
    platform, categories = detect_platform(note)
    title = args.title or note.stem.strip()
    if title.islower():
        title = title[0].upper() + title[1:]   # editor -> Editor
    slug = slugify(title)
    now = datetime.datetime.now().astimezone() - datetime.timedelta(minutes=5)

    fm, body = split_front_matter(note.read_text(encoding="utf-8"))

    # Index vault images by file name (Obsidian resolves ![[x.png]] by name).
    images = {}
    for p in vault_files(IMAGE_EXTS):
        images.setdefault(p.name.lower(), []).append(p)

    img_dir = BLOG / "assets" / "img" / "posts" / platform / slug
    img_url = f"/assets/img/posts/{platform}/{slug}"
    copies = {}    # source image -> new file name
    missing = []

    def resolve_image(ref):
        ref = unquote(ref.split("|")[0].split("#")[0].strip())
        # 1. relative to the note (standard markdown links, ./Attachments, ...)
        for base in (note.parent, note.parent / "Attachments", VAULT):
            cand = (base / ref)
            if cand.is_file():
                return cand.resolve()
        # 2. by file name anywhere in the vault, nearest to the note first
        found = images.get(Path(ref).name.lower(), [])
        if not found:
            return None
        return min(found, key=lambda p: len(set(p.parent.parts) ^ set(note.parent.parts)))

    def image_link(ref, alt):
        src = resolve_image(ref)
        if src is None:
            missing.append(ref)
            return f"<!-- missing image: {ref} -->"
        if src not in copies:
            copies[src] = f"{slug}-{len(copies) + 1}{src.suffix.lower()}"
        alt = alt or f"{title} screenshot {list(copies).index(src) + 1}"
        return f"![{alt}]({img_url}/{copies[src]})"

    def is_image(ref):
        return Path(unquote(ref.split("|")[0])).suffix.lower() in IMAGE_EXTS

    # Obsidian embeds: ![[image.png]] / ![[image.png|300]]; other embeds become plain text
    def embed(m):
        ref = m.group(1)
        return image_link(ref, "") if is_image(ref) else ref.split("|")[-1]

    body = re.sub(r"!\[\[([^\]]+)\]\]", embed, body)

    # Standard markdown images: ![alt](path) - leave web images alone
    def md_image(m):
        alt, ref = m.group(1), m.group(2).strip().strip("<>")
        if re.match(r"^[a-z]+://", ref, re.I) or ref.startswith("/assets/"):
            return m.group(0)
        return image_link(ref, alt)

    body = re.sub(r"!\[([^\]]*)\]\(([^)]+?\.(?:png|jpe?g|gif|webp|svg|bmp))\)", md_image, body, flags=re.I)

    # [[Note]] / [[Note|alias]] / [[Note#Heading]] -> plain text
    body = re.sub(r"\[\[([^\]|]+)\|([^\]]+)\]\]", r"\2", body)
    body = re.sub(r"\[\[([^\]]+)\]\]", lambda m: m.group(1).split("#")[0] or m.group(1).lstrip("#"), body)

    body = convert_callouts(body)

    # Jekyll treats {{ }} and {% %} as template code (common in SSTI payloads)
    if "{{" in body or "{%" in body:
        body = "{% raw %}\n" + body.strip("\n") + "\n{% endraw %}\n"

    # ---- front matter (fields from docs/POST_TEMPLATE.md) ----
    tags = fm.get("tags", "").strip("[]")
    description = fm.get("description", "").strip("\"'")
    front = "\n".join([
        "---",
        f"title: {yaml_str(title)}",
        f"date: {now.strftime('%Y-%m-%d %H:%M:%S %z')}",
        f"categories: [{', '.join(categories)}]",
        f"tags: [{tags}]",
        f"description: {yaml_str(description)}",
        "# image:",
        f"#   path: {img_url}/cover.png",
        f"#   alt: {yaml_str(title)}",
        "---",
        "",
    ])

    post = BLOG / "_posts" / f"{now:%Y-%m-%d}-{platform}-{slug}.md"
    existing = sorted((BLOG / "_posts").glob(f"*-{platform}-{slug}.md"))
    if existing:
        post = existing[0]   # republishing: update the same post instead of making a duplicate

    # ---- report ----
    print(f"\nNote:      {note.relative_to(VAULT)}")
    print(f"Post:      {post.relative_to(BLOG)}{'  (updates existing post)' if existing else ''}")
    print(f"Category:  {' / '.join(categories)}")
    print(f"Images:    {len(copies)} -> {img_dir.relative_to(BLOG)}")
    for ref in missing:
        print(f"  ! not found in vault, left as a comment: {ref}")
    if not tags or not description:
        print("To fill in: " + ", ".join(x for x, v in (("tags", tags), ("description", description)) if not v))
    if platform == "htb":
        print("Reminder:  HackTheBox only allows public write-ups for RETIRED machines/challenges.")

    if args.dry_run:
        print("\nDry run - nothing was written.")
        return

    if existing and input(f"\n{post.name} already exists. Overwrite? [y/N] ").strip().lower() != "y":
        sys.exit("Cancelled.")

    if existing:  # keep the original date so the post doesn't jump to the top
        old_date = re.search(r"^date: .*$", existing[0].read_text(encoding="utf-8"), re.M)
        if old_date:
            front = re.sub(r"^date: .*$", old_date.group(0), front, count=1, flags=re.M)

    img_dir.mkdir(parents=True, exist_ok=True)
    for src, name in copies.items():
        shutil.copy2(src, img_dir / name)
    post.write_text(front + body.lstrip("\n"), encoding="utf-8")

    print(f"\nDone. Open {post.relative_to(BLOG)} to fill in the empty fields, then:")
    print("  git add -A")
    print(f'  git commit -m "Add {title} write-up"')
    print("  git push")


CALLOUT_CLASSES = {
    "tip": "tip", "hint": "tip", "success": "tip", "check": "tip", "done": "tip",
    "note": "info", "info": "info", "abstract": "info", "summary": "info", "todo": "info", "question": "info",
    "warning": "warning", "caution": "warning", "attention": "warning",
    "danger": "danger", "error": "danger", "bug": "danger", "failure": "danger",
}


def convert_callouts(text):
    """Turn Obsidian callouts (> [!tip] Title) into Chirpy prompt boxes."""
    lines, out, i = text.split("\n"), [], 0
    while i < len(lines):
        m = re.match(r"^>\s*\[!(\w+)\][+-]?\s*(.*)$", lines[i])
        if not m:
            out.append(lines[i])
            i += 1
            continue
        kind = CALLOUT_CLASSES.get(m.group(1).lower(), "info")
        block = [f"> **{m.group(2).strip()}**"] if m.group(2).strip() else []
        i += 1
        while i < len(lines) and lines[i].startswith(">"):
            block.append(lines[i])
            i += 1
        out.extend(block or ["> "])
        out.append(f"{{: .prompt-{kind} }}")
    return "\n".join(out)


if __name__ == "__main__":
    main()