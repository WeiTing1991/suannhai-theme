# suannhai.nvim -- Neovim Colorscheme Plugin Design

## Summary

A Neovim colorscheme plugin for the Suannhai theme, following the tokyonight.nvim pattern. Provides all 8 curated color variants (3 Formosa + 5 Nippon) with `setup()` config, transparent mode, user hooks (`on_colors`, `on_highlights`), and plugin autodetection via lazy.nvim.

## Source of Truth

The canonical color definitions live in `colors/*.json` at the monorepo root. Each JSON file defines:
- 5 neutrals: `background`, `surface`, `border`, `comment`, `foreground`
- 6 accents: `keyword`, `function`, `string`, `type`, `number`, `constant`
- 1 diagnostic: `error`
- Metadata: `name`, `appearance` (dark/light)

The Lua palette files in the plugin are a direct transcription of these JSON values.

## File Structure

```
suannhai-nvim/
  colors/
    suannhai-jiufen.lua
    suannhai-lam-ni.lua
    suannhai-hue-poo.lua
    suannhai-rouiro.lua
    suannhai-sumi.lua
    suannhai-koiai.lua
    suannhai-torinoko.lua
    suannhai-shironeri.lua
  lua/
    suannhai/
      init.lua
      config.lua
      theme.lua
      util.lua
      palettes/
        init.lua
        jiufen.lua
        lam-ni.lua
        hue-poo.lua
        rouiro.lua
        sumi.lua
        koiai.lua
        torinoko.lua
        shironeri.lua
      groups/
        init.lua
        base.lua
        syntax.lua
        treesitter.lua
        semantic_tokens.lua
        terminal.lua
        gitsigns.lua
        telescope.lua
        blink.lua
        snacks.lua
        lazy.lua
        neo-tree.lua
        mini.lua
        fzf.lua
  README.md
```

## API

### Entry Points

Each `colors/suannhai-<variant>.lua` file is a one-liner:

```lua
require("suannhai").load("<variant>")
```

Users activate via `:colorscheme suannhai-jiufen` (or any variant name).

### setup()

Optional. Calling `setup()` before loading a colorscheme configures behavior:

```lua
require("suannhai").setup({
  transparent = false,
  on_colors = function(colors) end,
  on_highlights = function(hl, colors) end,
  plugins = {
    all = true,
    auto = true,
  },
})
```

- `transparent` (bool): sets editor/float/sidebar backgrounds to `NONE`
- `on_colors` (function): receives the palette table before highlight groups are built; user can mutate values
- `on_highlights` (function): receives the merged highlights table and palette after all groups are built; user can override any highlight
- `plugins.all` (bool): enable all plugin highlight groups
- `plugins.auto` (bool): auto-detect installed plugins via lazy.nvim
- Per-plugin overrides: `plugins.telescope = false` to disable a specific group

### load() Flow

1. Read config (merged defaults + user opts)
2. Deep-copy the palette for the requested variant
3. Compute derived colors (diff backgrounds, terminal colors, line_nr, selection, etc.)
4. Call `on_colors(palette)` if provided
5. Collect highlight groups: core groups always load, plugin groups based on config
6. Call `on_highlights(highlights, palette)` if provided
7. Apply all highlights via `vim.api.nvim_set_hl(0, group, hl)`
8. Set terminal colors via `vim.g.terminal_color_N`
9. Set `vim.g.colors_name = "suannhai-<variant>"`

## Palette Structure

Each palette Lua file returns a flat table:

```lua
return {
  -- Neutrals (from JSON)
  bg        = "#151A21",
  surface   = "#252C36",
  border    = "#3D4652",
  comment   = "#6F7480",
  fg        = "#D6CFC4",

  -- Accents (from JSON)
  keyword   = "#E05A4E",
  func      = "#D9A441",
  string    = "#7FA37A",
  type      = "#6FA6A8",
  number    = "#A98BB5",
  constant  = "#E08A50",

  -- Diagnostic (from JSON)
  error     = "#D64545",

  -- Metadata
  appearance = "dark",
}
```

The `palettes/init.lua` loader computes derived values from the base palette:

- `bg_dark`: slightly darker than `bg` (blend toward black)
- `selection`: blend of `border` with lower opacity
- `line_nr`: blend of `comment` toward `bg`
- `diff.add`, `diff.delete`, `diff.change`, `diff.text`: subtle tinted backgrounds using accent colors
- `warning`, `info`, `hint`, `ok`: derived from accents (function/yellow for warning, type/blue for info, comment for hint, string/green for ok)
- `terminal.*`: 16 ANSI colors mapped from the palette accents and neutrals

## Highlight Groups

### Core Groups (always loaded)

