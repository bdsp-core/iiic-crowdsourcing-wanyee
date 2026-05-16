# Email to Wan-Yee — files needed for BDSP publication & GitHub repo

**Subject:** Files needed to publish the crowdsourcing-IRR data + code

---

Hi Wan-Yee,

Brandon and I are getting the data and code package together for your Epilepsia paper so that everything can be posted on BDSP (https://bdsp.io/projects/87rztvzmyz9uh0esnd83/overview/) and on GitHub at https://github.com/bdsp-core/iiic-crowdsourcing-wanyee. The goal is for someone else to be able to reproduce every figure, table, and supplemental in the paper from what we share.

I've gone through the four notebooks you sent (`csvforeachexpertlevel...`, `Copy_of_IRR_gold_standard_and_expert`, `mixed_modeling`, `crowd_vs_individual_expert`) and mapped exactly which inputs each one needs. Brandon also dug up a `Centaur-IIIC-Contest/` folder on his machine that already covers some of them. Below is what we still need from you.

## Files we already have ✅

From the `Centaur-IIIC-Contest/` folder Brandon had locally, plus your Box
folder `Brandon - PHI/0_People/aa_BigFolders/WanYeeKong/WanYee_ACNS_IRR/`:

- `1251-all-reads_ac.csv` — per-read responses (657,326 rows).
- `1251-all-users.csv`, `1251-all-users_demo_info.csv` — user table with
  `country`, `experience_level`, `preferred_specialty`, `years_in_position`.
- `eeg-all-users-and-topics.csv` — raw user list (will be de-identified).
- **`Results SeizureLike Patterns Dec 12 2022 18.50.01 PM.csv`** (inside
  `files/Summary - SeizureLike Patterns.zip`) — Centaur per-question summary
  with `Case ID`, `Origin`, `Correct Label`.
- **`Reads SeizureLike Patterns Dec 12 2022 19.01.23 PM.csv`** (inside
  `files/Individual Reads SeizureLike Patterns.zip`) — alternate read export.
- **`goldstandardnew925nonandropnaforjj1016(in).csv`** (in `files/`) —
  ~508k-row slim test-set dataframe with `user_id`, `problem_id`, `title`,
  `Origin_x`, `goldstandardnew`, `experience_level`. All 8 experts are
  already labeled `Expert` here, which lets us run the **non-weighted**
  analyses and the IRR analyses without further preprocessing.

## Files we still need ❌

### Must have

1. **`test_df4.csv`** (the full ~45-column one) — the slim
   `goldstandardnew925...csv` lets us do the non-weighted analyses (Table 1,
   Figure 2 NW bars, Supps S1, S2, S4) but is missing the per-user weights
   (`combined_accuracy`, `GPDaccuracy`, ...) needed for **weighted-majority
   voting** and the **calibration/test split**. Without those, we'd have to
   re-derive the weights ourselves from the calibration set — doable, but
   would slightly diverge from your published numbers because the greedy
   set-cover for the calibration split would be reseeded. If you can send
   the full `test_df4.csv`, the weighted analyses (Figures 2 WM, 3, 4, 5,
   Supps S6-S11) match your paper exactly.

2. **`labels_experts30.xlsx`** — the pivoted 30-expert label matrix used for
   **Supplemental S4 and S5** (inter-rater agreement comparison). Already
   published with Jing 2023 (*Neurology*), so it should be easy to share again.

### Nice to have

3. **The `.mat` files in your old `E:\Data\` folder** — per-segment 30-expert
   vote arrays from the IIIC labeling study. Used to compute the
   `max_column` gold-standard override. We have some on the Box drive in
   `Missing_mat_files_2023May/` but it's not clear if that's the complete
   set. If `labels_experts30.xlsx` arrives we don't need these.

4. **Contest PNG images** — the `matchfile` column points to PNGs at
   `centaur-customer-uploads.s3.us-east-1.amazonaws.com/mgh-eeg/{LABEL}/{stub}.png`.
   Could you ask Erik / Centaur whether those can be exported for BDSP hosting?

## Other questions

- **Supplemental S3** (time in practice) — looks hand-assembled. If you have
  the underlying spreadsheet, pass it along; otherwise we'll reproduce the
  table verbatim from the paper. (No urgency.)

- **The `wyeekong/IRR` GitHub repo** referenced in `mixed_modeling.ipynb` —
  we'd appreciate access if it's still around. **Heads up that the token
  `ghp_WV2…` is checked into that notebook in plain text — please revoke
  and rotate it.** (We've already scrubbed it from the copy we're
  preparing to publish.)

- **8 expert identities — confirmed.** The slim CSV already tags all 8 as
  `Expert`: 41816 (Brandon), 123180 (Jin/JJ), 129198 (Fábio),
  129995 (Andres), 130067 (Masoom), 129968 (Gregory), 130226 (Aaron),
  130262 (Jong Woo). No follow-up needed.

## Author info for the BDSP page

Separately, we need BDSP-side info for each author. If you happen to know off-hand which co-authors already have BDSP accounts (and their email of record), please pass that along. For anyone without an account, the BDSP admin will email them an invite — we just need a current email and institutional affiliation for each.

Thanks Wan-Yee! Send everything to me directly or drop it on Brandon's shared Drive, whichever's easier.

Best,
[Brandon]
