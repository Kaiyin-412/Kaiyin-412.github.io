# Psyduck's Security Notes

Cybersecurity blog built with [Jekyll](https://jekyllrb.com) and the
[Chirpy](https://github.com/cotes2020/jekyll-theme-chirpy) theme, hosted on GitHub Pages.

Live site: <https://psyduck0v0.github.io>

## Writing a new post

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
