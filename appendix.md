---
title: "Appendix: Subliminal Watermarks"
page_kind: appendix
permalink: /appendix/
subtitle: "Full results, baseline comparisons, detector definitions, and experimental settings."
excerpt: "Expanded experimental evidence and reproducibility details for Subliminal Watermarks."
---

[← Back to the short article]({{ '/' | relative_url }})

This appendix collects the full reported evidence behind the article. Science rates count individual responses; coding rates count individual actions. The model-audit tables are **independent-query projections**, not measured error rates across independently trained models.

<nav class="appendix-toc" aria-label="Appendix contents" markdown="1">

- [A. Watermark background](#background)
- [B. Experimental setup](#setup)
- [C. Baseline laundering experiments](#laundering)
- [D. The likelihood-ratio detector](#robust-detection)
- [E. Single-response science results](#results)
- [F. Key specificity](#key-specificity)
- [G. Detection after laundering](#laundering-results)
- [H. Model-audit projections](#model-detection)
- [I. Coding-domain results](#coding-detection)
- [J. Interpretation and open questions](#interpretation)
- [K. Settings, calibration, and limitations](#experimental-details)
- [L. References](#references)

</nav>

## A. Watermark background {#background}

We use Aaronson's ([2022](#ref-aaronson2022)) Gumbel-Max watermark. It replaces sampling randomness with pseudorandom values that can be reconstructed from a secret key and the token context. At a fixed prefix, these values favor particular tokens; across prefixes, those preferences vary pseudorandomly.

More concretely, we prepare an $$n$$-gram hash table: at each step, the previous $$n$$ tokens and a secret key $$k$$ are hashed into a seed, and the seed generates one pseudorandom number $$u_v \in (0,1)$$ for every token $$v$$ in the vocabulary. Given the model's next-token probabilities $$p_v$$, return $$\arg\max_v \left[\log p_v + g_v\right]$$ with $$g_v = -\log(-\log u_v)$$, the standard Gumbel-Max trick. Because the seed depends only on the preceding $$n$$ tokens and the key, one can recompute every $$u_v$$ afterwards with the key.

The conventional test measures the _textual_ correlation between sampled tokens and these pseudorandom preferences:

$$
S(y) \;=\; \sum_{t=1}^{T} -\ln\big(1 - u^{(t)}_{y_t}\big),
$$

where $$u^{(t)}_{y_t}$$ is the pseudorandom number at the $$t$$-th token, recomputed from the key and the preceding $$n$$ tokens.

SynthID ([Dathathri et al., 2024](#ref-dathathri2024)), TextSeal ([Sander et al., 2026](#ref-sander2026)), green/red-list watermarking ([Kirchenbauer et al., 2023](#ref-kirchenbauer2023)), and ADFP ([Xu et al., 2026](#ref-xu2026)) provide related watermarking or antidistillation approaches. The [baseline experiments](#laundering) below measure how the tested implementations behave under laundering; they do not establish failure of every watermarking method or configuration.

## B. Experimental setup {#setup}

The science experiments use the same teacher and student: **Qwen3.5-9B → Qwen3.5-4B** ([Qwen Team, 2026](#ref-qwen2026)), both in thinking mode, distilled by SFT on 9,000 teacher traces from the science subset of Mixture-of-Thoughts ([Hugging Face, 2025](#ref-openr1-2025)). These runs use the same fine-tuned teacher adapter.

<div class="setup-overview" markdown="1">

| | Laundering ([baseline experiments](#laundering)) | Our detector ([detector construction](#robust-detection)) |
|---|---|---|
| Watermarks | TextSeal ($$\alpha = 0.1$$), SynthID, ADFP | Vanilla Gumbel-Max (TextSeal, $$\alpha = 0$$), keys $$k_1$$ and $$k_2$$ |
| What is tested | Teacher traces fed through the student | The student's *own* answers to new prompts |
| Score | Each scheme's token-level $$p$$-value | Fitted-reference <span class="score-label" markdown="span">LLR $$\eqref{eq:llr}$$</span> |
| Evaluation | Training-trace versus held-out-trace tests; accuracy on 1,000 held-out science MCQs. ADFP reports only training-trace detection here. | Science: 800 evaluation prompts per study; thresholds from 1,000 unwatermarked source-teacher responses on a separate prompt pool. |
| Detector trained on | No separately fitted detector | $$D'_w$$: 9,000 fresh prompts, disjoint from student-training, calibration, and evaluation prompts. All reported science fitted-detector results use this separate corpus. |

</div>

Detailed settings and evaluation conventions are collected in [settings and evaluation conventions](#experimental-details).

## C. Baseline laundering experiments {#laundering}

These experiments evaluate conventional watermark tests under two attacks. In both tables, **Baseline** denotes the clean, unwatermarked comparison. Their corpus-level or teacher-trace statistics differ from the response-level detection rates reported for our fitted detector. The [setup table](#setup) and [evaluation conventions](#experimental-details) specify those differences.

**Grandchild laundering.** Train a *child* on the watermarked teacher traces as usual, but don't deploy it. Instead, sample the child on the same prompts, keep the correct answers, and train a fresh *grandchild* from the original checkpoint on those. No explicit watermark is injected when the child generates the grandchild's training data; an inherited statistical signal may still remain.

<!-- ADFP source: Gautham Govind Anil, #group-project, 2026-10-30.
https://cs294288fa26.slack.com/archives/C0BUX23MV4K/p1793401181376409
Closed-detector training-trace p-values only; clean training p-value and accuracy were not reported. -->
<div class="table-wrap">
<table class="paper-table">
<thead>
<tr><th></th><th colspan="3" class="group">SynthID</th><th class="gap"></th><th colspan="3" class="group">TextSeal</th><th class="gap"></th><th class="group">ADFP (\(\lambda = 256\))</th></tr>
<tr><th>Student</th><th>Train \(p\)</th><th>Held-out \(p\)</th><th>Acc.</th><th class="gap"></th><th>Train \(p\)</th><th>Held-out \(p\)</th><th>Acc.</th><th class="gap"></th><th>Train \(p\)</th></tr>
</thead>
<tbody>
<tr><td>Baseline</td><td>0.35</td><td>0.69</td><td>79.0</td><td class="gap"></td><td>0.82</td><td>0.87</td><td>79.0</td><td class="gap"></td><td>–</td></tr>
<tr><td>Child</td><td>\(4.7 \times 10^{-15}\)</td><td>0.45</td><td>81.2</td><td class="gap"></td><td>\(1.3 \times 10^{-9}\)</td><td>0.85</td><td>69.3</td><td class="gap"></td><td>\(8.8 \times 10^{-8}\)</td></tr>
<tr><td>Grandchild</td><td class="hl">0.025</td><td>0.54</td><td>79.8</td><td class="gap"></td><td class="hl">0.48</td><td>0.58</td><td>70.2</td><td class="gap"></td><td class="hl">0.72</td></tr>
</tbody>
</table>
</div>

**TextSeal and SynthID fail to detect the grandchild on held-out traces at a 0.05 cutoff:** their $$p$$-values are 0.58 and 0.54, respectively. Their held-out tests also fail for the child. On training traces, TextSeal rises from $$1.3 \times 10^{-9}$$ to 0.48, and ADFP from $$8.8 \times 10^{-8}$$ to 0.72. SynthID's training-trace $$p=0.025$$ remains significant at 0.05, so the results do not support a claim that every tested method fails on every evaluation. ADFP has no held-out-trace result in this comparison.

**Entropy laundering.** We drop the highest-entropy 50% of tokens from the SFT loss, using one threshold over the whole training corpus. Dropped tokens remain in the context. Entropy is estimated with the student because the distiller does not have access to teacher logits. The intuition is that uncertain positions leave more room for a watermark to influence token choice. TextSeal and SynthID cells report “$$p$$-value / entropy-weighted $$p$$-value (accuracy)”; ADFP cells report “$$p$$-value (accuracy).”

<div class="table-wrap">
<table class="paper-table">
<thead>
<tr><th>Tokens dropped</th><th>TextSeal</th><th>SynthID</th><th>ADFP (\(\lambda = 64\))</th></tr>
</thead>
<tbody>
<tr><td>Baseline</td><td>0.36 / 0.85 (85.1%)</td><td>0.88 / 0.40 (85.1%)</td><td>1.0 (85.1%)</td></tr>
<tr><td>None</td><td>\(4.6 \times 10^{-9}\) / \(3.3 \times 10^{-10}\) (83.2%)</td><td>\(9.4 \times 10^{-7}\) / \(6.8 \times 10^{-15}\) (82.9%)</td><td>0.051 (55.9%)</td></tr>
<tr><td>Random 50%</td><td>\(1.5 \times 10^{-5}\) / \(6.4 \times 10^{-6}\) (82.0%)</td><td>\(3.3 \times 10^{-4}\) / \(5.5 \times 10^{-10}\) (82.9%)</td><td>–</td></tr>
<tr><td>Lowest-entropy 50%</td><td>\(5.2 \times 10^{-9}\) / \(3.7 \times 10^{-11}\) (82.9%)</td><td>\(9.7 \times 10^{-7}\) / \(7.7 \times 10^{-16}\) (83.0%)</td><td>–</td></tr>
<tr class="rule-above"><td>Highest-entropy 50%</td><td class="hl">0.22 / 0.83 (81.4%)</td><td class="hl">0.62 / 0.30 (82.4%)</td><td class="hl">0.93 (73.9%)</td></tr>
</tbody>
</table>
</div>

**Highest-entropy masking defeats both conventional TextSeal and SynthID tests at a 0.05 cutoff.** TextSeal's ordinary and entropy-weighted $$p$$-values are 0.22 and 0.83; SynthID's are 0.62 and 0.30. Random and lowest-entropy masking preserve strong evidence, making the choice of masked positions consequential. ADFP's unmasked $$p=0.051$$ is already above 0.05, so its row does not establish a transition from detection to non-detection at that cutoff. These are training-trace statistics, not per-response false-positive rates. The separate grandchild table reports held-out-trace tests for SynthID and TextSeal only.

## D. The likelihood-ratio detector {#robust-detection}

<figure>
  <img src="{{ '/assets/images/detector-pipeline.png' | relative_url }}" alt="The teacher generates three trace sets. The provider fine-tunes a clean teacher theta_c on clean traces D_c and a watermarked teacher theta_w on watermarked traces D'_w; the distiller fine-tunes on separate watermarked traces D_w.">
  <figcaption>The provider fine-tunes a clean teacher \(\theta_c\) on clean traces \(D_c\) and a watermarked teacher \(\theta_w\) on watermarked traces \(D'_w\), sampled on the same fresh prompts. The distiller fine-tunes on its own watermarked traces \(D_w\), which share no prompts with \(D_c\) or \(D'_w\).</figcaption>
</figure>

### Paired reference models

Let $$\theta_0$$ be the source teacher. On its own fresh prompts, the provider samples clean traces $$D_c$$ and watermarked traces $$D'_w$$, then fine-tunes two copies of the teacher with identical settings:

$$
\theta_c = \mathrm{SFT}(\theta_0, D_c), \qquad \theta_w = \mathrm{SFT}(\theta_0, D'_w).
$$

The paired fits use the same prompts and training settings, with watermarking as the experimental change. For a suspect prompt-response pair $$(x,y)$$, score the same response under both fitted references:

$$
\begin{equation}
\operatorname{LLR}(x, y) \;=\; \frac{1}{|y|} \log \frac{p_{\theta_w}(y \mid x)}{p_{\theta_c}(y \mid x)} , \label{eq:llr}
\end{equation}
$$

*How much more likely is this response under the watermarked reference than the clean reference?*
{: .key-idea}

The mean log-likelihood ratio (LLR) divides this difference by the number of scored response tokens $$|y|$$. A larger value favors the watermarked reference. Computing it requires two forward likelihood evaluations and no backward pass. The provider needs access to its fitted reference weights; the suspect model is queried only for text responses. With two keys $$k_1,k_2$$, we fit one watermarked reference per key and write $$s_1,s_2$$ for their corresponding LLR scores.

## E. Single-response science results {#results}

We calibrate each key's LLR using **1,000 unwatermarked responses from the clean source teacher $$\theta_0$$**, on fresh prompts excluded from detector training, student training, and student evaluation. The cutoff is the 951st-smallest calibration score; a response passes only if its score is strictly greater. Both keys use the same teacher responses. Clean students are used to measure false positives, not to set these cutoffs.

| Key | Score ($$D'_w$$) | Matching student flagged (TPR) | Clean student flagged (FPR) | AUROC |
|---|---|---|---|---|
| 1 | <span class="score-label" markdown="span">LLR $$\eqref{eq:llr}$$</span> | 800/800 (100%) | 22/800 (2.75%) | 1.0000 |
| 2 | <span class="score-label" markdown="span">LLR $$\eqref{eq:llr}$$</span> | 795/800 (99.375%) | 24/800 (3.00%) | 0.9987 |

The student-training prompts $$D_w$$, detector-training prompts $$D'_w$$, teacher-calibration prompts, and evaluation prompts are disjoint. The key-1 LLR flags every watermarked response; measured clean-student FPR is 2.75–3.00% across the two keys. These results concern fixed fitted students, not every possible clean model.

## F. Key specificity {#key-specificity}

Key contrast tests whether the learned signal distinguishes the two keyed students. With LLR detectors for both keys trained on $$D'_w$$, the contrast $$s_1-s_2$$ separates the key-1 and key-2 students with **AUROC 1.000** on 800 held-out prompts. All 800 key-1 responses have positive LLR contrast, and all 800 key-2 responses have negative LLR contrast. Zero is the boundary for choosing between these two keys, not the threshold for detecting a watermark. This result is specific to the two tested keys and fitted students.

The individual detectors are also key-specific, although their fixed thresholds are imperfect:

| Detector | Clean flagged | Key-1 flagged | Key-2 flagged | AUROC: matching vs. clean | AUROC: matching vs. wrong key |
|---|---|---|---|---|---|
| <span class="score-label" markdown="span">LLR $$\eqref{eq:llr}$$</span>, key 1 | 22 | 800 | 31 | 1.00000 | 1.00000 |
| <span class="score-label" markdown="span">LLR $$\eqref{eq:llr}$$</span>, key 2 | 24 | 0 | 795 | 0.99870 | 0.999995 |

*$$D'_w$$ LLR detectors · 800 responses per student · each key's threshold fixed from the same 1,000 clean source-teacher answers. The LLR contrast has AUROC 1.000 and separates the two keyed students at zero. Perfect ranking on this sample is not a guarantee of zero population error.*

## G. Detection after laundering {#laundering-results}

We evaluate the entropy-laundered and grandchild key-1 students and their matched clean controls using the $$D'_w$$ LLR detector. Both studies use the same key-1 teacher-calibrated cutoff as above:

| Study | Score | True Positive Rate | False Positive Rate | AUROC |
|---|---|---|---|---|
| Entropy laundering | <span class="score-label" markdown="span">LLR $$\eqref{eq:llr}$$</span> | 797/800 (99.625%) | 23/800 (2.875%) | $$0.9993 \pm 0.0005$$ |
| Grandchild laundering | <span class="score-label" markdown="span">LLR $$\eqref{eq:llr}$$</span> | 799/800 (99.875%) | 15/800 (1.875%) | $$0.9999 \pm 0.0001$$ |

*$$D'_w$$ LLR detector · 800 held-out science prompts per study · cutoff fixed from 1,000 clean source-teacher answers. The matched clean students are evaluation controls only. Entropy laundering removes the highest-entropy 50% of tokens from SFT loss. AUROC $$\pm$$ is half the width of a 95% bootstrap interval over paired prompts.*

**LLR detects more than 99.6% of responses after either laundering scheme**, with the original cutoff unchanged. It misses three entropy-laundered responses and one grandchild response in these 800-prompt evaluations.

## H. Model-audit projections {#model-detection}

To audit a model, fix the key and clean-teacher-calibrated LLR threshold in advance. Query $$N$$ independently sampled prompts and flag the model if **a strict majority of responses pass**. For $$N=10$$, at least six responses must pass; a five–five tie counts as negative.

If a fixed clean model passes one query with probability $$q$$ and a fixed watermarked model passes with probability $$t$$, the independent-query projections are

$$
\begin{aligned}
\mathrm{FPR}_N &= \Pr\!\left[\operatorname{Binomial}(N,q) \ge \lfloor N/2\rfloor+1\right],\\
\mathrm{TPR}_N &= \Pr\!\left[\operatorname{Binomial}(N,t) \ge \lfloor N/2\rfloor+1\right].
\end{aligned}
$$

Substituting the teacher-calibrated science response rates from the 800 held-out prompts gives:

| Study | Key | Score | Projected TPR, $$N=10$$ | Projected FPR, $$N=10$$ (probability) |
|---|---|---|---|---|
| Science | 1 | <span class="score-label" markdown="span">LLR $$\eqref{eq:llr}$$</span> | 100%* | $$8.26 \times 10^{-8}$$ |
| Science | 2 | <span class="score-label" markdown="span">LLR $$\eqref{eq:llr}$$</span> | 99.99999977% | $$1.38 \times 10^{-7}$$ |
| Entropy laundering | 1 | <span class="score-label" markdown="span">LLR $$\eqref{eq:llr}$$</span> | 99.99999998% | $$1.07 \times 10^{-7}$$ |
| Grandchild laundering | 1 | <span class="score-label" markdown="span">LLR $$\eqref{eq:llr}$$</span> | $$\approx 100\%$$ | $$8.55 \times 10^{-9}$$ |

\*100% is the plug-in estimate from 800/800 observed response detections; it does not establish population-perfect TPR. FPR entries are probabilities, not percentages.

These are projections for fixed fitted models and independent queries from the tested prompt and sampling distributions. The tiny FPRs are not directly measured error rates across a population of clean models. Correlated queries or repeated answers to one problem need separate validation, and teacher calibration does not guarantee the same FPR for an unfamiliar clean model.

## I. Coding-domain results {#coding-detection}

We also test grandchild laundering in a separate **Qwen3-4B** coding experiment. The source teacher is fine-tuned on successful trajectories from [Kimi-2.5 SWESmith](https://huggingface.co/datasets/open-athena/Kimi-2.5-swesmith-sandboxes-with_tests-oracle_verified_120s-maxeps-32k). As before, clean and keyed children distill the teacher's actions; grandchildren distill actions regenerated by the corresponding child with watermarking disabled. Each descendant starts from the original base checkpoint. The learned detector uses clean and keyed reference models fitted on separate coding tasks.

With clean-teacher calibration, LLR detects **67.00%** of keyed child actions and **69.25%** of keyed grandchild actions, compared with about 11% for conventional TextSeal:

| Generation | Detector | Keyed actions flagged (TPR) | Clean actions flagged (FPR) | AUROC |
|---|---|---|---|---|
| Child | <span class="score-label" markdown="span">LLR $$\eqref{eq:llr}$$</span> | <mark>268/400 (67.00%)</mark> | 22/400 (5.50%) | <mark>0.9201</mark> |
| Child | Conventional TextSeal | 47/400 (11.75%) | 20/400 (5.00%) | 0.6208 |
| Grandchild | <span class="score-label" markdown="span">LLR $$\eqref{eq:llr}$$</span> | <mark>277/400 (69.25%)</mark> | 17/400 (4.25%) | <mark>0.9314</mark> |
| Grandchild | Conventional TextSeal | 44/400 (11.00%) | 23/400 (5.75%) | 0.5952 |

Cutoffs use 1,000 unwatermarked actions from the clean source teacher across 200 held-out SWESmith tasks, with a shared child/grandchild cutoff for each detector. Confirmation uses 400 keyed and 400 clean actions per generation, one action per task, disjoint from calibration. Calibration actions are clustered by task; teacher calibration does not guarantee 5% FPR on student outputs. Detection is measured on SWESmith actions from one clean and one keyed model per generation.
{: .table-note}

Applying the strict-majority rule from [model-audit projections](#model-detection) with $$N=10$$ or $$N=50$$ gives the following model-detection projections:

| Generation | Detector | TPR<br>$$N=10$$ | FPR<br>$$N=10$$ | TPR<br>$$N=50$$ | FPR<br>$$N=50$$ |
|---|---|---|---|---|---|
| Child | <span class="score-label" markdown="span">LLR $$\eqref{eq:llr}$$</span> | 79.36486% | $$4.79 \times 10^{-6}$$ | 99.05680% | $$5.85 \times 10^{-20}$$ |
| Grandchild | <span class="score-label" markdown="span">LLR $$\eqref{eq:llr}$$</span> | 83.65702% | $$1.07 \times 10^{-6}$$ | 99.65691% | $$9.72 \times 10^{-23}$$ |

Strict majority requires at least six positive actions for $$N=10$$ and 26 for $$N=50$$. As before, these projections substitute the observed action rates into the binomial formula and assume independent queries across tasks; they are not measured model-audit outcomes. TPR entries are percentages; FPR entries are probabilities.
{: .table-note}

## J. Interpretation and open questions {#interpretation}

Could the provider score the watermark's known sampling distribution directly, without fitting references? The variants explored in this study worked on teacher-generated text but did not retain detection through distillation. We therefore use fitted clean and watermarked references to measure the signal learned during SFT.

Our working hypothesis is that watermarking induces statistical features that can be learned by both the 9B reference and the 4B student, even when conventional token tests weaken. These experiments do not identify a shared circuit, demonstrate inversion of a hash function, or establish a universal feature across architectures. Explaining that mechanism remains open.

## K. Settings, calibration, and limitations {#experimental-details}

### Training and sampling

- **Teacher and students.** The science experiments use the same science-SFT Qwen3.5-9B adapter. Their students start from Qwen3.5-4B and use LoRA rank 32. Each first-generation clean or keyed student is SFT-trained on 9,000 teacher traces; grandchildren train on child-generated traces.
- **Science detector rollouts.** Thinking mode; at most 1,024 new tokens per response. Sampling uses temperature 1.0, top-p 0.95, top-k 20, and presence penalty 1.5.
- **Science detector scoring.** The science-fitted $$D'_w$$ detectors are scored in FP32. The main science, entropy, grandchild, and clean-teacher calibration results retokenize returned response text without adding a synthetic EOS; explicit terminal special-token strings remain part of that text. Scoring keeps the full prompt and the first response tokens up to a 1,024-token total limit; only response tokens enter the per-token score.
- **Watermarks.** The science detector experiments use vanilla Gumbel-Max (TextSeal with $$\alpha = 0$$), a 3-token hash context, and keys $$k_1, k_2$$. The baseline laundering comparisons in [the baseline experiments](#laundering) use TextSeal with $$\alpha = 0.1$$, SynthID, and ADFP. ADFP uses $$\lambda = 256$$ in the grandchild table and $$\lambda = 64$$ in the entropy table.

### Science prompt partitions and detector labels

- $$D'_w$$ is the fresh detector-training corpus; $$D_w$$ denotes the student's training corpus, not a second set of detector results. This post excludes detector results fitted on $$D_w$$.
- **Decontamination.** The recorded near-duplicate audit found no matches between fresh detector-training, student-training, and detector-evaluation prompts. Our additional exact-prompt check found zero overlap between the 9,000 fresh detector-training prompts and either of the two 1,000-prompt science evaluation pools. The two evaluation pools also have no exact-prompt overlap.
- **Detector evaluation.** The main two-key study uses one 1,000-prompt science pool; entropy and grandchild laundering share another. We retain their original 400 development and 400 confirmation prompts and combine them into 800 evaluation prompts per study. The remaining 200 prompts were used in earlier student-calibrated analyses; they do not set the clean-teacher cutoffs reported here.
- **Clean-teacher calibration.** We generate 1,000 unwatermarked responses from the source teacher $$\theta_0$$ with the same thinking-mode sampling settings as the student evaluations. These prompts are disjoint from student training, detector training, all earlier science evaluation pools, and the additional student-calibration prompt pool. Both keys score this same teacher corpus. The clean source teacher $$\theta_0$$ is distinct from the fitted clean detector reference $$\theta_c$$.
- **Threshold.** For each key's LLR, sort the 1,000 clean source-teacher scores and use the 951st-smallest as the cutoff. Flag a response only if its score is **strictly greater** than that cutoff. Freeze the teacher cutoffs before computing the student-transfer results; clean-student responses do not fit these thresholds. The same key-1 cutoff applies unchanged to the main, entropy, and grandchild students. The nominal 5% teacher-calibration target does not guarantee a 5% FPR for a different clean model.
- **Key contrast.** The zero line for $$s_1-s_2$$ compares the two keys' LLR scores. It is not the threshold for deciding whether a response is watermarked.
- **Uncertainty and scope.** Teacher cutoffs are frozen before the transfer analysis, but the student evaluation responses had been inspected historically, so these are exploratory transfer results with one fitted student per condition. Science response-rate intervals use exact Clopper–Pearson bounds; AUROC intervals use paired-prompt bootstrap resamples. A bootstrap interval of [1, 1] for perfect ranking is not a guarantee of zero population error. Response resampling does not replicate model training, and the majority-vote numbers in [science](#model-detection) and [coding](#coding-detection) are conditional independent-query projections.

The fixed clean-teacher cutoffs used in the science experiments in [single-response detection](#results), [key specificity](#key-specificity), [laundering](#laundering-results), and [model-audit projections](#model-detection) are:

| Key | Score | Cutoff |
|---|---|---|
| 1 | <span class="score-label" markdown="span">LLR $$\eqref{eq:llr}$$</span> | −0.01502352 |
| 2 | <span class="score-label" markdown="span">LLR $$\eqref{eq:llr}$$</span> | −0.00625214 |

### Coding detection {#coding-settings}

The coding experiment in [the coding study](#coding-detection) uses its own SWESmith-SFT Qwen3-4B source teacher and separately fitted coding references. Keyed coding traces use TextSeal with $$\alpha = 0$$ and a 3-token hash context. Generation allows up to 28,672 prompt tokens and 4,096 response tokens within a 32,768-token context. Coding LLR scores the original generated response token IDs, including a terminal EOS when emitted, conditioned on the full prompt.

Calibration generates unwatermarked actions from that source teacher at temperature 1, top-k 20, top-p 0.95, with a 4,096-token response budget; watermark injection is disabled and outputs are not filtered by success. Each detector uses the 951st-smallest score from the 1,000-action clean-teacher pool, with a strict greater-than decision. This gives a shared child/grandchild cutoff of **0.014877768768661323** for per-token LLR and **1.5491128392910267** for the conventional TextSeal score $$-\log_{10}p$$. Confirmation models and scores are held fixed while replacing the earlier clean-student calibration. Coding and science use their own fitted references and thresholds.

### Reported scope

Both keyed science detectors are complete on the three main science students. Key-1 results are complete for entropy and grandchild laundering. Coding reports the child and grandchild results in [the coding study](#coding-detection). Additional replication and dilution analyses are outside the scope of this post.

### Baseline laundering evaluation conventions

- **Grandchild table.** For SynthID and TextSeal, "train" uses 3,000 traces the child trained on; "held-out" uses traces on prompts no student saw. Accuracy (%) is measured on 1,000 held-out science MCQs. We have not verified whether these MCQ prompt IDs coincide with the detector-study prompt IDs.
- **ADFP.** The displayed grandchild $$p$$-values use the teacher's training traces. At teacher-trace prefixes, the evaluator samples the student's next token and measures its keyed green-list membership, keeping the first occurrence of each evaluated context bigram. The reported $$p$$-value is the one-sided Hoeffding bound: $$p = \exp[-2N(\bar g - \gamma)^2]$$ when $$\bar g > \gamma$$, and $$p = 1$$ otherwise, with green-list fraction $$\gamma = 0.5$$. Here $$N$$ is the number of retained measurements and $$\bar g$$ their mean. It is a corpus-level statistic, not a per-response FPR. The clean training $$p$$-value and accuracy were not reported for this ADFP grandchild comparison.
- **Entropy table.** TextSeal and SynthID cells report $$p$$-value / entropy-weighted $$p$$-value (accuracy); ADFP cells report $$p$$-value (accuracy). Detection is evaluated on training traces. The highest-entropy mask is selected over the full training corpus; dropped tokens remain in the context but contribute no SFT loss.


## L. References {#references}

<div class="references" markdown="1">

- {: #ref-aaronson2022} Scott Aaronson. [My AI safety lecture for UT Effective Altruism](https://scottaaronson.blog/?p=6823). *Shtetl-Optimized* (blog), November 2022.
- {: #ref-anthropic2026} Anthropic. [Detecting and preventing distillation attacks](https://www.anthropic.com/news/detecting-and-preventing-distillation-attacks). February 2026.
- {: #ref-dathathri2024} Sumanth Dathathri, Abigail See, Sumedh Ghaisas, et al. [Scalable watermarking for identifying large language model outputs](https://www.nature.com/articles/s41586-024-08025-4). *Nature* 634, 818–823, 2024.
- {: #ref-openr1-2025} Hugging Face. [Mixture-of-Thoughts](https://huggingface.co/datasets/open-r1/Mixture-of-Thoughts), a dataset from [Open R1: A fully open reproduction of DeepSeek-R1](https://github.com/huggingface/open-r1). 2025.
- {: #ref-kirchenbauer2023} John Kirchenbauer, Jonas Geiping, Yuxin Wen, Jonathan Katz, Ian Miers, and Tom Goldstein. [A watermark for large language models](https://arxiv.org/abs/2301.10226). *ICML*, 2023.
- {: #ref-qwen2026} Qwen Team. [Qwen3.5: Towards native multimodal agents](https://qwen.ai/blog?id=qwen3.5). February 2026.
- {: #ref-sander2026} Tom Sander, Hongyan Chang, Tomáš Souček, et al. [TextSeal: A localized LLM watermark for provenance & distillation protection](https://arxiv.org/abs/2605.12456). arXiv:2605.12456, 2026.
- {: #ref-xu2026} Yixuan Even Xu, John Kirchenbauer, Yash Savani, Asher Trockman, Alexander Robey, Tom Goldstein, Fei Fang, and J.&nbsp;Zico Kolter. [Antidistillation fingerprinting](https://arxiv.org/abs/2602.03812). arXiv:2602.03812, 2026.

</div>

[← Back to the short article]({{ '/' | relative_url }})
