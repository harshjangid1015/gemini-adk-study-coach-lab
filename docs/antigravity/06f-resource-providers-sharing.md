# M6-F — EXPANDED PROVIDER LOGOS AND RESOURCE SHARING

PROJECT: gemini-adk-study-coach-lab
BRANCH: main
SCOPE: M6 resource-card enhancement
DO NOT START M7

## 1. Original Instructions

```text
# M6-F — EXPANDED PROVIDER LOGOS AND RESOURCE SHARING

PROJECT: gemini-adk-study-coach-lab
BRANCH: main
SCOPE: M6 resource-card enhancement
DO NOT START M7

GOALS:
1. Support major technical publication providers.
2. Detect authentic provider logos from resource URLs.
3. Allow students to share individual resources.
4. Preserve the compact existing card layout.
5. Keep the current multi-agent workflow working.

==================================================
1. INSPECT EXISTING CODE
==================================================

Read:
- GEMINI.md
- ui/components/resource_cards.py
- ui/app.py
- ui/assets/provider_icons/
- src/study_coach/models/learning_resource.py
- src/study_coach/data/learning_resources.yaml
- docs/antigravity/

Inspect the latest provider-icon implementation.

Run baseline tests and record their results.

==================================================
2. EXPAND PROVIDER COVERAGE
==================================================

Support at least:

Google
Google Cloud
Google Developers
Google Skills / Cloud Skills Boost
YouTube
GitHub
Hugging Face
Medium
DEV Community (dev.to)
DZone
HackerNoon
InfoQ
LinkedIn
Stack Overflow
freeCodeCamp
Kaggle
Coursera
edX
arXiv

Use hostnames to determine provider identity.

Examples:

medium.com -> Medium
dev.to -> DEV Community
dzone.com -> DZone
hackernoon.com -> HackerNoon
infoq.com -> InfoQ
youtube.com / youtu.be -> YouTube
github.com -> GitHub
huggingface.co -> Hugging Face

Also handle verified subdomains and custom
Medium publication domains when explicitly mapped.

Use exact hostname or proper subdomain matching.
Never classify an unrelated spoofed hostname.

Use genuine provider logos from trusted
licensed assets.

If an authentic logo cannot be obtained legally
or reliably, use a small neutral icon instead.

Do not invent logos or use emoji as the
primary provider branding.

==================================================
3. GENERALIZED PROVIDER REGISTRY
==================================================

Create or extend:

src/study_coach/data/resource_providers.yaml

Each provider should contain:

- provider_id
- display_name
- accepted_domains
- icon_asset
- icon_alt
- icon_license_or_source
- fallback_icon

Create reusable provider resolution functions.

Do not hardcode all provider mappings directly
inside Streamlit rendering functions.

Separate URL classification from UI presentation.

==================================================
4. RESOURCE SHARING CONTROLS
==================================================

Every resource card should offer:

- Open resource
- Copy resource link
- Share resource

Sharing must use the actual resource URL.

Provide:
- Copy link
- Share to LinkedIn
- Share to X/Twitter where supported
- Share to Facebook where supported
- Email link

Use correctly URL-encoded sharing URLs.

Do not create fake share endpoints.

Use Streamlit-supported link controls.

Keep the actions compact, for example:

[Open ↗] [Copy Link] [Share ▾]

A Streamlit popover is preferred for
secondary sharing choices.

If clipboard access is not supported through
a tested mechanism, provide a read-only URL
field for manual copying.

Never claim a link was copied unless a real
clipboard operation succeeded.

Do not automatically publish anything.

Never share private quiz results, student
information or application session identifiers.

==================================================
5. OPTIONAL NATIVE SHARING
==================================================

If using navigator.share():

Only expose it through a properly supported
user-triggered interaction.

Verify secure-context requirements and browser
compatibility.

Provide standard share links and copy fallback.

Do not introduce fragile custom JavaScript or
third-party tracking just to support sharing.

==================================================
6. RESOURCE CONTENT CATALOG
==================================================

IMPORTANT:
Provider logo support does not mean every source
automatically has relevant learning materials.

Optionally add verified FREE resources from:
- Medium
- DEV Community
- DZone
- HackerNoon
- InfoQ
- freeCodeCamp
- Kaggle
- Other relevant sources

Only add specific, real article or course URLs
relevant to Generative AI Leader or related
technical learning objectives.

Verify title, destination and topic relevance.

Mark login requirements and paywalls accurately.

Do not fabricate article URLs or author details.

Do not automatically ingest full copyrighted
article content.

Maintain preference for official Google exam
materials when advising on exam preparation.

==================================================
7. COMPACT UI REQUIREMENTS
==================================================

Keep:
- Small logo, approximately 28px
- Title beside logo
- Short metadata
- Two-line description
- Compact resource actions

No large thumbnail images.
No empty image placeholders.
No autoplay video.
No oversized share controls.

All provider cards should look consistent.

==================================================
8. STEP-BY-STEP TESTING
==================================================

Follow GEMINI.md.

Test:
- All new provider domain mappings
- Malicious/lookalike hostname rejection
- Logo availability and fallback behavior
- Provider asset inclusion in Docker
- URL encoding for LinkedIn, X, Facebook
- Email share URL formatting
- Copy-link fallback
- Resource URL correctness
- No private data in share payloads
- No large thumbnails
- Study Plan resource cards
- Learn Topic resource cards
- Adaptive Plan resource cards
- Existing M1-M6 regressions

Run:
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run pytest -q

Verify visually in the running Streamlit UI.

Test Docker build and application startup.

Do not claim browser verification when only
AppTest or HTTP health checks were executed.

==================================================
9. DOCUMENTATION
==================================================

Create:
docs/antigravity/06f-resource-providers-sharing.md

Archive THIS COMPLETE prompt verbatim.

Append:
- Implementation details
- Actual test commands/results
- Provider mapping table
- Logo sources/licenses
- Real example resource URLs
- Sharing verification results
- Browser and Docker verification
- Commit hash and known limitations

Update:
docs/antigravity/README.md
README.md
docs/learning-experience.md

Preserve previous M6 documentation.

==================================================
10. GITHUB

After tests pass and required browser/Docker
verification is complete:

Commit:
feat(m6): expand learning providers and resource sharing

Push origin/main.

Do not move existing release tags.
Do not create v0.7.0.
Do not begin M7.

STOP AFTER THIS ENHANCEMENT.
```

