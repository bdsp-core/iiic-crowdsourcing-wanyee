# BDSP admin steps — accept, auto-approve, publish

This walkthrough takes the BDSP project from "submitted" through to "published",
auto-approving all authors (the submitted version is the final version — no
copyediting required).

> Project slug: `87rztvzmyz9uh0esnd83`
> Project URL: https://bdsp.io/projects/87rztvzmyz9uh0esnd83/overview/

## Prereqs

1. The project has been **submitted** by Wan-Yee (you'll see status code 20).
2. All co-authors have been added to the project (use `docs/authors.md`).
   For authors without a BDSP account, send an `AuthorInvitation`; they
   must accept before the project can be published.
3. The fields in `docs/bdsp_publication_content.md` have been pasted into the
   appropriate sections (abstract, methods, content_description,
   usage_notes, ethics, acknowledgements, conflicts_of_interest, references,
   license = CC BY-NC 4.0, project_home_page = the GitHub repo).
4. Data files have been uploaded to the project's S3 folder.

## Step 1 — Accept (status 20 → 40)

URL: `/console/submitted-projects/87rztvzmyz9uh0esnd83/edit/`
Form: `EditSubmissionForm` (see `bdsp-django/console/forms.py:260`)
Set `decision = 2` (accept). This advances `submission_status` to 40 and
sets `editor_accept_datetime`.

## Step 2 — Copyedit with no changes (status 40 → 60)

URL: `/console/submitted-projects/87rztvzmyz9uh0esnd83/copyedit/`
Form: `CopyeditForm` (see `bdsp-django/console/forms.py:299`)
Set `made_changes = False`. Because there were no copyedit changes, BDSP
auto-runs `approve_all_authors()` (see
`bdsp-django/project/modelcomponents/activeproject.py:716`) and advances
the project straight to status 60 ("all authors approved, awaiting
publication"). This is the **auto-approve flow** the user asked for.

Alternative — if step 2 lands the project at status 50 (it shouldn't, if
`made_changes` is False), run this from the Django shell to force-approve
all authors:

```python
from project.models import ActiveProject
p = ActiveProject.objects.get(slug='87rztvzmyz9uh0esnd83')
assert p.submission_status == 50, p.submission_status
ok = p.approve_all_authors()
assert ok
```

## Step 3 — Publish (status 60 → Published)

URL: `/console/submitted-projects/87rztvzmyz9uh0esnd83/publish/`
Form: `PublishForm`. POSTing this form creates the immutable
`PublishedProject` snapshot and assigns the DOI. From this point the data
files are read-only.

## Sanity checks

After step 3, the project's public URL should return a "Published"
project view (no longer the draft `overview` URL). Verify:

```bash
curl -sI https://bdsp.io/content/iiic-crowdsourcing-wanyee/<version>/
```

(or whatever published slug BDSP issues).

## Troubleshooting

If the project gets stuck with `submission_status = 60` but
`author.approval_datetime is None`, run:

```bash
python manage.py fix_author_approval 87rztvzmyz9uh0esnd83
```

(See `bdsp-django/project/management/commands/fix_author_approval.py`.)
