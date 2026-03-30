# Portfolio Website - andrewvu.me

Static site generator for personal portfolio using Python (Jinja2, Mistune) and Tailwind CSS.

## Working Rules

- Rebuild the preview every time you finish a change before handing work back.
- After rebuilding, tell the user to refresh the local preview and what page to check.
- Prefer editing templates in `src/templates/` instead of touching built files in `dist/`.
- Keep new copy understated and natural. Avoid resume-speak and overhyped wording.
- For random pages, prefer playful interactive ideas, but keep the implementation easy to extend.

## Build Commands

```bash
# Install dependencies
pnpm install
uv sync

# Development server with hot reload
pnpm dev
```

## Preview Refresh

Use these after finishing a change:

```bash
uv run python src/build.py --output dist
pnpm tailwindcss -i ./src/index.css -o ./dist/index.css --minify
```

Then refresh the local preview in the browser.

## Windows Note

On this machine, prefer the explicit rebuild commands above instead of `pnpm build`.
The repo's shell build path is not the most reliable workflow on Windows.

## Project Structure

- `src/` - Python build scripts and Jinja2 templates
  - `build.py` - Main static site generator
  - `templates/` - Jinja2 HTML templates
  - `index.css` - Tailwind CSS source
- `posts/` - Markdown content files with frontmatter
- `public/` - Static assets (copied to dist/)
- `dist/` - Build output (gitignored)

## Tech Stack

- **Templates**: Jinja2
- **Markdown**: Mistune
- **Styling**: Tailwind CSS with Typography plugin
- **Dev server**: Flask
