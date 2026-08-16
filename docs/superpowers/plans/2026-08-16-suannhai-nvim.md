# suannhai.nvim Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Neovim colorscheme plugin with 8 curated color variants following the tokyonight.nvim pattern, distributed as a standalone repo linked to the monorepo via git submodule.

**Architecture:** Lua plugin with `setup()`/`load()` entry points. Each variant has a palette file transcribed from the canonical JSON color definitions. Highlight groups are modular (base, syntax, treesitter, semantic_tokens, terminal + 8 plugin groups) and collected by a group loader with lazy.nvim autodetection.

**Tech Stack:** Lua (Neovim API), no external dependencies

## Global Constraints

- All hex values come verbatim from `colors/*.json` in the monorepo -- no inventing colors
- Plugin must work without calling `setup()` (sensible defaults)
- All files go under `suannhai-nvim/` in the monorepo during development; this directory becomes the standalone repo root
- Follow tokyonight/luna patterns for group module interface: `M.get(colors, opts)` returning a highlight table
- Every group module returns a plain table of `{ GroupName = { fg = ..., bg = ..., ... } }` or `{ GroupName = "LinkTarget" }`

---

### Task 1: Core Infrastructure (util.lua, config.lua, init.lua, theme.lua)

**Files:**
- Create: `suannhai-nvim/lua/suannhai/util.lua`
- Create: `suannhai-nvim/lua/suannhai/config.lua`
- Create: `suannhai-nvim/lua/suannhai/init.lua`
- Create: `suannhai-nvim/lua/suannhai/theme.lua`

**Interfaces:**
- Produces:
  - `util.blend(fg, bg, alpha)` -> `string` (hex color)
  - `util.blend_bg(color, alpha, bg)` -> `string`
  - `util.brighten(color, amount)` -> `string`
  - `util.mod(modname)` -> `table` (safe require wrapper)
  - `util.resolve(highlights)` -> `nil` (resolves string links in highlight table)
  - `config.defaults` -> `table` (default config)
  - `config.setup(opts)` -> `nil`
  - `config.extend(opts)` -> `table` (merged config)
  - `M.setup(opts)` (init.lua) -> `nil`
  - `M.load(style)` (init.lua) -> `nil`
  - `theme.setup(style, opts)` -> `colors, groups, opts`

- [ ] **Step 1: Create util.lua**

```lua
-- suannhai-nvim/lua/suannhai/util.lua
local M = {}

--- Convert hex string to RGB table
---@param hex string
---@return number, number, number
function M.hex_to_rgb(hex)
  hex = hex:gsub("#", "")
  return tonumber(hex:sub(1, 2), 16), tonumber(hex:sub(3, 4), 16), tonumber(hex:sub(5, 6), 16)
end

--- Convert RGB values to hex string
---@param r number
---@param g number
---@param b number
---@return string
function M.rgb_to_hex(r, g, b)
  return string.format("#%02x%02x%02x", math.floor(r + 0.5), math.floor(g + 0.5), math.floor(b + 0.5))
end

--- Blend two hex colors. alpha=0 returns bg, alpha=1 returns fg.
---@param fg string hex color
---@param bg string hex color
---@param alpha number 0-1
---@return string hex color
function M.blend(fg, bg, alpha)
  local r1, g1, b1 = M.hex_to_rgb(fg)
  local r2, g2, b2 = M.hex_to_rgb(bg)
  local r = r1 * alpha + r2 * (1 - alpha)
  local g = g1 * alpha + g2 * (1 - alpha)
  local b = b1 * alpha + b2 * (1 - alpha)
  return M.rgb_to_hex(r, g, b)
end

--- Blend a color toward a background color
---@param color string hex color
---@param alpha number 0-1
---@param bg string hex background
---@return string hex color
function M.blend_bg(color, alpha, bg)
  return M.blend(color, bg, alpha)
end

--- Brighten a hex color by the given amount (0-1)
---@param color string hex color
---@param amount? number 0-1, default 0.3
---@return string hex color
function M.brighten(color, amount)
  amount = amount or 0.3
  return M.blend(color, "#ffffff", amount)
end

--- Darken a hex color by the given amount (0-1)
---@param color string hex color
---@param amount? number 0-1, default 0.3
---@return string hex color
function M.darken(color, amount)
  amount = amount or 0.3
  return M.blend(color, "#000000", amount)
end

--- Safely require a module
---@param modname string
---@return table
function M.mod(modname)
  local ok, mod = pcall(require, modname)
  if not ok then
    error("suannhai: failed to load module " .. modname .. ": " .. tostring(mod))
  end
  return mod
end

--- Resolve string links in a highlights table.
--- If a value is a string, replace it with { link = value }.
---@param highlights table
function M.resolve(highlights)
  for group, hl in pairs(highlights) do
    if type(hl) == "string" then
      highlights[group] = { link = hl }
    end
  end
end

return M
```

- [ ] **Step 2: Create config.lua**

```lua
-- suannhai-nvim/lua/suannhai/config.lua
local M = {}

---@class suannhai.Config
---@field transparent? boolean
---@field on_colors? fun(colors: table)
---@field on_highlights? fun(highlights: table, colors: table)
---@field plugins? table
M.defaults = {
  transparent = false,
  on_colors = function(colors) end,
  on_highlights = function(highlights, colors) end,
  plugins = {
    all = true,
    auto = true,
  },
}

---@type suannhai.Config
M.options = nil

---@param opts? suannhai.Config
function M.setup(opts)
  M.options = vim.tbl_deep_extend("force", {}, M.defaults, opts or {})
end

---@param opts? suannhai.Config
---@return suannhai.Config
function M.extend(opts)
  return opts and vim.tbl_deep_extend("force", {}, M.options or M.defaults, opts) or (M.options or M.defaults)
end

setmetatable(M, {
  __index = function(_, k)
    if k == "options" then
      return M.defaults
    end
  end,
})

return M
```

- [ ] **Step 3: Create theme.lua**

```lua
-- suannhai-nvim/lua/suannhai/theme.lua
local M = {}

---@param style string variant name (e.g. "jiufen")
---@param opts? suannhai.Config
function M.setup(style, opts)
  opts = require("suannhai.config").extend(opts)

  local colors = require("suannhai.palettes").setup(style, opts)
  local groups = require("suannhai.groups").setup(colors, opts)

  if vim.g.colors_name then
    vim.cmd("hi clear")
  end

  vim.o.termguicolors = true
  vim.g.colors_name = "suannhai-" .. style

  for group, hl in pairs(groups) do
    hl = type(hl) == "string" and { link = hl } or hl
    vim.api.nvim_set_hl(0, group, hl)
  end

  if colors.terminal then
    for i = 0, 15 do
      vim.g["terminal_color_" .. i] = colors.terminal[i]
    end
  end

  return colors, groups, opts
end

return M
```

- [ ] **Step 4: Create init.lua**

```lua
-- suannhai-nvim/lua/suannhai/init.lua
local config = require("suannhai.config")

local M = {}

---@param opts? suannhai.Config
function M.setup(opts)
  config.setup(opts)
end

---@param style string variant name (e.g. "jiufen")
function M.load(style)
  local ok, err = pcall(function()
    return require("suannhai.theme").setup(style)
  end)
  if not ok then
    vim.notify("suannhai: failed to load colorscheme: " .. tostring(err), vim.log.levels.ERROR)
  end
end

return M
```

