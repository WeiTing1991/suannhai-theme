# JetBrains Theme Plugin Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a JetBrains IDE theme plugin with all 8 Suannhai color variants (5 dark, 3 light), full UI theming and syntax highlighting, ready for Marketplace publishing.

**Architecture:** A pure-resource IntelliJ Platform plugin (no Java/Kotlin code). Each variant consists of a `.theme.json` file (UI chrome) and an `.xml` file (editor color scheme). The `.theme.json` references the `.xml` via `editorScheme`. All 8 themes are registered in `plugin.xml` and packaged into a single `.zip` via Gradle.

**Tech Stack:** IntelliJ Platform Gradle Plugin 2.x, JDK 17+, Gradle wrapper

## Global Constraints

- All hex colors must come from `colors/*.json` palette files — no invented colors
- Derived colors (hover, selection, backgrounds) use alpha transparency or brightness shifts of palette colors
- JetBrains `.theme.json` uses `#RRGGBB` format; `.xml` editor schemes use `RRGGBB` (no `#` prefix), but stored as decimal in `<option value="DECIMAL"/>` for foreground/background attributes
- Dark themes set `"dark": true`; light themes set `"dark": false` in `.theme.json`
- Plugin must target `sinceBuild = "241"` (IntelliJ 2024.1+), no upper bound
- Minimum 4.5:1 contrast ratio for text, 3:1 for UI elements

---

## File Structure

```
suannhai-jetbrains/
├── build.gradle.kts                          # Gradle build config
├── settings.gradle.kts                       # Project name
├── gradle.properties                         # Version, platform target
├── .gitignore                                # build/, .gradle/, .idea/
├── src/main/resources/
│   ├── META-INF/
│   │   ├── plugin.xml                        # Plugin descriptor
│   │   └── pluginIcon.svg                    # 40x40 Marketplace icon
│   ├── themes/
│   │   ├── suannhai_sumi.theme.json
│   │   ├── suannhai_rouiro.theme.json
│   │   ├── suannhai_koiai.theme.json
│   │   ├── suannhai_jiufen.theme.json
│   │   ├── suannhai_lam_ni.theme.json
│   │   ├── suannhai_torinoko.theme.json
│   │   ├── suannhai_shironeri.theme.json
│   │   └── suannhai_hue_poo.theme.json
│   └── colorSchemes/
│       ├── Suannhai Sumi.xml
│       ├── Suannhai Rouiro.xml
│       ├── Suannhai Koiai.xml
│       ├── Suannhai Jiufen.xml
│       ├── Suannhai Lam-ni.xml
│       ├── Suannhai Torinoko.xml
│       ├── Suannhai Shironeri.xml
│       └── Suannhai Hue-poo.xml
```

---

### Task 1: Gradle Project Scaffold

**Files:**
- Create: `suannhai-jetbrains/build.gradle.kts`
- Create: `suannhai-jetbrains/settings.gradle.kts`
- Create: `suannhai-jetbrains/gradle.properties`
- Create: `suannhai-jetbrains/.gitignore`

**Interfaces:**
- Consumes: nothing
- Produces: A working Gradle project that can run `./gradlew buildPlugin` (will produce empty plugin until themes added)

- [ ] **Step 1: Create `settings.gradle.kts`**

```kotlin
rootProject.name = "suannhai-jetbrains"
```

- [ ] **Step 2: Create `gradle.properties`**

```properties
pluginVersion = 0.1.0
pluginSinceBuild = 241
platformType = IC
platformVersion = 2024.1.7
```

- [ ] **Step 3: Create `build.gradle.kts`**

```kotlin
plugins {
    id("org.jetbrains.intellij.platform") version "2.5.0"
}

repositories {
    mavenCentral()
    intellijPlatform {
        defaultRepositories()
    }
}

dependencies {
    intellijPlatform {
        create(providers.gradleProperty("platformType"), providers.gradleProperty("platformVersion"))
        instrumentationTools()
    }
}

intellijPlatform {
    pluginConfiguration {
        id = "com.weitingchen.suannhai-theme"
        name = "Suannhai Theme"
        version = providers.gradleProperty("pluginVersion")
        ideaVersion {
            sinceBuild = providers.gradleProperty("pluginSinceBuild")
        }
        vendor {
            name = "WeitingChen"
            email = "72130405+WeiTing1991@users.noreply.github.com"
            url = "https://github.com/WeiTing1991/suannhai-theme"
        }
        description = """
            8 color themes inspired by Taiwanese and Japanese traditional colors.
            <br/><br/>
            <b>Formosa Collection (Taiwan):</b> Jiufen, Lâm-ní, Hue-pòo
            <br/>
            <b>Nippon Collection (Japan):</b> Rouiro, Sumi, Koiai, Torinoko, Shironeri
        """.trimIndent()
    }
}
```

- [ ] **Step 4: Create `.gitignore`**

```
build/
.gradle/
.idea/
*.iml
```

- [ ] **Step 5: Initialize Gradle wrapper**

```bash
cd suannhai-jetbrains
gradle wrapper --gradle-version 8.12
```

- [ ] **Step 6: Verify Gradle project compiles**

```bash
cd suannhai-jetbrains
./gradlew tasks --no-daemon
```

Expected: Gradle resolves dependencies and lists available tasks including `buildPlugin` and `runIde`.

- [ ] **Step 7: Commit**

```bash
git add suannhai-jetbrains/
git commit -m "feat(jetbrains): add Gradle project scaffold"
```

---

### Task 2: Plugin Descriptor and Icon

**Files:**
- Create: `suannhai-jetbrains/src/main/resources/META-INF/plugin.xml`
- Create: `suannhai-jetbrains/src/main/resources/META-INF/pluginIcon.svg`

**Interfaces:**
- Consumes: Gradle project from Task 1
- Produces: `plugin.xml` with all 8 `<themeProvider>` entries; plugin icon for Marketplace

- [ ] **Step 1: Create `plugin.xml`**

```xml
<idea-plugin>
    <depends>com.intellij.modules.platform</depends>

    <extensions defaultExtensionNs="com.intellij">
        <!-- Nippon Dark -->
        <themeProvider id="suannhai.sumi" path="/themes/suannhai_sumi.theme.json"/>
        <themeProvider id="suannhai.rouiro" path="/themes/suannhai_rouiro.theme.json"/>
        <themeProvider id="suannhai.koiai" path="/themes/suannhai_koiai.theme.json"/>

        <!-- Formosa Dark -->
        <themeProvider id="suannhai.jiufen" path="/themes/suannhai_jiufen.theme.json"/>
        <themeProvider id="suannhai.lam-ni" path="/themes/suannhai_lam_ni.theme.json"/>

        <!-- Nippon Light -->
        <themeProvider id="suannhai.torinoko" path="/themes/suannhai_torinoko.theme.json"/>
        <themeProvider id="suannhai.shironeri" path="/themes/suannhai_shironeri.theme.json"/>

        <!-- Formosa Light -->
        <themeProvider id="suannhai.hue-poo" path="/themes/suannhai_hue_poo.theme.json"/>
    </extensions>
</idea-plugin>
```

