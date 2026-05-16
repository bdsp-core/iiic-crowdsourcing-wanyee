# Author table — for adding to the BDSP publication

Authors must be added to the BDSP project in **the order listed below** (this
matches the author byline in the published paper). The first author (Kong) is
the **submitting author**; she is also the **corresponding author**.

| # | Name | Affiliation (current) | Email | ORCID | Status |
|---|------|----------------------|-------|-------|--------|
| 1 | Wan-Yee Kong         | Dept of Neurology, Beth Israel Deaconess Medical Center; Harvard Medical School, Boston MA | **wkong@bidmc.harvard.edu** *(confirmed, corresponding)* | — | **Submitting + corresponding** |
| 2 | Fábio A. Nascimento  | Assistant Professor of Neurology, Washington University School of Medicine, St. Louis MO | fabion@wustl.edu | 0000-0002-7161-6385 *(verify)* | confirmed |
| 3 | Aaron F. Struck      | Assoc. Professor & Head of Adult Epilepsy, Washington University School of Medicine, St. Louis MO *(moved from UW–Madison 7/2025)* | struck@neurology.wisc.edu *(UW; **WashU email is likely now active**)* | 0000-0002-9103-1798 *(verify)* | affil-change |
| 4 | Erik Duhaime         | Cofounder & CEO, Centaur Labs (Centaur.ai), Boston MA | erik@centaurlabs.com | — | confirmed |
| 5 | Srishti Kapur        | Senior Manager, Engagement, Centaur Labs, Boston MA | *(likely srishti@centaurlabs.com — **not publicly confirmed**)* | — | needs-confirm |
| 6 | Edilberto Amorim     | Assistant Professor of Neurology, UCSF / Zuckerberg San Francisco General Hospital, San Francisco CA | edilberto.amorim@ucsf.edu | 0000-0001-6972-5622 *(verify)* | confirmed |
| 7 | Gregory Kapinos      | Assistant Professor of Neurosurgery & Neurology, Icahn School of Medicine at Mount Sinai; Director Neurocritical Care, Elmhurst Hospital (NYC H+H), New York NY | *(likely gregory.kapinos@mountsinai.org — **not publicly confirmed**)* | 0000-0002-1527-4552 *(verify)* | needs-confirm |
| 8 | Andres A. Rodriguez-Ruiz | Associate Professor of Neurology; Director ICU EEG/Neurodiagnostics, Emory University School of Medicine, Atlanta GA | *(likely aarodr4@emory.edu — **not publicly confirmed**)* | 0000-0002-1425-9035 *(verify)* | needs-confirm |
| 9 | Brendan Thomas       | Massachusetts General Hospital, Dept of Neurology, Boston MA | **Not found** — ask Wan-Yee | — | needs-info |
| 10 | Masoom J. Desai     | Associate Professor of Neurology, Univ. of New Mexico School of Medicine, Albuquerque NM | *(likely mjdesai@salud.unm.edu — **not publicly confirmed**)* | 0000-0002-6316-8404 *(verify)* | needs-confirm |
| 11 | Jong Woo Lee        | Associate Professor of Neurology, HMS; Clinical Director, Epilepsy Division, Brigham and Women's Hospital, Boston MA | jlee38@bwh.harvard.edu *(institutional pattern; **not publicly confirmed**)* | 0000-0001-5283-7476 *(from paper, authoritative)* | confirmed-orcid |
| 12 | M. Brandon Westover | Emily Fisher Landau Professor of Neurology, HMS; BIDMC, Boston MA | mwestove@bidmc.harvard.edu *(BIDMC pattern)* / mb.westover@gmail.com *(personal, confirmed)* | 0000-0003-4803-312X *(from paper, authoritative)* | confirmed |
| 13 | Jin Jing            | Assistant Professor of Neurology, HMS; BIDMC, Boston MA | *(likely jjing1@bidmc.harvard.edu — **not publicly confirmed**; gmail jjzhdy@gmail.com appeared in original notebook)* | 0000-0002-2415-5854 *(verify)* | needs-confirm |

## What I'm confident about

- **#1 Kong, #2 Nascimento, #4 Duhaime, #6 Amorim, #12 Westover (personal)**
  emails are publicly verified.
- ORCIDs for **Lee (#11)** and **Westover (#12)** are from the published
  paper itself.

## What you / Wan-Yee need to confirm

- **#5 Kapur, #7 Kapinos, #8 Rodriguez-Ruiz, #10 Desai, #11 Lee, #13 Jing**
  — emails are pattern-guesses, not confirmed.
- **#9 Brendan Thomas** — no public faculty page found; need Wan-Yee to share
  his current email.
- **#3 Struck** — moved from UW–Madison to WashU in 7/2025. The published paper
  records his affiliation as Wisconsin, which is correct historically, but his
  current BDSP contact should be his WashU email.

## Checking which authors already have BDSP accounts

Run this on the BDSP admin server (see [`bdsp_admin_steps.md`](./bdsp_admin_steps.md))
to check each of the emails above:

```bash
cd /path/to/bdsp-django
python manage.py shell <<'PY'
from user.models import User
EMAILS = [
    "wkong@bidmc.harvard.edu",
    "fabion@wustl.edu",
    "struck@neurology.wisc.edu",
    "erik@centaurlabs.com",
    # ... add the rest from this table
    "mb.westover@gmail.com",
]
for e in EMAILS:
    try:
        u = User.objects.get(email__iexact=e)
        print(f"  EXISTS  {e:40s} -> id={u.id} ({u.get_full_name() or u.username})")
    except User.DoesNotExist:
        print(f"  MISSING {e:40s}")
PY
```

Authors who already have an account: add directly to the project's author
list. Authors without an account: create an `AuthorInvitation` via the
project's "Invite author" UI; they'll receive an email to create an account
and then auto-link to the project.
