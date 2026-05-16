# Handoff guide for finishing the BDSP publication

Single-source-of-truth for everything still needed to finish publishing
**Kong et al. 2025 (Epilepsia, doi:10.1111/epi.18547)** on BDSP. Each
section lists the content file, the destination, and step-by-step
instructions. Path conventions:

* **Repo root** (all paths below are relative to it):
  `/Users/mwestover/GithubRepos/wanyee-irr/iiic-crowdsourcing/`
* **GitHub:** https://github.com/bdsp-core/iiic-crowdsourcing-wanyee (live)
* **BDSP project:** https://bdsp.io/projects/87rztvzmyz9uh0esnd83/overview/
* **S3 destination:** `s3://bdsp-opendata-credentialed/iiic-irr-crowd/`
  *(credentialed access; access_policy = 2)*

---

## 1. Files I've produced (for your reference)

Every file in the repo, grouped by purpose. Paths are relative to the
repo root.

### Drafted content you'll paste into BDSP

| Destination | Source file |
|---|---|
| Every BDSP project-page section (title, abstract, methods, etc.) | `docs/bdsp_publication_content.md` |
| Author rows in the project | `docs/authors.md` |
| S3 folder structure (for upload) | `docs/s3_folder_layout.md` |
| BDSP admin workflow (accept → auto-approve → publish) | `docs/bdsp_admin_steps.md` |
| Email to Wan-Yee | `docs/email_to_wanyee.md` |
| End-to-end launch checklist | `docs/bdsp_launch_checklist.md` |

### Code that backs the publication

