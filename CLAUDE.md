# Portfolio Website - andrewvu.me

Static site generator for personal portfolio using Python (Jinja2, Mistune) and Tailwind CSS.

## Build Commands

```bash
# Install dependencies
pnpm install
uv sync

# Build for production (output: dist/)
pnpm build

# Development server with hot reload
pnpm dev
```

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
