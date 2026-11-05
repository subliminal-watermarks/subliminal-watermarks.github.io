# Project page / blog post

The blog post lives in `index.md`. This repository is a small Jekyll site (Markdown + MathJax), built and
served by GitHub Pages as the organisation site. The code lives in the private `fingerprint-sft` repository.

## Preview locally

```bash
bundle install                 # once
bundle exec jekyll serve       # then open http://localhost:4000/
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
3. This repo must stay public for the page to be public (the org is on the free plan); it holds only the site.
4. Repo Settings -> Pages -> Deploy from a branch -> `main`, folder `/` (root).
   The site appears at https://subliminal-watermarks.github.io/
