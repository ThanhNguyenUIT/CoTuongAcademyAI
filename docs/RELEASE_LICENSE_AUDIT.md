# Release license and dependency audit

**Reviewed:** 2026-09-27 · **Purpose:** local beta readiness review, not legal advice or a grant of rights.

## Dependency inventory

- Frontend/root lockfile: 366 `node_modules/*` entries total; 365 third-party package entries declare a license. Counts from lockfile metadata: MIT 294, Apache-2.0 20, ISC 20, MPL-2.0 12, BSD-2-Clause 8, BSD-3-Clause 6, BlueOak-1.0.0 1, 0BSD 1, MIT-0 1, Python-2.0 1, CC-BY-4.0 1. The remaining entry is the project's own private workspace package, which has no declared package license; it is not a third-party dependency. Recheck package-level license files/notices before redistribution.
- Python virtual environment inventory: 27 installed distributions. Direct runtime requirements are FastAPI (MIT), Uvicorn (BSD-3-Clause), HTTPX (BSD-3-Clause), PyYAML (MIT), plus their transitives. The environment also contains pytest/pip and other development tools. SPDX license fields/classifiers were read from installed distribution metadata; this is not a replacement for shipping each applicable license notice.
- `npm audit --json` after the test-tool upgrade reports zero vulnerabilities (371 dependency nodes including optional/peer entries). Python `pip check` passes; no Python CVE scanner was installed or run.
- Initially `npm audit` reported the Vitest `@vitest/mocker` path-traversal advisory. Vitest and its coverage package were updated to 4.1.11; root test tooling is pinned by the lockfile. The current audit is clean. The upstream fix release is [Vitest v4.1.11](https://github.com/vitest-dev/vitest/releases/tag/v4.1.11); advisory: [GHSA-82fw-gwwq-j7x9](https://github.com/vitest-dev/vitest/security/advisories/GHSA-82fw-gwwq-j7x9).
- An SPDX npm SBOM was **not** generated: `npm sbom --sbom-format=spdx --package-lock-only` exits `ESBOMPROBLEMS` because platform-optional WASI packages listed in the lockfile are not installed in this Windows node_modules. The manual license count above is a preliminary inventory, not a release SBOM.

## Engine and model files

Artifacts are in ignored `.local-engines/` and are not included in the frontend build/source archive:

| Artifact | Observed SHA-256 | Recorded terms | Distribution decision |
| --- | --- | --- | --- |
| Pikafish Windows binary, 2026-09-06 | `0D57D64C212E78F96CBA9E5E4F140D8872F8FAA42EA631A27AB6C5DB08509DA3` | GPLv3; local upstream `Copying.txt` present | Run locally only; redistribution not approved in this phase |
| `pikafish.nnue` | `7D13D73569A9B571BA0EB20CF1596247BC2A42738967E61AFEF6482B231E900E` | Local `NNUE-License.md`: legal use; non-commercial use requires permission | Non-commercial local testing only; written commercial permission absent |
| Fairy-Stockfish Windows binary, 14.0.1 XQ | `38C173576C13407B610A03DA8C31144BBDEE9F49D9D789C4E7B681CC18D36221` | GPLv3 per upstream release; exact binary is ignored from source | Local test only; complete distribution notices not assembled |
| Fairy Xiangqi NNUE | Integrated in binary; not separately present to hash | Upstream Networks record identifies the applicable Xiangqi Fairy weights as CC0 | Verify exact model provenance/version before redistributing |

Hash/version/source/benchmark evidence is also recorded in [ENGINE_LICENSE.md](ENGINE_LICENSE.md) and ADR-007. This review did not compile engine source or construct corresponding source offers/notice bundles for either binary.

## Course content and sample games

- There are no third-party PGN/game dump files in the content folder. The opening course YAML contains three authored illustrative lines, source links to XiangqiMaster and a WXF introductory PDF, and every item is marked `experimental`.
- The source references provide attribution/context but do not by themselves prove permission to copy, adapt, or redistribute course language, diagrams, or game scores. No explicit license/grant, educator review, or rights-holder approval is recorded for these course materials.
- The board is drawn in source (SVG/React) with Unicode pieces; no third-party image/font asset was found in `frontend/src`.
- Do not bundle or publish course content in beta until rights and attribution are documented and an Xiangqi educator approves the lesson. Do not scrape more material to fill this gap.

## Disposition

Local non-commercial evaluation can use the currently configured Pikafish artifacts under the included terms and keep all binaries/weights out of the distribution. Public/commercial release is blocked on rights-holder/legal review of content and exact shipped artifacts, appropriate engine source/license notices, a complete SBOM, and approval of the project's own distribution license. No external counsel or rights holder reviewed this report.
