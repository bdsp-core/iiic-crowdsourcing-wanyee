# Email to Jin Jing — canonical IIIC segment .mat files

**Subject:** IIIC segment .mat files — where do the canonical 50,697 live?

---

Hi Jin,

I'm helping Wan-Yee package the data and code from your *Epilepsia* 2025
crowdsourcing paper for release on BDSP and GitHub. The reproduction
pipeline is mostly working, and I'm now assembling a single HDF5 archive
that bundles the per-segment EEGs you used to render the contest images.

We have **5,801 of the ~8,904 contest segments** so far — they came out
of Wan-Yee's `WanYee_ACNS_IRR/ImageCode_JJ/Data/` folder on Box. The
**~3,100 missing are all `sid*` prefix** (e.g.
`sid1080_20170822_150113_12126`). None of them are in Wan-Yee's Box,
in your `Jin Jing's files/` Box folder, or in
`bdsp-opendata-credentialed/iiic-freq2/` or `iiic-freq3/`.

`bdsp-opendata-restricted/spikenet2/Events/weak/iiic/` covers a small
slice (456), but those `.mat` files are SpikeNet2-format (`data`,
`channels`, `Fs`) — missing the `spec_10min` precomputed 10-minute
regional spectrograms that your `main_getImage.m` script reads.

Could you point me at where the **canonical IIIC `.mat` files** live
— the 50,697 you scored with the 30 expert raters for the 2023
*Neurology* paper? Each file should contain:

```
data_50sec   (21, 10000)   float64    -- 50 s of 21-channel EEG at 200 Hz
spec_10min   (4, 2)        cell       -- LL/RL/LP/RP spectrograms,
                                        100 freq bins x 300 time bins each
```

Best guesses on my end: MGH research filesystem (your local working
directory at the time), an old `E:\Data\` drive, or an unindexed S3
bucket. If any of those rings a bell, even a directory path I can
point Wan-Yee or Brandon at would be huge.

Also: do you happen to have the **`labels_experts30.xlsx`** pivoted
matrix that your IRR notebook reads at
`/content/drive/MyDrive/IRR/labels_experts30.xlsx`? Wan-Yee says she
got it from you originally; we need it for Supplemental S4/S5 of the
crowdsourcing paper.

Thanks!
Brandon
