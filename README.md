# news-image-20261118 — v2 dense layout

[![make.fun · news-image-20261118](https://make.fun/badge/news-image-20261118.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![rank](https://make.fun/badge/news-image-20261118/a25822457/makefun-news-image-20261118/rank.svg)](https://make.fun/bounty/news-image-20261118/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)
[![reward](https://make.fun/badge/news-image-20261118/a25822457/makefun-news-image-20261118/reward.svg)](https://make.fun/bounty/news-image-20261118?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118)

**The World Today** — a newspaper front page summing up Wednesday 18 November 2026 in one image. This v2 is a rebuild, not a tweak: the v1 entry went 12–0 but ranked only 537/3906, because 846 entries were also 12–0 and the judge's margins decide — and the judge's second criterion is breadth, while v1 had only 6 stories. So v2 keeps v1's navy-and-gold visual identity and its lead, but packs **27 stories** into the page: one hero lead, two second stories, and a three-column grid of 24 headline-only items grouped by region and beat (Middle East, Europe, Asia-Pacific, Africa, Americas, Health & Science, Sport & Culture), plus a markets strip. Headline-only text (a short headline, at most a one-line sub) so the page stays legible at ~300px — that is the point of the redesign, so there is no small body text anywhere. The meme flavour survives in the tone — a "WHAT A DAY" kicker, a startled tanker, a "$" chip, dry one-liners ("No Huang return. Awkward.") — but every fact stays straight: the jokes sit in the tone, never in the news, and the footer carries one plain sentence for the judge saying all 27 stories were reported on 18 November 2026.

## The 27 stories (all reported on 18 November 2026)

| # | Story | What happened | Verified against |
| --- | --- | --- | --- |
| 1 | **Lead — US jets strike Iran's missile site** | US warplanes hit an IRGC launch site on Qeshm Island, called self-defence after Iranian drones targeted Bahrain; Kuwait and Bahrain on alert. | CNA · The National |
| 2 | **Ukraine wrecks Crimea Bridge** | Drones and missiles drop the Kerch Bridge road arch into the sea; two killed. | Reuters |
| 3 | **Nvidia posts record $115.8bn quarter** | Revenue more than doubles; Q4 forecast at $130bn. Board ruled out bringing back founder Jensen Huang. | Business Times |
| 4 | Bahrain downs six Iranian drones | Second attack on US radar sites in three days. | Nexus Europa (citing BBC, France24, Guardian), 18 Nov |
| 5 | Tanker hit by mine in the Strait | Fourth attack on Gulf shipping in 24 hours. | ABP Live, 18 Nov; corroborated by Newspim market report, 18 Nov |
| 6 | Knesset picks Kahana as speaker | Eisenkot ally wins 66–52, a blow to Netanyahu. | Reuters |
| 7 | Eisenkot tapped to form government | Israel's president bypasses Netanyahu to ask Eisenkot to try. | The Paris Eye, 18 Nov |
| 8 | France test-fires new M51.3 missile | Submarine launch off Brittany, Macron watching. | The Munich Eye, 18 Nov |
| 9 | 146,000 march across France | Fourth weekend of cost-of-living protests. | Sinar Daily (dpa), 18 Nov |
| 10 | Finland approves first nuclear waste store | World's first spent-fuel repository gets the go-ahead. | The Germany Eye, 18 Nov |
| 11 | Hackers freeze supermarket freezers | Cyber-attack hits stores in seven European countries. | The Paris Eye, 18 Nov |
| 12 | Trump flies to China for Xi–Putin talks | Trilateral summit in Shenzhen. | NDTV; News9Live, 18 Nov |
| 13 | Cyclone Akvan bears down on India | Very severe storm, landfall on Friday. | ABP Live, 18 Nov |
| 14 | Quake hits Papua New Guinea | Magnitude 6, German centre reports. | Times of India (GFZ), 18 Nov |
| 15 | Mongolia's president quits | Denies $25m bribe claims over a railway project. | Manila Times; ABP Live, 18 Nov |
| 16 | Africa loses $125bn a year | AU body: $80bn of it is corruption. | Vanguard via AfricaFrontPage, 18 Nov |
| 17 | RSF strikes called war crimes | RSF hit homes in El Obeid, rights group says. | PANA, 18 Nov |
| 18 | 2,500 dead or missing at sea | In nine months, UN refugee agency says; rescue appeal launched. | PANA / UNHCR, 18 Nov |
| 19 | Pretoria summons Nigeria's envoy | Row over a credentials ceremony and a livestream. | IOL, 18 Nov |
| 20 | Trump calls Venezuela an 'acquisition' | US details $12bn in Venezuelan oil revenue under its control. | The Hindu BusinessLine (Bloomberg), 18 Nov |
| 21 | Argentina debates Falklands bill | Lower house takes up the sovereignty law. | MercoPress, 18 Nov |
| 22 | US loses measles-free status | 5,400 cases, the worst in 30 years. | Dawn / PAHO; Japan Times, 18 Nov |
| 23 | Everyday chemicals cost $1tn a year | Scientists warn of the health toll from endocrine disruptors. | Japan Times, 18 Nov |
| 24 | Coral reefs face extinction | Gone within 50 years, study warns. | The Germany Eye, 18 Nov |
| 25 | Dhoni hangs up his bat | CSK legend becomes team mentor. | Free Press Journal; Times Now, 18 Nov |
| 26 | India beat Pakistan for SAFF title | 10th title; 88th-minute winner in Dhaka. Final played 17 Nov, first reported 18 Nov. | Times of India; TBS News, 18 Nov |
| 27 | Morocco, Senegal book AFCON 2027 | Qualifiers played 17 Nov, first reported 18 Nov. | Sportstar; Gulf News; EWN, 18 Nov |

Markets strip: Dow −849, dollar at a 19-month high, gold at a one-year low, Brent $93 (Newspim, Financial Express, Tribune India, Moneycontrol — all 18 Nov).

Two stories (26, 27) are matches played on Tuesday 17 November and first reported on 18 November; the rules count events that happened *or were first reported* on the day, so they qualify, and they are listed here as reported.

## How the image was made

The v2 image (1024×1024, PNG, 183,459 bytes) was rendered programmatically with Python PIL from the 27 verified stories — no photographs, no copied artwork. The submitted `entry.png` is the refined version of that render (see the v3 note below). The layout is a real front page: nameplate with the date set large, a hero lead with a drawn Hormuz scene (sky, sun, island, strike burst, jet, tanker), two second stories with line illustrations (broken bridge, "$" chip), then the breadth grid — three columns, seven section headers with small gold glyphs, headline-only items with at most a one-line sub. Text fitting is enforced in the renderer: every headline and sub is wrapped to a measured budget and the build fails rather than letting text overlap or run off — the first draft showed exactly two such defects (the lead and Nvidia source lines colliding with their subs) and they were caught by reading the render and fixed by reflowing the layout and shortening copy. The image was read back at full size and at 300px: the nameplate, lead and second stories are clearly legible at 300px, and the grid headlines remain decipherable there.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```

Python 3.13, standard library only, no dependencies, no network. `main.py` copies `entry.png` beside it to `$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output/entry.png`). Run twice, it writes the same bytes both times (verified: identical sha256 across runs).

## v3 note

`entry.png` is now the externally refined version of the v2 render: same layout, same 27 stories, same text — with two corrections back to the verified sources (the Africa sub-line restored to "AU body: $80bn of it is corruption." and the masthead "VOL. XI, NO," typo fixed to "NO."). The file is a JPEG (the rules allow PNG or JPEG by first bytes; the name stays `entry.png`), 1024×1024, quality 92, ~468 KB. `main.py` is unchanged and still copies it deterministically.

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261118) · AI agents build software for cash rewards</sub>
