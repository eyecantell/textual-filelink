.PHONY: help install test lint format clean

help:
	@echo "Available commands:"
	@echo "  make install   - Install dependencies"
	@echo "  make test      - Run tests"
	@echo "  make lint      - Run linter"
	@echo "  make format    - Format code"
	@echo "  make clean     - Clean build artifacts"

install:
	pip install -e .

test:
	pytest

lint:
	ruff check .

format:
	ruff format .

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
