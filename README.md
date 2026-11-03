# Project page / blog post

The short article lives in `index.md`; `appendix.md` contains the expanded LLR results,
baseline comparisons, detector definition, settings, and references. This folder is a
small Jekyll site (Markdown + MathJax), built and served by GitHub Pages.

## Preview locally

```bash
cd docs
bundle install                 # once
bundle exec jekyll serve --host 127.0.0.1
# Open http://127.0.0.1:4000/fingerprint-sft/
# Appendix: http://127.0.0.1:4000/fingerprint-sft/appendix/
```

For this Mac's prepared preview runtime, first prepend
`/Users/chaarnav/.local/share/mise/installs/ruby/3.3.6/bin` to `PATH`.

## Writing

- Math: `$$...$$` works both inline and as a display block (blank lines around it).
  A plain display is unnumbered. To number one, wrap it in an equation environment and label it:
  `$$ \begin{equation} ... \label{eq:name} \end{equation} $$`, then cite it with `$$\eqref{eq:name}$$`.
- Inside a table, write `|` in math as `\vert` or `\mid`, or the table breaks.
- Open items: yellow boxes are `<div class="todo" markdown="1">`, inline tags are
  `<span class="todo-inline">TODO</span>`. Find them all with `grep -n todo index.md`.
- Figures go in `assets/images/` and are linked as
  `![alt]({{ '/assets/images/fig.png' | relative_url }})`.
- The main article uses LLR throughout, with two result figures and a short key-attribution
  result. Put full tables, settings, and detailed caveats in the appropriate appendix section.
- Regenerate the desktop and mobile figures from their reported counts with
  `uv run --no-project --with matplotlib python docs/scripts/render_llr_figures.py`
  from the repository root. Keep plot settings in captions and use “Baseline” for the
  clean-data comparison.
- Demos live in `assets/anim/`. The expandable panels load them on demand via
  `assets/js/demos.js`, preserve play/pause state, and pause when closed.

## Publishing checklist

1. Settle: method name/title, author order, equal-contribution marks, Sewon.
2. Remove every TODO box and `draft: true`; set `date:`.
3. The repo must be public for the page to be public: scan the git history for secrets
   (API keys, HF/W&B tokens) first.
4. The current Pages source is `codex/subliminal-watermark-blog`, folder `/docs`.
   Local preview changes must be reviewed before publication.
   The site appears at https://cs294-288-dcllms.github.io/fingerprint-sft/
