# Validation status

## Current audit result November 9, 2026

- Audited public commit `3e80d52c9ae805610637e642c09c2bf09dbda6a3`: all 15 tracked files fetched from GitHub matched the local reviewed files after line-ending normalization.
- Fresh local test run: **43 passed, 1 existing dependency deprecation warning in 6.01 seconds**. Python compilation, JavaScript syntax checking and `pip check` passed.
- Fresh in-process API requests with real outbound OpenText retrieval returned HTTP 200 for all three supplied IDs. Each response had a matching source URL, valid SHA-256 hash, ETag and public cache headers. Returned Markdown character counts were 11,736 (1986936), 1,680 (2341059) and 4,737 (2310451); these are snapshot measurements, not fixed acceptance values.
- Homepage, JavaScript, health and OpenAPI endpoints returned 200. Invalid article IDs returned 422; unauthorized HTML imports returned 401.
- GitHub's API confirmed [CI run 42582978204](https://github.com/aparnasg/opentext-assessment/actions/runs/42582978204) completed successfully for that commit. Job-step metadata reported success for tests, compilation, SAM validation, SAM build and artifact upload. Full raw CI logs were not downloaded.
- Reviewed the supplied screenshots: the file list and both Mermaid diagrams render. No new automated browser or accessibility audit was performed.
- Pattern scanning of tracked text files found no email addresses, personal Windows paths, common provider-token patterns or private-key blocks. Reachable local commit author/committer emails used GitHub noreply addresses. These checks are not a complete security audit.
- The reviewed sanitized conversation transcript is now in the repository and linked from README. Its historical body remains unchanged from the original redacted export; omitted evidence and the export boundary are disclosed. It is not a full archive of every tool output or screenshot.

These results supersede earlier pending-status statements below, which are retained as development history. AWS deployment, production load testing and independent interview proficiency remain unverified. Direct dependencies are pinned; transitive dependency locking and vulnerability auditing remain production-hardening work.

## Earlier validation history

Executed on Windows, Python 3.12.3, November 5, 2026:

- Installed the seven pinned direct dependencies in an isolated virtual environment. Initial pip attempts stalled; an explicit PyPI index with cache and keyring disabled completed successfully. An attempted `legacy-certs` option was rejected by pip 24.0 and was not used in the successful install.
- `python -m compileall -q app`: passed.
- `python -m app.triangle`: printed `*`, `***`, `****` on separate lines.
- `python -m pytest -q --tb=short`: **16 passed, 1 warning in 2.13 seconds**. The warning is an upstream Starlette/AnyIO deprecated alias, not a failed assertion.
- Initial test run: 15 passed plus Windows test-runner setup/teardown errors caused by using a 2 MB parameter value in the generated test name. Added explicit short parameter IDs; the complete rerun passed.
- Disabled externally hosted Swagger/ReDoc assets after reviewing their conflict with the Content Security Policy; the OpenAPI JSON remains available.

Cloud deployment, SAM validation/build, live authenticated article conversion, browser UI testing, load tests and accessibility audits have not been performed. SAM CLI was not found locally. The GitHub workflow defines template validation and build checks for repository execution. The source HTML used by tests is synthetic. No remote repository was created.

## Follow-up: saved OpenText article

- User supplied `article-2341059.html` (150,152 bytes). Article body was embedded in `__NUXT_DATA__`, while visible HTML contained loading placeholders.
- Added a narrow parser for the matching article ID and its referenced title/content fields. No script execution or general object-graph deserialization.
- Added same-host HTTPS redirects, constrained to the same article ID and article route, with a three-hop limit. Other redirect destinations are rejected before requesting them.
- Converted the saved article to a 1,701-character Markdown document with title, summary, environment and hotfix table. Sidebar attachments are not included.
- Updated tests: **26 passed, 1 upstream deprecation warning in 10.13 seconds**. A new fixture initially included a literal closing script tag within JSON; corrected the fixture to use a representative article fragment, then reran successfully.
- Retried all three public example URLs using Python: each returned HTML without an extractable article body. The browser-saved conversion is verified; live fetch support remains incomplete. These failures do not establish whether login, browser-specific rendering or other upstream behavior is responsible.