- [ ] **Step 5: Verify directory structure exists**

```bash
ls suannhai-nvim/lua/suannhai/
```

Expected: `init.lua  config.lua  theme.lua  util.lua`

- [ ] **Step 6: Commit**

```bash
git add suannhai-nvim/lua/suannhai/init.lua suannhai-nvim/lua/suannhai/config.lua suannhai-nvim/lua/suannhai/theme.lua suannhai-nvim/lua/suannhai/util.lua
git commit -m "feat(nvim): add core infrastructure (init, config, theme, util)"
```

---

### Task 2: Palette Files and Loader

**Files:**
- Create: `suannhai-nvim/lua/suannhai/palettes/init.lua`
- Create: `suannhai-nvim/lua/suannhai/palettes/jiufen.lua`
- Create: `suannhai-nvim/lua/suannhai/palettes/lam-ni.lua`
- Create: `suannhai-nvim/lua/suannhai/palettes/hue-poo.lua`
- Create: `suannhai-nvim/lua/suannhai/palettes/rouiro.lua`
- Create: `suannhai-nvim/lua/suannhai/palettes/sumi.lua`
- Create: `suannhai-nvim/lua/suannhai/palettes/koiai.lua`
- Create: `suannhai-nvim/lua/suannhai/palettes/torinoko.lua`
- Create: `suannhai-nvim/lua/suannhai/palettes/shironeri.lua`

**Interfaces:**
- Consumes: `util.blend_bg`, `util.brighten`, `util.darken`
- Produces: `palettes.setup(style, opts)` -> `table` (full palette with derived colors)

- [ ] **Step 1: Create palettes/jiufen.lua**

```lua
-- suannhai-nvim/lua/suannhai/palettes/jiufen.lua
---@class suannhai.Palette
return {
  bg        = "#151A21",
  surface   = "#252C36",
  border    = "#3D4652",
  comment   = "#6F7480",
  fg        = "#D6CFC4",

  keyword   = "#E05A4E",
  func      = "#D9A441",
  string    = "#7FA37A",
  type      = "#6FA6A8",
  number    = "#A98BB5",
  constant  = "#E08A50",

  error     = "#D64545",

  appearance = "dark",
}
```

- [ ] **Step 2: Create palettes/lam-ni.lua**

```lua
-- suannhai-nvim/lua/suannhai/palettes/lam-ni.lua
return {
  bg        = "#0E1A28",
  surface   = "#172433",
  border    = "#2A3D52",
  comment   = "#5E7085",
  fg        = "#C8D0D8",

  keyword   = "#C4614F",
  func      = "#D4A24C",
  string    = "#6FA88C",
  type      = "#7FB5D5",
  number    = "#A192C4",
  constant  = "#D08A5C",

  error     = "#D45A52",

  appearance = "dark",
}
```

- [ ] **Step 3: Create palettes/hue-poo.lua**

```lua
-- suannhai-nvim/lua/suannhai/palettes/hue-poo.lua
return {
  bg        = "#FDF6EE",
  surface   = "#F5EADD",
  border    = "#D9CBB8",
  comment   = "#8C8073",
  fg        = "#3A3028",

  keyword   = "#B03A50",
  func      = "#B5721E",
  string    = "#4E7A46",
  type      = "#2A5F87",
  number    = "#A8506E",
  constant  = "#B0552E",

  error     = "#B03030",

  appearance = "light",
}
```

- [ ] **Step 4: Create palettes/rouiro.lua**

```lua
-- suannhai-nvim/lua/suannhai/palettes/rouiro.lua
return {
  bg        = "#0C0C0C",
  surface   = "#161616",
  border    = "#2E2C2A",
  comment   = "#656255",
  fg        = "#BDC0BA",

  keyword   = "#ED784A",
  func      = "#FFB11B",
  string    = "#5DAC81",
  type      = "#33A6B8",
  number    = "#8B81C3",
  constant  = "#CA7A2C",

  error     = "#C73E3A",

  appearance = "dark",
}
```

- [ ] **Step 5: Create palettes/sumi.lua**

```lua
-- suannhai-nvim/lua/suannhai/palettes/sumi.lua
return {
  bg        = "#1C1C1C",
  surface   = "#262626",
  border    = "#3A3835",
  comment   = "#9E7A7A",
  fg        = "#C4C7C1",

  keyword   = "#D75455",
  func      = "#E2943B",
  string    = "#7BA23F",
  type      = "#58B2DC",
  number    = "#8B81C3",
  constant  = "#C7802D",

  error     = "#CB4042",

  appearance = "dark",
}
```

- [ ] **Step 6: Create palettes/koiai.lua**

```lua
-- suannhai-nvim/lua/suannhai/palettes/koiai.lua
return {
  bg        = "#0F2540",
  surface   = "#16304E",
  border    = "#2E4560",
  comment   = "#77969A",
  fg        = "#BDC6D0",

  keyword   = "#F17C67",
  func      = "#F9BF45",
  string    = "#69B0AC",
  type      = "#7DB9DE",
  number    = "#9B90C2",
  constant  = "#E79460",

  error     = "#F75C2F",

  appearance = "dark",
}
```

- [ ] **Step 7: Create palettes/torinoko.lua**

```lua
-- suannhai-nvim/lua/suannhai/palettes/torinoko.lua
return {
  bg        = "#FFF1CF",
  surface   = "#F7E7C4",
  border    = "#D4C4A0",
  comment   = "#8A7A5E",
  fg        = "#3A3226",

  keyword   = "#973C3F",
  func      = "#BF783A",
  string    = "#454D32",
  type      = "#165E83",
  number    = "#745399",
  constant  = "#8F4B38",

  error     = "#A03030",

  appearance = "light",
}
```

- [ ] **Step 8: Create palettes/shironeri.lua**

```lua
-- suannhai-nvim/lua/suannhai/palettes/shironeri.lua
return {
  bg        = "#FCFAF2",
  surface   = "#F5F2E8",
  border    = "#BDC0BA",
  comment   = "#8C8578",
  fg        = "#2C2A26",

  keyword   = "#973C3F",
  func      = "#A86520",
  string    = "#227D51",
  type      = "#165E83",
  number    = "#745399",
  constant  = "#9C5A38",

  error     = "#A03030",

  appearance = "light",
}
```

- [ ] **Step 9: Create palettes/init.lua (loader with derived colors)**

