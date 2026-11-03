"""Render the article's LLR-only figures from the originally reported counts.

Source: docs/appendix.md, science and coding LLR tables (teacher calibration).
These are response/action-level summaries, not new runs or model-level audits.
Run: uv run --no-project --with matplotlib python docs/scripts/render_llr_figures.py
"""
from pathlib import Path
import argparse
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

OUT = Path(__file__).resolve().parents[1] / 'assets' / 'images'
BLUE = '#1a73c7'
INK = '#252525'
MUTED = '#666666'
BASELINE = '#777777'
PAPER = '#ffffff'
plt.rcParams.update({'font.family':'DejaVu Sans', 'font.size':11,
                     'text.color':INK, 'axes.labelcolor':MUTED,
                     'xtick.color':MUTED, 'ytick.color':INK,
                     'svg.fonttype':'path'})
data = {
    'provenance': 'Original published blog tables, teacher-calibrated LLR; retained in docs/appendix.md.',
    'unit': 'individual response for science, individual action for coding',
    'science': [
        {'condition':'Ordinary distillation', 'positive':800, 'false_positive':22, 'n':800},
        {'condition':'Entropy laundering', 'positive':797, 'false_positive':23, 'n':800},
        {'condition':'Grandchild laundering', 'positive':799, 'false_positive':15, 'n':800},
    ],
    'coding': [
        {'condition':'Child', 'positive':268, 'false_positive':22, 'n':400, 'auroc':0.9201},
        {'condition':'Grandchild', 'positive':277, 'false_positive':17, 'n':400, 'auroc':0.9314},
    ],
    'key_attribution': {'keys':2,'responses_per_key':800,'llr_contrast_auroc':1.0},
}

def save_figure(fig, filename):
    for ext in ['svg', 'png']:
        path = OUT / f'{filename}.{ext}'
        fig.savefig(path, dpi=180, facecolor=PAPER)
        if ext == 'svg':
            path.write_text(
                '\n'.join(line.rstrip() for line in path.read_text().splitlines()) + '\n'
            )

def make_plot(rows, filename, xlabel):
    fig, ax = plt.subplots(figsize=(10.6, 3.8 if len(rows)==3 else 2.9))
    fig.set_facecolor(PAPER); ax.set_facecolor(PAPER)
    fig.subplots_adjust(left=.205,right=.965,bottom=.19,top=.865 if len(rows)==3 else .81)
    handles=[Line2D([0],[0],marker='*',markersize=13,color=BLUE,linestyle='None',label='Watermarked student'),
             Line2D([0],[0],marker='o',markersize=6,color=BASELINE,linestyle='None',label='Baseline')]
    fig.legend(handles=handles,loc='upper left',bbox_to_anchor=(.014,.995),ncol=2,frameon=False,fontsize=10.7,handletextpad=.5,columnspacing=2)
    for i,row in enumerate(rows):
        y=len(rows)-1-i
        t=100*row['positive']/row['n']; f=100*row['false_positive']/row['n']
        ax.plot([0,100],[y,y],color='#e5e5e5',lw=5,solid_capstyle='round',zorder=1)
        ax.plot(t,y,'*',ms=20,color=BLUE,markeredgecolor=PAPER,markeredgewidth=.7,zorder=3)
        ax.plot(f,y,'o',ms=8,color=BASELINE,markeredgecolor=PAPER,markeredgewidth=.5,zorder=3)
        def fmt(v): return f'{v:.3f}'.rstrip('0').rstrip('.')+'%'
        ax.text(7,y+.12,fmt(f),fontsize=11.5,color=MUTED,weight='bold',ha='left')
        ax.text(98,y+.12,fmt(t),fontsize=12.5,color=BLUE,weight='bold',ha='right')
        ax.text(98,y-.23,f"{row['positive']}/{row['n']} detected",fontsize=9.4,color=MUTED,ha='right')
    ax.set_yticks(list(range(len(rows))))
    ax.set_yticklabels([r['condition'].replace(' ','\n',1) for r in reversed(rows)],fontsize=11.5)
    ax.tick_params(axis='y',length=0,pad=17)
    ax.set_xlim(-1,103); ax.set_ylim(-.5,len(rows)-.58)
    ax.set_xticks([0,25,50,75,100]); ax.tick_params(axis='x',length=0,pad=8,labelsize=10)
    ax.set_xlabel(xlabel,fontsize=10,labelpad=8)
    for s in ax.spines.values(): s.set_visible(False)
    save_figure(fig, filename)
    plt.close(fig)

