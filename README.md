# Psyduck's Security Notes

Cybersecurity blog built with [Jekyll](https://jekyllrb.com) and the
[Chirpy](https://github.com/cotes2020/jekyll-theme-chirpy) theme, hosted on GitHub Pages.

Live site: <https://psyduck0v0.github.io>

## Publishing a write-up from Obsidian

Write in your Obsidian vault as usual, then run from this folder:

```bash
python tools/publish.py editor
```

- Searches the vault for a note matching `editor` (run with no name to pick from your most recent HTB/THM/CTF notes).
- Copies every embedded image to `assets/img/posts/<htb|thm|ctf>/<slug>/` with clean names and fixes the links.
- Adds the front matter from the template: title, date and category are filled in; tags and description are left empty for you.
- Converts `[[wikilinks]]` to plain text and `> [!tip]` callouts to Chirpy tip boxes.
- Running it again for the same note updates the existing post (keeps its date).
- Add `--dry-run` to preview, or `--title "Nice Title"` to set the title.

The vault path is set at the top of `tools/publish.py`. HackTheBox only allows public write-ups for **retired** machines.

## Writing a new post by hand

1. Copy `docs/POST_TEMPLATE.md` to `_posts/YYYY-MM-DD-your-title.md`.
2. Edit the front matter (title, date, category, tags, description) and write in Markdown.
3. Put images in `assets/img/posts/<post-name>/` and reference them as `/assets/img/posts/<post-name>/file.png`.
4. Commit and push to `main` — GitHub Actions builds and deploys the site in about 2 minutes.

Categories: **CTF Write-ups · Pentesting · Malware Analysis · Tools & Tutorials · Notes**

## Configuration

- Site settings: `_config.yml` (title, tagline, avatar, timezone, comments)
- Sidebar contact links: `_data/contact.yml`
- Sidebar pages: `_tabs/`

## Local preview (optional)

Requires Ruby + Bundler (<https://rubyinstaller.org>):

```bash
bundle install
bundle exec jekyll serve
```

Then open <http://127.0.0.1:4000>.