```lua
-- suannhai-nvim/lua/suannhai/palettes/init.lua
local Util = require("suannhai.util")

local M = {}

---@param style string
---@param opts suannhai.Config
---@return table
function M.setup(style, opts)
  local raw = vim.deepcopy(Util.mod("suannhai.palettes." .. style))

  local is_light = raw.appearance == "light"

  -- Derived neutrals
  raw.bg_dark = is_light and Util.blend(raw.bg, "#ffffff", 0.7) or Util.darken(raw.bg, 0.15)
  raw.selection = Util.blend_bg(raw.border, 0.6, raw.bg)
  raw.line_nr = Util.blend_bg(raw.comment, 0.4, raw.bg)
  raw.cursor_line = Util.blend_bg(raw.surface, 0.5, raw.bg)

  -- Diagnostics derived from accents
  raw.warning = raw.func
  raw.info = raw.type
  raw.hint = raw.comment
  raw.ok = raw.string

  -- Diff backgrounds
  raw.diff = {
    add = Util.blend_bg(raw.string, 0.15, raw.bg),
    delete = Util.blend_bg(raw.error, 0.15, raw.bg),
    change = Util.blend_bg(raw.constant, 0.12, raw.bg),
    text = Util.blend_bg(raw.constant, 0.30, raw.bg),
  }

  -- Git colors (foreground)
  raw.git = {
    add = raw.string,
    delete = raw.error,
    change = raw.constant,
  }

  -- Terminal colors (ANSI 0-15), matching WezTerm mapping
  -- ansi: [surface, keyword, string, func, type, number, constant, fg]
  -- brights: [comment, bright_keyword, bright_string, bright_func, bright_type, bright_number, bright_constant, bright_fg]
  local bright_amount = is_light and 0.3 or 0.25
  raw.terminal = {
    [0]  = raw.surface,                              -- black
    [1]  = raw.keyword,                              -- red
    [2]  = raw.string,                               -- green
    [3]  = raw.func,                                 -- yellow
    [4]  = raw.type,                                 -- blue
    [5]  = raw.number,                               -- magenta
    [6]  = raw.constant,                             -- cyan
    [7]  = raw.fg,                                   -- white
    [8]  = raw.comment,                              -- bright black
    [9]  = Util.brighten(raw.keyword, bright_amount),  -- bright red
    [10] = Util.brighten(raw.string, bright_amount),   -- bright green
    [11] = Util.brighten(raw.func, bright_amount),     -- bright yellow
    [12] = Util.brighten(raw.type, bright_amount),     -- bright blue
    [13] = Util.brighten(raw.number, bright_amount),   -- bright magenta
    [14] = Util.brighten(raw.constant, bright_amount), -- bright cyan
    [15] = is_light and raw.bg or "#ffffff",           -- bright white
  }

  raw.none = "NONE"

  -- User hook
  if opts.on_colors then
    opts.on_colors(raw)
  end

  return raw
end

return M
```

- [ ] **Step 10: Commit**

```bash
git add suannhai-nvim/lua/suannhai/palettes/
git commit -m "feat(nvim): add 8 palette files and palette loader"
```

---

### Task 3: Core Highlight Groups (base, syntax, treesitter, semantic_tokens, terminal)

**Files:**
- Create: `suannhai-nvim/lua/suannhai/groups/base.lua`
- Create: `suannhai-nvim/lua/suannhai/groups/syntax.lua`
- Create: `suannhai-nvim/lua/suannhai/groups/treesitter.lua`
- Create: `suannhai-nvim/lua/suannhai/groups/semantic_tokens.lua`
- Create: `suannhai-nvim/lua/suannhai/groups/terminal.lua`
- Create: `suannhai-nvim/lua/suannhai/groups/init.lua`

**Interfaces:**
- Consumes: palette table from `palettes.setup()`, `config.extend()`, `util.resolve()`
- Produces: `groups.setup(colors, opts)` -> `table, table` (merged highlights, active group names)
- Each group module: `M.get(colors, opts)` -> `table`

- [ ] **Step 1: Create groups/base.lua**

```lua
-- suannhai-nvim/lua/suannhai/groups/base.lua
local M = {}

---@param c table palette
---@param opts suannhai.Config
---@return table
function M.get(c, opts)
  local transparent = opts.transparent

  return {
    Normal       = { fg = c.fg, bg = transparent and c.none or c.bg },
    NormalFloat  = { fg = c.fg, bg = transparent and c.none or c.surface },
    NormalNC     = { fg = c.fg, bg = transparent and c.none or c.bg },
    FloatBorder  = { fg = c.border, bg = transparent and c.none or c.surface },
    FloatTitle   = { fg = c.fg, bg = transparent and c.none or c.surface },

    Cursor       = { fg = c.bg, bg = c.fg },
    CursorLine   = { bg = transparent and c.none or c.cursor_line },
    CursorLineNr = { fg = c.fg },
    CursorColumn = { bg = transparent and c.none or c.cursor_line },
    LineNr       = { fg = c.line_nr },
    SignColumn   = { fg = c.comment },

    ColorColumn  = { bg = c.surface },
    Conceal      = { fg = c.comment },

    Visual       = { bg = c.selection },
    Search       = { fg = c.fg, bg = c.border },
    IncSearch    = { fg = c.bg, bg = c.constant },
    CurSearch    = { fg = c.bg, bg = c.constant },
    Substitute   = { fg = c.bg, bg = c.keyword },

    Pmenu        = { fg = c.fg, bg = c.surface },
    PmenuSel     = { bg = c.selection },
    PmenuSbar    = { bg = c.surface },
    PmenuThumb   = { bg = c.border },
    PmenuKind    = { fg = c.type, bg = c.surface },
    PmenuKindSel = { fg = c.type, bg = c.selection },

    StatusLine   = { fg = c.fg, bg = transparent and c.none or c.surface },
    StatusLineNC = { fg = c.comment, bg = transparent and c.none or c.surface },
    TabLine      = { fg = c.comment, bg = c.surface },
    TabLineFill  = { bg = c.bg },
    TabLineSel   = { fg = c.fg, bg = c.bg },

    WinBar       = { bg = transparent and c.none or c.bg },
    WinBarNC     = { bg = transparent and c.none or c.bg },
    WinSeparator = { fg = c.border },
    VertSplit    = { fg = c.border },

    Folded       = { fg = c.comment, bg = c.selection },
    FoldColumn   = { fg = c.comment, bg = transparent and c.none or c.bg },

    DiffAdd      = { fg = c.diff.add and nil, bg = c.diff.add },
    DiffChange   = { bg = c.diff.change },
    DiffDelete   = { fg = c.diff.delete and nil, bg = c.diff.delete },
    DiffText     = { bg = c.diff.text },

    DiagnosticError          = { fg = c.error },
    DiagnosticWarn           = { fg = c.warning },
    DiagnosticInfo           = { fg = c.info },
    DiagnosticHint           = { fg = c.hint },
    DiagnosticOk             = { fg = c.ok },
    DiagnosticUnderlineError = { undercurl = true, sp = c.error },
    DiagnosticUnderlineWarn  = { undercurl = true, sp = c.warning },
    DiagnosticUnderlineInfo  = { undercurl = true, sp = c.info },
    DiagnosticUnderlineHint  = { undercurl = true, sp = c.hint },
    DiagnosticUnderlineOk    = { undercurl = true, sp = c.ok },

    Error        = { fg = c.error },
    ErrorMsg     = { fg = c.error },
    WarningMsg   = { fg = c.warning },
    ModeMsg      = { fg = c.ok },
    MoreMsg      = { fg = c.type },
    Question     = { fg = c.ok },

    MatchParen   = { fg = c.constant, bold = true },
    NonText      = { fg = c.border },
    SpecialKey   = { fg = c.border },
    Whitespace   = { fg = c.border },

    Directory    = { fg = c.type },
    Title        = { fg = c.func, bold = true },
    QuickFixLine = { bg = c.selection },
    MsgSeparator = { fg = c.border },

    SpellBad     = { sp = c.error, undercurl = true },
    SpellCap     = { sp = c.warning, undercurl = true },
    SpellLocal   = { sp = c.info, undercurl = true },
    SpellRare    = { sp = c.hint, undercurl = true },

    -- LSP references
    LspReferenceRead  = { bg = c.selection },
    LspReferenceWrite = { bg = c.selection },
    LspReferenceText  = { bg = c.selection },
    LspSignatureActiveParameter = { fg = c.warning },
  }
end

return M
```

