.PHONY: help test test-unit test-integration test-all coverage clean install

help:
	@echo "Stream Client Test Commands:"
	@echo ""
	@echo "  make install          - Install dependencies including test tools"
	@echo "  make test            - Run all tests (unit + integration)"
	@echo "  make test-unit       - Run only unit tests (fast, mocked)"
	@echo "  make test-integration - Run only integration tests (requires server)"
	@echo "  make coverage        - Run tests with coverage report"
	@echo "  make clean           - Remove test artifacts and cache"
	@echo ""

install:
	pip install -r requirements.txt

test: test-unit test-integration

test-unit:
	@echo "🧪 Running unit tests..."
	pytest tests/unit/ -v

test-integration:
	@echo "🌐 Running integration tests (requires server at http://pi-server:8080)..."
	pytest tests/integration/ -v -m integration

test-all:
	@echo "🚀 Running all tests..."
	pytest tests/ -v

coverage:
	@echo "📊 Running tests with coverage..."
	pytest tests/ --cov=. --cov-report=html --cov-report=term
	@echo ""
	@echo "📄 Coverage report generated in htmlcov/index.html"

clean:
	@echo "🧹 Cleaning test artifacts..."
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf .coverage
	rm -rf **/__pycache__
	rm -rf **/*.pyc
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "✨ Clean complete"
