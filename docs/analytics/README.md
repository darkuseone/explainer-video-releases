# Shorts analytics: reading guide and research

Snapshot: 2026-11-07, Europe/Chisinau. Status: CHANNEL ANALYSIS COMPLETE WITH LIMITATIONS; NO REMOTE COMMIT.

## Actual exports, period and units

- `2026-11-07/raw/file1.csv`: channel daily engaged views, 28 dates, 2026-10-09 through 2026-11-05 inclusive. Two columns: Дата (ISO date), Заинтересованные просмотры (count). Sum **58,513**.
- `file2.csv`: content table, **24 video rows + one channel total**, **28 columns**. Video ID/title/publication date/runtime (seconds); engaged views; AVD (`h:mm:ss`); APV and stayed-to-watch (percent); audience counts; average views/viewer; subscribers gained/lost; likes/dislikes/like rating; shares/comments; starts/views; watch hours; net subscribers; thumbnail impressions/CTR. Exact headers, positional duplicate-label warning, hashes and units are archived in the manifest and findings.
- `file3.csv`: daily engaged views for **five videos only**, 140 rows = 5 × 28 dates, same October 9–November 5 range. Columns: date, ID, title, publication date, duration seconds, engaged-view count. This is not an all-video daily export and not a retention curve. Each of its five video sums matches file2 exactly.

The per-video table does not encode its date filter. Its total exactly matches file1, so the shared selected period is strongly inferred, not independently encoded. Report timezone is unknown. Publication dates are English date-only values, NOT timestamps that can be converted to Chisinau. Some daily activity predates publication metadata (planet even has one view October 22 vs publication October 26), and the table includes Big Bang dated November 6 while daily data ends November 5. Confirm Studio settings before publication-day/first-24h claims. Snapshot date is not report end date.

Raw files are preserved unchanged; UTF-8, comma-separated, dot decimals, quoted comma-containing titles. One video ID has leading whitespace (` -nJE4ORyT7o`); normalized ledger IDs trim it while raw exports remain untouched. Two columns both bear «Постоянные зрители»; positional fields preserve them without accidental dictionary overwriting. The meaning of column 14 vs 15 vs 16 must be confirmed in Studio.

## Baseline: exported channel total, not a sum/average of video rows

| Metric | Exported total |
|---|---:|
| Views / starts | 99,531 |
| Engaged views | 58,513 |
| Average view duration | 0:00:37 |
| Average percentage viewed | 74.77% |
| Stayed to watch | 68.54% |
| Swiped away | 31.46% (derived complement) |
| Watch time | 626.7582 hours |
| Unique viewers | 52,447 |
| New viewers | 49,653 |
| Unique reach / co-viewed views | 70,665 / 100,623 |
| Average views per viewer | 1.1157 |
| Subscribers gained / lost / net | 135 / 27 / +108 |
| Likes / dislikes / shares / new comments | 1,553 / 0 / 52 / 80 |
| Thumbnail impressions / CTR | 12,435 / 2.94% |

Descriptive conversions per 1,000 engaged views: **26.54 likes, 1.37 comments, 0.89 shares, 2.31 gained subscribers, 1.85 net subscribers**. These are event ratios, not unique-person conversion probabilities. Like rating 100% means no recorded dislikes in this export, not that 100% of viewers liked it.

Typical-video medians across all 24 rows: **1,086 engaged views; 67.55% stayed; 67.975% APV**. There are three rows with only 9, 9 and 38 engaged views. Excluding those tiny rows (21 videos, ≥499 engaged views), medians are **67.89% stayed / 67.94% APV**. This is a descriptive reliability filter, not a significance threshold. Runtime range 44–62 seconds; median/length effects are confounded by topic and publication age.

