# BDSP publication content — Kong et al. 2025

Project URL: https://bdsp.io/projects/87rztvzmyz9uh0esnd83/overview/

This file contains the prose to paste into each BDSP "ActiveProject" section
when filling out the publication. Section labels match the field names in the
BDSP Django models (`bdsp-django/project/modelcomponents/`). Resource type
is **Database** (resource_type = 0).

---

## title

```
Evaluating crowdsourcing for ICU EEG annotation: A comparison with expert performance — Data and Code
```

## version

```
1.0.0
```

## short_description  (≤250 chars)

```
Data and code from Kong et al. (Epilepsia 2025): 1,542 expert and non-expert
participants annotated 478,834 EEG epochs for seizures and rhythmic/periodic
patterns; mixed-effects analyses compare crowd vs expert accuracy.
```

## abstract  (HTML; the paper's abstract, adapted)

```html
<p>
<strong>Objective.</strong> Detection of seizures and rhythmic or periodic
patterns (SRPPs) on electroencephalography (EEG) is crucial for the diagnosis
and management of patients with neurological critical illness. Automated
detection methods require large, high-quality, expert-annotated datasets for
training, but expert annotation is bottlenecked by the limited supply of
trained neurophysiologists. Crowdsourcing may offer a scalable alternative.
This BDSP publication shares the underlying data and analysis code from a
study that evaluated whether crowdsourced annotations of short epochs of ICU
EEG can match expert-quality labels.
</p>

<p>
<strong>Methods.</strong> An EEG scoring contest was conducted via the
DiagnosUs mobile app (in collaboration with Centaur Labs) over a 1-month
period in 2021. Participants annotated 10-second EEG epochs (with an
accompanying 10-minute spectrogram) for six SRPP categories: seizure,
generalized periodic discharges (GPDs), lateralized periodic discharges
(LPDs), generalized rhythmic delta activity (GRDA), lateralized rhythmic
delta activity (LRDA), and "Other." Performance was assessed via pairwise
agreement, Fleiss' kappa, and Gwet's AC1 between expert raters, and via
accuracy comparisons between experts and the crowd using both individual
votes and weighted majority voting.
</p>

<p>
<strong>Results.</strong> A total of 1,542 participants (8 board-certified
clinical neurophysiologists/epileptologists and 1,534 non-experts) answered
478,834 questions across six SRPPs. Using unweighted individual votes, the
crowd's performance was inferior to experts overall and for every SRPP.
Using weighted majority voting, the crowd was non-inferior to experts
overall (accuracy 0.70 [0.69-0.70] vs 0.68 [0.68-0.70]) and matched or
exceeded experts in most SRPPs — except LPDs and "Other." No individual
expert outperformed the crowd on overall metrics.
</p>

<p>
<strong>Significance.</strong> This proof-of-concept demonstrates that
crowdsourcing, with appropriate weighting, can yield expert-level SRPP
annotations and offers a path toward the large, diverse datasets needed for
training automated detection algorithms.
</p>
```

## background  (HTML)

```html
<p>
Continuous EEG monitoring is now standard practice in many ICUs for
identifying seizures, periodic discharges, and rhythmic patterns associated
with secondary brain injury. Automated detection methods based on
machine-learning models — particularly deep neural networks — have advanced
rapidly, but every such method requires substantial volumes of
expert-annotated EEG. Manual annotation is labor-intensive and limited by
the number of trained neurophysiologists worldwide. Existing public EEG
datasets are mainly geared toward seizure detection/prediction; only one
public dataset to date is curated for the full set of seizures and
rhythmic/periodic patterns (SRPPs).
</p>

<p>
The classical "wisdom of the crowd" argument — that the aggregated judgment
of many non-experts can rival or exceed that of an individual expert —
has been validated in medical image annotation tasks (skin lesions, sleep
spindles, lung ultrasound, dermoscopy). Whether it generalises to the
more complex visual reasoning required for ICU EEG SRPP identification
was, until this study, an open question.
</p>
```