- [ ] **Step 2: Create `pluginIcon.svg`**

Create a simple 40x40 SVG icon. Use the Sumi keyword color (`#D75455`) as the primary mark on a dark background (`#1C1C1C`).

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 40 40">
  <rect width="40" height="40" rx="8" fill="#1C1C1C"/>
  <text x="20" y="27" text-anchor="middle" font-family="serif" font-size="22" font-weight="bold" fill="#D75455">S</text>
</svg>
```

- [ ] **Step 3: Verify plugin builds**

```bash
cd suannhai-jetbrains
./gradlew buildPlugin --no-daemon
```

Expected: Build succeeds (themes don't exist yet but plugin.xml is valid).

- [ ] **Step 4: Commit**

```bash
git add suannhai-jetbrains/src/main/resources/META-INF/
git commit -m "feat(jetbrains): add plugin.xml and icon"
```

---

### Task 3: Sumi Dark Theme (reference implementation)

This is the reference implementation. All subsequent variants follow this exact structure with different colors.

**Files:**
- Create: `suannhai-jetbrains/src/main/resources/themes/suannhai_sumi.theme.json`
- Create: `suannhai-jetbrains/src/main/resources/colorSchemes/Suannhai Sumi.xml`

**Interfaces:**
- Consumes: `plugin.xml` from Task 2, palette from `colors/nippon-sumi.json`
- Produces: Complete dark theme (UI + editor scheme) that serves as template for all other dark variants

**Palette reference (Sumi):**
- background: `#1C1C1C` | surface: `#262626` | border: `#3A3835` | comment: `#9E7A7A` | foreground: `#C4C7C1`
- keyword: `#D75455` | function: `#E2943B` | string: `#7BA23F` | type: `#58B2DC` | number: `#8B81C3` | constant: `#C7802D`
- error: `#CB4042`

- [ ] **Step 1: Create `suannhai_sumi.theme.json`**

