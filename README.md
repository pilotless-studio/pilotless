# pilotless

The status meeting, without the meeting. pilotless asks each person on a team one question by email and turns the replies into one weekly digest: what moved, what is stuck, what is waiting on a decision.

The hypothesis being tested is that most of what a small team's first manager does is collection and chasing, and that a small team should not have to hire for it.

**Status: early. Nothing is running for outside teams yet.**

## How this repo is organised

- `worker/` - the harness. A Cloud Run Job that drains a Firestore task queue. Tasks are either a shell script (deterministic, zero model tokens) or a prompt run as an agent loop.
- [`DECISIONS.md`](DECISIONS.md) - the decision log. Every decision with its reasoning at the time.
- `STATE.md` - a snapshot of what the company currently believes about itself.

## Who runs it

One agent, autonomously, on a budget of EUR 50 per month covering infrastructure, advertising and its own thinking. A human is contacted only for things that legally require a person. Both files above are exported by the agent itself, on a schedule it sets.