- [ ] **Step 2: Create groups/syntax.lua**

```lua
-- suannhai-nvim/lua/suannhai/groups/syntax.lua
local M = {}

---@param c table palette
---@param opts suannhai.Config
---@return table
function M.get(c, opts)
  return {
    Comment    = { fg = c.comment },
    Constant   = { fg = c.constant },
    String     = { fg = c.string },
    Character  = { fg = c.string },
    Number     = { fg = c.number },
    Boolean    = { fg = c.constant },
    Float      = { fg = c.number },

    Identifier = { fg = c.fg },
    Function   = { fg = c.func },

    Statement    = { fg = c.keyword },
    Conditional  = { fg = c.keyword },
    Repeat       = { fg = c.keyword },
    Label        = { fg = c.keyword },
    Operator     = { fg = c.comment },
    Keyword      = { fg = c.keyword },
    Exception    = { fg = c.keyword },

    PreProc    = { fg = c.comment },
    Include    = { fg = c.keyword },
    Define     = { fg = c.comment },
    Macro      = { fg = c.keyword },
    PreCondit  = { fg = c.keyword },

    Type         = { fg = c.type },
    StorageClass = { fg = c.keyword },
    Structure    = { fg = c.type },
    Typedef      = { fg = c.type },

    Special     = { fg = c.constant },
    SpecialChar = { fg = c.constant },
    Delimiter   = { fg = c.comment },
    Debug       = { fg = c.keyword },
    Tag         = { fg = c.type },

    Error      = { fg = c.error },
    Todo       = { fg = c.fg, bold = true },
    Underlined = { underline = true },

    Added   = { fg = c.git.add },
    Changed = { fg = c.git.change },
    Removed = { fg = c.git.delete },
  }
end

return M
```

- [ ] **Step 3: Create groups/treesitter.lua**

```lua
-- suannhai-nvim/lua/suannhai/groups/treesitter.lua
local M = {}

---@param c table palette
---@param opts suannhai.Config
---@return table
function M.get(c, opts)
  return {
    -- Identifiers
    ["@variable"]                = { fg = c.fg },
    ["@variable.builtin"]        = { fg = c.keyword },
    ["@variable.parameter"]      = { fg = c.fg },
    ["@variable.member"]         = { fg = c.fg },
    ["@variable.special"]        = { fg = c.keyword },

    -- Constants
    ["@constant"]                = { fg = c.constant },
    ["@constant.builtin"]        = { fg = c.constant },
    ["@constant.macro"]          = { fg = c.keyword },

    -- Modules
    ["@module"]                  = { fg = c.comment },
    ["@module.builtin"]          = { fg = c.comment },
    ["@label"]                   = { fg = c.keyword },

    -- Strings
    ["@string"]                  = { fg = c.string },
    ["@string.documentation"]    = { fg = c.comment },
    ["@string.regexp"]           = { fg = c.string },
    ["@string.escape"]           = { fg = c.constant },
    ["@string.special"]          = { fg = c.constant },
    ["@string.special.symbol"]   = { fg = c.constant },

    -- Characters
    ["@character"]               = { fg = c.string },
    ["@character.special"]       = { fg = c.constant },

    -- Booleans & Numbers
    ["@boolean"]                 = { fg = c.constant },
    ["@number"]                  = { fg = c.number },
    ["@number.float"]            = { fg = c.number },

    -- Types
    ["@type"]                    = { fg = c.type },
    ["@type.builtin"]            = { fg = c.type },
    ["@type.definition"]         = { fg = c.type },
    ["@type.qualifier"]          = { fg = c.keyword },

    -- Attributes / Annotations
    ["@attribute"]               = { fg = c.constant },
    ["@property"]                = { fg = c.fg },

    -- Functions
    ["@function"]                = { fg = c.func },
    ["@function.builtin"]        = { fg = c.func },
    ["@function.call"]           = { fg = c.func },
    ["@function.macro"]          = { fg = c.keyword },
    ["@function.method"]         = { fg = c.func },
    ["@function.method.call"]    = { fg = c.func },

    -- Constructor
    ["@constructor"]             = { fg = c.type },

    -- Operators & Punctuation
    ["@operator"]                = { fg = c.comment },
    ["@punctuation.bracket"]     = { fg = c.comment },
    ["@punctuation.delimiter"]   = { fg = c.comment },
    ["@punctuation.special"]     = { fg = c.comment },

    -- Keywords
    ["@keyword"]                 = { fg = c.keyword },
    ["@keyword.modifier"]        = { fg = c.keyword },
    ["@keyword.type"]            = { fg = c.keyword },
    ["@keyword.coroutine"]       = { fg = c.keyword },
    ["@keyword.function"]        = { fg = c.keyword },
    ["@keyword.operator"]        = { fg = c.comment },
    ["@keyword.import"]          = { fg = c.keyword },
    ["@keyword.export"]          = { fg = c.keyword },
    ["@keyword.repeat"]          = { fg = c.keyword },
    ["@keyword.return"]          = { fg = c.keyword },
    ["@keyword.debug"]           = { fg = c.keyword },
    ["@keyword.exception"]       = { fg = c.keyword },
    ["@keyword.conditional"]     = { fg = c.keyword },
    ["@keyword.conditional.ternary"] = { fg = c.keyword },
    ["@keyword.directive"]       = { fg = c.comment },
    ["@keyword.directive.define"] = { fg = c.comment },
    ["@keyword.storage"]         = { fg = c.keyword },

    -- Comments
    ["@comment"]                 = { fg = c.comment },
    ["@comment.documentation"]   = { fg = c.comment },
    ["@comment.error"]           = { fg = c.error },
    ["@comment.warning"]         = { fg = c.warning },
    ["@comment.info"]            = { fg = c.info },
    ["@comment.hint"]            = { fg = c.hint },
    ["@comment.todo"]            = { fg = c.fg, bold = true },
    ["@comment.note"]            = { fg = c.fg, bold = true },

    -- Tags (HTML/JSX)
    ["@tag"]                     = { fg = c.type },
    ["@tag.attribute"]           = { fg = c.func },
    ["@tag.delimiter"]           = { fg = c.comment },
    ["@tag.builtin"]             = { fg = c.type },

    -- Markup (Markdown)
    ["@markup"]                  = { fg = c.fg },
    ["@markup.heading"]          = { fg = c.func, bold = true },
    ["@markup.italic"]           = { italic = true },
    ["@markup.strong"]           = { bold = true },
    ["@markup.strikethrough"]    = { strikethrough = true },
    ["@markup.underline"]        = { underline = true },
    ["@markup.raw"]              = { fg = c.string },
    ["@markup.raw.markdown_inline"] = { fg = c.constant },
    ["@markup.link"]             = { fg = c.type },
    ["@markup.link.label"]       = { fg = c.type },
    ["@markup.link.url"]         = { fg = c.string, underline = true },
    ["@markup.list"]             = { fg = c.comment },
    ["@markup.list.checked"]     = { fg = c.ok },
    ["@markup.list.unchecked"]   = { fg = c.comment },
    ["@markup.math"]             = { fg = c.number },

    -- Diff
    ["@diff.plus"]               = { fg = c.git.add },
    ["@diff.minus"]              = { fg = c.git.delete },
    ["@diff.delta"]              = { fg = c.git.change },

    -- Misc
    ["@none"]                    = {},
    ["@annotation"]              = "PreProc",
  }
end

return M
```