Reconciliation: row sums are 58,471 engaged views (42 below total), 99,444 views (87 below total), 130/9 gained/lost subscribers (vs total 135/27), net +121 (vs +108), 626.2747 watch hours (0.4835 below total) and 12,374 impressions (61 below total). Likes, shares and comments reconcile exactly. Do not invent why content is absent; deleted/unlisted/filter differences are possibilities, not findings. Unique viewers are non-additive across videos. Full rows and reconciliation: [dated findings](2026-11-07/findings.md).

## Top three by engaged-view volume within the selected period

| Video | Engaged / views | Stayed | AVD / APV | Gained subs | Why worth studying |
|---|---:|---:|---:|---:|---|
| «Вселенная как пирог с изюмом» | 12,720 / 24,758 | 67.21% | 37 s / 86.23% | 19 | Strong depth, not the highest stop rate; familiar-object title and 44-second runtime are hypotheses to test, not proven causes. |
| «Планета, где ты не доживёшь до первого дня рождения» | 9,730 / 14,130 | 78.95% | 40 s / 77.09% | 24 | Both strong opening selection and depth; 297 likes. Personal consequence is explicit in the title. |
| «Динозавры видели другую Луну» | 7,895 / 12,733 | 70.51% | 38 s / 77.93% | 24 | Concrete familiar subjects with a surprising claim; 3.04 gained subs per 1k engaged, vs channel 2.31. |

Together they contribute **51.86%** of channel engaged views; adding «Ложка нейтронной звезды…» (7,209) brings this to **64.18%**. These are period-volume winners, not equal-age causal winners.

## Bottom three: distinguish reach from script performance

Raw engaged-volume bottom: **MacBook 9; garlic 9; Big Bang 38**. MacBook stayed 88.89%, APV 45.21%; garlic stayed 50%, APV 88.61%; Big Bang stayed 52.78%, APV 68.17%. Samples and dates are inadequate to call any of these scripts successes/failures. The channel export cannot tell why they got so little distribution.

Lowest APV among videos with ≥499 engaged views (diagnostic bottom, not least lifetime reach):

| Video | Engaged | Stayed | AVD / APV | Gained subs | Diagnostic |
|---|---:|---:|---:|---:|---|
| «Зажми нос и помычи…» | 979 | 68.94% | 22 s / 36.90% | 1 | Stop rate near channel baseline but depth much weaker; inspect where explanation loses viewers. Interactive title alone did not hold attention. |
| «Две звезды из трёх мертвы…» | 947 | 67.89% | 33 s / 56.39% | 1 | Opening selection near typical-video baseline, weaker continuation. Exact spoken script/curve unavailable. |
| «Твой мозг врёт тебе так же, как ChatGPT» | 1,193 | 61.88% | 27 s / 56.90% | 5 | Both opening selection and depth weaker, but gained-subscriber ratio 4.19/1k is above channel; not a universal loser. |

Additional opening flags: DNA **48.59% stayed**, 499 engaged / 1,044 starts, despite 48.10 likes and 6.01 comments per 1k engaged (only 24 likes and 3 comments). Lightning **54.74% stayed / 60.74% APV**. Different funnel problems need different fixes.

## Eight channel-specific observations and proposed tests