```json
{
  "name": "Suannhai Sumi",
  "dark": true,
  "author": "WeitingChen",
  "editorScheme": "/colorSchemes/Suannhai Sumi.xml",
  "colors": {},
  "ui": {
    "*": {
      "arc": "4",
      "background": "#262626",
      "foreground": "#C4C7C1",
      "selectionBackground": "#3A3835",
      "selectionForeground": "#C4C7C1",
      "disabledBackground": "#1C1C1C",
      "disabledForeground": "#9E7A7A",
      "disabledText": "#9E7A7A",
      "inactiveBackground": "#262626",
      "inactiveForeground": "#9E7A7A",
      "errorForeground": "#CB4042",
      "borderColor": "#3A3835",
      "focusedBorderColor": "#D75455",
      "focusColor": "#D7545566",
      "separatorColor": "#3A3835"
    },
    "ActionButton": {
      "hoverBackground": "#3A3835",
      "hoverBorderColor": "#3A3835",
      "pressedBackground": "#3A383580",
      "pressedBorderColor": "#3A383580"
    },
    "Button": {
      "default": {
        "foreground": "#C4C7C1",
        "startBackground": "#D75455",
        "endBackground": "#D75455",
        "startBorderColor": "#D75455",
        "endBorderColor": "#D75455",
        "focusedBorderColor": "#D75455"
      },
      "startBackground": "#3A3835",
      "endBackground": "#3A3835",
      "startBorderColor": "#3A3835",
      "endBorderColor": "#3A3835"
    },
    "CheckBox": {
      "background": "#262626",
      "select": "#D75455"
    },
    "ComboBox": {
      "nonEditableBackground": "#262626",
      "selectionBackground": "#3A3835",
      "ArrowButton": {
        "iconColor": "#C4C7C1",
        "disabledIconColor": "#9E7A7A"
      }
    },
    "CompletionPopup": {
      "selectionBackground": "#3A3835",
      "matchForeground": "#D75455"
    },
    "Component": {
      "focusColor": "#D7545566",
      "borderColor": "#3A3835",
      "focusedBorderColor": "#D75455",
      "disabledBorderColor": "#262626",
      "errorFocusColor": "#CB404266",
      "warningFocusColor": "#E2943B66",
      "infoFocusColor": "#58B2DC66"
    },
    "Counter": {
      "background": "#D75455",
      "foreground": "#C4C7C1"
    },
    "DebuggerTabs": {
      "selectedBackground": "#1C1C1C",
      "underlinedTabBackground": "#1C1C1C"
    },
    "DefaultTabs": {
      "background": "#262626",
      "underlineColor": "#D75455",
      "inactiveUnderlineColor": "#D7545480",
      "hoverBackground": "#3A383540",
      "underlinedTabBackground": "#1C1C1C"
    },
    "DragAndDrop": {
      "borderColor": "#D75455"
    },
    "Editor": {
      "background": "#1C1C1C",
      "foreground": "#C4C7C1",
      "shortcutForeground": "#58B2DC"
    },
    "EditorTabs": {
      "background": "#262626",
      "underlineColor": "#D75455",
      "underlineHeight": 2,
      "inactiveUnderlineColor": "#D7545480",
      "underlinedTabBackground": "#1C1C1C",
      "hoverBackground": "#3A383540"
    },
    "FileColor": {
      "Yellow": "#E2943B15",
      "Green": "#7BA23F15",
      "Blue": "#58B2DC15",
      "Violet": "#8B81C315",
      "Orange": "#C7802D15",
      "Rose": "#CB404215"
    },
    "Label": {
      "foreground": "#C4C7C1",
      "disabledForeground": "#9E7A7A",
      "errorForeground": "#CB4042",
      "infoForeground": "#9E7A7A",
      "successForeground": "#7BA23F"
    },
    "Link": {
      "activeForeground": "#58B2DC",
      "hoverForeground": "#58B2DC",
      "visitedForeground": "#8B81C3",
      "pressedForeground": "#58B2DC"
    },
    "List": {
      "selectionBackground": "#3A3835",
      "selectionForeground": "#C4C7C1",
      "hoverBackground": "#3A383540"
    },
    "NavBar": {
      "borderColor": "#3A3835"
    },
    "Notification": {
      "background": "#262626",
      "borderColor": "#3A3835",
      "errorBackground": "#CB40421a",
      "errorBorderColor": "#CB4042",
      "errorForeground": "#C4C7C1"
    },
    "Panel": {
      "background": "#262626",
      "foreground": "#C4C7C1"
    },
    "Plugins": {
      "lightSelectionBackground": "#3A3835",
      "tagBackground": "#3A3835",
      "tagForeground": "#C4C7C1",
      "Button": {
        "installBackground": "#D7545430",
        "installForeground": "#D75455",
        "installBorderColor": "#D75455",
        "updateBackground": "#D75455",
        "updateForeground": "#C4C7C1"
      }
    },
    "Popup": {
      "background": "#262626",
      "borderColor": "#3A3835",
      "Header": {
        "activeBackground": "#3A3835",
        "inactiveBackground": "#262626"
      }
    },
    "ProgressBar": {
      "trackColor": "#3A3835",
      "progressColor": "#D75455",
      "indeterminateStartColor": "#D75455",
      "indeterminateEndColor": "#D7545440",
      "failedColor": "#CB4042",
      "failedEndColor": "#CB404240",
      "passedColor": "#7BA23F",
      "passedEndColor": "#7BA23F40"
    },
    "ScrollBar": {
      "Mac": {
        "thumbColor": "#3A383560",
        "thumbBorderColor": "#3A383560",
        "hoverThumbColor": "#3A383590",
        "hoverThumbBorderColor": "#3A383590",
        "Transparent": {
          "thumbColor": "#3A383540",
          "thumbBorderColor": "#3A383540",
          "hoverThumbColor": "#3A383570",
          "hoverThumbBorderColor": "#3A383570"
        }
      }
    },
    "SearchEverywhere": {
      "Header": {
        "background": "#262626"
      },
      "SearchField": {
        "background": "#262626",
        "borderColor": "#3A3835"
      },
      "Tab": {
        "selectedBackground": "#3A3835",
        "selectedForeground": "#C4C7C1"
      }
    },
    "SearchMatch": {
      "startBackground": "#D7545440",
      "endBackground": "#D7545440"
    },
    "SpeedSearch": {
      "background": "#262626",
      "foreground": "#C4C7C1",
      "borderColor": "#D75455",
      "errorForeground": "#CB4042"
    },
    "StatusBar": {
      "background": "#262626",
      "borderColor": "#3A3835",
      "hoverBackground": "#3A3835"
    },
    "TabbedPane": {
      "tabSelectionHeight": 2,
      "underlineColor": "#D75455",
      "contentAreaColor": "#3A3835",
      "hoverColor": "#3A383540"
    },
    "Table": {
      "stripeColor": "#26262680",
      "lightSelectionBackground": "#3A3835",
      "lightSelectionForeground": "#C4C7C1"
    },
    "TextField": {
      "background": "#1C1C1C"
    },
    "TitlePane": {
      "background": "#262626",
      "inactiveBackground": "#262626",
      "foreground": "#C4C7C1",
      "inactiveForeground": "#9E7A7A",
      "Button": {
        "hoverBackground": "#3A3835"
      }
    },
    "ToggleButton": {
      "onBackground": "#D75455",
      "onForeground": "#C4C7C1",
      "offBackground": "#3A3835",
      "offForeground": "#9E7A7A",
      "buttonColor": "#C4C7C1"
    },
    "ToolBar": {
      "background": "#262626",
      "borderHandleColor": "#3A3835"
    },
    "ToolWindow": {
      "background": "#262626",
      "Header": {
        "background": "#262626",
        "inactiveBackground": "#262626",
        "borderColor": "#3A3835"
      },
      "HeaderTab": {
        "selectedBackground": "#1C1C1C",
        "hoverBackground": "#3A383540",
        "underlineColor": "#D75455"
      },
      "Button": {
        "hoverBackground": "#3A3835",
        "selectedBackground": "#3A3835"
      }
    },
    "Tree": {
      "selectionBackground": "#3A3835",
      "modifiedItemForeground": "#58B2DC",
      "hoverBackground": "#3A383540",
      "rowHeight": 24
    },
    "ValidationTooltip": {
      "errorBackground": "#CB40421a",
      "errorBorderColor": "#CB4042",
      "warningBackground": "#E2943B1a",
      "warningBorderColor": "#E2943B"
    },
    "VersionControl": {
      "GitLog": {
        "headIconColor": "#D75455",
        "localBranchIconColor": "#7BA23F",
        "remoteBranchIconColor": "#8B81C3",
        "tagIconColor": "#E2943B",
        "otherIconColor": "#58B2DC"
      },
      "Log": {
        "Commit": {
          "currentBranchBackground": "#D754551a",
          "unmatchedForeground": "#9E7A7A"
        }
      },
      "FileHistory": {
        "Commit": {
          "selectedBranchBackground": "#3A3835"
        }
      }
    },
    "WelcomeScreen": {
      "background": "#1C1C1C",
      "borderColor": "#3A3835",
      "headerBackground": "#262626",
      "footerBackground": "#262626",
      "Projects": {
        "background": "#262626",
        "selectionBackground": "#3A3835"
      },
      "SidePanel": {
        "background": "#262626"
      }
    }
  }
}
```

- [ ] **Step 2: Create `Suannhai Sumi.xml`**