- [ ] **Step 4: Create groups/semantic_tokens.lua**

```lua
-- suannhai-nvim/lua/suannhai/groups/semantic_tokens.lua
local M = {}

---@param c table palette
---@param opts suannhai.Config
---@return table
function M.get(c, opts)
  return {
    ["@lsp.type.class"]          = "@type",
    ["@lsp.type.comment"]        = "@comment",
    ["@lsp.type.decorator"]      = { fg = c.constant },
    ["@lsp.type.enum"]           = "@type",
    ["@lsp.type.enumMember"]     = { fg = c.constant },
    ["@lsp.type.function"]       = "@function",
    ["@lsp.type.interface"]      = "@type",
    ["@lsp.type.keyword"]        = "@keyword",
    ["@lsp.type.macro"]          = { fg = c.keyword },
    ["@lsp.type.method"]         = "@function.method",
    ["@lsp.type.namespace"]      = "@module",
    ["@lsp.type.number"]         = "@number",
    ["@lsp.type.operator"]       = "@operator",
    ["@lsp.type.parameter"]      = "@variable.parameter",
    ["@lsp.type.property"]       = "@property",
    ["@lsp.type.string"]         = "@string",
    ["@lsp.type.struct"]         = "@type",
    ["@lsp.type.type"]           = "@type",
    ["@lsp.type.typeParameter"]  = "@type",
    ["@lsp.type.variable"]       = "@variable",

    ["@lsp.mod.deprecated"]      = { strikethrough = true },
    ["@lsp.mod.readonly"]        = { fg = c.constant },
    ["@lsp.mod.defaultLibrary"]  = { fg = c.type },

    ["@lsp.typemod.function.defaultLibrary"] = "@function.builtin",
    ["@lsp.typemod.variable.defaultLibrary"] = { fg = c.type },
  }
end

return M
```

- [ ] **Step 5: Create groups/terminal.lua**

```lua
-- suannhai-nvim/lua/suannhai/groups/terminal.lua
local M = {}

---@param c table palette
---@param opts suannhai.Config
---@return table
function M.get(c, opts)
  return {
    _terminal_colors = c.terminal,
  }
end

return M
```

- [ ] **Step 6: Create groups/init.lua (group loader)**

```lua
-- suannhai-nvim/lua/suannhai/groups/init.lua
local Util = require("suannhai.util")

local M = {}

-- Plugin name -> group module name
M.plugins = {
  ["gitsigns.nvim"]           = "gitsigns",
  ["telescope.nvim"]          = "telescope",
  ["fzf-lua"]                 = "fzf",
  ["blink.cmp"]               = "blink",
  ["snacks.nvim"]             = "snacks",
  ["lazy.nvim"]               = "lazy",
  ["neo-tree.nvim"]           = "neo-tree",
  ["mini.nvim"]               = "mini",
}

---@param name string
---@return table
function M.get_group(name)
  return Util.mod("suannhai.groups." .. name)
end

---@param name string
---@param colors table
---@param opts suannhai.Config
---@return table
function M.get(name, colors, opts)
  local mod = M.get_group(name)
  return mod.get(colors, opts)
end

---@param colors table
---@param opts suannhai.Config
---@return table, table
function M.setup(colors, opts)
  opts = opts or {}
  opts.plugins = opts.plugins or {}

  -- Core groups always load
  local groups = {
    base = true,
    syntax = true,
    treesitter = true,
    semantic_tokens = true,
    terminal = true,
  }

  -- Plugin groups
  if opts.plugins.all then
    for _, group in pairs(M.plugins) do
      groups[group] = true
    end
  elseif opts.plugins.auto and package.loaded.lazy then
    local ok, lazy_config = pcall(function()
      return require("lazy.core.config").plugins
    end)
    if ok and lazy_config then
      for plugin, group in pairs(M.plugins) do
        if lazy_config[plugin] then
          groups[group] = true
        end
      end
      -- mini.nvim umbrella
      if lazy_config["mini.nvim"] then
        groups["mini"] = true
      end
    end
  end

  -- Per-plugin overrides
  for plugin, group in pairs(M.plugins) do
    local use = opts.plugins[group]
    use = use == nil and opts.plugins[plugin] or use
    if use ~= nil then
      if type(use) == "table" then
        use = use.enabled
      end
      groups[group] = use or nil
    end
  end

  local names = vim.tbl_keys(groups)
  table.sort(names)

  local ret = {}
  local terminal_colors = nil

  for _, group in ipairs(names) do
    for k, v in pairs(M.get(group, colors, opts)) do
      if k == "_terminal_colors" then
        terminal_colors = v
      else
        ret[k] = v
      end
    end
  end

  Util.resolve(ret)

  -- User hook
  if opts.on_highlights then
    opts.on_highlights(ret, colors)
  end

  -- Re-attach terminal colors after user hook (not a highlight group)
  if terminal_colors then
    ret._terminal_colors = terminal_colors
  end

  return ret, groups
end

return M
```

- [ ] **Step 7: Update theme.lua to handle _terminal_colors from groups**

The `theme.lua` from Task 1 needs a small update -- terminal colors now come from the groups table as `_terminal_colors` rather than from `colors.terminal` directly:

Replace the terminal handling in `theme.lua` with:

```lua
-- suannhai-nvim/lua/suannhai/theme.lua
local M = {}

---@param style string variant name (e.g. "jiufen")
---@param opts? suannhai.Config
function M.setup(style, opts)
  opts = require("suannhai.config").extend(opts)

  local colors = require("suannhai.palettes").setup(style, opts)
  local groups = require("suannhai.groups").setup(colors, opts)

  if vim.g.colors_name then
    vim.cmd("hi clear")
  end

  vim.o.termguicolors = true
  vim.g.colors_name = "suannhai-" .. style

  local terminal_colors = nil

  for group, hl in pairs(groups) do
    if group == "_terminal_colors" then
      terminal_colors = hl
    else
      hl = type(hl) == "string" and { link = hl } or hl
      vim.api.nvim_set_hl(0, group, hl)
    end
  end

  if terminal_colors then
    for i = 0, 15 do
      vim.g["terminal_color_" .. i] = terminal_colors[i]
    end
  end

  return colors, groups, opts
end

return M
```

- [ ] **Step 8: Commit**

