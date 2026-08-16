# Suannhai JetBrains Theme — Design Spec

## Overview

A JetBrains IDE theme plugin providing all 8 Suannhai color variants (5 dark, 3 light) with full UI theming and syntax highlighting. Targets all JetBrains IDEs (primarily CLion and Rider). Publishable to the JetBrains Marketplace.

## Approach

Approach A: DevKit Plugin with Gradle (`intellij-platform-gradle-plugin`). No code generation — hand-authored theme files with colors sourced from `colors/*.json` palette files.

## Project Structure

```
suannhai-jetbrains/
├── build.gradle.kts
├── settings.gradle.kts
├── gradle.properties
├── gradle/wrapper/
├── src/main/resources/
│   ├── META-INF/
│   │   ├── plugin.xml
│   │   └── pluginIcon.svg
│   ├── themes/
│   │   ├── suannhai-sumi.theme.json
│   │   ├── suannhai-rouiro.theme.json
│   │   ├── suannhai-koiai.theme.json
│   │   ├── suannhai-jiufen.theme.json
│   │   ├── suannhai-lam-ni.theme.json
│   │   ├── suannhai-torinoko.theme.json
│   │   ├── suannhai-shironeri.theme.json
│   │   └── suannhai-hue-poo.theme.json
│   └── colorSchemes/
│       ├── Suannhai Sumi.xml
│       ├── Suannhai Rouiro.xml
│       ├── Suannhai Koiai.xml
│       ├── Suannhai Jiufen.xml
│       ├── Suannhai Lam-ni.xml
│       ├── Suannhai Torinoko.xml
│       ├── Suannhai Shironeri.xml
│       └── Suannhai Hue-poo.xml
└── .gitignore
```

Each variant has two files:
- `.theme.json` — UI chrome (sidebar, tabs, borders, buttons, panels)
- `.xml` — Editor color scheme (syntax highlighting, editor colors)

The `.theme.json` references its `.xml` via the `editorScheme` property.

## Variants

| Name | Collection | Appearance |
|------|-----------|------------|
| Suannhai Sumi | Nippon | Dark |
| Suannhai Rouiro | Nippon | Dark |
| Suannhai Koiai | Nippon | Dark |
| Suannhai Jiufen | Formosa | Dark |
| Suannhai Lam-ni | Formosa | Dark |
| Suannhai Torinoko | Nippon | Light |
| Suannhai Shironeri | Nippon | Light |
| Suannhai Hue-poo | Formosa | Light |

## Color Mapping — UI Theme (.theme.json)

Maps the palette roles to JetBrains UI properties, following the same approach as the Zed theme:

| Palette Role | JetBrains UI Usage |
|---|---|
| `background` | Editor background, toolbar |
| `surface` | Panel backgrounds, tab bar, title bar, tool windows |
| `border` | Borders, separators, indent guides |
| `comment` | Disabled text, placeholder, muted icons |
| `foreground` | Primary text, icons, labels |
| `keyword` | Primary accent (caret, focused borders, active links, buttons) |
| `function` | Secondary accent (selected tabs, active indicators) |
| `string` | Success states, VCS added, diff added |
| `type` | Info states, links, renamed |
| `constant` | Warning states, VCS modified |
| `error` | Error underlines, error badges, VCS deleted |

Derived colors (hover, selection, badges) use alpha/brightness adjustments.

## Color Mapping — Editor Scheme (.xml)

Maps Zed syntax tokens to JetBrains editor attributes:

| Zed Syntax Token | JetBrains Attribute | Palette Color |
|---|---|---|
| `keyword.*` | `DEFAULT_KEYWORD` | keyword |
| `function.*` | `DEFAULT_FUNCTION_DECLARATION`, `DEFAULT_FUNCTION_CALL` | function |
| `string.*` | `DEFAULT_STRING` | string |
| `type.*`, `constructor` | `DEFAULT_CLASS_NAME`, `DEFAULT_INTERFACE_NAME` | type |
| `number.*` | `DEFAULT_NUMBER` | number |
| `constant.*`, `boolean` | `DEFAULT_CONSTANT`, `DEFAULT_PREDEFINED_SYMBOL` | constant |
| `comment.*` | `DEFAULT_LINE_COMMENT`, `DEFAULT_DOC_COMMENT` | comment |
| `variable.*`, `property`, `field` | `DEFAULT_IDENTIFIER`, `DEFAULT_INSTANCE_FIELD` | foreground |
| `operator`, `punctuation.*` | `DEFAULT_OPERATION_SIGN`, `DEFAULT_BRACKETS` | comment (muted) |
| `string.escape` | `DEFAULT_VALID_STRING_ESCAPE` | constant |
| `attribute`, `function.decorator` | `DEFAULT_METADATA` | constant |
| `tag.*` | `HTML_TAG_NAME`, `XML_TAG_NAME` | type |

JetBrains XML uses RRGGBB without `#`. Theme JSON uses `#RRGGBB`.

### CLion/Rider-specific Attributes

Since CLion and Rider are primary targets:
- C/C++: `OC.DIRECTIVE`, `OC.MACRO`, `OC.STRUCT_FIELD`, `OC.ENUM_CONST`
- C#: `CSHARP_KEYWORD`, `CSHARP_CLASS_IDENTIFIER`, `CSHARP_STRUCT_IDENTIFIER`

These map to the same palette roles as their generic equivalents.

## Plugin Configuration

- **Plugin ID:** `com.weitingchen.suannhai-theme`
- **Plugin Name:** Suannhai Theme
- **Vendor:** WeitingChen
- **Platform:** IntelliJ Platform (IC) — compatible with all JetBrains IDEs
- **Since-build:** `241` (2024.1+)
- **Until-build:** unset (no upper bound)
- **Dependency:** `com.intellij.modules.platform`
- **No source code** — pure resource plugin

## Development Workflow

- `./gradlew runIde` — launches sandbox IDE with theme for testing
- `./gradlew buildPlugin` — produces `.zip` in `build/distributions/`

## Marketplace Publishing

1. Create JetBrains Marketplace account at https://plugins.jetbrains.com
2. Upload `.zip` from `./gradlew buildPlugin`
3. Fill in description, tags ("Theme", "Color Scheme"), screenshots
4. Submit for review
5. Updates: bump version in `gradle.properties`, rebuild, upload
