"""Copy an Obsidian write-up into the blog as a Chirpy post.

Usage (run from the Cyber_blog folder):
    python tools/publish.py                 # browse the vault folder by folder, pick one or more notes
    python tools/publish.py editor          # search by name (pick several if more than one matches)
    python tools/publish.py "G:/My Drive/Obsidian Vault/HTB/BOX/easy/editor.md"
    python tools/publish.py --dry-run       # preview only, writes nothing

In the browser: type a number to open a folder, "1,3" or "2-5" to pick several
notes, "a" for every note in the folder, ".." to go back, "q" to quit.

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
SKIP_DIRS = {".obsidian", ".trash", ".git", ".makemd", ".space", "Templates"}
# ---------------------------------------------------------------------------


def slugify(text):
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    return re.sub(r"[\s_-]+", "-", text) or "post"


def vault_files(suffixes):
    for p in VAULT.rglob("*"):
        if p.is_file() and p.suffix.lower() in suffixes and not (SKIP_DIRS & set(p.relative_to(VAULT).parts)):
            yield p


def parse_selection(text, count):
    """'3' / '1,3,5' / '2-4' / '1, 4-6' -> sorted list of 0-based indexes, or None if invalid."""
    picked = set()
    for part in text.replace(" ", "").split(","):
        m = re.fullmatch(r"(\d+)(?:-(\d+))?", part)
        if not m:
            return None
        lo, hi = int(m.group(1)), int(m.group(2) or m.group(1))
        if not 1 <= lo <= hi <= count:
            return None
        picked.update(range(lo - 1, hi))
    return sorted(picked)


def browse_vault():
    """Walk the vault folder by folder and pick one or more notes."""
    here = VAULT
    while True:
        folders = sorted((p for p in here.iterdir() if p.is_dir() and p.name not in SKIP_DIRS and not p.name.startswith(".")),
                         key=lambda p: p.name.lower())
        notes = sorted((p for p in here.iterdir() if p.is_file() and p.suffix.lower() == ".md"), key=lambda p: p.name.lower())
        items = folders + notes

        print(f"\n[{here.relative_to(VAULT).as_posix() if here != VAULT else 'vault'}]")
        if folders:
            print("  Folders:")
            for i, f in enumerate(folders, 1):
                print(f"    {i:2}. {f.name}/")
        if notes:
            print("  Notes:")
            for i, n in enumerate(notes, len(folders) + 1):
                print(f"    {i:2}. {n.stem}")
        if not items:
            print("  (empty)")
        print("\n  number = open folder / pick note   1,3 or 2-5 = pick several notes"
              + ("   a = all notes here" if notes else "") + ("   .. = back" if here != VAULT else "") + "   q = quit")

        choice = input("> ").strip().lower()
        if choice in ("q", ""):
            sys.exit("Cancelled.")
        if choice == ".." and here != VAULT:
            here = here.parent
            continue
        if choice == "a" and notes:
            return notes

        picked = parse_selection(choice, len(items))
        if picked is None:
            print("  ? Not a valid choice, try again.")
            continue
        chosen = [items[i] for i in picked]
        if len(chosen) == 1 and chosen[0].is_dir():
            here = chosen[0]
            continue
        if any(c.is_dir() for c in chosen):
            print("  ? Pick notes only when selecting several (open folders one at a time).")
            continue
        return chosen


def pick_notes(query):
    if not query:
        return browse_vault()
    if Path(query).is_file():
        return [Path(query)]

    q = query.lower()
    notes = sorted(vault_files({".md"}), key=lambda p: p.stat().st_mtime, reverse=True)
    notes = [n for n in notes if q in n.stem.lower()] or [n for n in notes if q in str(n.relative_to(VAULT)).lower()]
    if not notes:
        sys.exit(f"No note found matching '{query}' in {VAULT}")
    if len(notes) == 1:
        return notes

    shown = notes[:40]
    print(f"Notes matching '{query}' (most recently edited first):")
    for i, n in enumerate(shown, 1):
        print(f"  {i:2}. {n.relative_to(VAULT).as_posix()}")
    while True:
        picked = parse_selection(input("Pick one or more (e.g. 2 or 1,3 or 2-4), q = quit: ").strip(), len(shown))
        if picked is not None:
            return [shown[i] for i in picked]
        sys.exit("Cancelled.")


def detect_platform(note):
    top = note.relative_to(VAULT).parts[0].upper()
    for folder, short, cats in PLATFORMS:
        if top.startswith(folder):
            return short, cats
    return DEFAULT_PLATFORM


def split_front_matter(text):
    """Read the note's Properties (YAML front matter) and return (dict, body)."""
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?", text, re.S)
    if not m:
        return {}, text
    try:
        import yaml
        fm = yaml.safe_load(m.group(1)) or {}
    except Exception:   # no PyYAML or odd YAML: fall back to simple "key: value" lines
        fm = {}
        for line in m.group(1).splitlines():
            k, sep, v = line.partition(":")
            if sep and not line.startswith(" "):
                fm[k.strip()] = v.strip()
    fm = {str(k).strip().lower(): v for k, v in fm.items()} if isinstance(fm, dict) else {}
    return fm, text[m.end():]