1. **Separate visual approval from hook success.** DNA was praised by the creator, but its exported stayed rate is 48.59%, below the 68.54% channel total. Keep its craft quality; test a clearer, less overclaimed opening. This does not prove its exact first line caused swipes.
2. **Retain the familiar-to-surprising principle, not the raisin metaphor.** Three period leaders describe concrete subjects/contrasts. New analogies and distinct stories may help; repeated dough/pie imagery is neither requested nor supported.
3. **Stopping and holding are separate.** Universe stops 67.21% but holds 86.23% APV; planet stops 78.95% and holds 77.09%; humming stops 68.94% but holds only 36.90%. Fix openings for weak stops and explanation/payoff for weak depth.
4. **Depth is not subscription conversion.** Oncology has 781 engaged views, 65.67% APV and four gained subs (**5.12/1k**); universe 19/12,720 (**1.49/1k**). Counts are small; preserve high-interest utility and test a specific reason to return, not only cosmic reach.
5. **Interaction is not sufficient.** 2D vision stayed 72.49%, APV 67.94%, comments 7; humming has a hands-on title too but 36.90% APV and one comment. Test whether the demonstration quickly leads to a clear explanation instead of assuming 'do this' guarantees engagement.
6. **No retention or length rule is proven.** Best APV among sizeable rows is the 44-second universe, but 53-second Sun has 81.81% APV and 43-second AVD. Keep one coherent idea and cut density, not automatically everything to 44 seconds. Dense DNA/simulation/oncology scripts warrant clarity edits as hypotheses.
7. **Distribution may develop after day one.** Planet's series peaks October 28 at 3,223 engaged, later than its October 26 publication label; universe peaks October 21 at 6,437. Last seven available dates have 9,424 channel engaged views vs preceding seven 27,105 (−65.23%), but this is not proof of declining production quality; cohorts, topics and distribution differ. No scheduling change is justified from this export.
8. **Use metric-specific winners, not one success score.** Neutron star has 20 comments from 7,209 engaged (2.77/1k); Sun has 12 gained subs from 3,377 (3.55/1k); antimatter has 68 likes from 1,297 (52.43/1k). Preserve these distinct outcomes and inspect relevant mechanisms. CTR 8.67% on Tesla comes from only 173 impressions and does not establish a strong Shorts opening (stayed 56.31%).

## Runtime and publication-day checks (exploratory only)

Among the 21 rows with ≥499 engaged views, the 13 videos at 44–55 seconds have median APV **73.28%**, while the eight at 58–62 seconds have median **63.29%**; median stayed is **67.21% vs 68.415%**. This suggests testing lower explanatory density, not that length itself caused the difference. Groups differ in topic, date and audience exposure. Do not force every video shorter or remove useful connections to inflate APV mechanically.

Publication-date-label groups (not timezone-verified local posting days): Monday 4 videos / 13,436 engaged; Tuesday 4 / 4,543; Wednesday 3 / 14,536; Thursday 3 / 8,803; Friday 5 / 9,428; Saturday 2 / 2,193; Sunday 3 / 5,532. These totals are confounded by a few large videos, unequal ages, and inconsistent date metadata. The top three labels span Wednesday/Monday/Thursday. There is **no defensible 'best posting day' finding** here.

## Repository/script audit and concrete writing changes

Verified topic/title mappings: DNA→dna10; simulation→sim10; garlic→gar10 family; Big Bang→bang10 family; MacBook→mbp10 family; cancer vaccine→onc10; splitting Earth with nuclear bombs→nuk10 family. The separate «Как работает ядерная бомба: три числа» is NOT the same topic as nuk10's Earth-splitting script. Humming→hum9 and Eiffel→eif9 are supported by publish metadata. pos10 remains unverified. Exact uploaded versions cannot be determined from title alone; do not equate a versioned release with a YouTube ID without confirmation.

The current repository tree has actual scripts for DNA, simulation, garlic, MacBook, oncology and nuk10. Current release listing contains mbp10, mbp10v2, bang10v3/v4. It does NOT expose the full scripts of the three period leaders or the brain/dead-star bottom examples. For humming, only publish text was available. Therefore winner-vs-loser **spoken-hook** comparison is incomplete: leaders can be compared on titles, not claimed transcript wording. Do not pretend those titles are the first spoken lines. See `script_comparison.md` for exact retrieved openings and their scope.

