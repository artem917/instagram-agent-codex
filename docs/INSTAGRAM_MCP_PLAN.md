# Instagram MCP preparation — research and proposed contract

Checked 2026-10-12. V0 implements **no Instagram connection, server or tools**.
The plugin's mcp.json contains zero servers. This document proposes a custom
MCP adapter over Meta's official HTTPS API; an official Meta MCP endpoint was
not established by the sources inspected. No public MCP URL is invented.

## Established API requirements

Meta's official Postman collection describes Instagram Login for professional
Business/Creator accounts, without a linked Facebook Page. Its publishing
permission is instagram_business_content_publish; profile/basic access uses
instagram_business_basic. Comments/messages are separate scopes and are
outside the proposed minimum. The older business_* scope names were replaced
in 2025. Ads/tagging aren't supplied by this API setup.
[Meta collection](https://www.postman.com/meta/instagram/folder/6raa77c/instagram-api-with-instagram-login),
[current collection permissions](https://www.postman.com/meta/instagram/folder/1z5vxzu/instagram-api-with-instagram-login).

The official Facebook Login collection separately documents media containers,
status polling and media_publish. Those samples demonstrate the publishing
mechanism but do **not** establish the exact Instagram Login token/endpoint
behavior. Do not reuse Page tokens or require Facebook linking just because
that separate flow does. Minimum MVP is one approved image/caption; broader
Reels/carousel/Stories support needs fresh format/account-specific verification.
[Meta publishing samples](https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api?entity=request-23987686-ab559ffb-8e2c-4b0a-b43a-5737b6d2f672).

## OAuth, own tests and third-party accounts

Plan: register the appropriate Meta app, use Instagram's user consent/code
flow with a registered redirect URI, perform exchanges only in the backend,
and store credentials outside model context/logs. Use state/nonce, exact
redirect matching, expiry from provider responses, verified granted scopes,
revocation handling and least privilege. Never collect an Instagram password.
MCP client authorization and Meta account authorization are separate boundaries.

Meta's collection says testers need app roles, required permission grants and
access to the professional account. This is not arbitrary third-party access.
An owner-only test MVP cannot be advertised as available to clients. Expected
external-account release gates are App Review/Advanced Access for required
permissions and any Business Verification demanded by the app dashboard.
**Current exact access-level/verification requirements remain UNVERIFIED**:
the corresponding Meta developer pages returned unavailable/login-only content
in this research environment. They must be read in an authorized dashboard
before enabling external accounts; no account or review was created here.
[Meta tester requirements](https://www.postman.com/meta/instagram/documentation/6yqw8pt/instagram-api?entity=request-23987686-26e7999c-fc7e-44c8-8f71-ab2de8d35c32),
[access-level reference](https://developers.facebook.com/docs/development/release/access-levels/),
[app review](https://developers.facebook.com/docs/app-review/).

Do not treat paid Meta Verified badges as developer Business Verification.
Token lifetime/refresh details, current API version, user-profile fields,
publishing quota and media transport/format limits are deployment gates, not
facts verified by this offline plugin. Query the provider's current permissions
and quota where supported; don't hardcode an assumed 60-day lifetime. Meta must
be able to obtain media if URL-based publishing is selected; localhost files
are not publicly reachable media. Confirm the actual supported upload method.

## Minimal proposed interface

| Tool | Behavior | Approval and boundary |
| --- | --- | --- |
| instagram_connect | Begin account consent; return a browser handoff/connection status, never tokens. | Explicit user connect request; trustworthy OAuth UI completes consent. |
| instagram_status | Account type, scopes, expiry/health and blocked reasons. | Read-only, scoped to the requesting user/account. |
| instagram_profile | Minimal authorized profile fields. | Read-only; no arbitrary handle lookup or cross-account access. |
| instagram_draft_create | Store an immutable draft/version from user-provided text/media. | Explicit request to save; local write only. |
| instagram_preview | Show exact account, caption/media, validation and payload hash. | Read-only/offline preview; no hidden upload/container creation. |
| instagram_publish | Create/upload a container and publish the approved draft. | Fresh explicit confirmation before **the first external write**, bound to exact account/draft/payload. |

The machine-readable proposal is [instagram-mcp-contract.json](instagram-mcp-contract.json).
It is not registered and not implemented. No tool schema enables a live action.

For writes, the server must require a one-time approval receipt issued by a
trusted user interaction, bound to user, connection/account, draft version,
media hashes, complete payload, expiry and operation. An LLM-provided
`confirmed:true` or echoed "yes" cannot create that receipt. Account consent
is not blanket permission to publish. Changing any payload component invalidates
approval. Apply a durable idempotency journal and reconcile ambiguous timeouts:
UNKNOWN is not "failed/not published", and a retry must not create a second post.
Do not configure schedulers, outreach, comments or DMs in this MVP.

Proposed states: DISCONNECTED → OAUTH_PENDING → CONNECTED_READ → DRAFT →
PREVIEWED → APPROVED → PUBLISHING → PUBLISHED or UNKNOWN/FAILED. Authentication
revocation, missing identity/scopes, changed content and expired approvals stop
writes. Draft updates require a new version and a new preview/approval.

## Cost estimate without a paid intermediary

- V0/adapter development on an existing computer: $0 incremental hosting;
  current Codex/model usage still follows the user's account plan.
- A small owner-only pilot may fit free hosting/storage tiers; estimate
  $0–$5/month for low traffic, excluding domain, media bandwidth and overages.
  This is an engineering estimate, not a deploy-ready quote. Cloudflare has
  Free/Paid tiers and a $5 paid subscription example; no service is provisioned.
  [Official pricing](https://developers.cloudflare.com/workers/platform/pricing/).
- No Instagram per-request fee was established in the accessible Meta sources.
  Treat any direct fee as UNKNOWN, not a guaranteed free API. No ManyChat/paid
  middleware subscription is required by this proposed architecture.
- Budget roughly 40–80 engineering hours for a narrow authenticated owner-only
  adapter, consent/preview/idempotency and tests. This is an estimate; App Review,
  eligibility/legal review and maintenance are separate and have no verified ETA.

## Russian developer: confirmed constraints versus unknown eligibility

1. Instagram access in Russia has a documented blocking history; Meta's own
   2022 statement also records the Russian Facebook block. Reliable access to
   consent/developer pages and provider-fetchable media is an operational gate.
   It is not proof that every graph.instagram.com endpoint is blocked on every
   route. No ISP/location or logged-in account was tested here.
   [Meta statement](https://about.fb.com/news/2022/02/metas-ongoing-efforts-regarding-russias-invasion-of-ukraine/amp/),
   [UN report recording Instagram/Facebook blocking](https://documents.un.org/api/symbol/access?l=ru&s=a%2F77%2F220&t=pdf).
2. Meta states Russian advertisers cannot create/run ads; that is an ads
   restriction. Do not infer an organic publishing API ban solely from it.
   [Meta announcement](https://about.fb.com/news/2022/02/metas-ongoing-efforts-regarding-russias-invasion-of-ukraine/amp/).
3. Russian advertising-law amendments under 72-ФЗ are a commercial-content
   legal gate for prohibited/restricted resources. Classification of a specific
   post or developer activity needs legal review; no general ban on writing
   an offline drafting plugin is asserted.
   The prohibition took effect 1 September 2025.
   [Advertising restriction](https://www.consultant.ru/document/cons_doc_LAW_502592/b004fed0b70d0f223e4a81f8ad6cd92af90a7e3b/),
   [effective date](https://www.consultant.ru/document/cons_doc_LAW_502592/30b3f8c55f65557c253227a65b908cc075ce114a/).
4. Russia is absent from OpenAI's current API supported-country list; the
   policy concerns accessing/offering API services from supported locations.
   It does not prove a Russian citizen in another supported location is
   ineligible. Directory publisher verification is a separate gate. V0 needs
   no new OpenAI API key or public-directory approval.
   [OpenAI country policy](https://developers.openai.com/api/docs/supported-countries),
   [publisher/submission requirements](https://developers.openai.com/plugins/deploy/submission).
5. Russian Meta app registration, phone/identity/business verification, required
   access levels and review acceptance are **UNKNOWN for this owner**. Neither
   categorical availability nor categorical nationality-based refusal was
   established. Hosting/billing/legal-entity eligibility is also untested.
   Do not substitute somebody else's identity, a paid badge or a proxy assumption
   for verification. A private owner eligibility check is required before OAuth.

## Release boundary

This is a local/repo plugin release, not OpenAI moderation. The official
submission guide currently says an MCP cannot be added to an already submitted
skills-only plugin via the normal update path. Therefore keep V0 local and
settle the real MCP/ownership design **before** the first future public submission.
[Submission rule](https://developers.openai.com/plugins/deploy/submission).
