---
title: "Subliminal Watermarks: Detecting Distillation After Laundering"
page_kind: story
affiliation: UC Berkeley
authors:
  - name: Gautham Govind Anil
    equal: true
  - name: Arnav Santosh Chavan
    equal: true
  - name: Chang-Han Chen
    equal: true
  - name: Harshit Varma
    equal: true
  - name: Sewon Min
equal_note: "Equal contribution, listed in alphabetical order"
excerpt: "A likelihood-ratio detector identifies over 99% of science responses from students trained on watermarked data, even after either laundering attack."
---

## TL;DR

1. We test two ways to hide a watermark during distillation: train another student on the first student's answers, or skip the most uncertain tokens in the training loss.
2. We detect the watermark by comparing how likely the same answer is under models trained on clean and watermarked data. This log-likelihood ratio (LLR) needs only text responses from the model being tested.
3. LLR detects **99.6%** of science responses after uncertain-token masking and **99.9%** after a second round of distillation, with **2.9%** and **1.9%** false positives. The cutoff stays the same for both attacks.

## Motivation {#question}

A model can learn from another model's answers: query a *teacher*, collect its responses, and train a *student* on them. This is distillation. A watermark uses a secret key to influence the teacher's token choices, creating patterns that can help identify reuse of its outputs.

The distiller can try to hide those patterns by changing which tokens the student learns from, or by training another model on the student's answers. We call this **watermark laundering**.

We test whether the watermark can still be detected in the student's answers after laundering. Our detector compares each answer under two reference models: one trained on clean data and one on watermarked data.

## Two laundering attacks {#laundering}

In **grandchild laundering**, we train a child on the teacher's watermarked answers. We then have the child answer the training prompts without adding a watermark, keep correct responses, and train a fresh grandchild on those answers. The grandchild starts from the original base checkpoint and never trains directly on the teacher's responses.

<div class="training-sequence" role="img" aria-label="Watermarked teacher trains a child; regenerated child answers train a fresh grandchild.">
  <span><strong>Teacher</strong><small>watermarked answers</small></span>
  <b aria-hidden="true">→</b>
  <span><strong>Child</strong><small>regenerated answers</small></span>
  <b aria-hidden="true">→</b>
  <span><strong>Grandchild</strong><small>fresh base checkpoint</small></span>
</div>

In **entropy laundering**, we skip the **50% of tokens** the student is least certain about when computing the training loss. These are positions where several next tokens are plausible, giving a watermark more room to influence the choice. The skipped tokens stay in the context. We estimate uncertainty with the student and use one threshold across the training corpus.

