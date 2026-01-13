# Building the Jupyter Book

This project uses a custom LaTeX template to style code cell inputs and outputs differently in the PDF output.

## Quick Start

### Option 1: Using the Bash Script

```bash
./build.sh
```

### Option 2: Using the Python Script

```bash
./build.py
```

### Option 3: Using Make

```bash
make build      # Build with execution
make pdf        # Build PDF only (faster, no execution)
make clean      # Clean build artifacts
```

### Option 4: Manual Build

```bash
# Copy template first
mkdir -p _build/templates/tex/myst/custom_latex_book
cp templates/tex/custom/* _build/templates/tex/myst/custom_latex_book/

# Then build
jupyter book build --execute --pdf
```

## Custom Template Features

The custom LaTeX template (`templates/tex/custom/`) provides:

- **Code Input Cells**: Light blue-gray background with "Input" label
- **Code Output Cells**: Light beige background with "Output" label
- Styled boxes with borders and rounded corners using `tcolorbox`

## Template Location

- **Source**: `templates/tex/custom/` (version controlled)
- **Build location**: `_build/templates/tex/myst/custom_latex_book/` (auto-copied)

The build scripts automatically copy the template from source to the build location before building.

## Output Files

- **PDF**: `_build/exports/intro.pdf`
- **Site**: `_build/site/` (HTML website from `myst.yml` site config)
- **Static HTML**: `_build/html/` (static HTML for deployment)

## Running Locally

### Development Server (Recommended)

For development with live reload that automatically reflects changes:

```bash
# Using Make
make serve

# Or directly
jupyter book start
```

This will:

- Start a development server with hot reload
- Automatically rebuild when you edit your markdown files
- Open in your browser (typically at <http://localhost:3000>)
- Watch for changes and refresh automatically

Press `Ctrl+C` to stop the server.

### Static Server

To view a pre-built site in a web browser:

```bash
# Build the HTML site first
jupyter book build --html

# Serve the built site (if it outputs to _build/html/)
python3 -m http.server 8000 --directory _build/html

# Or if it outputs to _build/site/public/
python3 -m http.server 8000 --directory _build/site/public
```

Then open <http://localhost:8000> in your browser.

## Local vs GitHub Actions Configuration

**Local builds** use:

- Python `jupyter-book` package
- Command: `jupyter book build` (with space)
- Respects `myst.yml` configuration
- May output to `_build/site/` when `site:` is configured in `myst.yml`

**GitHub Actions** uses:

- Python `jupyter-book` package (aligned with local)
- Command: `jupyter book build --html --ci`
- Builds static HTML to `_build/html/` for deployment
- Automatically handles output location differences

## Troubleshooting

If the template isn't being used:

1. Check that `myst.yml` has `template: custom_latex_book` in the exports section
2. Verify the template files exist in `templates/tex/custom/`
3. Run the build script to ensure the template is copied to the build directory