JetBrains editor scheme XML. Color values in `<option>` elements use hex string format (`RRGGBB` without `#`). The `FONT_TYPE` attribute controls style: `0` = plain, `1` = bold, `2` = italic, `3` = bold+italic.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<scheme name="Suannhai Sumi" version="142" parent_scheme="Darcula">
  <metaInfo>
    <property name="created">2026-08-16T00:00:00</property>
    <property name="ide">idea</property>
    <property name="ideVersion">2024.1</property>
    <property name="modified">2026-08-16T00:00:00</property>
    <property name="originalScheme">Suannhai Sumi</property>
  </metaInfo>

  <colors>
    <!-- Editor -->
    <option name="CARET_COLOR" value="D75455"/>
    <option name="CARET_ROW_COLOR" value="262524"/>
    <option name="SELECTION_BACKGROUND" value="3A3835"/>
    <option name="SELECTION_FOREGROUND"/>
    <option name="GUTTER_BACKGROUND" value="1C1C1C"/>
    <option name="LINE_NUMBERS_COLOR" value="433838"/>
    <option name="LINE_NUMBER_ON_CARET_ROW_COLOR" value="C4C7C1"/>
    <option name="INDENT_GUIDE" value="2b2a28"/>
    <option name="SELECTED_INDENT_GUIDE" value="3A3835"/>
    <option name="RIGHT_MARGIN_COLOR" value="2b2a28"/>
    <option name="VISUAL_INDENT_GUIDE" value="2b2a28"/>

    <!-- Search -->
    <option name="SEARCH_RESULT_ATTRIBUTES" value="D7545440"/>

    <!-- Console ANSI colors -->
    <option name="CONSOLE_BACKGROUND_KEY" value="1C1C1C"/>
    <option name="CONSOLE_BLACK_OUTPUT" value="1C1C1C"/>
    <option name="CONSOLE_DARKGRAY_OUTPUT" value="9E7A7A"/>
    <option name="CONSOLE_RED_OUTPUT" value="CB4042"/>
    <option name="CONSOLE_GREEN_OUTPUT" value="7BA23F"/>
    <option name="CONSOLE_YELLOW_OUTPUT" value="E2943B"/>
    <option name="CONSOLE_BLUE_OUTPUT" value="58B2DC"/>
    <option name="CONSOLE_MAGENTA_OUTPUT" value="8B81C3"/>
    <option name="CONSOLE_CYAN_OUTPUT" value="58B2DC"/>
    <option name="CONSOLE_WHITE_OUTPUT" value="C4C7C1"/>
    <option name="CONSOLE_GRAY_OUTPUT" value="9E7A7A"/>
    <option name="CONSOLE_NORMAL_OUTPUT" value="C4C7C1"/>
    <option name="CONSOLE_ERROR_OUTPUT" value="CB4042"/>
    <option name="CONSOLE_USER_INPUT" value="7BA23F"/>
    <option name="CONSOLE_SYSTEM_OUTPUT" value="9E7A7A"/>

    <!-- VCS gutters -->
    <option name="ADDED_LINES_COLOR" value="7BA23F"/>
    <option name="MODIFIED_LINES_COLOR" value="58B2DC"/>
    <option name="DELETED_LINES_COLOR" value="CB4042"/>
    <option name="WHITESPACES_MODIFIED_LINES_COLOR" value="C7802D"/>

    <!-- Diff -->
    <option name="DIFF_INSERTED" value="7BA23F20"/>
    <option name="DIFF_DELETED" value="CB404220"/>
    <option name="DIFF_MODIFIED" value="58B2DC20"/>
    <option name="DIFF_CONFLICT" value="C7802D20"/>

    <!-- Notification -->
    <option name="NOTIFICATION_BACKGROUND" value="262626"/>
    <option name="INFORMATION_HINT" value="262626"/>

    <!-- Breadcrumbs -->
    <option name="BREADCRUMBS_DEFAULT" value="9E7A7A"/>
    <option name="BREADCRUMBS_HOVERED" value="C4C7C1"/>
    <option name="BREADCRUMBS_CURRENT" value="C4C7C1"/>
    <option name="BREADCRUMBS_INACTIVE" value="9E7A7A"/>

    <!-- Tearline / folding -->
    <option name="TEARLINE_COLOR" value="3A3835"/>
    <option name="SELECTED_TEARLINE_COLOR" value="D75455"/>
    <option name="FOLDED_TEXT_BORDER_COLOR" value="3A3835"/>
  </colors>

  <attributes>
    <!-- ==================== General ==================== -->
    <option name="TEXT">
      <value>
        <option name="FOREGROUND" value="C4C7C1"/>
        <option name="BACKGROUND" value="1C1C1C"/>
      </value>
    </option>

    <!-- ==================== Syntax ==================== -->
    <option name="DEFAULT_KEYWORD">
      <value>
        <option name="FOREGROUND" value="D75455"/>
      </value>
    </option>
    <option name="DEFAULT_FUNCTION_DECLARATION">
      <value>
        <option name="FOREGROUND" value="E2943B"/>
      </value>
    </option>
    <option name="DEFAULT_FUNCTION_CALL">
      <value>
        <option name="FOREGROUND" value="E2943B"/>
      </value>
    </option>
    <option name="DEFAULT_STRING">
      <value>
        <option name="FOREGROUND" value="7BA23F"/>
      </value>
    </option>
    <option name="DEFAULT_VALID_STRING_ESCAPE">
      <value>
        <option name="FOREGROUND" value="C7802D"/>
      </value>
    </option>
    <option name="DEFAULT_INVALID_STRING_ESCAPE">
      <value>
        <option name="FOREGROUND" value="CB4042"/>
        <option name="EFFECT_TYPE" value="1"/>
        <option name="EFFECT_COLOR" value="CB4042"/>
      </value>
    </option>
    <option name="DEFAULT_NUMBER">
      <value>
        <option name="FOREGROUND" value="8B81C3"/>
      </value>
    </option>
    <option name="DEFAULT_CONSTANT">
      <value>
        <option name="FOREGROUND" value="C7802D"/>
      </value>
    </option>
    <option name="DEFAULT_PREDEFINED_SYMBOL">
      <value>
        <option name="FOREGROUND" value="C7802D"/>
      </value>
    </option>
    <option name="DEFAULT_CLASS_NAME">
      <value>
        <option name="FOREGROUND" value="58B2DC"/>
      </value>
    </option>
    <option name="DEFAULT_INTERFACE_NAME">
      <value>
        <option name="FOREGROUND" value="58B2DC"/>
      </value>
    </option>
    <option name="DEFAULT_CLASS_REFERENCE">
      <value>
        <option name="FOREGROUND" value="58B2DC"/>
      </value>
    </option>
    <option name="DEFAULT_IDENTIFIER">
      <value>
        <option name="FOREGROUND" value="C4C7C1"/>
      </value>
    </option>
    <option name="DEFAULT_INSTANCE_FIELD">
      <value>
        <option name="FOREGROUND" value="C4C7C1"/>
      </value>
    </option>
    <option name="DEFAULT_INSTANCE_METHOD">
      <value>
        <option name="FOREGROUND" value="E2943B"/>
      </value>
    </option>
    <option name="DEFAULT_STATIC_FIELD">
      <value>
        <option name="FOREGROUND" value="C7802D"/>
      </value>
    </option>
    <option name="DEFAULT_STATIC_METHOD">
      <value>
        <option name="FOREGROUND" value="E2943B"/>
        <option name="FONT_TYPE" value="2"/>
      </value>
    </option>
    <option name="DEFAULT_PARAMETER">
      <value>
        <option name="FOREGROUND" value="C4C7C1"/>
      </value>
    </option>
    <option name="DEFAULT_LOCAL_VARIABLE">
      <value>
        <option name="FOREGROUND" value="C4C7C1"/>
      </value>
    </option>
    <option name="DEFAULT_GLOBAL_VARIABLE">
      <value>
        <option name="FOREGROUND" value="C4C7C1"/>
      </value>
    </option>
    <option name="DEFAULT_METADATA">
      <value>
        <option name="FOREGROUND" value="C7802D"/>
      </value>
    </option>

    <!-- Comments -->
    <option name="DEFAULT_LINE_COMMENT">
      <value>
        <option name="FOREGROUND" value="9E7A7A"/>
      </value>
    </option>
    <option name="DEFAULT_BLOCK_COMMENT">
      <value>
        <option name="FOREGROUND" value="9E7A7A"/>
      </value>
    </option>
    <option name="DEFAULT_DOC_COMMENT">
      <value>
        <option name="FOREGROUND" value="9E7A7A"/>
      </value>
    </option>
    <option name="DEFAULT_DOC_COMMENT_TAG">
      <value>
        <option name="FOREGROUND" value="C4C7C1"/>
      </value>
    </option>
    <option name="DEFAULT_DOC_MARKUP">
      <value>
        <option name="FOREGROUND" value="9E7A7A"/>
      </value>
    </option>
    <option name="DEFAULT_DOC_COMMENT_TAG_VALUE">
      <value>
        <option name="FOREGROUND" value="C4C7C1"/>
      </value>
    </option>

    <!-- Operators and punctuation -->
    <option name="DEFAULT_OPERATION_SIGN">
      <value>
        <option name="FOREGROUND" value="a9918f"/>
      </value>
    </option>
    <option name="DEFAULT_BRACKETS">
      <value>
        <option name="FOREGROUND" value="a9918f"/>
      </value>
    </option>
    <option name="DEFAULT_PARENTHS">
      <value>
        <option name="FOREGROUND" value="a9918f"/>
      </value>
    </option>
    <option name="DEFAULT_BRACES">
      <value>
        <option name="FOREGROUND" value="a9918f"/>
      </value>
    </option>
    <option name="DEFAULT_DOT">
      <value>
        <option name="FOREGROUND" value="a9918f"/>
      </value>
    </option>
    <option name="DEFAULT_COMMA">
      <value>
        <option name="FOREGROUND" value="a9918f"/>
      </value>
    </option>
    <option name="DEFAULT_SEMICOLON">
      <value>
        <option name="FOREGROUND" value="a9918f"/>
      </value>
    </option>

    <!-- Labels and tags -->
    <option name="DEFAULT_LABEL">
      <value>
        <option name="FOREGROUND" value="D75455"/>
      </value>
    </option>
    <option name="DEFAULT_TAG">
      <value>
        <option name="FOREGROUND" value="58B2DC"/>
      </value>
    </option>
    <option name="DEFAULT_ATTRIBUTE">
      <value>
        <option name="FOREGROUND" value="E2943B"/>
      </value>
    </option>
    <option name="DEFAULT_ENTITY">
      <value>
        <option name="FOREGROUND" value="C7802D"/>
      </value>
    </option>

    <!-- Markup -->
    <option name="DEFAULT_TEMPLATE_LANGUAGE_COLOR">
      <value>
        <option name="FOREGROUND" value="D75455"/>
      </value>
    </option>

    <!-- ==================== Errors / Warnings ==================== -->
    <option name="ERRORS_ATTRIBUTES">
      <value>
        <option name="EFFECT_COLOR" value="CB4042"/>
        <option name="ERROR_STRIPE_COLOR" value="CB4042"/>
        <option name="EFFECT_TYPE" value="1"/>
      </value>
    </option>
    <option name="WARNING_ATTRIBUTES">
      <value>
        <option name="EFFECT_COLOR" value="E2943B"/>
        <option name="ERROR_STRIPE_COLOR" value="E2943B"/>
        <option name="EFFECT_TYPE" value="1"/>
      </value>
    </option>
    <option name="INFO_ATTRIBUTES">
      <value>
        <option name="EFFECT_COLOR" value="58B2DC"/>
        <option name="EFFECT_TYPE" value="1"/>
      </value>
    </option>
    <option name="DEPRECATED_ATTRIBUTES">
      <value>
        <option name="EFFECT_COLOR" value="9E7A7A"/>
        <option name="EFFECT_TYPE" value="5"/>
      </value>
    </option>
    <option name="UNUSED_SYMBOL">
      <value>
        <option name="FOREGROUND" value="9E7A7A"/>
        <option name="EFFECT_TYPE" value="1"/>
      </value>
    </option>
    <option name="WRONG_REFERENCES_ATTRIBUTES">
      <value>
        <option name="FOREGROUND" value="CB4042"/>
        <option name="EFFECT_COLOR" value="CB4042"/>
        <option name="EFFECT_TYPE" value="1"/>
      </value>
    </option>
    <option name="DUPLICATE_FROM_SERVER">
      <value>
        <option name="EFFECT_COLOR" value="E2943B"/>
        <option name="EFFECT_TYPE" value="1"/>
      </value>
    </option>

    <!-- ==================== Matched/Unmatched Braces ==================== -->
    <option name="MATCHED_BRACE_ATTRIBUTES">
      <value>
        <option name="FOREGROUND" value="C4C7C1"/>
        <option name="BACKGROUND" value="3A3835"/>
        <option name="FONT_TYPE" value="1"/>
      </value>
    </option>
    <option name="UNMATCHED_BRACE_ATTRIBUTES">
      <value>
        <option name="FOREGROUND" value="CB4042"/>
        <option name="BACKGROUND" value="CB40421a"/>
        <option name="FONT_TYPE" value="1"/>
      </value>
    </option>

    <!-- ==================== Search results ==================== -->
    <option name="SEARCH_RESULT_ATTRIBUTES">
      <value>
        <option name="BACKGROUND" value="D7545440"/>
        <option name="ERROR_STRIPE_COLOR" value="D75455"/>
      </value>
    </option>
    <option name="WRITE_SEARCH_RESULT_ATTRIBUTES">
      <value>
        <option name="BACKGROUND" value="D7545460"/>
        <option name="ERROR_STRIPE_COLOR" value="D75455"/>
      </value>
    </option>
    <option name="TEXT_SEARCH_RESULT_ATTRIBUTES">
      <value>
        <option name="BACKGROUND" value="D7545430"/>
        <option name="ERROR_STRIPE_COLOR" value="D75455"/>
      </value>
    </option>

    <!-- ==================== TODO ==================== -->
    <option name="TODO_DEFAULT_ATTRIBUTES">
      <value>
        <option name="FOREGROUND" value="C4C7C1"/>
        <option name="FONT_TYPE" value="2"/>
        <option name="ERROR_STRIPE_COLOR" value="E2943B"/>
      </value>
    </option>

    <!-- ==================== Hyperlinks ==================== -->
    <option name="HYPERLINK_ATTRIBUTES">
      <value>
        <option name="FOREGROUND" value="58B2DC"/>
        <option name="EFFECT_COLOR" value="58B2DC"/>
        <option name="EFFECT_TYPE" value="1"/>
      </value>
    </option>
    <option name="FOLLOWED_HYPERLINK_ATTRIBUTES">
      <value>
        <option name="FOREGROUND" value="8B81C3"/>
        <option name="EFFECT_COLOR" value="8B81C3"/>
        <option name="EFFECT_TYPE" value="1"/>
      </value>
    </option>

    <!-- ==================== Injected language ==================== -->
    <option name="INJECTED_LANGUAGE_FRAGMENT">
      <value>
        <option name="BACKGROUND" value="262626"/>
      </value>
    </option>

    <!-- ==================== Inline hints ==================== -->
    <option name="INLINE_PARAMETER_HINT">
      <value>
        <option name="FOREGROUND" value="9E7A7A"/>
        <option name="BACKGROUND" value="3A3835"/>
      </value>
    </option>
    <option name="INLINE_PARAMETER_HINT_HIGHLIGHTED">
      <value>
        <option name="FOREGROUND" value="C4C7C1"/>
        <option name="BACKGROUND" value="3A3835"/>
      </value>
    </option>
    <option name="INLINE_PARAMETER_HINT_CURRENT">
      <value>
        <option name="FOREGROUND" value="C4C7C1"/>
        <option name="BACKGROUND" value="D7545440"/>
      </value>
    </option>

    <!-- ==================== Identifier under caret ==================== -->
    <option name="IDENTIFIER_UNDER_CARET_ATTRIBUTES">
      <value>
        <option name="BACKGROUND" value="3A3835"/>
        <option name="ERROR_STRIPE_COLOR" value="C4C7C1"/>
      </value>
    </option>
    <option name="WRITE_IDENTIFIER_UNDER_CARET_ATTRIBUTES">
      <value>
        <option name="BACKGROUND" value="3A3835"/>
        <option name="ERROR_STRIPE_COLOR" value="E2943B"/>
      </value>
    </option>

    <!-- ==================== HTML/XML ==================== -->
    <option name="HTML_TAG_NAME">
      <value>
        <option name="FOREGROUND" value="58B2DC"/>
      </value>
    </option>
    <option name="HTML_ATTRIBUTE_NAME">
      <value>
        <option name="FOREGROUND" value="E2943B"/>
      </value>
    </option>
    <option name="HTML_ATTRIBUTE_VALUE">
      <value>
        <option name="FOREGROUND" value="7BA23F"/>
      </value>
    </option>
    <option name="HTML_ENTITY_REFERENCE">
      <value>
        <option name="FOREGROUND" value="C7802D"/>
      </value>
    </option>
    <option name="XML_TAG_NAME">
      <value>
        <option name="FOREGROUND" value="58B2DC"/>
      </value>
    </option>
    <option name="XML_ATTRIBUTE_NAME">
      <value>
        <option name="FOREGROUND" value="E2943B"/>
      </value>
    </option>
    <option name="XML_ATTRIBUTE_VALUE">
      <value>
        <option name="FOREGROUND" value="7BA23F"/>
      </value>
    </option>
    <option name="XML_TAG_DATA">
      <value>
        <option name="FOREGROUND" value="C4C7C1"/>
      </value>
    </option>
    <option name="XML_ENTITY_REFERENCE">
      <value>
        <option name="FOREGROUND" value="C7802D"/>
      </value>
    </option>

    <!-- ==================== C/C++ (CLion) ==================== -->
    <option name="OC.DIRECTIVE">
      <value>
        <option name="FOREGROUND" value="9E7A7A"/>
      </value>
    </option>
    <option name="OC.MACRO">
      <value>
        <option name="FOREGROUND" value="D75455"/>
      </value>
    </option>
    <option name="OC.STRUCT_FIELD">
      <value>
        <option name="FOREGROUND" value="C4C7C1"/>
      </value>
    </option>
    <option name="OC.ENUM_CONST">
      <value>
        <option name="FOREGROUND" value="C7802D"/>
      </value>
    </option>
    <option name="OC.CONCEPT">
      <value>
        <option name="FOREGROUND" value="58B2DC"/>
        <option name="FONT_TYPE" value="2"/>
      </value>
    </option>
    <option name="OC.TYPEDEF">
      <value>
        <option name="FOREGROUND" value="58B2DC"/>
      </value>
    </option>
    <option name="OC.STRUCT_LIKE">
      <value>
        <option name="FOREGROUND" value="58B2DC"/>
      </value>
    </option>
    <option name="OC.LABEL">
      <value>
        <option name="FOREGROUND" value="D75455"/>
      </value>
    </option>
    <option name="OC.OVERLOADED_OPERATOR">
      <value>
        <option name="FOREGROUND" value="E2943B"/>
      </value>
    </option>

    <!-- ==================== C# (Rider) ==================== -->
    <option name="CSHARP_KEYWORD">
      <value>
        <option name="FOREGROUND" value="D75455"/>
      </value>
    </option>
    <option name="CSHARP_CLASS_IDENTIFIER">
      <value>
        <option name="FOREGROUND" value="58B2DC"/>
      </value>
    </option>
    <option name="CSHARP_STRUCT_IDENTIFIER">
      <value>
        <option name="FOREGROUND" value="58B2DC"/>
      </value>
    </option>
    <option name="CSHARP_INTERFACE_IDENTIFIER">
      <value>
        <option name="FOREGROUND" value="58B2DC"/>
      </value>
    </option>
    <option name="CSHARP_ENUM_IDENTIFIER">
      <value>
        <option name="FOREGROUND" value="58B2DC"/>
      </value>
    </option>
    <option name="CSHARP_METHOD_IDENTIFIER">
      <value>
        <option name="FOREGROUND" value="E2943B"/>
      </value>
    </option>
    <option name="CSHARP_FIELD_IDENTIFIER">
      <value>
        <option name="FOREGROUND" value="C4C7C1"/>
      </value>
    </option>
    <option name="CSHARP_PROPERTY_IDENTIFIER">
      <value>
        <option name="FOREGROUND" value="C4C7C1"/>
      </value>
    </option>
    <option name="CSHARP_PARAMETER_IDENTIFIER">
      <value>
        <option name="FOREGROUND" value="C4C7C1"/>
      </value>
    </option>
    <option name="CSHARP_LOCAL_VARIABLE_IDENTIFIER">
      <value>
        <option name="FOREGROUND" value="C4C7C1"/>
      </value>
    </option>
    <option name="CSHARP_NAMESPACE_IDENTIFIER">
      <value>
        <option name="FOREGROUND" value="a9918f"/>
      </value>
    </option>
    <option name="CSHARP_STRING_ESCAPE">
      <value>
        <option name="FOREGROUND" value="C7802D"/>
      </value>
    </option>

    <!-- ==================== JSON ==================== -->
    <option name="JSON.PROPERTY_KEY">
      <value>
        <option name="FOREGROUND" value="D75455"/>
      </value>
    </option>
    <option name="JSON.STRING">
      <value>
        <option name="FOREGROUND" value="7BA23F"/>
      </value>
    </option>
    <option name="JSON.NUMBER">
      <value>
        <option name="FOREGROUND" value="8B81C3"/>
      </value>
    </option>
    <option name="JSON.KEYWORD">
      <value>
        <option name="FOREGROUND" value="C7802D"/>
      </value>
    </option>

    <!-- ==================== Markdown ==================== -->
    <option name="MARKDOWN_HEADER">
      <value>
        <option name="FOREGROUND" value="D75455"/>
        <option name="FONT_TYPE" value="1"/>
      </value>
    </option>
    <option name="MARKDOWN_BOLD">
      <value>
        <option name="FOREGROUND" value="a9918f"/>
        <option name="FONT_TYPE" value="1"/>
      </value>
    </option>
    <option name="MARKDOWN_ITALIC">
      <value>
        <option name="FOREGROUND" value="C4C7C1"/>
        <option name="FONT_TYPE" value="2"/>
      </value>
    </option>
    <option name="MARKDOWN_CODE_SPAN">
      <value>
        <option name="FOREGROUND" value="7BA23F"/>
      </value>
    </option>
    <option name="MARKDOWN_LINK_DESTINATION">
      <value>
        <option name="FOREGROUND" value="58B2DC"/>
      </value>
    </option>
    <option name="MARKDOWN_LINK_TEXT">
      <value>
        <option name="FOREGROUND" value="7BA23F"/>
      </value>
    </option>

    <!-- ==================== YAML ==================== -->
    <option name="YAML_SCALAR_KEY">
      <value>
        <option name="FOREGROUND" value="D75455"/>
      </value>
    </option>
    <option name="YAML_SCALAR_VALUE">
      <value>
        <option name="FOREGROUND" value="7BA23F"/>
      </value>
    </option>
    <option name="YAML_ANCHOR">
      <value>
        <option name="FOREGROUND" value="C7802D"/>
      </value>
    </option>
  </attributes>