## methods  (HTML; condensed from paper Sections 2.1-2.10)

```html
<h3>Participants and scoring contest</h3>
<p>
Conducted under IRB protocols at MGH (#2013P001024) and BIDMC (#2024P000804)
with consent waivers for use of de-identified EEG data. EEG segments were
drawn from the IIIC labeling study (Jing et al., 2023). The contest was
launched at the Critical Care EEG Monitoring Research Consortium (CCEMRC)
annual meeting on June 6, 2021 and hosted on the DiagnosUs iOS app for one
month. Each question displayed a 10-second EEG epoch (bipolar montage) with
a 10-minute companion spectrogram (Figure 1 of the paper). Top performers
received small monetary prizes; the contest also served as an educational
tool with real-time feedback. Participants self-reported their experience
level; "Expert" was defined as having completed at least one year of
specialty training (board-certified in epilepsy or clinical neurophysiology).
</p>

<h3>Gold standard</h3>
<p>
The reference labels were inherited from prior work (Jing et al., 2023,
<em>Neurology</em>), in which 30 expert raters scored 50,697 EEG segments
from 2,711 patients. Only segments receiving ≥10 expert votes were retained;
the modal class with the highest vote count was taken as the gold-standard
SRPP label.
</p>

<h3>Calibration / test split</h3>
<p>
For each qualified user (one who answered at least one question covering
each of the six SRPPs in their own answers and in the gold standard), a
"greedy set cover" was used to select a minimal calibration set per user;
all remaining responses formed that user's test set. The calibration
dataset is used only to compute per-user, per-pattern accuracies (which
serve as voting weights); performance is evaluated on the test set.
</p>

<h3>Inter-rater agreement</h3>
<p>
Pairwise agreement was computed over all overlapping items (pairs with ≥5
shared questions retained). Fleiss' kappa was computed by comparing
observed item-level agreement to expected agreement; Gwet's AC1 was
computed as an alternative metric less sensitive to skewed prevalence.
</p>

<h3>Mixed-effects models</h3>
<p>
Four mixed-effects models were fitted using Restricted Maximum Likelihood
(REML), each with a random intercept for problem_id to capture
between-problem variability:
</p>
<ul>
  <li>Model 1 — overall, non-weighted: <code>accuracy ~ group + avg_question_count + (1 | problem_id)</code></li>
  <li>Model 2 — by-pattern, non-weighted: <code>accuracy ~ group * pattern + avg_question_count + (1 | problem_id)</code></li>
  <li>Model 3 — overall, weighted majority: same fixed effects, outcome is per-problem WM correctness</li>
  <li>Model 4 — by-pattern, weighted majority</li>
</ul>

<h3>Weighted majority voting</h3>
<p>
For each problem, the predicted class is
<code>argmax_c &sum;<sub>i</sub> w<sub>i</sub> &middot; I(c<sub>ij</sub> = c)</code>
where w<sub>i</sub> is user i's weight, defined as the mean of their six
per-pattern calibration accuracies.
</p>

<h3>Non-inferiority test</h3>
<p>
A non-inferiority margin of 0.05 was chosen <em>a priori</em>. The null
hypothesis is that Expert accuracy exceeds Crowd accuracy by more than the
margin; rejection demonstrates non-inferiority. Per-pattern p-values were
Bonferroni-corrected; p < 0.025 was considered statistically significant.
</p>

<h3>Sensitivity analyses</h3>
<p>
(i) Leave-one-group-out: sequentially removed each crowd subgroup (MD/DO,
Medical student, NP/PA/pharmacist, Other students, Other) and recomputed
weighted-majority accuracy. (ii) Sample-size bootstrap: drew 1,000 bootstrap
samples of N users (N = 5...50) and recomputed crowd WM accuracy. (iii) Hard
filter: excluded the bottom 20% of crowd raters by calibration accuracy.
(iv) By-subgroup forest plot: fitted separate mixed models pitting each
crowd subgroup against the experts.
</p>
```

