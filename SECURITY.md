# Security policy

ResQPulse AI is a research prototype. **It is not certified for real emergency dispatch**: every alert must be reviewed
by a person, and it should not be deployed on a public network without authentication.

## Known limitations
- The API has no authentication and allows all CORS origins; run it on a trusted machine or private network only.
- Alerts are stored in memory and in local JSONL logs, unencrypted.
- The HTTPS option in the docs uses a self-signed certificate for local demos only.

## Reporting a vulnerability
Please use GitHub's **Report a vulnerability** (Security tab → Advisories) to report privately. Do not open a public
issue for security problems. We aim to respond within a week.