```bash
git add suannhai-nvim/lua/suannhai/groups/ suannhai-nvim/lua/suannhai/theme.lua
git commit -m "feat(nvim): add core highlight groups (base, syntax, treesitter, semantic_tokens, terminal)"
```

---

### Task 4: Plugin Highlight Groups

**Files:**
- Create: `suannhai-nvim/lua/suannhai/groups/gitsigns.lua`
- Create: `suannhai-nvim/lua/suannhai/groups/telescope.lua`
- Create: `suannhai-nvim/lua/suannhai/groups/fzf.lua`
- Create: `suannhai-nvim/lua/suannhai/groups/blink.lua`
- Create: `suannhai-nvim/lua/suannhai/groups/snacks.lua`
- Create: `suannhai-nvim/lua/suannhai/groups/lazy.lua`
- Create: `suannhai-nvim/lua/suannhai/groups/neo-tree.lua`
- Create: `suannhai-nvim/lua/suannhai/groups/mini.lua`

**Interfaces:**
- Consumes: palette table, config table
- Produces: each module exports `M.get(colors, opts)` -> `table`

- [ ] **Step 1: Create groups/gitsigns.lua**

```lua
-- suannhai-nvim/lua/suannhai/groups/gitsigns.lua
local M = {}

function M.get(c, opts)
  return {
    GitSignsAdd          = { fg = c.git.add },
    GitSignsChange       = { fg = c.git.change },
    GitSignsDelete       = { fg = c.git.delete },
    GitSignsAddNr        = { fg = c.git.add },
    GitSignsChangeNr     = { fg = c.git.change },
    GitSignsDeleteNr     = { fg = c.git.delete },
    GitSignsAddLn        = { bg = c.diff.add },
    GitSignsChangeLn     = { bg = c.diff.change },
    GitSignsDeleteLn     = { bg = c.diff.delete },
    GitSignsCurrentLineBlame = { fg = c.comment },
  }
end

return M
```

- [ ] **Step 2: Create groups/telescope.lua**

```lua
-- suannhai-nvim/lua/suannhai/groups/telescope.lua
local M = {}

function M.get(c, opts)
  local transparent = opts.transparent
  return {
    TelescopeNormal         = { fg = c.fg, bg = transparent and c.none or c.surface },
    TelescopeBorder         = { fg = c.border, bg = transparent and c.none or c.surface },
    TelescopeTitle          = { fg = c.func, bold = true },
    TelescopePromptNormal   = { fg = c.fg, bg = transparent and c.none or c.surface },
    TelescopePromptBorder   = { fg = c.border, bg = transparent and c.none or c.surface },
    TelescopePromptTitle    = { fg = c.func, bold = true },
    TelescopePromptPrefix   = { fg = c.keyword },
    TelescopePromptCounter  = { fg = c.comment },
    TelescopeResultsNormal  = { fg = c.fg, bg = transparent and c.none or c.surface },
    TelescopeResultsBorder  = { fg = c.border, bg = transparent and c.none or c.surface },
    TelescopeResultsTitle   = { fg = c.func },
    TelescopePreviewNormal  = { fg = c.fg, bg = transparent and c.none or c.bg },
    TelescopePreviewBorder  = { fg = c.border, bg = transparent and c.none or c.bg },
    TelescopePreviewTitle   = { fg = c.func },
    TelescopeSelection      = { bg = c.selection },
    TelescopeSelectionCaret = { fg = c.keyword },
    TelescopeMatching       = { fg = c.keyword, bold = true },
    TelescopeMultiSelection = { fg = c.type },
    TelescopeMultiIcon      = { fg = c.type },
  }
end

return M
```

- [ ] **Step 3: Create groups/fzf.lua**

```lua
-- suannhai-nvim/lua/suannhai/groups/fzf.lua
local M = {}

function M.get(c, opts)
  local transparent = opts.transparent
  return {
    FzfLuaNormal       = { fg = c.fg, bg = transparent and c.none or c.surface },
    FzfLuaBorder       = { fg = c.border, bg = transparent and c.none or c.surface },
    FzfLuaTitle        = { fg = c.func, bold = true },
    FzfLuaHeaderBind   = { fg = c.keyword },
    FzfLuaHeaderText   = { fg = c.comment },
    FzfLuaFzfMatch     = { fg = c.keyword },
    FzfLuaFzfCursorLine = { bg = c.selection },
    FzfLuaFzfNormal    = { fg = c.fg },
    FzfLuaFzfPointer   = { fg = c.keyword },
    FzfLuaFzfSeparator = { fg = c.border },
    FzfLuaCursorLine   = { bg = c.selection },
    FzfLuaPreviewNormal = { fg = c.fg, bg = transparent and c.none or c.bg },
    FzfLuaPreviewBorder = { fg = c.border, bg = transparent and c.none or c.bg },
    FzfLuaPreviewTitle = { fg = c.func },
  }
end

return M
```

- [ ] **Step 4: Create groups/blink.lua**

```lua
-- suannhai-nvim/lua/suannhai/groups/blink.lua
local M = {}

function M.get(c, opts)
  local transparent = opts.transparent
  return {
    BlinkCmpMenu            = { fg = c.fg, bg = transparent and c.none or c.surface },
    BlinkCmpMenuBorder      = { fg = c.border, bg = transparent and c.none or c.surface },
    BlinkCmpMenuSelection   = { bg = c.selection },
    BlinkCmpLabel           = { fg = c.fg },
    BlinkCmpLabelMatch      = { fg = c.keyword, bold = true },
    BlinkCmpLabelDeprecated = { fg = c.comment, strikethrough = true },
    BlinkCmpKind            = { fg = c.type },
    BlinkCmpKindFunction    = { fg = c.func },
    BlinkCmpKindMethod      = { fg = c.func },
    BlinkCmpKindVariable    = { fg = c.fg },
    BlinkCmpKindField       = { fg = c.fg },
    BlinkCmpKindKeyword     = { fg = c.keyword },
    BlinkCmpKindClass       = { fg = c.type },
    BlinkCmpKindStruct      = { fg = c.type },
    BlinkCmpKindInterface   = { fg = c.type },
    BlinkCmpKindModule      = { fg = c.constant },
    BlinkCmpKindProperty    = { fg = c.fg },
    BlinkCmpKindConstant    = { fg = c.constant },
    BlinkCmpKindSnippet     = { fg = c.string },
    BlinkCmpKindText        = { fg = c.comment },
    BlinkCmpKindValue       = { fg = c.constant },
    BlinkCmpKindEnum        = { fg = c.type },
    BlinkCmpKindEnumMember  = { fg = c.constant },
    BlinkCmpDoc             = { fg = c.fg, bg = transparent and c.none or c.surface },
    BlinkCmpDocBorder       = { fg = c.border, bg = transparent and c.none or c.surface },
    BlinkCmpSignatureHelp       = { fg = c.fg, bg = transparent and c.none or c.surface },
    BlinkCmpSignatureHelpBorder = { fg = c.border, bg = transparent and c.none or c.surface },
  }
end

return M
```

- [ ] **Step 5: Create groups/snacks.lua**

