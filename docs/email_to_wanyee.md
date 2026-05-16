# Email to Wan-Yee — short list of files still needed

**Subject:** Final files for the IRR paper data + code release on BDSP

---

Hi Wan-Yee,

Brandon and I have most of what we need to publish the data and code from
your Epilepsia paper on BDSP (https://bdsp.io/projects/87rztvzmyz9uh0esnd83/)
and GitHub (https://github.com/bdsp-core/iiic-crowdsourcing-wanyee). I've
already gone through your four notebooks, set up the cleaned-up reproduction
code, and run partial reproductions against the data we have — the numbers
match your paper to about ±0.02 on every figure I've checked so far (e.g.
Figure 3 forest-plot estimates all line up; Supp S4 Fleiss κ / Gwet AC1
match to within 0.03). So this email is *not* a fishing expedition — it's
a tight ask for the last two files that would lock in exact-paper
reproducibility.

## What we already have (from Brandon's Box and SSD)

- `1251-all-reads_ac.csv`, `1251-all-users.csv`, `1251-all-users_demo_info.csv`,
  `eeg-all-users-and-topics.csv` — the raw Centaur Labs exports.
- `Results SeizureLike Patterns Dec 12 2022 18.50.01 PM.csv` (inside
  `files/Summary - SeizureLike Patterns.zip`) — the per-question summary
  with `Case ID`, `Origin`, and `Correct Label`.
- **`goldstandardnew925nonandropnaforjj1016(in).csv`** — your post-dropna
  intermediate dataframe (508k rows). All 8 study experts are tagged
  `experience_level = Expert`, which is great. This gets us close enough
  to reproduce Figures 2, 3 and Supp S4 within rounding.
- The 8 study expert `user_id`s (41816 BW, 123180 JJ, 129198 Fábio,
  129995 Andres, 130067 Masoom, 129968 Greg, 130226 Aaron, 130262 Jong Woo)
  — all present in the reads file, no follow-up needed.
- `old/emails.txt` and `old/shortlisted user_mbw.xlsx` — confirmed contact
  emails for every author.

## What we still need from your Google Drive

### 1. **`test_df4.csv`** *(the full ~45-column version)*

The slim CSV we found is just 6 columns. The full `test_df4.csv` your
notebooks load from `/content/drive/MyDrive/IRR/test_df4.csv` has the
per-user calibration weights (`combined_accuracy`, `GPDaccuracy`,
`LPDaccuracy`, `grdaaccuracy`, `lrdaaccuracy`, `otheraccuracy`,
`seizureaccuracy`) plus the test/calibration split flags. Without those
columns we can recompute the weights ourselves from the full data, but the
calibration/test split (which trims your participant pool from 2,786 →
1,542 and the response count from 508k → 478k+17k = 496k) re-shuffles
because the greedy set cover gets reseeded. With the full file, our
numbers will match your published Table 1 and Figures 2-5 exactly.

### 2. **`labels_experts30.xlsx`**

The pivoted 30-expert label matrix you loaded from
`/content/drive/MyDrive/IRR/labels_experts30.xlsx`. Needed only for
**Supplemental S5** (the split-violin study-experts vs gold-standard-experts
plot). Already published with your *Neurology* 2023 paper, so it should
be easy to share again.

## Optional / nice to have

- **The full set of `.mat` files** that backed `ImageCode_JJ/Data/`.
  Brandon is currently rcloning the Box copy to a local SSD; if that goes
  smoothly we won't need anything from you here. I've already written and
  smoke-tested a converter that bundles them into a single
  `iiic_contest_eeg.h5` (~12 GB) for BDSP distribution instead of 10,000+
  individual .mat files.
- **Contest PNG images** — the `matchfile` URLs in `test_df4` point to
  `centaur-customer-uploads.s3.us-east-1.amazonaws.com/mgh-eeg/{LABEL}/{stub}.png`.
  Could you ask Erik / Centaur whether they'd be willing to export those
  ~10,704 PNGs so we can host them on BDSP? If not, we can regenerate them
  from the EEG `.mat` files.
- **Supplemental S3 spreadsheet** (years-in-practice for the 8 study
  experts and 30 gold-standard experts). Looks hand-assembled; no urgency.

## Security note

The `mixed_modeling.ipynb` you sent has a GitHub personal access token
checked into Cell 2 (`ghp_WV2…`). I've scrubbed it from the copy we're
preparing to publish, but please **revoke and rotate that token** in your
GitHub settings — it's been exposed in any copy of the notebook that's
been emailed around. Same with the `wyeekong/IRR` private repo it points
to: if you can grant me read access (or just send the `test_df2.7z` it
hosts), we can verify there's nothing else hiding there.

## Author info for BDSP

I have your corresponding email (wkong@bidmc.harvard.edu) confirmed. For
the rest of the author list, please confirm whether each co-author
prefers their **institutional** address or the **personal address** on
record in `emails.txt`. We can use either, but BDSP only stores one
per author and authors with existing BDSP accounts will be matched on it.

Thanks Wan-Yee — drop everything in your shared Drive (or email directly)
and we'll have the whole package ready to publish within a day or two of
receiving these two files.

Best,
Brandon
