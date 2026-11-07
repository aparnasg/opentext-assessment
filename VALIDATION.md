# Validation status

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