```lua
-- suannhai-nvim/lua/suannhai/groups/snacks.lua
local M = {}

function M.get(c, opts)
  local transparent = opts.transparent
  return {
    SnacksNormal        = { fg = c.fg, bg = transparent and c.none or c.surface },
    SnacksBorder        = { fg = c.border },
    SnacksTitle         = { fg = c.func, bold = true },
    SnacksNotifierInfo  = { fg = c.info },
    SnacksNotifierWarn  = { fg = c.warning },
    SnacksNotifierError = { fg = c.error },
    SnacksNotifierDebug = { fg = c.comment },
    SnacksNotifierTrace = { fg = c.hint },
    SnacksDashboardHeader  = { fg = c.keyword },
    SnacksDashboardFooter  = { fg = c.comment },
    SnacksDashboardKey     = { fg = c.constant },
    SnacksDashboardIcon    = { fg = c.type },
    SnacksDashboardDesc    = { fg = c.fg },
    SnacksDashboardSpecial = { fg = c.func },
    SnacksIndent           = { fg = c.border },
    SnacksIndentScope      = { fg = c.comment },
  }
end

return M
```

- [ ] **Step 6: Create groups/lazy.lua**

```lua
-- suannhai-nvim/lua/suannhai/groups/lazy.lua
local M = {}

function M.get(c, opts)
  return {
    LazyButton       = { fg = c.fg, bg = c.surface },
    LazyButtonActive = { fg = c.bg, bg = c.keyword },
    LazyH1           = { fg = c.bg, bg = c.keyword, bold = true },
    LazyH2           = { fg = c.func, bold = true },
    LazyComment      = { fg = c.comment },
    LazyNormal       = { fg = c.fg, bg = c.bg },
    LazySpecial      = { fg = c.constant },
    LazyProgressDone = { fg = c.keyword },
    LazyProgressTodo = { fg = c.border },
    LazyReasonPlugin = { fg = c.type },
    LazyReasonCmd    = { fg = c.func },
    LazyReasonEvent  = { fg = c.constant },
    LazyReasonFt     = { fg = c.string },
    LazyReasonKeys   = { fg = c.number },
    LazyReasonStart  = { fg = c.keyword },
  }
end

return M
```

- [ ] **Step 7: Create groups/neo-tree.lua**

```lua
-- suannhai-nvim/lua/suannhai/groups/neo-tree.lua
local M = {}

function M.get(c, opts)
  local transparent = opts.transparent
  return {
    NeoTreeNormal          = { fg = c.fg, bg = transparent and c.none or c.surface },
    NeoTreeNormalNC        = { fg = c.fg, bg = transparent and c.none or c.surface },
    NeoTreeDimText         = { fg = c.comment },
    NeoTreeDirectoryIcon   = { fg = c.type },
    NeoTreeDirectoryName   = { fg = c.type },
    NeoTreeRootName        = { fg = c.func, bold = true },
    NeoTreeFileName        = { fg = c.fg },
    NeoTreeFileIcon        = { fg = c.comment },
    NeoTreeIndentMarker    = { fg = c.border },
    NeoTreeExpander        = { fg = c.comment },
    NeoTreeGitAdded        = { fg = c.git.add },
    NeoTreeGitModified     = { fg = c.git.change },
    NeoTreeGitDeleted      = { fg = c.git.delete },
    NeoTreeGitConflict     = { fg = c.constant },
    NeoTreeGitUntracked    = { fg = c.comment },
    NeoTreeGitIgnored      = { fg = c.border },
    NeoTreeFloatBorder     = { fg = c.border },
    NeoTreeFloatTitle      = { fg = c.func },
    NeoTreeTitleBar        = { fg = c.bg, bg = c.func },
    NeoTreeCursorLine      = { bg = c.selection },
    NeoTreeWinSeparator    = { fg = c.border },
  }
end

return M
```

- [ ] **Step 8: Create groups/mini.lua**

```lua
-- suannhai-nvim/lua/suannhai/groups/mini.lua
local M = {}

function M.get(c, opts)
  return {
    MiniCursorword        = { underline = true },
    MiniCursorwordCurrent = { underline = true },

    MiniIndentscopeSymbol = { fg = c.border },
    MiniIndentscopePrefix = { nocombine = true },

    MiniStatuslineDevinfo    = { fg = c.fg, bg = c.surface },
    MiniStatuslineFileinfo   = { fg = c.fg, bg = c.surface },
    MiniStatuslineFilename   = { fg = c.comment, bg = c.bg },
    MiniStatuslineInactive   = { fg = c.comment, bg = c.bg },
    MiniStatuslineModeNormal = { fg = c.bg, bg = c.type, bold = true },
    MiniStatuslineModeInsert = { fg = c.bg, bg = c.string, bold = true },
    MiniStatuslineModeVisual = { fg = c.bg, bg = c.number, bold = true },
    MiniStatuslineModeReplace = { fg = c.bg, bg = c.keyword, bold = true },
    MiniStatuslineModeCommand = { fg = c.bg, bg = c.func, bold = true },

    MiniTablineCurrent       = { fg = c.fg, bg = c.bg, bold = true },
    MiniTablineVisible       = { fg = c.comment, bg = c.surface },
    MiniTablineHidden        = { fg = c.comment, bg = c.surface },
    MiniTablineModifiedCurrent  = { fg = c.constant, bg = c.bg, bold = true },
    MiniTablineModifiedVisible  = { fg = c.constant, bg = c.surface },
    MiniTablineModifiedHidden   = { fg = c.constant, bg = c.surface },
    MiniTablineFill          = { bg = c.surface },
    MiniTablineTabpagesection = { fg = c.bg, bg = c.keyword },

    MiniDiffSignAdd    = { fg = c.git.add },
    MiniDiffSignChange = { fg = c.git.change },
    MiniDiffSignDelete = { fg = c.git.delete },

    MiniPickNormal  = { fg = c.fg, bg = c.surface },
    MiniPickBorder  = { fg = c.border, bg = c.surface },
    MiniPickMatchCur = { bold = true },
    MiniPickMatchMarked = { fg = c.keyword, bold = true },
    MiniPickMatchRanges = { fg = c.keyword },

    MiniIconsAzure  = { fg = c.type },
    MiniIconsBlue   = { fg = c.type },
    MiniIconsCyan    = { fg = c.type },
    MiniIconsGreen  = { fg = c.string },
    MiniIconsGrey   = { fg = c.comment },
    MiniIconsOrange = { fg = c.constant },
    MiniIconsPurple = { fg = c.number },
    MiniIconsRed    = { fg = c.keyword },
    MiniIconsYellow = { fg = c.func },
  }
end

return M
```

- [ ] **Step 9: Commit**

```bash
git add suannhai-nvim/lua/suannhai/groups/gitsigns.lua suannhai-nvim/lua/suannhai/groups/telescope.lua suannhai-nvim/lua/suannhai/groups/fzf.lua suannhai-nvim/lua/suannhai/groups/blink.lua suannhai-nvim/lua/suannhai/groups/snacks.lua suannhai-nvim/lua/suannhai/groups/lazy.lua suannhai-nvim/lua/suannhai/groups/neo-tree.lua suannhai-nvim/lua/suannhai/groups/mini.lua
git commit -m "feat(nvim): add plugin highlight groups"
```

---

### Task 5: Entry Point Files and README