</scheme>
```

- [ ] **Step 3: Test in sandbox IDE**

```bash
cd suannhai-jetbrains
./gradlew runIde
```

In the sandbox IDE: Settings > Appearance > Theme > select "Suannhai Sumi". Verify:
- Editor background is dark (`#1C1C1C`)
- Sidebar/panels use surface color (`#262626`)
- Syntax colors match the palette (open a C++ or JSON file)
- Tab underline uses keyword color (`#D75455`)
- Error underlines are red (`#CB4042`)

- [ ] **Step 4: Commit**

```bash
git add suannhai-jetbrains/src/main/resources/themes/suannhai_sumi.theme.json
git add "suannhai-jetbrains/src/main/resources/colorSchemes/Suannhai Sumi.xml"
git commit -m "feat(jetbrains): add Sumi dark theme"
```

---

### Task 4: Remaining 4 Dark Variants

Create the remaining dark themes: Rouiro, Koiai, Jiufen, Lam-ni. Each follows the exact same structure as Sumi (Task 3) with colors swapped from their respective palette JSON.

**Files:**
- Create: `suannhai-jetbrains/src/main/resources/themes/suannhai_rouiro.theme.json`
- Create: `suannhai-jetbrains/src/main/resources/colorSchemes/Suannhai Rouiro.xml`
- Create: `suannhai-jetbrains/src/main/resources/themes/suannhai_koiai.theme.json`
- Create: `suannhai-jetbrains/src/main/resources/colorSchemes/Suannhai Koiai.xml`
- Create: `suannhai-jetbrains/src/main/resources/themes/suannhai_jiufen.theme.json`
- Create: `suannhai-jetbrains/src/main/resources/colorSchemes/Suannhai Jiufen.xml`
- Create: `suannhai-jetbrains/src/main/resources/themes/suannhai_lam_ni.theme.json`
- Create: `suannhai-jetbrains/src/main/resources/colorSchemes/Suannhai Lam-ni.xml`

