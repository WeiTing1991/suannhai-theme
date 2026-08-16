# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-08-16

### Added

- JetBrains IDE theme plugin (IntelliJ, CLion, Rider, WebStorm, PyCharm, etc.)
  - All 8 variants: Sumi, Rouiro, Koiai, Jiufen, Lam-ni, Torinoko, Shironeri, Hue-poo
- Icon assets (app, circle, glyph, favicon) in `assets/icons/`

### Fixed

- JetBrains: reduce FileColor opacity (15 → 03) to prevent visible tint on inactive editor tabs

### Changed

- JetBrains: update plugin icon to mountain-and-sea design
- Palette validation script (`scripts/validate-palettes.py`) to check Zed and JetBrains themes against canonical `colors/` definitions
- JetBrains plugin version now reads from git tag in CI release workflow

## [0.1.0] - 2026-08-15

### Added

- Initial release with 8 theme variants for Zed and WezTerm
- Formosa: Jiufen (dark), Lam-ni (dark), Hue-poo (light)
- Nippon: Rouiro (dark), Sumi (dark), Koiai (dark), Torinoko (light), Shironeri (light)
- Full syntax coverage for TypeScript, Python, C#, C++, Rust

### Changed


### Removed