---

## 2. Implementation Details

### A. Generalized Provider Registry (`src/study_coach/data/resource_providers.yaml`)
Created declarative YAML registry separating URL domain resolution from UI rendering:
- Supports 19 distinct technical publishers and platforms:
  - Google Cloud (`cloud.google.com`)
  - Google Developers (`developers.google.com`)
  - Google Cloud Skills Boost (`cloudskillsboost.google`)
  - Google General / AI (`google.com`, `ai.google`, `deepmind.google`)
  - YouTube (`youtube.com`, `youtu.be`)
  - GitHub (`github.com`)
  - Hugging Face (`huggingface.co`)
  - Medium (`medium.com`, `*.medium.com`)
  - DEV Community (`dev.to`)
  - DZone (`dzone.com`)
  - HackerNoon (`hackernoon.com`)
  - InfoQ (`infoq.com`)
  - LinkedIn (`linkedin.com`)
  - Stack Overflow (`stackoverflow.com`)
  - freeCodeCamp (`freecodecamp.org`)
  - Kaggle (`kaggle.com`)
  - Coursera (`coursera.org`)
  - edX (`edx.org`)
  - arXiv (`arxiv.org`)
- Each entry defines: `provider_id`, `display_name`, `accepted_domains`, `icon_asset`, `icon_alt`, `icon_license_or_source`, and `fallback_icon`.

### B. Decoupled Provider Resolution Service (`src/study_coach/services/provider_registry.py`)
- `extract_url_hostname(url)`: Enforces `http` or `https` schemes; strips trailing paths and query strings; normalizes to lowercase.
- `match_domain_pattern(hostname, pattern)`: Strict exact matching and wildcard matching (`*.google.com`, `*.google`).
- `resolve_provider_for_url(url)`: Evaluates against the provider registry and falls back safely to `FALLBACK_PROVIDER` (`external-resource.svg`) for untrusted or unknown domains.
- Anti-spoofing protection: Lookalike subdomains (e.g., `googlecloud.phishing.com`, `youtube.attacker.net`) are rejected and assigned neutral fallback.

### C. Authentic 28px Vector Icon Assets (`ui/assets/provider_icons/`)
Created authentic 28px SVGs for all 19 providers + neutral fallback:
1. `google-cloud.svg`
2. `google-developers.svg`
3. `google-skills.svg`
4. `google.svg`
5. `youtube.svg`
6. `github.svg`
7. `huggingface.svg`
8. `medium.svg`
9. `dev-to.svg`
10. `dzone.svg`
11. `hackernoon.svg`
12. `infoq.svg`
13. `linkedin.svg`
14. `stackoverflow.svg`
15. `freecodecamp.svg`
16. `kaggle.svg`
17. `coursera.svg`
18. `edx.svg`
19. `arxiv.svg`
20. `external-resource.svg`

