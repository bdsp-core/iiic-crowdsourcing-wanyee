# BDSP launch checklist

Step-by-step actions to take the project at
https://bdsp.io/projects/87rztvzmyz9uh0esnd83/ from "initiated" through
"published". Each step indicates who can do it.

> **Note on roles.** Wan-Yee is the **submitting + corresponding author**.
> Brandon (or another BDSP editor) has admin access; this is who runs the
> editor/admin steps. Claude doesn't have BDSP credentials and can't run
> these directly — but every piece of content needed for each step is
> already drafted in `docs/`.

---

## Phase 1 — Fill in the project page (submitting author = Wan-Yee, or admin on her behalf)

For each BDSP section, copy/paste the HTML block from
[`docs/bdsp_publication_content.md`](./bdsp_publication_content.md). The
mapping is:

| BDSP form field | Source block in `bdsp_publication_content.md` |
|---|---|
| `title` | "## title" |
| `version` | "## version" |
| `short_description` | "## short_description" |
| `abstract` (HTML) | "## abstract" |
| `background` (HTML) | "## background" |
| `methods` (HTML) | "## methods" |
| `content_description` (HTML) | "## content_description" |
| `usage_notes` (HTML) | "## usage_notes" |
| `ethics_statement` (HTML) | "## ethics_statement" |
| `acknowledgements` (HTML) | "## acknowledgements" |
| `conflicts_of_interest` (HTML) | "## conflicts_of_interest" |
| `references` (HTML) | "## references" |
| `release_notes` (HTML) | "## release_notes" |
| `project_home_page` | https://github.com/bdsp-core/iiic-crowdsourcing-wanyee |
| `access_policy` | 0 (Open) |
| `license` | CC BY-NC 4.0 |

**Checklist:**
- [ ] Paste each section.
- [ ] Set `resource_type = Database` (0).
- [ ] Pick "CC BY-NC 4.0" from the BDSP License dropdown. *If it isn't there, ask Magnus/Eli to add it before continuing.*
- [ ] Save draft.

---

## Phase 2 — Add the 13 authors (submitting author or admin)

For each author in [`docs/authors.md`](./authors.md), in the exact order shown
(1 Kong → 13 Jing):

