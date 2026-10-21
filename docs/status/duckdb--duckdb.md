---
title: "duckdb/duckdb weekly status: stalled PRs and unowned issues"
description: "duckdb/duckdb this week: 757 commits, 5 stalled pull requests and 5 unowned issues, from public GitHub activity. Unofficial weekly status report."
---

[All status pages](./) · [Unowned issues across all projects](unowned.html) · [How to write a weekly status report from GitHub](../weekly-status-report.html)

# Weekly status: duckdb/duckdb

_2026-10-14 to 2026-10-20 (7 full days, UTC). Unofficial: generated from this repository's public GitHub activity by [pilotless status](https://github.com/pilotless-studio/pilotless). Not affiliated with the project, and no information here that GitHub does not publish._

**757 commits** to `main` by 50 people, **275 pull requests merged**, **100 open pull requests**, **45 open issues** on this page of results.

### Stalled pull requests
Open, and untouched for seven days or more:

- [#25897](https://github.com/duckdb/duckdb/pull/25897) Add regression test for QUALIFY above a filtered aggregate subquery - last touched 30 days ago
- [#25349](https://github.com/duckdb/duckdb/pull/25349) Add operator-owned sub-plans to EXPLAIN - last touched 30 days ago
- [#24942](https://github.com/duckdb/duckdb/pull/24942) Support multi-index scans with full filter coverage - last touched 29 days ago
- [#26060](https://github.com/duckdb/duckdb/pull/26060) Fix CSV heap OOB read from over-value that shares a longer value's prefix with the null st - last touched 27 days ago
- [#26087](https://github.com/duckdb/duckdb/pull/26087) Parquet: decompress pages directly from the prefetch buffer - last touched 27 days ago

### Issues nobody has picked up
Open, unassigned, and with no replies yet:

- [#27601](https://github.com/duckdb/duckdb/issues/27601) Parquet reader reads whole row groups when filtering on a small field of a large struct - opened 0 days ago
- [#27591](https://github.com/duckdb/duckdb/issues/27591) Window DISTINCT aggregate livelocks (100 % CPU, never returns) when a build task hits the  - opened 0 days ago
- [#27586](https://github.com/duckdb/duckdb/issues/27586) ST_Intersects/ST_Contains/ST_Within lose row-group pruning with an IN or OR filter on 2.0 - opened 0 days ago
- [#27583](https://github.com/duckdb/duckdb/issues/27583) append_metadata.cmake silently generates a truncated extension footer with CMake 3.17.5 - opened 0 days ago
- [#27573](https://github.com/duckdb/duckdb/issues/27573) When reading an xlsx file using duckdb read_xlsx, a text value of 0.07 is returned as 7.00 - opened 0 days ago

---

The two lists above are what a status meeting is usually for. Nobody had to attend one to produce this page.

If you maintain duckdb/duckdb and would rather this page did not exist, [open an issue](https://github.com/pilotless-studio/pilotless/issues/new) and it will be deleted - no argument, no reply needed beyond the repository name.

**Want this for your own repositories?** [Install the pilotless GitHub App](https://pilotless-web-o53cqe2tiq-ew.a.run.app/install?src=directory.a2) — one click, then a pinned weekly status digest in each selected repo. Prefer CI-only? The [status-action](https://github.com/pilotless-studio/pilotless#status-action) is still two lines of YAML with no account and nothing leaving GitHub.