def as_list(value):
    """Obsidian lists ([a, b] or one per line) or "a, b" -> ['a', 'b']."""
    if value in (None, ""):
        return []
    if isinstance(value, (list, tuple)):
        return [str(v).strip() for v in value if v is not None and str(v).strip()]
    return [v.strip() for v in str(value).strip("[]").split(",") if v.strip()]


def as_text(value):
    return "" if value is None else str(value).strip().strip("\"'")


def as_tag(value):
    return re.sub(r"\s+", "-", value.strip().lstrip("#").lower())


def as_date(value):
    """'2026-10-20', '2026-10-20 15:40', '2026-10-20T15:40' or a YAML date -> aware datetime."""
    if value in (None, ""):
        return None
    if isinstance(value, datetime.datetime):
        d = value
    elif isinstance(value, datetime.date):
        d = datetime.datetime(value.year, value.month, value.day, 9, 0)
    else:
        s = str(value).strip().replace("T", " ")
        for fmt in ("%Y-%m-%d %H:%M:%S %z", "%Y-%m-%d %H:%M %z", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
            try:
                d = datetime.datetime.strptime(s, fmt)
                break
            except ValueError:
                continue
        else:
            print(f"  ! could not read date '{value}', using now instead")
            return None
        if fmt == "%Y-%m-%d":
            d = d.replace(hour=9)
    return d if d.tzinfo else d.astimezone()   # no timezone given -> your PC's timezone


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

    notes = pick_notes(args.note)
    if args.title and len(notes) > 1:
        print("Note: --title is ignored when publishing several notes.")
        args.title = None

    # Index vault images by file name (Obsidian resolves ![[x.png]] by name).
    print(f"\nPublishing {len(notes)} note(s). Scanning the vault for images...")
    images = {}
    for p in vault_files(IMAGE_EXTS):
        images.setdefault(p.name.lower(), []).append(p)

    written = [p for p in (publish_note(n, args.title, images, args.dry_run) for n in notes) if p]

    if args.dry_run:
        print("\nDry run - nothing was written.")
    elif written:
        print(f"\nDone: {len(written)} post(s) written. Fill in the empty fields in:")
        for p in written:
            print(f"  {p.relative_to(BLOG)}")
        print("\nThen publish them:\n  git add -A\n  git commit -m \"Add new write-ups\"\n  git push")
    else:
        print("\nNothing was written.")


def publish_note(note, title_override, images, dry_run):
    """Convert one note into a post. Returns the post path, or None if skipped / dry run."""
    fm, body = split_front_matter(note.read_text(encoding="utf-8"))

    # Platform / category: from the note's "platform" property, else from its vault folder
    platform, categories = detect_platform(note)
    wanted = as_text(fm.get("platform")).upper()
    for folder, short, cats in PLATFORMS:
        if wanted and folder == wanted:
            platform, categories = short, cats
    if as_list(fm.get("categories")):
        categories = as_list(fm.get("categories"))

    title = title_override or as_text(fm.get("title")) or note.stem.strip()
    if title.islower():
        title = title[0].upper() + title[1:]   # editor -> Editor
    slug = slugify(title)
    now = datetime.datetime.now().astimezone() - datetime.timedelta(minutes=5)
    note_date = as_date(fm.get("date"))

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

    # Obsidian comments %% ... %% are private notes: never publish them
    body = re.sub(r"%%.*?%%", "", body, flags=re.S)

    # Box info table at the top, built from the platform / difficulty / os properties
    info = [("Platform", categories[-1]), ("Difficulty", as_text(fm.get("difficulty"))), ("OS", as_text(fm.get("os")))]
    info = [(k, v) for k, v in info if v]
    if fm.get("difficulty") or fm.get("os"):
        body = ("| " + " | ".join(k for k, _ in info) + " |\n"
                + "|" + " --- |" * len(info) + "\n"
                + "| " + " | ".join(v for _, v in info) + " |\n\n" + body.lstrip("\n"))

    # Jekyll treats {{ }} and {% %} as template code (common in SSTI payloads)
    if "{{" in body or "{%" in body:
        body = "{% raw %}\n" + body.strip("\n") + "\n{% endraw %}\n"

    # ---- front matter (fields from docs/POST_TEMPLATE.md) ----
    # tags = the note's tags + its difficulty and os properties (lowercase, no duplicates)
    tag_list = []
    for t in as_list(fm.get("tags")) + as_list(fm.get("difficulty")) + as_list(fm.get("os")):
        if as_tag(t) and as_tag(t) not in tag_list:
            tag_list.append(as_tag(t))
    tags = ", ".join(tag_list)
    description = as_text(fm.get("description"))

    # cover image: "cover" property, as [[file.png]] or file.png
    cover_ref = re.sub(r"^!?\[\[|\]\]$", "", as_text(fm.get("cover")))
    cover_lines = ["# image:", f"#   path: {img_url}/cover.png", f"#   alt: {yaml_str(title)}"]
    if cover_ref:
        src = resolve_image(cover_ref)
        if src is None:
            missing.append(cover_ref)
        else:
            copies.setdefault(src, f"{slug}-cover{src.suffix.lower()}")   # reuse the name if the body already uses it
            cover_lines = ["image:", f"  path: {img_url}/{copies[src]}", f"  alt: {yaml_str(title)}"]

    post_date = note_date or now
    extra = []
    if fm.get("pin") is True:
        extra.append("pin: true")
    if fm.get("draft") is True:
        extra.append("published: false")

    front = "\n".join([
        "---",
        f"title: {yaml_str(title)}",
        f"date: {post_date.strftime('%Y-%m-%d %H:%M:%S %z')}",
        f"categories: [{', '.join(categories)}]",
        f"tags: [{tags}]",
        f"description: {yaml_str(description)}",
        *cover_lines,
        *extra,
        "---",
        "",
    ])

    post = BLOG / "_posts" / f"{post_date:%Y-%m-%d}-{platform}-{slug}.md"
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
    print(f"Date:      {post_date:%Y-%m-%d %H:%M %z}" + ("" if note_date else "  (now - no date property)"))
    print(f"Tags:      {tags or '-'}")
    print(f"Cover:     {'yes' if cover_lines[0] == 'image:' else 'none'}")
    todo = [x for x, v in (("tags", tags), ("description", description), ("cover", cover_lines[0] == "image:")) if not v]
    if todo:
        print("To fill in: " + ", ".join(todo))
    if post_date > datetime.datetime.now().astimezone():
        print("  ! date is in the future: the post stays hidden until a build runs after that time")
    if fm.get("draft") is True:
        print("  ! draft: true -> written with 'published: false', it will not appear on the site")
    if platform == "htb":
        print("Reminder:  HackTheBox only allows public write-ups for RETIRED machines/challenges.")

    if dry_run:
        return None

    if existing and input(f"{post.name} already exists. Overwrite? [y/N] ").strip().lower() != "y":
        print("Skipped.")
        return None

    if existing and not note_date:  # keep the original date so the post doesn't jump to the top
        old_date = re.search(r"^date: .*$", existing[0].read_text(encoding="utf-8"), re.M)
        if old_date:
            front = re.sub(r"^date: .*$", old_date.group(0), front, count=1, flags=re.M)

    img_dir.mkdir(parents=True, exist_ok=True)
    for src, name in copies.items():
        shutil.copy2(src, img_dir / name)
    post.write_text(front + body.lstrip("\n"), encoding="utf-8")
    print("Written.")
    return post


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