**Files:**
- Create: `suannhai-nvim/colors/suannhai-jiufen.lua`
- Create: `suannhai-nvim/colors/suannhai-lam-ni.lua`
- Create: `suannhai-nvim/colors/suannhai-hue-poo.lua`
- Create: `suannhai-nvim/colors/suannhai-rouiro.lua`
- Create: `suannhai-nvim/colors/suannhai-sumi.lua`
- Create: `suannhai-nvim/colors/suannhai-koiai.lua`
- Create: `suannhai-nvim/colors/suannhai-torinoko.lua`
- Create: `suannhai-nvim/colors/suannhai-shironeri.lua`
- Modify: `suannhai-nvim/README.md`

**Interfaces:**
- Consumes: `require("suannhai").load(style)`

- [ ] **Step 1: Create all 8 entry point files**

Each file is a one-liner. Create these files:

`suannhai-nvim/colors/suannhai-jiufen.lua`:
```lua
require("suannhai").load("jiufen")
```

`suannhai-nvim/colors/suannhai-lam-ni.lua`:
```lua
require("suannhai").load("lam-ni")
```

`suannhai-nvim/colors/suannhai-hue-poo.lua`:
```lua
require("suannhai").load("hue-poo")
```

`suannhai-nvim/colors/suannhai-rouiro.lua`:
```lua
require("suannhai").load("rouiro")
```

`suannhai-nvim/colors/suannhai-sumi.lua`:
```lua
require("suannhai").load("sumi")
```

`suannhai-nvim/colors/suannhai-koiai.lua`:
```lua
require("suannhai").load("koiai")
```

`suannhai-nvim/colors/suannhai-torinoko.lua`:
```lua
require("suannhai").load("torinoko")
```

`suannhai-nvim/colors/suannhai-shironeri.lua`:
```lua
require("suannhai").load("shironeri")
```

- [ ] **Step 2: Write README.md**

```markdown
<p align="center">
  <h1 align="center">Suannhai for Neovim</h1>
</p>

Traditional color themes from Formosa and Nippon for [Neovim](https://neovim.io/).

## Requirements

- Neovim >= 0.8.0
- `termguicolors` enabled

## Install

### lazy.nvim

```lua
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

## Configuration

`setup()` is optional. Defaults work out of the box.

```lua
require("suannhai").setup({
  transparent = false,
  on_colors = function(colors)
    -- Mutate palette values before highlights are built
  end,
  on_highlights = function(hl, colors)
    -- Override any highlight group after all groups are built
  end,
  plugins = {
    all = true,   -- enable all plugin groups
    auto = true,  -- auto-detect via lazy.nvim
    -- Per-plugin override:
    -- telescope = false,
  },
})
```

## Available Schemes

### Formosa

| Name | Appearance | Command |
| ---- | ---------- | ------- |
| Suannhai Jiufen | Dark | `:colorscheme suannhai-jiufen` |
| Suannhai Lam-ni | Dark | `:colorscheme suannhai-lam-ni` |
| Suannhai Hue-poo | Light | `:colorscheme suannhai-hue-poo` |

### Nippon

| Name | Appearance | Command |
| ---- | ---------- | ------- |
| Suannhai Rouiro | Dark | `:colorscheme suannhai-rouiro` |
| Suannhai Sumi | Dark | `:colorscheme suannhai-sumi` |
| Suannhai Koiai | Dark | `:colorscheme suannhai-koiai` |
| Suannhai Torinoko | Light | `:colorscheme suannhai-torinoko` |
| Suannhai Shironeri | Light | `:colorscheme suannhai-shironeri` |

## Supported Plugins

- [gitsigns.nvim](https://github.com/lewis6991/gitsigns.nvim)
- [telescope.nvim](https://github.com/nvim-telescope/telescope.nvim)
- [fzf-lua](https://github.com/ibhagwan/fzf-lua)
- [blink.cmp](https://github.com/Saghen/blink.cmp)
- [snacks.nvim](https://github.com/folke/snacks.nvim)
- [lazy.nvim](https://github.com/folke/lazy.nvim)
- [neo-tree.nvim](https://github.com/nvim-neo-tree/neo-tree.nvim)
- [mini.nvim](https://github.com/echasnovski/mini.nvim)
```

- [ ] **Step 3: Commit**

```bash
git add suannhai-nvim/colors/ suannhai-nvim/README.md
git commit -m "feat(nvim): add colorscheme entry points and README"
```

---

### Task 6: Smoke Test in Neovim

**Files:** None (manual verification)

**Interfaces:** None

- [ ] **Step 1: Test loading the colorscheme**

Open Neovim with the plugin on the runtimepath:

```bash
nvim --cmd "set rtp+=suannhai-nvim" -c "colorscheme suannhai-jiufen"
```

Verify:
- No errors in `:messages`
- `:echo g:colors_name` outputs `suannhai-jiufen`
- Syntax colors are visible (open a Lua or Python file)
- `:hi Normal` shows the expected bg/fg

- [ ] **Step 2: Test each variant loads without error**

```vim
:colorscheme suannhai-lam-ni
:colorscheme suannhai-hue-poo
:colorscheme suannhai-rouiro
:colorscheme suannhai-sumi
:colorscheme suannhai-koiai
:colorscheme suannhai-torinoko
:colorscheme suannhai-shironeri
```

Verify no errors in `:messages` after each switch.

- [ ] **Step 3: Test transparent mode**

```vim
:lua require("suannhai").setup({ transparent = true })
:colorscheme suannhai-jiufen
:hi Normal
```

Verify `Normal` has `guibg=NONE`.

- [ ] **Step 4: Test on_highlights hook**

```vim
:lua require("suannhai").setup({ on_highlights = function(hl, c) hl.Normal = { fg = "#ff0000", bg = c.bg } end })
:colorscheme suannhai-jiufen
:hi Normal
```

Verify `Normal` has `guifg=#ff0000`.

- [ ] **Step 5: Final commit (if any fixes needed)**

```bash
git add -u suannhai-nvim/
git commit -m "fix(nvim): address smoke test issues"
```

---

### Task 7: Repository Setup (Separate Repo + Submodule)

**Files:**
- Remove: `suannhai-nvim/` (current directory)
- Add: `suannhai-nvim` as git submodule

**This task is done manually by the user.** Steps for reference:

- [ ] **Step 1: Create the GitHub repo**

```bash
gh repo create WeiTing1991/suannhai.nvim --public --description "Traditional color themes from Formosa and Nippon for Neovim"
```

- [ ] **Step 2: Initialize and push to the new repo**

```bash
cd suannhai-nvim
git init
git add .
git commit -m "feat: initial suannhai.nvim colorscheme plugin"
git remote add origin git@github.com:WeiTing1991/suannhai.nvim.git
git branch -M main
git push -u origin main
cd ..
```

- [ ] **Step 3: Remove the directory from the monorepo and add as submodule**

```bash
git rm -r suannhai-nvim
git commit -m "chore: remove suannhai-nvim directory (moving to submodule)"
git submodule add git@github.com:WeiTing1991/suannhai.nvim.git suannhai-nvim
git add .gitmodules suannhai-nvim
git commit -m "chore: add suannhai.nvim as submodule"
```
