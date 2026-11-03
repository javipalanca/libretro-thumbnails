---
name: libretro-thumbnails
description: Find and download real video game images (box art, title screens, in-game screenshots) from the libretro-thumbnails archive on GitHub. Use it whenever a project needs a cover, title screen or screenshot of a real game, before trying any other image source.
---

# Game images from libretro-thumbnails

[libretro-thumbnails](https://github.com/libretro-thumbnails) has one GitHub repository per system (`DOS`, `ScummVM`,
`Nintendo_-_Super_Nintendo_Entertainment_System`, `Sega_-_Mega_Drive_-_Genesis`, `Commodore_-_Amiga`,
`Sinclair_-_ZX_Spectrum`, `Amstrad_-_CPC`, `Microsoft_-_MSX`, `Sony_-_PlayStation`…; spaces become `_`).
Every repository has three folders:

| Folder | Content |
|---|---|
| `Named_Boxarts/` | box art / cover |
| `Named_Titles/` | title screen |
| `Named_Snaps/` | in-game screenshot |

Files generally use `.png` names based on No-Intro/DAT titles; verify their actual image format.

## Workflow

Use `scripts/libretro.py` (Python 3.9+, standard library only; Git and network access required). Resolve its path relative to this SKILL.md. It indexes repos without downloading images, searches, and
downloads files pinned to a commit, with provenance.

```bash
S="/absolute/path/to/this/skill/scripts/libretro.py" # Resolve from this SKILL.md

# 1. Search one or more systems (caches a file index per repo in ~/.cache/libretro-thumbnails)
python3 "$S" search "monkey island" --repo ScummVM --repo DOS --kind boxart

# 2. Download an exact match into the project, pinned to the commit that was indexed
python3 "$S" get ScummVM "Named_Boxarts/Secret of Monkey Island, The.png" --out assets/covers/monkey-island.png

# 3. Each download saves provenance beside the image, including requested and resolved paths
python3 "$S" get DOS "Named_Snaps/Loom.png" --out assets/shots/loom.png
```

If the script cannot be used, do it by hand:
- `git clone --filter=blob:none --no-checkout --depth 1 https://github.com/libretro-thumbnails/<Repo>`, then
  `git ls-tree -r --name-only HEAD` to list the files.
- Download from `https://raw.githubusercontent.com/libretro-thumbnails/<Repo>/<commit>/<url-encoded path>`.

## Select a system

Match the requested platform before searching. Common repository names:

| System | Repository |
|---|---|
| DOS | `DOS` |
| ScummVM | `ScummVM` |
| Super Nintendo / SNES | `Nintendo_-_Super_Nintendo_Entertainment_System` |
| Mega Drive / Genesis | `Sega_-_Mega_Drive_-_Genesis` |
| Amiga | `Commodore_-_Amiga` |
| ZX Spectrum | `Sinclair_-_ZX_Spectrum` |
| Amstrad CPC | `Amstrad_-_CPC` |
| MSX | `Microsoft_-_MSX` |
| PlayStation | `Sony_-_PlayStation` |

For other systems, inspect the upstream GitHub organization; do not guess an identifier.
`repos` lists only locally cached repositories. Add `--refresh` to search/get to update an index.
Ask for the platform when it materially changes the result and cannot be inferred.

## Naming rules (for searching)

- `:` and other forbidden characters become `_` ("Indiana Jones and the Fate of Atlantis_ The Action Game").
- A leading article moves to the end: "Secret of Monkey Island, The".
- Variants go in brackets: `(1990)`, `(Demo)`, `(CD_DOS_English)`, `(Windows_German)`, `(SCI remake)`.
- Search with a short, distinctive fragment and case-insensitive matching.

## Choosing the right file (accuracy first)

- Match the exact game: sequels and remakes have near-identical names (Kathy Rain ≠ Kathy Rain 2,
  King's Quest I ≠ King's Quest I SCI remake).
- Honor the requested platform, language and edition first. Otherwise prefer the original release (year, platform, language) over demos, remasters and special editions.
  If only another edition exists, use it but keep the file name in the credit so the edition is visible.
- Prefer original-platform screenshots (e.g. `(EGA_DOS_English)`) for historical accuracy.
- Inspect the downloaded image visually before using it; verify the game, edition and image type.
- If nothing matches, report it. Never substitute an image of a different game.

## Gotchas

- **Symlinks.** The script recognizes Git symlink entries, resolves relative destinations, and rejects cycles or paths outside the repository.
- **Wrong extensions.** Some `.png` files are really GIF or JPEG; check the magic bytes. The script fixes the extension.
- **Images come at mixed sizes.** Resize for your use case; keep pixel-art screenshots at integer scales with
  `image-rendering: pixelated`.
- **Outputs.** Read the returned `file` path: the extension may change. Downloads also save `<image>.json`; existing outputs require `--force`.
- **Pin to a commit.** Don't hotlink `master`: download and pin the commit for reproducibility.

## Rights and credits

Box art and screenshots are copyrighted by their publishers and developers. libretro-thumbnails does not relicense them.
- Use small resolutions for identification, criticism or historical context.
- Always show a visible credit linking to the exact file on GitHub (`page` in the provenance JSON).
- Don't use this archive for company or engine logos; take those from official sources.