**Interfaces:**
- Consumes: Sumi theme from Task 3 as template; palettes from `colors/nippon-rouiro.json`, `colors/nippon-koiai.json`, `colors/formosa-jiufen.json`, `colors/formosa-lam-ni.json`
- Produces: 4 complete dark themes

**Color substitution table — copy Sumi's files and replace every color occurrence:**

| Role | Sumi | Rouiro | Koiai | Jiufen | Lam-ni |
|------|------|--------|-------|--------|--------|
| background | `1C1C1C` | `0C0C0C` | `0F2540` | `151A21` | `0E1A28` |
| surface | `262626` | `161616` | `16304E` | `252C36` | `172433` |
| border | `3A3835` | `2E2C2A` | `2E4560` | `3D4652` | `2A3D52` |
| comment | `9E7A7A` | `656255` | `77969A` | `6F7480` | `5E7085` |
| foreground | `C4C7C1` | `BDC0BA` | `BDC6D0` | `D6CFC4` | `C8D0D8` |
| keyword | `D75455` | `ED784A` | `F17C67` | `E05A4E` | `C4614F` |
| function | `E2943B` | `FFB11B` | `F9BF45` | `D9A441` | `D4A24C` |
| string | `7BA23F` | `5DAC81` | `69B0AC` | `7FA37A` | `6FA88C` |
| type | `58B2DC` | `33A6B8` | `7DB9DE` | `6FA6A8` | `7FB5D5` |
| number | `8B81C3` | `8B81C3` | `9B90C2` | `A98BB5` | `A192C4` |
| constant | `C7802D` | `CA7A2C` | `E79460` | `E08A50` | `D08A5C` |
| error | `CB4042` | `C73E3A` | `F75C2F` | `D64545` | `D45A52` |