## content_description  (HTML)

```html
<p>This BDSP folder contains:</p>

<ul>
  <li><strong><code>test_df4.csv</code></strong> — the master per-response
  dataframe (one row per (user, question) response, ~478,834 rows in the
  test split + ~17,619 in the calibration split). Columns include
  <code>user_id</code>, <code>problem_id</code>, <code>title</code> (the
  user's selected SRPP), <code>goldstandardnew</code> (the gold-standard
  SRPP), <code>experience_level</code>, <code>preferred_specialty</code>,
  per-pattern calibration accuracies, the user's overall
  <code>combined_accuracy</code> (used as the weight for weighted-majority
  voting), and the contest image URL.</li>

  <li><strong><code>eeg-all-users-and-topics.csv</code> /
  <code>1251-all-users.csv</code> / <code>1251-all-users_demo_info.csv</code></strong>
  — de-identified Centaur Labs user tables. Email addresses, first/last
  names, and any other directly identifying fields have been stripped.</li>

  <li><strong><code>1251-all-reads_ac.csv</code></strong> — the per-read
  raw export from the DiagnosUs contest (657,326 reads across 4,951 users
  on 10,704 unique EEG questions). This is the source from which
  <code>test_df4.csv</code> was built.</li>

  <li><strong><code>labels_experts30.xlsx</code></strong> — the 30-expert
  pivoted label matrix from Jing et al. 2023. One row per EEG segment, one
  column per expert; numeric values 0-5 map to (other, seizure, lpd, gpd,
  lrda, grda). Used for the inter-rater-agreement analyses in
  Supplemental S4 and S5.</li>

  <li><strong><code>images/</code></strong> (optional) — the contest
  images themselves: 10-second EEG epochs in bipolar montage plus a
  10-minute spectrogram per segment, as displayed to participants. The
  filename stem matches the segment identifier used in
  <code>test_df4.csv</code>'s <code>matchfile</code> column.</li>
</ul>

<p>
The same EEG <em>signal</em> data (the source recordings from which the
contest images were generated) is available as part of the IIIC dataset
that supports Jing et al., 2023, also hosted on BDSP.
</p>
```

## usage_notes  (HTML)

```html
<p>
A complete, documented Python reproduction of every figure and table in
the paper is available on GitHub at
<a href="https://github.com/bdsp-core/iiic-crowdsourcing-wanyee">https://github.com/bdsp-core/iiic-crowdsourcing-wanyee</a>.
</p>

<p>To reproduce the paper from this data:</p>

<ol>
  <li>Clone the GitHub repository and create a Python environment
  (<code>pip install -r requirements.txt</code>).</li>
  <li>Place <code>test_df4.csv</code> and (optionally)
  <code>labels_experts30.xlsx</code>,
  <code>1251-all-users_demo_info.csv</code> in the repository's
  <code>data/</code> folder.</li>
  <li>Run <code>python scripts/reproduce_all.py</code> to regenerate every
  figure, table, and supplemental analysis. Individual figures can be run
  via the per-script entry points (e.g.
  <code>python scripts/figure3_forest_plot.py</code>).</li>
</ol>

<p>
Outputs are written to <code>figures/</code> as PNG + PDF, with a CSV of the
underlying numeric values for each figure to ease spot-checking.
</p>

<p><strong>Suggested use cases:</strong></p>
<ul>
  <li>Training and evaluating machine-learning classifiers for ICU EEG
  pattern detection (the per-question gold-standard labels in
  <code>test_df4.csv</code> are suitable as training targets).</li>
  <li>Benchmarking new crowdsourcing or label-aggregation algorithms (the
  per-response, per-user dataset supports virtually any weighting scheme).</li>
  <li>Methodological research on inter-rater agreement and consensus
  building among medical experts.</li>
</ul>
```

