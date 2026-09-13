# Hosted deployment and operations

The new Railway project is `agentic-portfolio`. It contains two backend containers and private-network PostgreSQL. Never link these commands to a pre-existing production project.

## Service controls

On 13 September 2026, Railway's API explicitly rejected the old `railway.json` format as deprecated. We removed that ignored configuration and applied service controls through the documented GraphQL API. See [Railway's migration notice](https://docs.railway.com/infrastructure-as-code#migrating-from-config-as-code).

`deploy/railway-controls.json` is an application-owned settings document, **not** Railway IaC and not automatically applied by deployments. The helper checks the exact linked project, environment, service ID and service name. It never creates/deletes resources, changes account plans, manages other services or writes credentials. It reads the existing Railway CLI login in memory.

From this repository root, after `railway link` selects the correct new service:

```sh
node tools/configure_railway.mjs --project PROJECT_ID --environment ENVIRONMENT_ID --service SERVICE_ID
node tools/configure_railway.mjs --project PROJECT_ID --environment ENVIRONMENT_ID --service SERVICE_ID --apply
railway up --detach --json --project PROJECT_ID --environment ENVIRONMENT_ID --service SERVICE_ID
```

Replace the uppercase ID placeholders with verified IDs from `railway status --json`. The first helper call previews only. Settings apply to newly deployed containers; verify the **active** deployment afterward, not just the saved setting. Current controls: one replica, one vCPU, 1 GB RAM, serverless sleeping, `/ready`, 120-second readiness deadline, three on-failure restarts. PostgreSQL is separately capped at one vCPU/1 GB and remains awake.

Railway may evolve its API or CLI authentication format; a rejected request is a deployment blocker, not permission to bypass the control. Future adoption of Railway IaC must use a named partial for each independent repository, with an explicitly reviewed plan that deletes nothing.

## Provider keys and frontends

Provider keys belong only in the corresponding Railway backend variables. Vercel has no model keys or database credentials. The only production frontend configuration is the non-secret `VITE_LIVE_AVAILABLE` flag when live mode is released. The exact `ALLOWED_ORIGIN` must match the public frontend URL. Do not send API requests from unapproved preview origins.

Each frontend has a same-origin `/api/:path*` rewrite to its own Railway backend. Replay mode loads only static files under `/replays/`; it is usable with the API blocked. Direct CLI deployment is supported from `web/`:

```sh
npx vercel --prod --yes --scope YOUR_VERCEL_TEAM
```

GitHub push-to-deploy integration is not configured: the Vercel GitHub app still lacks access to these private repositories. Direct authenticated CLI deployments work. Do not grant access to unrelated repositories to resolve this.

## Invitations and live disable

```sh
uv run python tools/hosted_invite.py invite --project PROJECT_ID --environment ENVIRONMENT_ID --service SERVICE_ID
uv run python tools/hosted_invite.py revoke --id INVITATION_ID --project PROJECT_ID --environment ENVIRONMENT_ID --service SERVICE_ID
```

The bearer token is saved to ignored, mode-0600 `.local/hosted-invite.txt`, with non-secret metadata in `.local/hosted-invite.json`. Share the token privately, not in an issue, URL or replay. The default invitation permits five starts over seven days. Revocation invalidates existing sessions as well as new token exchanges. The helper uses SSH and the application's own invite/revoke command; no public database endpoint is needed.

Disable new model execution:

```sh
railway variable set LIVE_ENABLED=false --skip-deploys --project PROJECT_ID --environment ENVIRONMENT_ID --service SERVICE_ID
railway service redeploy --yes --project PROJECT_ID --environment ENVIRONMENT_ID --service SERVICE_ID
```

Check `/api/ready` once after redeployment; it must report `liveEnabled:false`. An already-started model request may still finish and be billed. Cancellation separately revokes a run's execution lease. Re-enable with `LIVE_ENABLED=true` only when provider credit, application ledger and release gates allow it.

## Cost and data

The shared plan target is $10/month **additional** cost, of which $5 is allocated to model usage ($2.50 per provider). Initial observed idle memory was approximately 65–150 MB for PostgreSQL, 8 MB for commerce, and 73 MB for artwork; PostgreSQL volume use was about 0.9 GB. These are brief startup observations, not a monthly bill forecast. Light, mostly idle traffic appears compatible with the target, but CPU, egress, scans and browser/model workloads vary. The one-GB caps are ceilings, not reserved allocations or a $10 account-wide hard limit.

The existing Railway Pro and Vercel Hobby plans were reused without upgrades. No provider credit was purchased. Do not set a shared workspace hard spending cap: it could shut down unrelated production applications. Review this project's usage separately. Public replay traffic makes no model or backend calls; no uptime pings or keep-alive automation was added.

Seven-day cleanup is opportunistic on successful database transactions; idle/sleeping services do **not** guarantee wall-clock deletion at exactly seven days. Expired data is inaccessible immediately through authorization checks, then pruned on subsequent activity. Do not upload confidential artwork to this demonstration. PostgreSQL stores bounded decoded previews/measurements, not a production object-store archive.

If observed infrastructure cost exceeds the target, disable live execution and stop only the portfolio backend deployments. Static replays remain available. Keep database recovery/retention consequences explicit before deleting any resource.
