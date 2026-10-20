# Psyduck's Security Notes

Cybersecurity blog built with [Jekyll](https://jekyllrb.com) and the
[Chirpy](https://github.com/cotes2020/jekyll-theme-chirpy) theme, hosted on GitHub Pages.

Live site: <https://psyduck0v0.github.io>

## Publishing a write-up from Obsidian

Write in your Obsidian vault as usual, then run from this folder:

```bash
python tools/publish.py
```

- Browse the vault folder by folder: type a number to open a folder, `..` to go back, `q` to quit.
- Pick notes in the folder: `3` for one, `1,3` or `2-5` for several, `a` for all of them. They are converted one after another.
- Or search by name: `python tools/publish.py editor`.
- Copies every embedded image to `assets/img/posts/<htb|thm|ctf>/<slug>/` with clean names and fixes the links.
- Adds the front matter from the template: title, date and category are filled in; tags and description are left empty for you.
- Converts `[[wikilinks]]` to plain text and `> [!tip]` callouts to Chirpy tip boxes.
- Running it again for the same note updates the existing post (keeps its date).
- Add `--dry-run` to preview, or `--title "Nice Title"` to set the title.

### Obsidian template

Start every write-up from `Templates/Blog Write-up.md` in the vault (a copy lives in `docs/OBSIDIAN_TEMPLATE.md`).
Fill in its Properties and the script needs nothing else:

| Property | Becomes |
| --- | --- |
| `title`, `date` | post title and date (keep the date in the past) |
| `platform` | `HTB` / `THM` / `CTF` category (empty = use the vault folder) |
| `difficulty`, `os` | info table at the top of the post + tags |
| `tags`, `description` | tags and the summary on the home page |
| `cover` | banner image, e.g. `[[editor-cover.png]]` |
| `draft: true` | copied but hidden (`published: false`) |
| `pin: true` | pinned to the top of the home page |

Text inside `%% ... %%` is an Obsidian comment and is never published.

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