- DNA opens «Ты — программа. И я докажу это за минуту.» The literal overclaim precedes explicit DNA context. Test naming DNA immediately and clarifying the analogy; do not claim viewers proved this diagnosis.
- Simulation opens «Ты — код. Я это уже доказал. Вопрос: кто его запустил?» It assumes a previous episode and frames analogies as clues. Write a standalone first sentence with uncertainty; physical limits/quantum analogies are not observational evidence for a computer simulation.
- Garlic opens with a clear topic/question but quickly jumps garlic preparation→pressure→cholesterol→cold→cancer→oil. Choose the one promised question and sufficient evidence, not an anthology. Nine engaged views cannot evaluate its hook.
- Oncology opens with a clear personal-vaccine tension, then lists several different interventions and ends with stacked CTAs. Test a single patient's mechanism/evidence boundary and one return reason. Its four gained subs are encouraging, not proof that the existing CTA caused them.
- MacBook has relevant product context immediately and a situational joke, but only nine engaged views. Repository script is v1 (includes the subsequently removed twist phrase); never use that old phrase again or treat archived product claims as fact-checked evidence.

Next three comparable scripts: (1) draft three truthful context+hook openings, choose one understandable without prior videos; (2) one coherent causal explanation, define terms immediately, trim side claims not connecting words; (3) after the payoff use at most one topic-specific invitation. Preserve high-quality visuals and topic-specific art direction. Optional humor should sharpen the explanation, not interrupt it. Log the main hypothesis per video, measure equal-age stayed/AVD/APV and gained subs per 1k engaged as available, and avoid claiming three uploads constitute an A/B experiment.

## Read each metric correctly

| Metric | Meaning / unit | Correct use and traps |
|---|---|---|
| Views | Count of starts/replays for Shorts since 31 March 2025; no minimum viewing time | Reach, not unique people, not proof of attention. Do not compare old and new definitions unlabelled. |
| Engaged views | Times viewers stayed past initial seconds, excluding loops | Main attention-volume comparison. Not unique viewers, not an exact three-second count. |
| Stayed to watch | Percentage of relevant Shorts viewing decisions that stayed past initial seconds | Opening diagnostic; inspect the UI/export scope. Do not substitute thumbnail CTR or engaged views / all views. |
| Swiped away | Complement of stayed-to-watch when both describe the same partition | Derive 100 minus stayed only when the report confirms the same scope; mark as derived. |
| Shown in feed | Feed appearances, count | Distribution opportunity; distinct from thumbnail impressions. |
| Average view duration (AVD) | Time watched among engaged views; export may use hh:mm:ss or seconds | Preserve source format; normalize to seconds only after inspection. For Shorts, do NOT divide total channel watch time by raw starts. |
| Average percentage viewed (APV) | Average fraction of runtime watched by those who stayed, percent | Conditional on staying. Not completion rate. Can exceed 100% with rewatching; does not mean everyone completed. |
| Retention curve | Audience remaining/rewatching by video position | Needed to identify the moment of a drop. AVD/APV cannot identify which line lost viewers. |
| Watch time | Usually hours in Studio exports, verify header | Keep hours separate from AVD seconds; do not assume scopes reconcile automatically. |
| Likes, comments, shares | Interaction counts | Report counts plus per-1,000-engaged-view descriptive ratios when available. These are not unique-person probabilities. |
| Subscribers | May mean net change, gained, or lost | Preserve exact header semantics. Never relabel net subscribers as gained. |
| Thumbnail impressions / CTR | Registered thumbnail exposures / percentage yielding a view | Useful on eligible thumbnail surfaces; NOT the Shorts-feed stop rate. |
| Traffic source | Shorts feed, Search, Browse, External, etc. | Compare source mix; do not infer source from impressions alone. |

Illustrative arithmetic, NOT channel data: 40 seconds AVD on a 50-second video corresponds to 80% APV when definitions and scope match. A five-percentage-point rise is not a five-percent relative rise.

## Benchmarks: external context, not algorithm gates

YouTube publishes the signals, not a universal pass threshold or guaranteed viral formula. The existing local skill's 70% stayed-to-watch target is an internal aspiration, not a YouTube rule. Keep feed stop rate separate from APV.

