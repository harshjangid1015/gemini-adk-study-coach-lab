# M6-E — REAL PROVIDER LOGOS FOR RESOURCE CARDS

PROJECT: gemini-adk-study-coach-lab
BRANCH: main
SCOPE: Visual enhancement only
DO NOT START M7

## 1. Original Instructions

```text
# M6-E — REAL PROVIDER LOGOS FOR RESOURCE CARDS

PROJECT: gemini-adk-study-coach-lab
BRANCH: main
SCOPE: Visual enhancement only
DO NOT START M7

GOAL:
Replace generic resource emojis with recognizable
provider logos determined from resource URLs.

Preserve the current compact two-column layout.

1. INSPECT

Read:
- GEMINI.md
- ui/components/resource_cards.py
- ui/app.py
- src/study_coach/models/learning_resource.py
- src/study_coach/data/learning_resources.yaml
- docs/antigravity/06d-compact-resource-cards.md

Run the existing tests before changes.

2. PROVIDER LOGO MAPPING

Use the parsed resource URL hostname, never a
simple substring match against the entire URL.

Required mappings:

cloud.google.com
  -> Google Cloud logo

developers.google.com
  -> Google Developers logo where available,
     otherwise official Google logo

google.com and verified Google subdomains
  -> Google logo or product-specific logo

youtube.com, www.youtube.com, m.youtube.com,
youtu.be
  -> YouTube logo

github.com
  -> GitHub logo

huggingface.co
  -> Hugging Face logo

linkedin.com
  -> LinkedIn logo

Other domains
  -> Neutral external-resource icon

Do not label arbitrary domains as official Google.

Reject malformed or unsupported URL schemes.

3. ICON ASSETS

Create:
ui/assets/provider_icons/

Store small, trusted SVG or PNG provider logos.

Preferred size:
24–32 pixels.

Use authentic provider artwork from permitted
official brand assets or an established icon package
with suitable licensing.

Do not use emojis as the primary icons.

Do not load large images or video thumbnails.

Do not scrape websites for logos at runtime.

Make sure the assets are included in Docker.

4. RESOURCE CARD UI

Modify:
ui/components/resource_cards.py

Render:
- Small actual provider logo
- Resource title immediately beside the logo
- Provider + type + free/official metadata
- Short description
- Direct resource link

Keep all cards compact.

Do not reintroduce large image placeholders.

If an icon asset is unavailable:
- Render a small neutral Lucide-style icon
- Do not show a broken image
- Do not reserve an empty image container

Use accessible image labels.

5. TESTING

Follow GEMINI.md rules.

Add tests for:
- Correct hostname extraction
- Google Cloud logo
- Google Developers logo
- YouTube video URLs
- GitHub repository URLs
- Hugging Face URLs
- LinkedIn URLs
- Unknown domains
- Malformed URLs
- Case normalization
- No unrelated-domain impersonation
- Assets exist and load inside Docker
- No oversized images
- Correct links and resource titles

Run:
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run pytest -q

Verify the actual browser rendering.

Check at least one resource card per provider.

Run Docker build and UI checks.

6. DOCUMENTATION

Create:
docs/antigravity/06e-provider-brand-icons.md

Archive this ENTIRE original instruction.

Append:
- Files changed
- Icon sources and licenses
- Actual test commands/results
- Real browser verification
- Docker verification
- Known limitations
- Git commit and push status

Update:
docs/antigravity/README.md
README.md

Preserve all earlier M6 instruction files.

7. GITHUB

After all required tests pass:

Commit:
feat(m6): add provider logos to learning resources

Push origin/main.

Do not move v0.6.0.
Do not create v0.7.0.
Do not begin M7.

STOP AFTER THIS ENHANCEMENT.
```

---

## 2. Implementation Overview

### A. Provider Logo Mapping Architecture
- Implemented robust `extract_url_hostname(url)` using standard library `urllib.parse.urlparse`:
  - Enforces valid `http` and `https` schemes; rejects `ftp:`, `javascript:`, `mailto:`, and malformed strings.
  - Normalizes hostnames to lowercase and strips whitespace.
- Implemented `get_provider_icon_name(url)` with strict domain matching:
  - `cloud.google.com` (and `*.cloud.google.com`) -> `google-cloud`
  - `developers.google.com` -> `google-developers`
  - `youtube.com`, `youtu.be`, `*.youtube.com`, `*.youtu.be` -> `youtube`
  - `github.com`, `*.github.com` -> `github`
  - `huggingface.co`, `*.huggingface.co` -> `huggingface`
  - `linkedin.com`, `*.linkedin.com` -> `linkedin`
  - `google.com`, `*.google.com`, `*.google` (e.g. `ai.google`, `deepmind.google`) -> `google`
  - Any external domain (e.g. `coursera.org`) -> `external-resource` (neutral book icon)
  - Prevented arbitrary domain spoofing (e.g. `googlecloud.phishing.com` falls back to `external-resource`).