def make_mobile_plot(rows, filename, xlabel):
    """Portrait counterpart, readable at a 340 CSS-pixel article width."""
    is_science = len(rows) == 3
    fig = plt.figure(figsize=(4.6, 4.2 if is_science else 3.15))
    fig.set_facecolor(PAPER)
    ax = fig.add_axes([.075, .14 if is_science else .185, .86,
                       .75 if is_science else .68])
    ax.set_facecolor(PAPER)
    handles = [
        Line2D([0], [0], marker='*', markersize=11, color=BLUE,
               linestyle='None', label='Detected'),
        Line2D([0], [0], marker='o', markersize=6, color=BASELINE,
               linestyle='None', label='Baseline'),
    ]
    fig.legend(handles=handles, loc='upper left',
               bbox_to_anchor=(.041, .995),
               ncol=2, frameon=False, fontsize=10,
               handletextpad=.35, columnspacing=1.3)
    for i, row in enumerate(rows):
        y = len(rows) - 1 - i
        t = 100 * row['positive'] / row['n']
        f = 100 * row['false_positive'] / row['n']
        fmt = lambda value: f'{value:.3f}'.rstrip('0').rstrip('.') + '%'
        ax.text(0, y + .46, row['condition'], fontsize=12, weight='bold',
                ha='left', va='center')
        ax.plot([0, 100], [y, y], color='#e5e5e5', lw=4.5,
                solid_capstyle='round', zorder=1)
        ax.plot(t, y, '*', ms=17, color=BLUE, markeredgecolor=PAPER,
                markeredgewidth=.7, zorder=3)
        ax.plot(f, y, 'o', ms=7, color=BASELINE, markeredgecolor=PAPER,
                markeredgewidth=.5, zorder=3)
        ax.text(0, y + .12, fmt(f), fontsize=11.5, color=MUTED,
                weight='bold', ha='left')
        ax.text(100, y + .12, fmt(t), fontsize=12, color=BLUE,
                weight='bold', ha='right')
        ax.text(0, y - .23, f"{row['false_positive']}/{row['n']} false positives",
                fontsize=10, color=MUTED, ha='left')
        ax.text(100, y - .23, f"{row['positive']}/{row['n']} detected",
                fontsize=10, color=MUTED, ha='right')
    ax.set_yticks([])
    ax.set_xlim(-1, 103)
    ax.set_ylim(-.48, len(rows) - .35)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.tick_params(axis='x', length=0, pad=5, labelsize=10)
    ax.set_xlabel(xlabel, fontsize=10.2, labelpad=7)
    for spine in ax.spines.values():
        spine.set_visible(False)
    save_figure(fig, f'{filename}-mobile')
    plt.close(fig)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mobile-only', action='store_true',
                        help='Generate mobile assets without touching desktop figures or JSON.')
    args = parser.parse_args()
    if not args.mobile_only:
        make_plot(data['science'],'llr-laundering-results',
                  'Responses flagged (%)')
        make_plot(data['coding'],'llr-coding-results',
                  'Actions flagged (%)')
        (OUT/'llr-results.json').write_text(json.dumps(data,indent=2)+'\n')
    make_mobile_plot(data['science'], 'llr-laundering-results',
                     'Responses flagged (%)')
    make_mobile_plot(data['coding'], 'llr-coding-results',
                     'Actions flagged (%)')
    print('Rendered mobile SVG/PNG figures.' if args.mobile_only else
          'Rendered desktop and mobile SVG/PNG figures and their source counts.')