## ethics_statement  (HTML)

```html
<p>
This study used de-identified EEG data and was conducted under institutional
review board (IRB) protocols at Massachusetts General Hospital
(Protocol no. MGH 2013P001024) and Beth Israel Deaconess Medical Center
(BIDMC #2024P000804). Both protocols provided waiver of consent for the
research use of de-identified EEG. Contest participants registered freely
through the DiagnosUs app and were notified that aggregated, de-identified
contest results would be used for research.
</p>

<p>
No directly identifying information about EEG patients is included in this
data package; all per-segment identifiers are pseudonymous and cannot be
linked to a specific individual without keys held by Massachusetts General
Hospital.
</p>

<p>
For contest participants, the BDSP release contains only the Centaur Labs
<code>user_id</code> and self-reported demographics (country,
experience_level, preferred_specialty); names, email addresses, and any
other directly identifying fields present in the original Centaur exports
have been removed prior to upload.
</p>
```

## acknowledgements  (HTML)

```html
<p>
The authors gratefully acknowledge the contributions of all participants in
the SRPP scoring contest. The contest was hosted by Centaur Labs on the
DiagnosUs platform. The 30-expert gold-standard labels are inherited from
the IIIC labeling study (Jing et al., 2023, <em>Neurology</em>) and the
authors thank all contributors to that effort.
</p>
```

## conflicts_of_interest  (HTML)

```html
<p>
This work was supported by the National Institutes of Health (NIH; RF1AG064312,
RF1NS120947, R01AG073410, R01HL161253, R01NS126282, R01AG073598, R01NS131347,
R01NS130119) and the National Science Foundation (NSF; 2014431).
</p>

<p>
Dr. Westover is a co-founder, scientific advisor, consultant to, and has
personal equity interest in Beacon Biosignals. He also receives royalties for
authoring <em>Pocket Neurology</em> from Wolters Kluwer and <em>Atlas of
Intensive Care Quantitative EEG</em> by Demos Medical. Erik Duhaime and
Srishti Kapur are employees and have personal equity interest in Centaur
Labs. There are no conflicts of interest for the other authors.
</p>
```

## references  (HTML; one item — the published paper)

```html
<ol>
  <li>
    Kong W-Y, Nascimento FA, Struck A, Duhaime E, Kapur S, Amorim E,
    Kapinos G, Rodriguez A, Thomas B, Desai M, Lee JW, Westover MB, Jing J.
    Evaluating crowdsourcing for ICU EEG annotation: A comparison with
    expert performance. <em>Epilepsia</em> 2025;66(11):4366-4380.
    <a href="https://doi.org/10.1111/epi.18547">doi:10.1111/epi.18547</a>
  </li>
  <li>
    Jing J, Ge W, Struck AF, Fernandes MB, Hong S, An S, et al. Interrater
    reliability of expert electroencephalographers identifying seizures and
    rhythmic and periodic patterns in EEGs. <em>Neurology</em>
    2023;100(17):e1737-e1749.
    <a href="https://doi.org/10.1212/WNL.0000000000201670">doi:10.1212/WNL.0000000000201670</a>
  </li>
</ol>
```

## release_notes  (HTML)

```html
<p>Version 1.0.0 — initial public release accompanying the published
manuscript (Epilepsia, August 2025).</p>
```

## project_home_page

```
https://github.com/bdsp-core/iiic-crowdsourcing-wanyee
```

## access_policy

```
0 (Open — once the IRB / DUA terms below are accepted)
```

## license

```
CC BY-NC 4.0 (Attribution-NonCommercial 4.0 International)
```

Note: the BDSP `license` field is a foreign key to a `License` row; pick the
matching entry from BDSP's available licenses. If a CC BY-NC entry doesn't
exist yet in BDSP's License table the admin will need to add one.
