<h1 align="center">Suannhai for JetBrains</h1>

<h4 align="center">
  <a href="#installation">Install</a>
  ·
  <a href="#build-from-source">Build</a>
  ·
  <a href="https://github.com/WeiTing1991/suannhai-theme">Suannhai Theme</a>
</h4>

<div align="center"><p>
    <a href="https://plugins.jetbrains.com/plugin/33591-suannhai-theme">
      <img alt="JetBrains Plugin Version" src="https://img.shields.io/jetbrains/plugin/v/33591-suannhai-theme?style=for-the-badge&logo=jetbrains&color=8bd5ca&logoColor=D9E0EE&labelColor=302D41"/>
    </a>
    <a href="https://plugins.jetbrains.com/plugin/33591-suannhai-theme">
      <img alt="JetBrains Plugin Downloads" src="https://img.shields.io/jetbrains/plugin/d/33591-suannhai-theme?style=for-the-badge&logo=jetbrains&color=c69ff5&logoColor=D9E0EE&labelColor=302D41"/>
    </a>
    <a href="https://github.com/WeiTing1991/suannhai-theme/blob/main/LICENSE">
      <img alt="License" src="https://img.shields.io/github/license/WeiTing1991/suannhai-theme?style=for-the-badge&logo=starship&color=ee999f&logoColor=D9E0EE&labelColor=302D41"/>
    </a>
</p></div>

Traditional color themes from Formosa and Nippon for JetBrains IDEs (IntelliJ, CLion, Rider, WebStorm, PyCharm, etc.).

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

### From JetBrains Marketplace

1. Open your JetBrains IDE (IntelliJ, CLion, Rider, WebStorm, PyCharm, etc.)
2. Go to **Settings** > **Plugins** > **Marketplace**
3. Search for `Suannhai`
4. Click **Install** and restart the IDE
5. Go to **Settings** > **Appearance & Behavior** > **Appearance**
6. Select a `Suannhai` variant from the **Theme** dropdown

### Manual Install

1. Download the latest `.zip` from [Releases](https://github.com/WeiTing1991/suannhai-theme/releases) or [Marketplace](https://plugins.jetbrains.com/plugin/33591-suannhai-theme)
2. Go to **Settings** > **Plugins** > **Gear icon** > **Install Plugin from Disk...**
3. Select the `.zip` file and restart the IDE

## Build from Source

```bash
cd suannhai-jetbrains
./gradlew buildPlugin
```

The plugin `.zip` will be in `build/distributions/`.

## Changelog

See [CHANGELOG.md](../CHANGELOG.md) for release history.