- [ ] Search BDSP user table by email.
- [ ] **If a BDSP account exists:** add the existing user as an author at `display_order = N`.
- [ ] **If no account exists:** create an `AuthorInvitation` with their email; they'll receive a sign-up link. Once they accept, they auto-link as author.
- [ ] Set `is_submitting = True` on Kong (#1) only.
- [ ] Set `is_corresponding = True` on Kong (#1) only.
- [ ] For each author, add their affiliation string from the table.

Admins can pre-check which authors already have accounts using the Django
shell snippet in [`docs/authors.md`](./authors.md#checking-which-authors-already-have-bdsp-accounts).

**Checklist:**
- [ ] All 13 authors added in correct display order.
- [ ] Kong is the unique `is_submitting` + `is_corresponding`.
- [ ] All authors with accounts are linked; invitations sent to the rest.

---

## Phase 3 — Stage the data in S3 (admin)

The S3 layout is fully spec'd in [`docs/s3_folder_layout.md`](./s3_folder_layout.md).

**Pre-upload (local prep):**
- [ ] Confirm S3 bucket + project-slug prefix (still pending — Brandon to paste).
- [ ] Run the de-identification on the raw Centaur user CSVs (drop `email`, `first`, `last`, `app_display_name`).
- [ ] Once `test_df4.csv` arrives from Wan-Yee, build `iiic_contest_eeg.h5`:

  ```bash
  python scripts/bundle_eeg_h5.py \
    --mat-dir /Volumes/Extreme\ SSD/WanYee_ACNS_IRR/ImageCode_JJ/Data \
    --out data/iiic_contest_eeg.h5 \
    --annotations data/test_df4.csv \
    --experts30 data/labels_experts30.xlsx
  ```

- [ ] Write `annotations/test_df4_dictionary.md` (column-by-column data dictionary; can be derived programmatically once `test_df4.csv` is in hand).
- [ ] Write `eeg_signals/iiic_contest_eeg_schema.md` (the schema doc + reader snippet — most of this can be copy-pasted from the bundler's docstring).
- [ ] Build the `contest_images/manifest.csv` (one row per PNG with `segment_id`, `srpp_label`, `png_filename`, `sha256`). *Only if Centaur releases the PNGs.*

**Upload:**
- [ ] `aws s3 sync` the local staging directory up to `s3://<bucket>/<project-slug>/`.
- [ ] Verify with `aws s3 ls --recursive --human-readable s3://<bucket>/<project-slug>/`.

---

## Phase 4 — Editor accept + auto-approve + publish (admin)

Sequence as documented in [`docs/bdsp_admin_steps.md`](./bdsp_admin_steps.md):

- [ ] **Accept:** go to `/console/submitted-projects/87rztvzmyz9uh0esnd83/edit/`, submit the editor form with `decision = 2` (accept). Status: 20 → 40.
- [ ] **Copyedit with no changes:** go to `/console/submitted-projects/87rztvzmyz9uh0esnd83/copyedit/`, submit with `made_changes = False`. Status: 40 → 60. This auto-approves all authors.
- [ ] **Publish:** go to `/console/submitted-projects/87rztvzmyz9uh0esnd83/publish/`, submit the publish form. Status: 60 → Published. DOI registered.
- [ ] (Sanity) verify the public published URL renders.

---

## Phase 5 — GitHub + cross-references

- [ ] **Push the GitHub repo** (`bdsp-core/iiic-crowdsourcing-wanyee`):

  ```bash
  cd /Users/mwestover/GithubRepos/wanyee-irr/iiic-crowdsourcing
  gh repo create bdsp-core/iiic-crowdsourcing-wanyee \
    --public \
    --description "Code + data pointers for Kong et al. 2025 (Epilepsia, doi:10.1111/epi.18547)" \
    --source . --remote origin --push
  ```

- [ ] Once the BDSP project has a DOI, update the GitHub README:
  - swap the `https://bdsp.io/projects/87rztvzmyz9uh0esnd83/` placeholder for the final published URL
  - add the DOI badge
- [ ] Update the BDSP page's `project_home_page` if the GitHub URL changes.
- [ ] Tag a `v1.0.0` release on GitHub matching the BDSP `version`.

---

## What's blocking each phase right now

| Phase | Blocker |
|---|---|
| 1 (page) | Nothing — content is ready in `docs/bdsp_publication_content.md`. Just paste. |
| 2 (authors) | Pending: institutional vs personal email preference for ~7 authors (see `docs/authors.md`). Wan-Yee's reply will resolve. |
| 3 (S3 upload) | Pending: S3 bucket + project-slug path from Brandon; `test_df4.csv` + `labels_experts30.xlsx` from Wan-Yee; SSD copy completion (for the `.mat` bundle source). |
| 4 (publish) | Pending: Phases 1-3 complete. |
| 5 (GitHub) | Push pending Brandon's go-ahead. Repo is local and committed. |

---

## What Claude (this assistant) can do right now

- ✏️ Refine any of the prose in `docs/bdsp_publication_content.md` before you paste it.
- 🧪 Write the de-identification script (`scripts/deidentify_for_release.py`) — would slot into Phase 3.
- 📜 Write `annotations/test_df4_dictionary.md` and `eeg_signals/iiic_contest_eeg_schema.md` from templates; the data dictionary fills in once `test_df4.csv` arrives but the structure can be drafted now.
- 🔁 Once the SSD copy finishes, run the full bundler over the 10,704 `.mat` files to produce the publishable `iiic_contest_eeg.h5`.
- 🚀 Once you say "push," run the `gh repo create … --push` from Phase 5.

## What Claude *can't* do without your action

- ❌ Log into BDSP. No admin credentials.
- ❌ Upload to S3. No AWS credentials configured here.
- ❌ Send the email to Wan-Yee. (Email is drafted at `docs/email_to_wanyee.md`; you copy/send.)
- ❌ Pick a license entry from BDSP's License dropdown. If "CC BY-NC 4.0" isn't already in the BDSP Licenses table, you'll need to ask Magnus/Eli to add it.
