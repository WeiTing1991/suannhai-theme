# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- JetBrains IDE theme plugin (IntelliJ, CLion, Rider, WebStorm, PyCharm, etc.)
  - All 8 variants: Sumi, Rouiro, Koiai, Jiufen, Lam-ni, Torinoko, Shironeri, Hue-poo
  - Full UI theming (sidebar, tabs, panels, buttons, status bar)
  - Editor color scheme with syntax highlighting for C/C++, C#, HTML/XML, JSON, YAML, Markdown
  - Marketplace-ready plugin package
- Palette validation script (`scripts/validate-palettes.py`) to check Zed and JetBrains themes against canonical `colors/` definitions
- JetBrains plugin version now reads from git tag in CI release workflow

### Changed

- JetBrains README: add marketplace badges, install/build sections, changelog link
- Root README: JetBrains entry now links to both local folder and Marketplace

### Fixed

- JetBrains: reduce FileColor opacity to prevent tinted inactive tabs

## [0.1.0] - 2026-08-15

### Added

- Initial release with 8 theme variants for Zed and WezTerm
- Formosa: Jiufen (dark), Lam-ni (dark), Hue-poo (light)
- Nippon: Rouiro (dark), Sumi (dark), Koiai (dark), Torinoko (light), Shironeri (light)
- Full syntax coverage for TypeScript, Python, C#, C++, Rust

### Changed


### Removed
