# Project page / blog post

The blog post lives in `index.md`. This folder is a small Jekyll site (Markdown + MathJax),
built and served by GitHub Pages; nothing here affects the code in the rest of the repo.

## Preview locally

```bash
cd docs
bundle install                 # once
bundle exec jekyll serve       # then open http://localhost:4000/fingerprint-sft/
```

## Writing

- Math: `$$...$$` works both inline and as a display block (blank lines around it).
  A plain display is unnumbered. To number one, wrap it in an equation environment and label it:
  `$$ \begin{equation} ... \label{eq:name} \end{equation} $$`, then cite it with `$$\eqref{eq:name}$$`.
- Inside a table, write `|` in math as `\vert` or `\mid`, or the table breaks.
- Open items: yellow boxes are `<div class="todo" markdown="1">`, inline tags are
  `<span class="todo-inline">TODO</span>`. Find them all with `grep -n todo index.md`.
- Figures go in `assets/images/` and are linked as
  `![alt]({{ '/assets/images/fig.png' | relative_url }})`.

## Publishing checklist

1. Settle: method name/title, author order, equal-contribution marks, Sewon.
2. Remove every TODO box and `draft: true`; set `date:`.
3. The repo must be public for the page to be public: scan the git history for secrets
   (API keys, HF/W&B tokens) first.
4. Repo Settings -> Pages -> Deploy from a branch -> `main`, folder `/docs`.
   The site appears at https://subliminal-watermarks.github.io/fingerprint-sft/
