# GitHub repository setup

The repository is public. Use the GitHub **About** panel to add a concise
description and topics so people can discover it.

Suggested description:

> Nebula is an open-source Python desktop browser built with PySide6 and Qt WebEngine.

Suggested topics:

`python`, `pyside6`, `qt`, `qtwebengine`, `chromium`, `web-browser`, `desktop-app`,
`privacy`

Enable **Issues** and **Actions** in repository settings. Discussions are
optional and can be enabled if maintainers want a separate place for questions
and ideas. The repository includes issue forms, pull-request guidance, and a
workflow that runs the unit tests.

## Labels and starter issues

GitHub's standard labels include `bug`, `documentation`, `enhancement`,
`good first issue`, and `help wanted`. Keep those labels current and use
`good first issue` for small, well-scoped tasks with enough detail for a new
contributor to begin.

## Version tags and releases

Create a tag only when a version is ready to publish. Match the version in
`pyproject.toml`, then create and push an annotated tag:

```powershell
git tag -a v2.1.0 -m "Nebula 2.1.0"
git push origin v2.1.0
```

Replace `v2.1.0` with the version being released. Then create a GitHub Release
from that tag and include a short list of user-facing changes.
