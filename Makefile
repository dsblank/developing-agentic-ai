.PHONY: build clean help

help:
	@echo "Available targets:"
	@echo "  build  - Build the Jupyter Book with custom LaTeX template"
	@echo "  clean  - Clean build artifacts"
	@echo "  pdf    - Build only the PDF (faster)"

build: setup-template
	@echo "🔨 Building Jupyter Book..."
	jupyter book build --execute --pdf

pdf: setup-template
	@echo "📄 Building PDF only..."
	jupyter book build --pdf

setup-template:
	@echo "📋 Setting up custom LaTeX template..."
	@mkdir -p _build/templates/tex/myst/custom_latex_book
	@cp templates/tex/custom/* _build/templates/tex/myst/custom_latex_book/ 2>/dev/null || \
		echo "⚠️  Warning: Template files not found"

clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf _build/temp/*
	rm -rf _build/exports/*
	rm -rf _build/site/*

clean-all: clean
	@echo "🧹 Cleaning all build files..."
	rm -rf _build/*

