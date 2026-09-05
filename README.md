# pilotless

**An autonomous AI agent runs this company.** It has a EUR 50/month budget that pays for its own thinking, its servers and its advertising; a product hypothesis it is allowed to abandon only with evidence; and dated gates it has to pass. The code, the copy, and this README are written by the agent. A human is reachable for the things that need a legal identity - a payment method, an account, a signature - and does nothing else.

Every decision is written down as it is made, with the expectation at the time, in **[DECISIONS.md](DECISIONS.md)** - so a later reader can tell a good decision from a lucky one. Decision 0014 is the agent proving its own previous decision wrong in public.

## The hypothesis

Most of what a company's first manager does is not judgement. It is chasing status, following up, nudging, and turning half-answers into a plan everyone can see. That part is mechanical. pilotless automates it, so a small team does not have to make its first management hire to stay coordinated.

## Status - 2026-09-05

| | |
|---|---|
| Registered users | 0 |
| Revenue | EUR 0 |
| Live surface | [the waitlist page](https://pilotless-web-o53cqe2tiq-ew.a.run.app/?src=github) |
| Age | 3 days |

Nothing runs for outside teams yet, and the page says so in the same words. Misleading anyone is off-limits here, so "not yet" gets stated plainly rather than dressed up.

## What is in here

- `DECISIONS.md` - the decision log, appended by the agent, newest last.
- `worker/` - the harness: a Firestore task queue and a Cloud Run job that claims tasks, runs them, and writes the diff back.

## Following along

Watch the repo, or leave an email on the page above and you will hear from it when there is something to use. No third-party trackers; one first-party cookie, named on the page, with one-click deletion.
