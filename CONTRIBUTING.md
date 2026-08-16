# Contributing

Contributions are welcome and very much appreciated!

## Code contributions

We accept contributions through pull requests. Here's how:

1. Fork the repository and clone the fork.
2. Create a branch off `main`.
3. Make your changes.
4. Test locally in the target editor (Zed, Neovim, WezTerm).
5. Check contrast ratios -- 4.5:1 minimum for text colors against their background.
6. Update `CHANGELOG.md` under `[Unreleased]`.
7. Commit your changes and push your branch to GitHub.
8. Create a pull request through the GitHub website.

### Adding a new editor port

Each editor lives in its own subdirectory (`suannhai-zed/`, `suannhai-nvim/`, etc.). When adding a new port:

- Create a `suannhai-<editor>/` directory at the repo root.
- Use the palette files in `colors/` as the single source of truth.
- Include a README inside the subdirectory with install instructions.
- Add the editor to the supported list in the root `README.md`.

### Color changes

- All color values come from the palette files in `colors/`.
- Formosa colors use Tai-lo romanization for naming. Hex values can be adjusted for contrast, but names stay in Taiwanese.
- The Nippon variants are built entirely from colors documented at [nipponcolors.com](https://nipponcolors.com). Every accent, neutral, and error color must trace back to a named color on that site. When proposing a color change for a Nippon variant, include the nipponcolors name and verify the hex matches.
- Run contrast checks before submitting -- 4.5:1 minimum for text, 3:1 for UI elements. Comment text on background is the most common failure.

## Bug reports

When reporting a bug please include:

- Editor name and version.
- Theme variant (e.g. Suannhai Jiufen).
- Operating system name and version.
- A screenshot showing the issue.
- Steps to reproduce.

## Feature requests

When proposing a new feature please include:

- A clear explanation of how it would work.
- Keep the scope as narrow as possible to make it easier to implement.
