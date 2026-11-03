# libretro-thumbnails

An agent skill for finding and downloading real video game covers, title screens and gameplay screenshots from [libretro-thumbnails](https://github.com/libretro-thumbnails).

It prioritizes the correct game, platform and edition, pins downloads to a Git commit and saves source information beside every image. It does not download ROMs or generate replacement artwork.

## Install

Once this repository is public:

```sh
npx skills add JaviPalanca/libretro-thumbnails
```

Alternatively, place the repository in your agent's skills directory. See [SKILL.md](SKILL.md) for agent instructions.

## Requirements

- Python 3.9 or newer; no third-party Python packages.
- Git and internet access to GitHub.
- Node.js/npm only if using the `skills` installer.

## Examples

Ask your agent: “Find an original DOS screenshot of Monkey Island and include its source credit.”

Or run the script directly from this repository:

```sh
python3 scripts/libretro.py search 'monkey island' --repo ScummVM --repo DOS --kind boxart
python3 scripts/libretro.py get ScummVM 'Named_Boxarts/Secret of Monkey Island, The.png' --out assets/monkey-island.png
```

Copy an exact path from the search results into `get`; the sample path may differ from current upstream names.

Image kinds: `boxart`, `title`, `snap`. Search multiple systems by repeating `--repo`.

Indexes live in `~/.cache/libretro-thumbnails`. Add `--refresh` to `search` or `get` to rebuild an index. `repos` lists cached repositories only.

Downloads print JSON and save `<image>.json` with the commit, requested path, resolved path, source link and actual output path. Files containing JPEG or GIF data receive the appropriate extension. Existing outputs are protected; use `--force` to replace them. The old `--json` flag remains accepted.

## Checks

```sh
python3 -m unittest discover -s tests -v
```

## Credits and rights

Downloaded artwork belongs to its respective rights holders. This project does not grant rights to those images. Preserve provenance and include a visible link to the exact source file when using them.
