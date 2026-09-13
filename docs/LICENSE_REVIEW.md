# Publication licence and asset review

Reviewed 13 September 2026 for source publication and the static portfolio demo. This is an engineering inventory, not a legal opinion or a grant of rights in the original project.

- [Locked dependency inventory](dependency-licenses.json): 60 installed Python distributions and 154 npm lock entries, including development tools and optional platforms. Every Python/npm entry declares licence metadata.
- Browser runtime dependency licence/copyright texts are retained in [third-party-notices.txt](../web/public/third-party-notices.txt), also deployed with the static frontend. No package source or licence was modified.
- Server-side obligations are not all MIT: psycopg/psycopg-binary declare LGPL-3.0-only; certifi declares MPL-2.0; pypdfium2/PDFium has multiple upstream dependency notices. These packages retain their distribution licence files. Review LGPL relinking/source and PDFium notices before any separate binary redistribution; this source release does not relicense them.
- The six artwork designs are original programmatically generated fixtures. Public PDFs reproduce those fixtures and genuine recorded reports. UI screenshots are unmodified captures of this application. No employer code, external artwork, customer uploads, fonts downloaded from an unreviewed source or third-party logos are included.
- There is no public backend container image or vendored node_modules/.venv distribution in this release. Docker files install pinned upstream packages with their own notices.
- No permissive source licence was added. Original code and fixtures remain copyright Shashank under [NOTICE.md](../NOTICE.md).
