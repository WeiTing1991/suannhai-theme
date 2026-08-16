<h1 align="center">Suannhai for WezTerm</h1>

<h4 align="center">
  <a href="#installation">Install</a>
  ·
  <a href="https://github.com/WeiTing1991/suannhai-theme">Suannhai Theme</a>
</h4>

Traditional color themes from Formosa and Nippon for [WezTerm](https://wezfurlong.org/wezterm/).

## Themes

### Formosa

- Suannhai Jiufen (Dark)
- Suannhai Lam-ni (Dark)
- Suannhai Hue-poo (Light)

### Nippon

- Suannhai Rouiro (Dark)
- Suannhai Sumi (Dark)
- Suannhai Koiai (Dark)
- Suannhai Torinoko (Light)
- Suannhai Shironeri (Light)

## Installation

Copy the `.toml` files from `colors/` into your WezTerm color scheme directory:

```bash
# macOS / Linux
cp colors/*.toml ~/.config/wezterm/colors/

# or specify a custom directory in wezterm.lua
config.color_scheme_dirs = { '/path/to/suannhai-wezterm/colors' }
```

Then set the scheme in your `wezterm.lua`:

```lua
config.color_scheme = 'Suannhai Jiufen'
```

## Changelog

See [CHANGELOG.md](../CHANGELOG.md) for release history.