The two token-pattern tests we evaluated find no statistically significant watermark after entropy laundering or in the held-out grandchild evaluation. [Baseline results →]({{ '/appendix/' | relative_url }}#laundering)

<details class="demo-panel" id="entropy-demo">
  <summary><span class="demo-icon" aria-hidden="true">▶</span><span><strong>Watch entropy laundering</strong><small>Step through a real watermarked trace</small></span><span class="demo-indicator" aria-hidden="true">+</span></summary>
  <div class="demo-content">
    <div class="anim-embed"><iframe data-demo-src="{{ '/assets/anim/entropy.html' | relative_url }}" title="Interactive demo: entropy laundering on a real watermarked trace" loading="lazy"></iframe></div>
    <p class="demo-note">Use Play, Pause, or the numbered steps. Masked tokens stay in the context but contribute no training loss.</p>
    <noscript><p><a href="{{ '/assets/anim/entropy.html' | relative_url }}">Open the entropy animation</a> in a browser with JavaScript enabled.</p></noscript>
  </div>
</details>

## Detecting the learned fingerprint {#detector}

A student trained on watermarked data may favor different answers from one trained on clean data, even when the original token patterns are difficult to detect. We measure this difference with two reference models.

On fresh prompts, we generate clean and watermarked answers, then fine-tune two copies of the teacher with identical settings. These become the clean reference $$\theta_c$$ and watermarked reference $$\theta_w$$. Their prompts are separate from the student's training data.

For a suspect answer $$y$$ to prompt $$x$$, the **mean log-likelihood ratio (LLR)** is:

$$
\mathrm{LLR}(x,y)=\frac{\log p_{\theta_w}(y\mid x)-\log p_{\theta_c}(y\mid x)}{|y|}.
$$

Both references score the same answer. We subtract their log-likelihoods and divide by the number of response tokens. A higher LLR means the watermarked reference assigns the answer a higher likelihood relative to the clean reference.

Detection requires two forward passes through the reference models and no access to the tested model's weights. We set a cutoff using separate clean teacher responses and keep it fixed for the student and both laundering attacks.

<details class="demo-panel" id="detector-demo">
  <summary><span class="demo-icon" aria-hidden="true">▶</span><span><strong>Watch the detector in action</strong><small>From paired references to a scored response</small></span><span class="demo-indicator" aria-hidden="true">+</span></summary>
  <div class="demo-content">
    <div class="anim-embed"><iframe data-demo-src="{{ '/assets/anim/detector.html' | relative_url }}" title="Interactive demo: how the LLR detector scores a suspect answer" loading="lazy"></iframe></div>
    <p class="demo-note">Five steps, including a real science example. Use Play or move through the steps at your own pace.</p>
    <noscript><p><a href="{{ '/assets/anim/detector.html' | relative_url }}">Open the detector animation</a> in a browser with JavaScript enabled.</p></noscript>
  </div>
</details>

## Results {#results}

Our science experiments distill **Qwen3.5-9B → Qwen3.5-4B** using 9,000 teacher traces. The detector uses a separate 9,000-prompt corpus. We score the students' own answers to **800 held-out prompts per condition**, with a cutoff calibrated on 1,000 separate clean teacher responses.

<figure class="result-figure">
  <picture><source media="(max-width: 600px)" srcset="{{ '/assets/images/llr-laundering-results-mobile.svg' | relative_url }}"><img src="{{ '/assets/images/llr-laundering-results.svg' | relative_url }}" alt="LLR science detection: ordinary distillation 800 of 800 responses, 100%, with 2.75% Baseline false positives; entropy laundering 797 of 800, 99.625%, with 2.875% false positives; grandchild laundering 799 of 800, 99.875%, with 1.875% false positives. All use the same key-1 cutoff."></picture>
  <figcaption><strong>Figure 1.</strong> LLR detection after ordinary distillation and two laundering attacks. Stars show watermarked-student detection. Baseline shows false positives on matched students trained on clean data. Each point counts 800 science responses; the key-1 cutoff is unchanged across all three conditions.</figcaption>
</figure>

The same cutoff detects **797 of 800** responses after entropy laundering and **799 of 800** grandchild responses. It flags 23 and 15 responses from the corresponding clean students, respectively.

[Full results and experimental settings →]({{ '/appendix/' | relative_url }}#laundering-results)

### Identifying the key

We also test whether the detector can distinguish two secret keys. We fit one watermarked reference per key and compare their LLR scores on each student's answers.

The matching key scores higher on **all 800 answers from each student**, giving **1.000 AUROC**—a ranking score where 1.0 means perfect separation. [Key-specificity results →]({{ '/appendix/' | relative_url }}#key-specificity)

### Coding results

We repeat the child and grandchild experiments with **Qwen3-4B** on coding tasks. We evaluate individual actions on held-out SWESmith tasks. LLR detects **69.25%** of grandchild actions at **4.25%** false positives, with **0.9314 AUROC**.

<figure class="result-figure">
  <picture><source media="(max-width: 600px)" srcset="{{ '/assets/images/llr-coding-results-mobile.svg' | relative_url }}"><img src="{{ '/assets/images/llr-coding-results.svg' | relative_url }}" alt="LLR coding detection: child 268 of 400 actions, 67%, with 5.5% Baseline false positives and AUROC 0.9201; grandchild 277 of 400 actions, 69.25%, with 4.25% false positives and AUROC 0.9314."></picture>
  <figcaption><strong>Figure 2.</strong> LLR detection for Qwen3-4B on coding tasks. Baseline is the matched student trained on clean data. Each point counts 400 held-out SWESmith actions. The plot measures watermark detection, not task success.</figcaption>
</figure>

[Coding results and settings →]({{ '/appendix/' | relative_url }}#coding-detection)

## What remains open {#limits}

We tested one trained student per condition. More training runs, clean models, and attacks are needed to check how broadly these results hold.

[Full appendix: expanded results, baselines, settings, and references →]({{ '/appendix/' | relative_url }})