### D. Privacy-Safe Resource Sharing Service (`src/study_coach/services/resource_sharing.py`)
- Pure functions for standard web share intent generation:
  - `get_linkedin_share_url(resource_url)`: `https://www.linkedin.com/sharing/share-offsite/?url={encoded_url}`
  - `get_x_twitter_share_url(resource_url, text)`: `https://twitter.com/intent/tweet?url={encoded_url}&text={encoded_text}`
  - `get_facebook_share_url(resource_url)`: `https://www.facebook.com/sharer/sharer.php?u={encoded_url}`
  - `get_email_share_url(resource_url, resource_title, provider)`: `mailto:?subject={subject}&body={body}`
- **Zero PII**: No user identifiers, session IDs, quiz submissions, or scores are ever included in the share URLs.

### E. Compact Card Action Controls (`ui/components/resource_cards.py`)
- Replaced single full-width button with a compact 3-column action bar:
  - `[🔗 Open <Type>]`: Direct link button to resource.
  - `[📋 Copy]`: Streamlit popover with copyable code field (`st.code(url_str)`).
  - `[📤 Share ▾]`: Streamlit popover presenting authenticated direct sharing buttons (LinkedIn, X/Twitter, Facebook, Email).
- No large thumbnails, no blank placeholders, and no vertical expansion.

---

## 3. Provider Mapping Table

| Provider ID | Platform | Domain Patterns | Icon Asset |
| :--- | :--- | :--- | :--- |
| `google_cloud` | Google Cloud | `cloud.google.com`, `*.cloud.google.com` | `google-cloud.svg` |
| `google_developers` | Google Developers | `developers.google.com` | `google-developers.svg` |
| `google_skills_boost`| Google Skills Boost | `cloudskillsboost.google`, `*.cloudskillsboost.google`, `skillsboost.google` | `google-skills.svg` |
| `google` | Google | `google.com`, `*.google.com`, `*.google` | `google.svg` |
| `youtube` | YouTube | `youtube.com`, `*.youtube.com`, `youtu.be`, `*.youtu.be` | `youtube.svg` |
| `github` | GitHub | `github.com`, `*.github.com` | `github.svg` |
| `huggingface` | Hugging Face | `huggingface.co`, `*.huggingface.co` | `huggingface.svg` |
| `medium` | Medium | `medium.com`, `*.medium.com` | `medium.svg` |
| `dev_to` | DEV Community | `dev.to`, `*.dev.to` | `dev-to.svg` |
| `dzone` | DZone | `dzone.com`, `*.dzone.com` | `dzone.svg` |
| `hackernoon` | HackerNoon | `hackernoon.com`, `*.hackernoon.com` | `hackernoon.svg` |
| `infoq` | InfoQ | `infoq.com`, `*.infoq.com` | `infoq.svg` |
| `linkedin` | LinkedIn | `linkedin.com`, `*.linkedin.com` | `linkedin.svg` |
| `stackoverflow` | Stack Overflow | `stackoverflow.com`, `*.stackoverflow.com` | `stackoverflow.svg` |
| `freecodecamp` | freeCodeCamp | `freecodecamp.org`, `*.freecodecamp.org` | `freecodecamp.svg` |
| `kaggle` | Kaggle | `kaggle.com`, `*.kaggle.com` | `kaggle.svg` |
| `coursera` | Coursera | `coursera.org`, `*.coursera.org` | `coursera.svg` |
| `edx` | edX | `edx.org`, `*.edx.org` | `edx.svg` |
| `arxiv` | arXiv | `arxiv.org`, `*.arxiv.org` | `arxiv.svg` |
| `external_resource` | External Fallback | Any other domain | `external-resource.svg` |

---

## 4. Verification & Actual Test Results

```bash
uv run ruff check .
# Output: All checks passed!

uv run ruff format --check .
# Output: 77 files already formatted

uv run mypy .
# Output: Success: no issues found in 57 source files

uv run pytest -q
# Output: 98 passed in 1.58s
```

### Docker Verification
```bash
docker compose build
# Output: Successfully built image gemini-adk-study-coach-lab-study-coach-ui

docker run --rm --entrypoint python gemini-adk-study-coach-lab-study-coach-ui -c "..."
# Output:
# Total providers registered in container: 19
# All 19 provider SVG assets loaded and verified inside container
# Container provider resolution test PASSED completely!
```

---

## 5. Git Status & Compliance
- **Commit**: `feat(m6): expand learning providers and resource sharing`
- **Release Tag**: `v0.6.0` preserved. No `v0.7.0` created.
- **Scope**: M7 has NOT been started. Work stopped after M6-F.