A third-party study published 29 September 2026 measured 575 Shorts across 18 connected channels on 15 September 2026. Its 40–60-second band has only 53 Shorts: median APV 59.0%, p25 42.9%, p75 73.9%. These are a vendor's self-selected, mostly small-channel sample, not platform norms. Within that band, reaching the proposed 70% APV threshold did not separate the rate of reaching 1,000 views: 28.6% above vs 28.1% below. This is descriptive evidence against treating a threshold as a guarantee, not evidence retention is irrelevant. Do not adopt the vendor's causal interpretations without independent evidence.

Our main benchmark should be this channel's comparable Shorts at equal age and similar source mix. The current exported aggregate (68.54% stayed / 74.77% APV) is a useful provisional reference, but its unequal-age content mix prevents treating it as a matched experimental baseline. Separate 45–50 from 51–60 seconds only when samples allow it. Improvement hypotheses can be pre-registered as +3–5 percentage points stayed-to-watch versus a matched recent baseline, with no loss in AVD or subscriber conversion; this is a proposed experiment, not a promise.

## What the research supports

1. Diagnose a funnel: distribution opportunities -> stayed-to-watch -> depth/AVD/APV -> satisfaction and subscriptions. High APV with weak stop rate means the remaining viewers liked it, not that the opening worked for everyone.
2. YouTube explicitly names chose-to-view, AVD and APV, then likes and post-watch surveys. Topic interest, competition and seasonality also affect reach. No evidence here supports an exact weighted score or a guaranteed posting-day trick.
3. Do not rank only on lifetime views. A recent upload and an old one have different opportunity. Compare first 24 hours and first seven days, then separately lifetime.
4. A strong first sentence should identify the topic and tension honestly. A sensational premise that is false is not a successful hook even if it stops a swipe.
5. Without retention curves, claims such as 'viewers left at the jargon line' are hypotheses. Mark them as such and inspect timed retention before editing for that reason.
6. Comments/subscriptions are outcomes to measure, not proof of ranking weights. Try one relevant question or a specific reason to return, after delivering value. Do not stack four CTAs or fabricate controversy.
7. July 2025 clarified an existing mass-production/repetition restriction; AI is not categorically banned. Changing palette/topic alone does not guarantee originality. Distinct explanations, evidence, commentary and narrative substance matter. A recurring intro/outro is not automatically prohibited.
8. Reused-content monetization assessment is separate from copyright. Commentary can add value but does not grant permission to use third-party clips. Disclose realistic synthetic/altered scenes where required.

## Ledger contract

One row per video per weekly snapshot for a single canonical report window/scope. Store raw files unchanged under the dated folder and record SHA-256, export title, encoding, delimiter, decimal convention, date bounds, filters, units, report timezone and source filename in that snapshot's manifest. Exclude Total/Итого rows from per-video rows; reconcile them separately. Keep omitted rows and hidden/suppressed metrics explicit; do not treat them as zero.

Primary key: snapshot_date + video_id for the canonical report. If different date ranges/filters are needed in one snapshot, keep separate scoped ledgers, not duplicate unlabelled rows. Use YouTube video ID as identity, never title. Record title changes and release mapping confidence. Preserve publication timestamps in source zone, and convert explicit timestamps to Europe/Chisinau for reporting; date-only exports cannot establish a local posting hour/day precisely.

Append future snapshots idempotently: skip an identical key+content; preserve a correction as a versioned audit entry rather than silently overwriting history. Do not sum cumulative lifetime snapshots. Subtract cumulative counts only when scopes align; rate differences are percentage-point changes, not event-count deltas. Weekly-window counts may be summed only across nonoverlapping windows of identical scope.

Aggregate AVD using engaged-view weighting only with matching definitions/scopes. Weight APV by engaged views where compatible; label this as an aggregate of video-level rates, not unique-audience retention. Recompute CTR using impressions; weight stayed rate using the appropriate feed decision denominator, never a simple mean presented as a channel total. Missing denominator means no valid aggregate. Show medians separately as a typical-video benchmark.

## Weekly procedure