Also update the muted/operator color (`a9918f` in Sumi) — this is a blend of comment and foreground. Derive similarly for each variant. Reference each variant's Zed theme for the exact muted color used.

- [ ] **Step 1: Create Rouiro theme files**

Copy Sumi's `.theme.json` and `.xml`, update:
- `"name": "Suannhai Rouiro"`, `"editorScheme": "/colorSchemes/Suannhai Rouiro.xml"`
- `parent_scheme="Darcula"` (stays same — dark)
- Replace all color values per the table above
- Muted/operator color: reference `suannhai-zed/themes/suannhai-rouiro.json` for the exact value

- [ ] **Step 2: Create Koiai theme files**

Same process as Step 1 with Koiai colors.

- [ ] **Step 3: Create Jiufen theme files**

Same process as Step 1 with Jiufen colors.

- [ ] **Step 4: Create Lam-ni theme files**

Same process as Step 1 with Lam-ni colors.

- [ ] **Step 5: Test all dark variants in sandbox**

```bash
cd suannhai-jetbrains
./gradlew runIde
```

Switch between all 5 dark themes in Settings > Appearance > Theme. Verify each has visually distinct colors matching its palette.

- [ ] **Step 6: Commit**

```bash
git add suannhai-jetbrains/src/main/resources/themes/ suannhai-jetbrains/src/main/resources/colorSchemes/
git commit -m "feat(jetbrains): add Rouiro, Koiai, Jiufen, Lam-ni dark themes"
```