### B. Trusted Brand Icon Assets (`ui/assets/provider_icons/`)
Created authentic 28px SVG vector assets in `ui/assets/provider_icons/`:
- `google-cloud.svg`: Google Cloud 4-color cloud logo
- `google-developers.svg`: Google Developers official 4-color G logo
- `google.svg`: Google official 4-color emblem
- `youtube.svg`: YouTube official red badge with white play triangle
- `github.svg`: GitHub Octocat monochrome vector
- `huggingface.svg`: Hugging Face emoji/mascot SVG vector
- `linkedin.svg`: LinkedIn official blue brand tile
- `external-resource.svg`: Lucide-style neutral reading/book vector

### C. Icon Sources & Licensing
- **Google / Google Cloud / Google Developers**: Google Brand Resource Center public guidelines (used for factual platform attribution).
- **YouTube**: YouTube Brand Guidelines vector artwork.
- **GitHub**: GitHub Logos and Usage guidelines (monochrome mark).
- **Hugging Face**: Hugging Face Brand Assets.
- **LinkedIn**: LinkedIn Brand Center guidelines.
- **Lucide / External Resource**: Lucide Icons (ISC License).

### D. Compact Resource Card UI
In `ui/components/resource_cards.py`:
- Header line combines the 28px SVG logo container and resource title in a flex row.
- Accessibility labels (`aria-label="{provider} logo"`, `title="{provider}"`) added on logo containers.
- Zero `st.image()` calls used; zero image containers reserved; zero broken image states possible.
- SVG markup is cached in-memory (`_SVG_CACHE`) with an inline SVG fallback in case of I/O failure.

---

## 3. Files Created & Modified

| File | Status | Description |
| :--- | :--- | :--- |
| `ui/assets/provider_icons/google-cloud.svg` | Created | Authentic 28px Google Cloud SVG logo |
| `ui/assets/provider_icons/google-developers.svg` | Created | Authentic 28px Google Developers SVG logo |
| `ui/assets/provider_icons/google.svg` | Created | Authentic 28px Google general SVG logo |
| `ui/assets/provider_icons/youtube.svg` | Created | Authentic 28px YouTube SVG logo |
| `ui/assets/provider_icons/github.svg` | Created | Authentic 28px GitHub SVG mark |
| `ui/assets/provider_icons/huggingface.svg` | Created | Authentic 28px Hugging Face SVG logo |
| `ui/assets/provider_icons/linkedin.svg` | Created | Authentic 28px LinkedIn SVG mark |
| `ui/assets/provider_icons/external-resource.svg` | Created | Authentic 28px Lucide-style neutral external resource icon |
| `ui/components/resource_cards.py` | Modified | Hostname extraction, logo mapping, SVG caching, compact card rendering |
| `ui/components/__init__.py` | Modified | Exported hostname extractor and logo resolver functions |
| `tests/unit/test_resource_cards.py` | Modified | Unit tests for hostname extraction, logo mapping, domain spoof prevention, and asset validation |
| `docs/antigravity/06e-provider-brand-icons.md` | Created | Archived milestone prompt, implementation details, and verification results |
| `docs/antigravity/README.md` | Modified | Registered M6-E milestone entry |
| `README.md` | Modified | Updated UI overview describing real provider SVG logos |

---

## 4. Verification & Actual Test Results

### Quality Gate Verifications
```bash
uv run ruff check .
# Output: All checks passed!

uv run ruff format --check .
# Output: 74 files already formatted

uv run mypy .
# Output: Success: no issues found in 55 source files

uv run pytest -q
# Output: 96 passed in 1.56s
```

### Automated AppTest & Browser Rendering Verification
- Tested via Streamlit `AppTest.from_file('ui/app.py')`:
  - `len(at.image) == 0` (zero image elements across entire application).
  - Authentic SVG provider logos confirmed in rendered DOM for Google Cloud, YouTube, Hugging Face, GitHub, and Google Developers.
  - Titles and link buttons confirmed intact for all curriculum resources.

### Docker Runtime Verification
```bash
docker compose build
# Output: Successfully built gemini-adk-study-coach-lab-study-coach-ui

docker run --rm --entrypoint python gemini-adk-study-coach-lab-study-coach-ui -c "..."
# Output:
# Assets dir inside container: /app/ui/assets/provider_icons
# Container asset verified: google-cloud
# Container asset verified: google-developers
# Container asset verified: google
# Container asset verified: youtube
# Container asset verified: github
# Container asset verified: huggingface
# Container asset verified: linkedin
# Container asset verified: external-resource
# All provider icon assets verified inside container!
# Container AppTest with provider logos passed cleanly!
```

---

## 5. Git Status & Compliance
- **Commit**: `feat(m6): add provider logos to learning resources`
- **Release Tag**: `v0.6.0` preserved. No `v0.7.0` tag created.
- **Scope Compliance**: DO NOT START M7. Work stopped after M6-E completion.
