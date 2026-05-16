# Email to Wan-Yee — files needed for BDSP publication & GitHub repo

**Subject:** Files needed to publish the crowdsourcing-IRR data + code

---

Hi Wan-Yee,

Brandon and I are getting the data and code package together for your Epilepsia paper so that everything can be posted on BDSP (https://bdsp.io/projects/87rztvzmyz9uh0esnd83/overview/) and on GitHub at https://github.com/bdsp-core/iiic-crowdsourcing-wanyee. The goal is for someone else to be able to reproduce every figure, table, and supplemental in the paper from what we share.

I've gone through the four notebooks you sent (`csvforeachexpertlevel...`, `Copy_of_IRR_gold_standard_and_expert`, `mixed_modeling`, `crowd_vs_individual_expert`) and mapped exactly which inputs each one needs. Brandon also dug up a `Centaur-IIIC-Contest/` folder on his machine that already covers some of them. Below is what we still need from you.

## Files we already have ✅

- `1251-all-reads_ac.csv` — per-read individual responses (657,326 rows).
- `1251-all-users.csv` and `1251-all-users_demo_info.csv` — Centaur Labs user table with `country`, `experience_level`, `preferred_specialty`, `years_in_position`. 3,300 users have demo info; 1,651 users have reads but no demo. We've already confirmed all 8 experts' `user_id`s appear in the reads.
- `eeg-all-users-and-topics.csv` — Centaur Labs raw user list (id, email, first, last, locale, participated_in_topics). Will be de-identified before publishing.

## Files we still need ❌

### Must have (blocks ~all reproductions)

1. **`test_df4.csv`** — the master analysis dataframe used by `mixed_modeling.ipynb` and `crowd_vs_individual_expert.ipynb` (their cell 3 reads it from `/content/drive/MyDrive/IRR/test_df4.csv`). This is the row-per-response table after you've already merged in the gold-standard label and the per-user-per-pattern calibration accuracies. **This single file unblocks Table 1 and Figures 2–5 plus Supplementals S2, S6–S11**.

2. **`labels_experts30.xlsx`** — the pivoted 30-expert label matrix used for **Supplemental S4 and S5** (inter-rater agreement comparison). `Copy_of_IRR_gold_standard_and_expert.ipynb` cell 2 reads it from `/content/drive/MyDrive/IRR/labels_experts30.xlsx`. Already published with Jing 2023 (*Neurology*), so it should be easy to share again.

3. **`Results SeizureLike Patterns Dec 12 2022 18.50.01 PM.csv`** — the Centaur Labs *per-question* summary export with `Case ID`, `Origin`, and `Correct Label` columns. Used by `csvforeachexpertlevelandcompletewithgoldstandard.ipynb` cell 0. Without this we can't reproduce the upstream "build test_df4" pipeline end-to-end (though we don't strictly need it if you can send #1 directly).

### Nice to have (for full provenance)

4. **The `.mat` files in your old `E:\Data\` folder** — per-segment 30-expert vote arrays from the IIIC labeling study. Used to compute the `max_column` gold-standard override. Same files as the Jing 2023 *Neurology* paper. If they're gone, we'll work from `labels_experts30.xlsx` alone.

5. **Contest PNG images** — the `matchfile` column in `test_df4.csv` points to PNGs at `centaur-customer-uploads.s3.us-east-1.amazonaws.com/mgh-eeg/{LABEL}/{stub}.png`. Could you ask Erik / Centaur whether those PNGs can be exported to a folder we can host on BDSP? If not, we can regenerate them from the source IIIC EEGs.

## Other questions

- **Supplemental S3** (time in practice for the 8 study experts and the 30 gold-standard experts) — looks like that table was assembled by hand. Do you have the underlying spreadsheet? If so, pass it along; otherwise we'll just reproduce the table verbatim from the paper.

- **The `wyeekong/IRR` GitHub repo** referenced in your `mixed_modeling.ipynb` (the one that downloads `test_df2.7z`) — we'd appreciate access if it's still around. **Also: heads up that the token `ghp_WV2…` is checked into that notebook in plain text — please revoke and rotate that token before anything gets pushed publicly.**

- **8 expert identities** — Brandon's reads file already confirms the 8 expert `user_id`s match: `41816` (Brandon), `123180` (Jin), `129198` (Fábio), `129995` (Andres), `130067` (Masoom), `129968` (Gregory), `130226` (Aaron), `130262` (Jong Woo). But the `experience_level` column in `1251-all-users_demo_info.csv` doesn't tag any of them as "Expert" — looks like you set that flag manually downstream. Could you confirm the rule you used, or send the lookup table that mapped `user_id` → "Expert"?

## Author info for the BDSP page

Separately, we need BDSP-side info for each author. If you happen to know off-hand which co-authors already have BDSP accounts (and their email of record), please pass that along. For anyone without an account, the BDSP admin will email them an invite — we just need a current email and institutional affiliation for each.

Thanks Wan-Yee! Send everything to me directly or drop it on Brandon's shared Drive, whichever's easier.

Best,
[Brandon]