---

### Task 5: 3 Light Variants

Create the 3 light themes: Torinoko, Shironeri, Hue-poo. These use `"dark": false` and `parent_scheme="Default"` instead of `"Darcula"`.

**Files:**
- Create: `suannhai-jetbrains/src/main/resources/themes/suannhai_torinoko.theme.json`
- Create: `suannhai-jetbrains/src/main/resources/colorSchemes/Suannhai Torinoko.xml`
- Create: `suannhai-jetbrains/src/main/resources/themes/suannhai_shironeri.theme.json`
- Create: `suannhai-jetbrains/src/main/resources/colorSchemes/Suannhai Shironeri.xml`
- Create: `suannhai-jetbrains/src/main/resources/themes/suannhai_hue_poo.theme.json`
- Create: `suannhai-jetbrains/src/main/resources/colorSchemes/Suannhai Hue-poo.xml`

**Interfaces:**
- Consumes: Sumi theme (Task 3) as structural template; palettes from `colors/nippon-torinoko.json`, `colors/nippon-shironeri.json`, `colors/formosa-hue-poo.json`
- Produces: 3 complete light themes

**Key differences from dark themes:**
- `.theme.json`: `"dark": false`
- `.xml`: `parent_scheme="Default"` instead of `"Darcula"`
- Background is light, foreground is dark — all UI color semantics are inverted
- Reference each variant's Zed theme to see how hover/selection alpha values differ for light backgrounds

**Color substitution table:**

| Role | Torinoko | Shironeri | Hue-poo |
|------|----------|-----------|---------|
| background | `FFF1CF` | `FCFAF2` | `FDF6EE` |
| surface | `F7E7C4` | `F5F2E8` | `F5EADD` |
| border | `D4C4A0` | `BDC0BA` | `D9CBB8` |
| comment | `8A7A5E` | `8C8578` | `8C8073` |
| foreground | `3A3226` | `2C2A26` | `3A3028` |
| keyword | `973C3F` | `973C3F` | `B03A50` |
| function | `BF783A` | `A86520` | `B5721E` |
| string | `454D32` | `227D51` | `4E7A46` |
| type | `165E83` | `165E83` | `2A5F87` |
| number | `745399` | `745399` | `A8506E` |
| constant | `8F4B38` | `9C5A38` | `B0552E` |
| error | `A03030` | `A03030` | `B03030` |

- [ ] **Step 1: Create Torinoko theme files**

Copy Sumi's structure, set `"dark": false`, `parent_scheme="Default"`, apply Torinoko colors. Reference `suannhai-zed/themes/suannhai-torinoko.json` for muted/operator color and alpha values.

- [ ] **Step 2: Create Shironeri theme files**

Same process with Shironeri colors.

- [ ] **Step 3: Create Hue-poo theme files**

Same process with Hue-poo colors.

- [ ] **Step 4: Test all light variants in sandbox**

```bash
cd suannhai-jetbrains
./gradlew runIde
```

Switch between all 3 light themes. Verify light backgrounds, dark foreground text, and that contrast is readable.

- [ ] **Step 5: Commit**

```bash
git add suannhai-jetbrains/src/main/resources/themes/ suannhai-jetbrains/src/main/resources/colorSchemes/
git commit -m "feat(jetbrains): add Torinoko, Shironeri, Hue-poo light themes"
```

---

### Task 6: Build Verification and Final Polish

**Files:**
- Modify: Any theme files needing adjustment after testing

**Interfaces:**
- Consumes: All themes from Tasks 3-5, plugin setup from Tasks 1-2
- Produces: A verified, buildable `.zip` ready for Marketplace upload

- [ ] **Step 1: Build the plugin**

```bash
cd suannhai-jetbrains
./gradlew clean buildPlugin
```

Expected: `build/distributions/suannhai-jetbrains-0.1.0.zip` is created.

- [ ] **Step 2: Verify ZIP contents**

```bash
cd suannhai-jetbrains
unzip -l build/distributions/suannhai-jetbrains-0.1.0.zip
```

Expected: Contains `lib/suannhai-jetbrains-0.1.0.jar` with all theme files inside.

- [ ] **Step 3: Launch sandbox and test all 8 themes**

```bash
cd suannhai-jetbrains
./gradlew runIde
```

For each of the 8 themes, verify:
- Theme appears in Settings > Appearance > Theme dropdown
- Editor background and foreground colors are correct
- Syntax highlighting works (open a C++, C#, JSON, and Markdown file)
- Tab underline color matches keyword accent
- VCS gutter colors work (green added, blue modified, red deleted)
- Error underlines show in red
- Search highlighting is visible

- [ ] **Step 4: Fix any visual issues found during testing**

Adjust colors in the relevant `.theme.json` or `.xml` files.

- [ ] **Step 5: Final commit**

```bash
git add suannhai-jetbrains/
git commit -m "feat(jetbrains): finalize and verify all 8 theme variants"
```
