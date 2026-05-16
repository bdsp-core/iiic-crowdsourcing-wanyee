# Author table — for adding to the BDSP publication

Authors must be added to the BDSP project in **the order listed below** (this
matches the author byline in the published paper). The first author (Kong) is
the **submitting author**; she is also the **corresponding author**.

| # | Name | Affiliation (current) | Email | ORCID | Status |
|---|------|----------------------|-------|-------|--------|
| 1 | Wan-Yee Kong         | Dept of Neurology, Beth Israel Deaconess Medical Center; Harvard Medical School, Boston MA | **wkong@bidmc.harvard.edu** *(confirmed, corresponding)* | — | **Submitting + corresponding** |
| 2 | Fábio A. Nascimento  | Assistant Professor of Neurology, Washington University School of Medicine, St. Louis MO | **fabion@wustl.edu** *(confirmed, also in study emails.txt)* | 0000-0002-7161-6385 *(verify)* | confirmed |
| 3 | Aaron F. Struck      | Assoc. Professor & Head of Adult Epilepsy, Washington University School of Medicine, St. Louis MO *(moved from UW–Madison 7/2025)* | **afstruck00@gmail.com** *(confirmed; ask Wan-Yee for institutional WashU/Wisc email)* | 0000-0002-9103-1798 *(verify)* | affil-change |
| 4 | Erik Duhaime         | Cofounder & CEO, Centaur Labs (Centaur.ai), Boston MA | **erik@centaurlabs.com** *(confirmed)* | — | confirmed |
| 5 | Srishti Kapur        | Senior Manager, Engagement, Centaur Labs, Boston MA | **srishti@centaurlabs.com** *(confirmed via study emails.txt)* | — | confirmed |
| 6 | Edilberto Amorim     | Assistant Professor of Neurology, UCSF / Zuckerberg San Francisco General Hospital, San Francisco CA | edilberto.amorim@ucsf.edu *(confirmed institutional)* / edilbertoamorim@gmail.com *(personal, in study emails.txt)* | 0000-0001-6972-5622 *(verify)* | confirmed |
| 7 | Gregory Kapinos      | Assistant Professor of Neurosurgery & Neurology, Icahn School of Medicine at Mount Sinai; Director Neurocritical Care, Elmhurst Hospital (NYC H+H), New York NY | **kapigreg@gmail.com** *(confirmed personal; institutional likely gregory.kapinos@mountsinai.org but not confirmed)* | 0000-0002-1527-4552 *(verify)* | partial-confirm |
| 8 | Andres A. Rodriguez-Ruiz | Associate Professor of Neurology; Director ICU EEG/Neurodiagnostics, Emory University School of Medicine, Atlanta GA | **rodriguezandr@gmail.com** *(confirmed personal; institutional likely aarodr4@emory.edu but not confirmed)* | 0000-0002-1425-9035 *(verify)* | partial-confirm |
| 9 | Brendan Thomas       | Massachusetts General Hospital, Dept of Neurology, Boston MA | **brenleethomas@gmail.com** *(confirmed via study emails.txt)* | — | confirmed |
| 10 | Masoom J. Desai     | Associate Professor of Neurology, Univ. of New Mexico School of Medicine, Albuquerque NM | **dr.masoom@gmail.com** *(confirmed personal; institutional likely mjdesai@salud.unm.edu but not confirmed)* | 0000-0002-6316-8404 *(verify)* | partial-confirm |
| 11 | Jong Woo Lee        | Associate Professor of Neurology, HMS; Clinical Director, Epilepsy Division, Brigham and Women's Hospital, Boston MA | **jlee38@bwh.harvard.edu** *(confirmed via study emails.txt)* | 0000-0001-5283-7476 *(from paper, authoritative)* | confirmed |
| 12 | M. Brandon Westover | Emily Fisher Landau Professor of Neurology, HMS; BIDMC, Boston MA | **mb.westover@gmail.com** *(confirmed personal)* / mwestove@bidmc.harvard.edu *(BIDMC pattern, verify)* | 0000-0003-4803-312X *(from paper, authoritative)* | confirmed |
| 13 | Jin Jing            | Assistant Professor of Neurology, HMS; BIDMC, Boston MA | **jjzhdy@gmail.com** *(confirmed personal via study emails.txt; institutional likely jjing1@bidmc.harvard.edu — not confirmed)* | 0000-0002-2415-5854 *(verify)* | partial-confirm |

## What I'm confident about

All 13 authors now have at least one confirmed email — most from
`/Volumes/Extreme SSD/WanYee_ACNS_IRR/old/emails.txt`, which was the original
study-coordination email list Wan-Yee maintained:

- **#1 Kong (corresponding)**: wkong@bidmc.harvard.edu (paper itself).
- **#2 Nascimento, #4 Duhaime, #6 Amorim (institutional)**: publicly verified.
- **#3 Struck, #5 Kapur, #7 Kapinos, #8 Rodriguez-Ruiz, #9 Thomas, #10 Desai,
  #11 Lee, #12 Westover (personal), #13 Jing**: confirmed via the study
  emails.txt — these are the emails the authors used to coordinate the work.
- ORCIDs for **Lee (#11)** and **Westover (#12)** are from the published
  paper itself (authoritative).

## What is still uncertain

- **Institutional vs personal email**: For most authors we only have a
  personal Gmail (Struck, Kapinos, Rodriguez-Ruiz, Thomas, Desai, Jing).
  For BDSP, ask whether each prefers their institutional address (which
  may anchor their long-term archival identity) or their personal address
  (which we already have).
- **#3 Struck** — moved from UW–Madison to WashU in 7/2025. The published
  paper records his affiliation as Wisconsin, which is correct historically,
  but his current BDSP contact should reflect the move.
- **Most ORCIDs** flagged "verify" were pulled from search results; confirm
  on orcid.org before adding them to BDSP. Lee's and Westover's are from the
  paper and are authoritative.

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