**base.lua** -- Editor UI highlights:
- Normal, NormalFloat, NormalNC
- Cursor, CursorLine, CursorLineNr, LineNr
- Visual, Search, IncSearch, CurSearch
- Pmenu, PmenuSel, PmenuSbar, PmenuThumb
- StatusLine, StatusLineNC, TabLine, TabLineSel
- SignColumn, FoldColumn, ColorColumn
- DiffAdd, DiffChange, DiffDelete, DiffText
- DiagnosticError/Warn/Info/Hint + underline variants
- FloatBorder, WinSeparator, VertSplit
- SpellBad, SpellCap, SpellLocal, SpellRare
- Directory, Title, MatchParen, NonText, SpecialKey

**syntax.lua** -- Vim syntax highlights:
- Comment, Constant, String, Number, Boolean, Float
- Identifier, Function, Statement, Keyword
- Operator, PreProc, Include, Define
- Type, Structure, StorageClass, Typedef
- Special, SpecialChar, Delimiter
- Error, Todo, Underlined
- Variable, Property

**treesitter.lua** -- Treesitter captures:
- `@keyword`, `@keyword.*` -> keyword color
- `@function`, `@function.*` -> func color
- `@string`, `@string.*` -> string color
- `@type`, `@type.*` -> type color
- `@number`, `@number.*` -> number color
- `@constant`, `@constant.*` -> constant color
- `@variable`, `@variable.*` -> fg/fg variants
- `@comment`, `@comment.*` -> comment color
- `@punctuation.*` -> muted fg
- `@tag`, `@tag.*` -> type color (for HTML/JSX)
- `@markup.*` -> appropriate mappings for markdown

**semantic_tokens.lua** -- LSP semantic token highlights:
- Links to treesitter groups where appropriate
- Specific overrides for decorator, macro, etc.

**terminal.lua** -- Terminal ANSI colors:
- Maps the 16 ANSI colors (0-15) from palette accents and neutrals
- Black = bg, White = fg, Red = error, Green = string, Yellow = func, Blue = type, Magenta = number, Cyan = type (bright variant), with bright versions computed via util.brighten

### Plugin Groups

Each plugin group file exports `get(colors, opts)` returning a highlight table.

**gitsigns.lua**: GitSignsAdd, GitSignsChange, GitSignsDelete and their line/number variants
**telescope.lua**: TelescopeNormal, TelescopeBorder, TelescopePrompt*, TelescopeSelection, TelescopeMatching
**fzf.lua**: FzfLuaNormal, FzfLuaBorder, FzfLuaTitle, etc.
**blink.lua**: BlinkCmpMenu, BlinkCmpMenuSelection, BlinkCmpLabel, kind highlights
**snacks.lua**: SnacksNormal, SnacksBorder, SnacksTitle, dashboard highlights
**lazy.lua**: LazyButton, LazyH1, LazySpecial, LazyProgressDone/Todo
**neo-tree.lua**: NeoTreeNormal, NeoTreeDirectoryIcon/Name, NeoTreeGitAdded/Modified/Deleted
**mini.lua**: MiniStatusline*, MiniTabline*, MiniCursorword, MiniIndentscopeSymbol

## Variants

| Variant    | Appearance | Entry File                  |
|------------|------------|-----------------------------|
| jiufen     | dark       | colors/suannhai-jiufen.lua  |
| lam-ni     | dark       | colors/suannhai-lam-ni.lua  |
| hue-poo    | light      | colors/suannhai-hue-poo.lua |
| rouiro     | dark       | colors/suannhai-rouiro.lua  |
| sumi       | dark       | colors/suannhai-sumi.lua    |
| koiai      | dark       | colors/suannhai-koiai.lua   |
| torinoko   | light      | colors/suannhai-torinoko.lua|
| shironeri  | light      | colors/suannhai-shironeri.lua|

## Repository Strategy

The plugin lives in its own repo: `WeiTing1991/suannhai.nvim`

In the monorepo (`suannhai-theme`), the `suannhai-nvim/` directory is a **git submodule** pointing to that repo. This means:
- The plugin repo has `lua/` and `colors/` at its root -- plugin managers work out of the box
- The monorepo keeps all editor themes visible in one place via submodules
- Development can happen in either repo; changes sync via submodule update

### Setup steps (one-time)
1. Create GitHub repo `WeiTing1991/suannhai.nvim`
2. Push plugin code to the new repo
3. Remove existing `suannhai-nvim/` from the monorepo
4. Add it back as a submodule: `git submodule add git@github.com:WeiTing1991/suannhai.nvim.git suannhai-nvim`

## Installation (README)

```lua
-- lazy.nvim
{
  "WeiTing1991/suannhai.nvim",
  lazy = false,
  priority = 1000,
  config = function()
    require("suannhai").setup({})
    vim.cmd.colorscheme("suannhai-jiufen")
  end,
}
```

## Out of Scope (for now)

- Lualine theme integration
- Extras generation (alacritty, kitty, etc.)
- Caching
- `dim_inactive`
- Style overrides for comments/keywords/functions/variables (italic, bold)
- `day_brightness` equivalent (palettes are curated, not computed)