## Final follow-up: live retrieval resolved for the three examples

The user supplied a complete copied Network response (150,942 bytes). It contains closing HTML and matching Nuxt article data; the existing parser converted it successfully. Live comparisons then showed `/support/article/2341059` returned a generic page with HTTP 200, while the title-plus-ID route returned article data. Testing the neutral `/support/article/knowledge/<id>` path returned matching article data for all three IDs. The fetcher now uses this observed public webpage route for number-only inputs. It does not call an internal content API, impersonate a logged-in user or execute scripts. The route convention remains an upstream dependency requiring monitoring.

Final local verification after this fix:

- `python -m pytest -q --tb=short`: **26 passed, 1 upstream deprecation warning in 12.04 seconds**.
- In-process FastAPI requests through HTTPX ASGITransport, using real outbound OpenText retrieval, each returned **HTTP 200** and `public, max-age=60, s-maxage=300`:
  - 1986936: UFT One/UFT Developer remote-session article; 11,740 Markdown characters.
  - 2341059: Content Manager hotfix article; 1,701 Markdown characters.
  - 2310451: Third-party software on Advanced Authentication Appliance article; 4,737 Markdown characters.
- Markdown files were saved alongside the repository as review artifacts; actual article bodies are excluded from the source ZIP.

These successful live checks supersede earlier retrieval failures. They establish live fetching and API conversion for the examples at the time of testing; they do not establish complete content fidelity, attachment coverage, production load performance or AWS deployment readiness. Manual comparison of all three full articles remains necessary. Browser interaction with the updated UI has not been tested by the agent.

## Markdown formatting cleanup

- Normalized redundant nested bold/italic HTML and merged adjacent spans of matching emphasis before Markdown generation. Removed redundant emphasis within headings. Code/preformatted content is excluded from this normalization.
- Added six regression cases covering nested emphasis, adjacent bold segments, whitespace, headings, ordinary emphasis and literal stars in code.
- Full local suite: **32 passed, 1 existing dependency deprecation warning in 4.09 seconds**.
- Reconverted the saved 2341059 HTML: the Note and Last update formatting is clean, Environment is a plain Markdown heading, and all 16 hotfix data rows remain (17 table lines including the header).
- Refreshed the saved Markdown and source ZIP. User should refresh the local website and verify the updated output; no additional live fetch was performed for this cleanup.

## Separate bonus triangle function

- `triangle()` now handles the required fixed 3-by-4 output; `triangle_mn(m, n)` is the separate bonus function. The fixed function delegates to the general function so rounding and validation stay in one place.
- Verified exact outputs for fixed dimensions, 1-by-1, one row, one column and 5-by-8. Invalid zero, negative, boolean, fractional and string dimensions raise ValueError.
- Full suite: **43 passed, 1 existing dependency deprecation warning in 2.88 seconds**.
- Ran both CLI examples successfully: `python -m app.triangle` and `python -c "from app.triangle import triangle_mn; print(triangle_mn(5, 8))"`.
- Updated README, session record and source ZIP. GitHub publication and CI/cloud build verification remain pending.

## GitHub publication and CI evidence

- Source published at https://github.com/aparnasg/opentext-assessment.
- User supplied the successful workflow URL: https://github.com/aparnasg/opentext-assessment/actions/runs/42351565069.
- The user's GitHub Actions screenshot shows an overall green result for Build and test, commit 141f165. The workflow contains Python tests, compilation, SAM validation, SAM build and artifact upload. The agent could not fetch the run page through the web reader; individual step logs were not independently inspected.
- User also supplied a local test screenshot confirming 43 passed, 1 existing dependency warning in 2.91 seconds, and reported comparing all three browser conversions with the originals.
- These results supersede earlier notes that repository publication and the initial CI run were pending. AWS deployment and performance load testing remain unperformed. The actual sanitized AI conversation export remains outstanding.