| What it does | Source file |
|---|---|
| Imports + loads `test_df4.csv` | `src/data_loading.py` |
| Mixed-effects models + non-inferiority tests | `src/mixed_models.py` |
| Pairwise agreement, Fleiss κ, Gwet AC1 | `src/irr.py` |
| Weighted-majority voting | `src/scoring.py` |
| Sample-size bootstrap (Fig 5) | `src/bootstrap.py` |
| Plot helpers | `src/plotting.py` |
| Constants + paths | `src/config.py` |
| Bundles per-segment .mat files into HDF5 | `scripts/bundle_eeg_h5.py` |
| MATLAB image generator (Jin's original) | `scripts/contest_image_gen/main_getImage.m` |
| Python port of the image generator | `scripts/contest_image_gen/make_contest_image.py` |
| One script per figure/table | `scripts/{table1, figure2_*..figure5_*, supp_s1..s11_*}.py` |
| One-shot reproducer | `scripts/reproduce_all.py` |

### Notebook originals (preserved, scrubbed)

| File | Notes |
|---|---|
| `notebooks_original/build_test_df4.ipynb` | Upstream pipeline that constructs `test_df4.csv` |
| `notebooks_original/IRR_gold_standard_and_expert.ipynb` | IRR analyses (Supp S4, S5) |
| `notebooks_original/mixed_modeling.ipynb` | Mixed-effects modelling for Figs 2-3 + Table 1 |
| `notebooks_original/crowd_vs_individual_expert.ipynb` | Figs 4-5 + most supplementals |
| `notebooks_original/README.md` | Scrubbing notes (GH PAT redacted, PII emails redacted) |

### Sample output / reference

| File | What it is |
|---|---|
| `docs/sample_outputs/contest_image_pat0002.png` | Python-generated sample of the contest stimulus |
| `scripts/contest_image_gen/sample_reference.png` | Jin's MATLAB-generated baseline for the same segment |

---

## 2. Filling in the BDSP project page (manual, via the web UI)

You'll be logged in as a BDSP admin/editor with rights to edit the
ActiveProject at https://bdsp.io/projects/87rztvzmyz9uh0esnd83/overview/.

> ⚠️ Set `resource_type = Database` and `access_policy = 2 (Credentialed)`.
> The published data goes to `s3://bdsp-opendata-credentialed/iiic-irr-crowd/`,
> which is the bucket bound to the Credentialed policy.

### 2.1 Open `docs/bdsp_publication_content.md`

This single file has every section pre-written. Each section is marked
with a `## section_name` header followed by a code block. The
section-name → BDSP form-field mapping is:

| `##` heading in the source file | BDSP form field |
|---|---|
| `## title` | Title |
| `## version` | Version |
| `## short_description` | Short description |
| `## abstract` | Abstract |
| `## background` | Background |
| `## methods` | Methods |
| `## content_description` | Content description |
| `## usage_notes` | Usage notes |
| `## ethics_statement` | Ethics statement |
| `## acknowledgements` | Acknowledgements |
| `## conflicts_of_interest` | Conflicts of interest |
| `## references` | References |
| `## release_notes` | Release notes |
| `## project_home_page` | Project home page |

### 2.2 Pasting steps

1. Open the BDSP edit form for the project.
2. For each section:
   * Open `docs/bdsp_publication_content.md`.
   * Find the matching `## section_name` heading.
   * Copy **only the contents between the ` ```html ` and ` ``` `
     delimiters** (or between ` ``` ` for plain-text sections). Do **not**
     paste the heading or the backticks themselves.
   * Paste into the matching BDSP form textarea.
3. Set `resource_type = Database`.
4. Set `access_policy = 2 (Credentialed)`.
5. License: pick "CC BY-NC 4.0" from the dropdown. *If it isn't in the
   dropdown, ask Magnus / Eli to add a License row for "Creative Commons
   Attribution-NonCommercial 4.0 International" before continuing.*
6. Project home page: `https://github.com/bdsp-core/iiic-crowdsourcing-wanyee`
7. Click Save (don't submit for publication yet — there's more to do).

---

## 3. Adding the 13 authors

Open `docs/authors.md`. Authors are listed in the exact order they should
appear in BDSP. Kong is the **submitting + corresponding author**;
no one else carries either flag.

### 3.1 Check who already has a BDSP account

Run this on the prod EC2 (you have SSH access), inside a Django shell:

```bash
ssh bdspweb-prod-bidmc
cd /bdsp/bdsp.io_webapp
sudo docker-compose exec -T prod python bdsp-django/manage.py shell <<'PY'
from user.models import User
EMAILS = [
    "wkong@bidmc.harvard.edu",
    "fabion@wustl.edu",
    "afstruck00@gmail.com",
    "erik@centaurlabs.com",
    "srishti@centaurlabs.com",
    "edilberto.amorim@ucsf.edu",
    "kapigreg@gmail.com",
    "rodriguezandr@gmail.com",
    "brenleethomas@gmail.com",
    "dr.masoom@gmail.com",
    "jlee38@bwh.harvard.edu",
    "mb.westover@gmail.com",
    "jjzhdy@gmail.com",
]
for e in EMAILS:
    try:
        u = User.objects.get(email__iexact=e)
        print(f"  EXISTS  {e:40s} -> id={u.id} ({u.get_full_name() or u.username})")
    except User.DoesNotExist:
        print(f"  MISSING {e:40s}")
PY
```

### 3.2 Add each author through the UI

For each row in `docs/authors.md`:

* **If `EXISTS`:** in the BDSP project's Authors section, click "Add
  author" and pick the matching email. Set `display_order = N` (the row
  number in `authors.md`). Affiliation = the value in the table.
* **If `MISSING`:** click "Invite author" and enter their email +
  affiliation. They'll get a sign-up email; once they accept, they're
  auto-linked.
* **Kong only:** set both `is_submitting = True` and
  `is_corresponding = True`.

### 3.3 Open questions for Wan-Yee (already in the email)

* For each author with a personal Gmail in `emails.txt`, does she
  recommend using institutional (e.g. `edilberto.amorim@ucsf.edu`) or
  personal (`edilbertoamorim@gmail.com`) for the BDSP record?
* Struck moved from UW-Madison to WashU in 7/2025. Use his WashU
  affiliation, not the paper-time one, for BDSP.

---

## 4. Staging the data in S3

Target: `s3://bdsp-opendata-credentialed/iiic-irr-crowd/`. I already
verified write access via the `opendata-write` profile.

### 4.1 De-identify the raw Centaur exports

Two user-table CSVs have PII (`email`, `first`, `last`,
`app_display_name`). The read-table doesn't. Run:

```bash
cd /Users/mwestover/GithubRepos/wanyee-irr/iiic-crowdsourcing
mkdir -p staging/raw_contest_exports

# eeg-all-users-and-topics.csv -- drop email/first/last/app_display_name
python3 -c "
import pandas as pd
df = pd.read_csv('data/eeg-all-users-and-topics.csv')
df = df.drop(columns=[c for c in ('email','first','last','app_display_name') if c in df.columns])
df.to_csv('staging/raw_contest_exports/eeg-all-users-and-topics_deidentified.csv', index=False)
print(f'Wrote {len(df)} rows, cols = {df.columns.tolist()}')
"

# 1251-all-users.csv
python3 -c "
import pandas as pd
df = pd.read_csv('data/1251-all-users.csv')
df = df.drop(columns=[c for c in ('email','first','last','app_display_name') if c in df.columns])
df.to_csv('staging/raw_contest_exports/1251-all-users_deidentified.csv', index=False)
print(f'Wrote {len(df)} rows, cols = {df.columns.tolist()}')
"

# 1251-all-users_demo_info.csv
python3 -c "
import pandas as pd
df = pd.read_csv('data/1251-all-users_demo_info.csv')
df = df.drop(columns=[c for c in ('email','first','last','app_display_name') if c in df.columns])
df.to_csv('staging/raw_contest_exports/1251-all-users_demo_info_deidentified.csv', index=False)
print(f'Wrote {len(df)} rows, cols = {df.columns.tolist()}')
"

# 1251-all-reads_ac.csv -- already de-identified, just copy
cp data/1251-all-reads_ac.csv staging/raw_contest_exports/

# Centaur summary export
cp data/centaur_summary.csv staging/raw_contest_exports/Results_SeizureLike_Patterns_Dec_12_2022.csv
```

### 4.2 Once `test_df4.csv` arrives from Wan-Yee

```bash
cd /Users/mwestover/GithubRepos/wanyee-irr/iiic-crowdsourcing
mkdir -p staging/annotations
cp /path/to/test_df4.csv staging/annotations/
cp /path/to/labels_experts30.xlsx staging/annotations/
```

### 4.3 Once the SSD copy of `ImageCode_JJ/Data/` finishes

Run the bundler to produce the single HDF5 archive:

```bash
mkdir -p staging/eeg_signals
python scripts/bundle_eeg_h5.py \
  --mat-dir "/Volumes/Extreme SSD/WanYee_ACNS_IRR/ImageCode_JJ/Data" \
  --out staging/eeg_signals/iiic_contest_eeg.h5 \
  --annotations staging/annotations/test_df4.csv \
  --experts30 staging/annotations/labels_experts30.xlsx
```

This takes ~7 minutes and produces a ~12 GB file. The script tolerates
re-runs (overwrite mode).

### 4.4 Drop the static files into staging

```bash
cd /Users/mwestover/GithubRepos/wanyee-irr/iiic-crowdsourcing
cp LICENSE staging/LICENSE.txt
cp README.md staging/

cat > staging/citation.bib <<'BIB'
@article{kong2025crowdsourcing,
  author  = {Kong, Wan-Yee and Nascimento, F{\'a}bio A. and Struck, Aaron and
             Duhaime, Erik and Kapur, Srishti and Amorim, Edilberto and
             Kapinos, Gregory and Rodriguez, Andres and Thomas, Brendan and
             Desai, Masoom and Lee, Jong Woo and Westover, M. Brandon and
             Jing, Jin},
  title   = {Evaluating crowdsourcing for ICU EEG annotation:
             A comparison with expert performance},
  journal = {Epilepsia},
  year    = {2025},
  volume  = {66},
  number  = {11},
  pages   = {4366--4380},
  doi     = {10.1111/epi.18547}
}
BIB

cat > staging/CHANGELOG.md <<'CHG'
# Changelog

## 1.0.0 -- 2026-MM-DD (initial release)
- Initial public release accompanying the published manuscript
  (Epilepsia, 2025; doi:10.1111/epi.18547).
- Annotations, raw contest exports (de-identified), bundled EEG
  signals (HDF5), and optional contest images.
CHG
```

### 4.5 Upload

```bash
aws --profile opendata-write s3 sync \
  /Users/mwestover/GithubRepos/wanyee-irr/iiic-crowdsourcing/staging/ \
  s3://bdsp-opendata-credentialed/iiic-irr-crowd/ \
  --exclude '.DS_Store'

# Verify
aws --profile opendata-write s3 ls --recursive --human-readable --summarize \
  s3://bdsp-opendata-credentialed/iiic-irr-crowd/
```

Expected total: ~12–18 GB (dominated by `iiic_contest_eeg.h5`).

---

## 5. Editor accept → auto-approve → publish

Once sections 2-4 are done:

### 5.1 Accept
* URL: `https://bdsp.io/console/submitted-projects/87rztvzmyz9uh0esnd83/edit/`
* Form: `EditSubmissionForm`. Set `decision = 2` (accept). Save.
* Status: 20 → 40.

### 5.2 Copyedit with no changes (auto-approves all authors)
* URL: `https://bdsp.io/console/submitted-projects/87rztvzmyz9uh0esnd83/copyedit/`
* Form: `CopyeditForm`. Set `made_changes = False`. Save.
* Status: 40 → 60. BDSP's
  [`approve_all_authors()`](https://github.com/bdsp-core/bdsp-website/blob/main/bdsp-django/project/modelcomponents/activeproject.py#L716)
  fires automatically.

### 5.3 Publish
* URL: `https://bdsp.io/console/submitted-projects/87rztvzmyz9uh0esnd83/publish/`
* Form: `PublishForm`. Save.
* Status: 60 → Published. DOI registered. Data folder becomes read-only.

### 5.4 Sanity checks
* Visit the published URL and confirm all sections render.
* Click the DOI link — it should resolve to BDSP.
* Open https://github.com/bdsp-core/iiic-crowdsourcing-wanyee — make sure
  the README still points at the BDSP page (consider updating it to the
  final published URL after DOI registration).
* Tag a `v1.0.0` release on GitHub matching the BDSP version:
  ```bash
  cd /Users/mwestover/GithubRepos/wanyee-irr/iiic-crowdsourcing
  git tag -a v1.0.0 -m "Initial release accompanying BDSP publication"
  git push origin v1.0.0
  ```

### 5.5 If `submission_status = 60` but author approvals didn't fire

(Rare; happens if BDSP crashed mid-transition.) Fix via Django shell:

```bash
ssh bdspweb-prod-bidmc
cd /bdsp/bdsp.io_webapp
sudo docker-compose exec -T prod python bdsp-django/manage.py fix_author_approval 87rztvzmyz9uh0esnd83
```

---

## 6. What's still missing (waiting on)

| Item | From | Status |
|---|---|---|
| `test_df4.csv` (full 45-col version) | Wan-Yee | Email drafted: `docs/email_to_wanyee.md` |
| `labels_experts30.xlsx` | Wan-Yee | Same email |
| Author email preferences (institutional vs personal) | Wan-Yee | Same email |
| Full set of `.mat` files in `ImageCode_JJ/Data/` | SSD copy in progress | Should be ready in a few hours |
| GitHub PAT in `mixed_modeling.ipynb` revoked | Wan-Yee | Already scrubbed in the published copy, but she still needs to revoke it on her GitHub |

---

## 7. Files I'm still going to produce (when unblocked)

I can write these without further input from you, but they're more useful
once the dependencies above arrive. Tell me when to go:

* `scripts/deidentify_for_release.py` — formalised version of the inline
  commands in section 4.1.
* `staging/annotations/test_df4_dictionary.md` — column-by-column data
  dictionary; can only fill the column descriptions once `test_df4.csv`
  arrives, but the structure can be laid down now.
* `staging/eeg_signals/iiic_contest_eeg_schema.md` — schema doc with
  example reader snippets; mostly ready (mirrors the bundler docstring),
  just needs final tuning after the full bundle runs.

---

## 8. Quick reference: where Claude's work currently lives

* **Locally:** `/Users/mwestover/GithubRepos/wanyee-irr/iiic-crowdsourcing/`
* **GitHub:** https://github.com/bdsp-core/iiic-crowdsourcing-wanyee (8 commits, public)
* **S3 (write-verified, currently empty):** `s3://bdsp-opendata-credentialed/iiic-irr-crowd/`
* **BDSP project page (placeholder content):** https://bdsp.io/projects/87rztvzmyz9uh0esnd83/overview/