1. Audit all supplied files before interpretation. Confirm the actual table/series/totals exports from their headers and rows; do not infer type from file size. If files are missing, report the blocker and request materialization, not invented findings.
2. Archive originals and metadata locally. Compare actual date windows, total rows, duplicates, scopes and units. Parse localized decimal commas, BOM and durations explicitly.
3. Build the canonical per-video ledger and a separate traffic-source breakdown if available. Join by video ID. Match releases using verified titles/IDs and publication/version evidence.
4. Compare equal-age cohorts (24h, 7d; lifetime separately). Rank attention volume, stop rate, AVD/APV and subscriber conversion separately. Report top/bottom three with raw denominators; avoid a hidden composite quality score. Low exposure is not proof of poor scripting.
5. Code scripts without peeking at rankings where feasible: exact opening line, topic, question/contradiction/scene/utility hook, stakes, jargon, number density, story progression, CTA, length and publication day. Then compare groups. Small samples and topic/day confounding prevent causal conclusions.
6. Align retention dips/spikes with timed transcript, footage, captions and audio. A spike can be replay/confusion rather than delight. Label each statement Observed / Hypothesis / Test.
7. Choose one primary creative change for the next comparable set of videos; write the predicted metric and guardrails before publishing. Hold other decisions as stable as practical. Consecutive uploads are not randomized A/B tests.
8. Report what changed, whether equal-age metrics improved, uncertainty, and one next action. Keep an experiment log. Update reusable rules only after repeated evidence, except explicit user requirements and verified policy requirements.
9. Preserve raw analytics locally. External sharing requires explicit owner permission for that destination/content. The parent reports that GitHub storage is now approved. This executor has no available CloudAgent repository-write tool (confirmed discovery), and the source-control skill requires repository-content changes through that workflow, not shell git/API writes. Thus no remote commit/push was performed. Parent must use its authorized repository-writing workflow. The local folder is ready; no commit link exists.

## Ask for these next

- Screenshot of Studio report title, date range, filters, report timezone, duplicated audience-column labels and publication metadata; the three CSVs are now received and archived.
- Advanced Mode Content=Shorts by video: video ID, title, publication date, duration, views, engaged views, AVD, APV, watch time, likes, comments, shares, subscribers gained and lost, impressions and CTR where available.
- Per-video shown-in-feed and stayed-to-watch/swiped-away cards, as exports if available or screenshots with date ranges. Do not promise every metric is CSV-exportable.
- Per-video retention graphs for leading/lagging videos, with first seconds and full curve, and exact published versions/transcripts.
- Traffic-source breakdown per video; first 24h and first seven-day comparisons, plus an identical weekly window. Audience geography and 'when your viewers are on YouTube' only if testing scheduling, not to explain historical weekdays without evidence.

## Sources checked this turn

Official definitions and historical change:
- https://support.google.com/youtube/answer/12220281?hl=en
- https://support.google.com/youtube/answer/10059070?hl=en
- https://support.google.com/youtube/thread/333869549/a-change-to-how-we-count-views-on-shorts?hl=en (26 March 2025)

Official discovery and policies:
- https://support.google.com/youtube/answer/11914225?hl=en&co=YOUTUBE._YTVideoType%3Dshorts
- https://support.google.com/youtube/answer/1311392?hl=en (15 July 2025 update; live policy text may evolve)
- https://support.google.com/youtube/thread/356734251/response-to-creator-questions-about-ypp-policies-july-2025?hl=en-GB
- https://support.google.com/youtube/answer/3399767 (normal subscribe/like/comment requests allowed; artificial engagement prohibited)

Third-party benchmark, explicitly limited sample:
- https://shortlens.app/research/average-view-percentage-by-length (29 September 2026)

Official live definitions page also carries an August 24, 2026 counting update across formats. For this Shorts analysis the relevant historical break remains March 31, 2025; always retain source definitions and report date rather than assuming all exports use a timeless metric.
