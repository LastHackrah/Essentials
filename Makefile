.PHONY: help install install-dev clean test lint format check dashboard etl inspect

# Default target
.DEFAULT_GOAL := help

# Python and virtual environment
PYTHON := python3
VENV := .venv
BIN := $(VENV)/bin
PYTHON_VENV := $(BIN)/python
PIP := $(BIN)/pip

# Directories
SRC_DIRS := etl dsl config dashboards
DATA_DIRS := data/raw data/processed data/metadata

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

##@ General

help: ## Display this help message
	@echo "$(BLUE)Data Analytics Dashboard - Makefile Commands$(NC)"
	@echo ""
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make $(GREEN)<target>$(NC)\n"} /^[a-zA-Z_0-9-]+:.*?##/ { printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2 } /^##@/ { printf "\n$(BLUE)%s$(NC)\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Setup & Installation

install: ## Install production dependencies
	@echo "$(BLUE)Installing production dependencies...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt
	@echo "$(GREEN)✓ Production dependencies installed$(NC)"

install-dev: ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements-dev.txt
	@echo "$(GREEN)✓ Development dependencies installed$(NC)"

setup: install-dev ## Complete development setup (install-dev + create directories)
	@echo "$(BLUE)Setting up project directories...$(NC)"
	@mkdir -p $(DATA_DIRS)
	@mkdir -p dev_docs
	@echo "$(GREEN)✓ Project setup complete$(NC)"

##@ Code Quality

format: ## Format code with black and isort
	@echo "$(BLUE)Formatting code...$(NC)"
	$(BIN)/black $(SRC_DIRS) *.py
	$(BIN)/isort $(SRC_DIRS) *.py
	@echo "$(GREEN)✓ Code formatted$(NC)"

lint: ## Run linters (flake8, pylint)
	@echo "$(BLUE)Running flake8...$(NC)"
	$(BIN)/flake8 $(SRC_DIRS) *.py || true
	@echo ""
	@echo "$(BLUE)Running pylint...$(NC)"
	$(BIN)/pylint $(SRC_DIRS) *.py || true
	@echo "$(GREEN)✓ Linting complete$(NC)"

typecheck: ## Run mypy type checker
	@echo "$(BLUE)Running mypy...$(NC)"
	$(BIN)/mypy $(SRC_DIRS) || true
	@echo "$(GREEN)✓ Type checking complete$(NC)"

check: format lint typecheck ## Run all code quality checks (format, lint, typecheck)
	@echo "$(GREEN)✓ All code quality checks complete$(NC)"

##@ Testing

test: ## Run DSL tests
	@echo "$(BLUE)Running DSL tests...$(NC)"
	$(PYTHON_VENV) test_dsl.py
	@echo "$(GREEN)✓ Tests complete$(NC)"

test-pytest: ## Run pytest tests (if available)
	@echo "$(BLUE)Running pytest...$(NC)"
	$(BIN)/pytest tests/ -v || echo "$(YELLOW)No tests found$(NC)"

test-cov: ## Run tests with coverage report
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	$(BIN)/pytest tests/ --cov=. --cov-report=term-missing --cov-report=html || echo "$(YELLOW)No tests found$(NC)"

##@ ETL Pipeline

etl: ## Run ETL pipeline for all datasets
	@echo "$(BLUE)Running ETL pipeline...$(NC)"
	$(PYTHON_VENV) run_etl.py --verbose

etl-dataset: ## Run ETL pipeline for specific dataset (use DATASET=name)
	@echo "$(BLUE)Running ETL pipeline for $(DATASET)...$(NC)"
	@if [ -z "$(DATASET)" ]; then \
		echo "$(RED)Error: DATASET not specified. Use: make etl-dataset DATASET=credit_card_fraud$(NC)"; \
		exit 1; \
	fi
	$(PYTHON_VENV) run_etl.py --datasets $(DATASET) --verbose

inspect: ## List all processed datasets
	@echo "$(BLUE)Listing processed datasets...$(NC)"
	$(PYTHON_VENV) inspect_datasets.py --list

inspect-dataset: ## Inspect specific dataset (use DATASET=name)
	@echo "$(BLUE)Inspecting dataset: $(DATASET)$(NC)"
	@if [ -z "$(DATASET)" ]; then \
		echo "$(RED)Error: DATASET not specified. Use: make inspect-dataset DATASET=credit_card_fraud$(NC)"; \
		exit 1; \
	fi
	$(PYTHON_VENV) inspect_datasets.py --dataset $(DATASET)

##@ Dashboard

dashboard: ## Launch fraud detection dashboard
	@echo "$(BLUE)Launching fraud detection dashboard...$(NC)"
	$(BIN)/streamlit run run_dashboard.py -- dsl/examples/happy_path.yaml

dashboard-minimal: ## Launch minimal example dashboard
	@echo "$(BLUE)Launching minimal dashboard...$(NC)"
	$(BIN)/streamlit run run_dashboard.py -- dsl/examples/minimal.yaml

dashboard-custom: ## Launch custom dashboard (use SPEC=path/to/spec.yaml)
	@echo "$(BLUE)Launching custom dashboard: $(SPEC)$(NC)"
	@if [ -z "$(SPEC)" ]; then \
		echo "$(RED)Error: SPEC not specified. Use: make dashboard-custom SPEC=my_dashboard.yaml$(NC)"; \
		exit 1; \
	fi
	$(BIN)/streamlit run run_dashboard.py -- $(SPEC)

dashboard-enhanced: ## Launch enhanced fraud analysis dashboard (v1.1 features)
	@echo "$(BLUE)Launching enhanced dashboard (DashSpec v1.1)...$(NC)"
	$(BIN)/streamlit run run_dashboard.py -- dsl/examples/enhanced_fraud_analysis.yaml

dashboard-fraud: ## Launch comprehensive fraud detection dashboard (v1.2)
	@echo "$(BLUE)Launching fraud detection analytics (v1.2)...$(NC)"
	$(BIN)/streamlit run run_dashboard.py -- dsl/examples/fraud_detection_v1.2.yaml

dashboard-pollution: ## Launch US pollution analysis dashboard (v1.2)
	@echo "$(BLUE)Launching US pollution analytics (v1.2)...$(NC)"
	$(BIN)/streamlit run run_dashboard.py -- dsl/examples/us_pollution_v1.2.yaml

dashboard-spotify: ## Launch Spotify tracks analysis dashboard (v1.2)
	@echo "$(BLUE)Launching Spotify music analytics (v1.2)...$(NC)"
	$(BIN)/streamlit run run_dashboard.py -- dsl/examples/spotify_tracks_v1.2.yaml

dashboard-reviews: ## Launch Amazon food reviews analysis dashboard (v1.2)
	@echo "$(BLUE)Launching Amazon reviews analytics (v1.2)...$(NC)"
	$(BIN)/streamlit run run_dashboard.py -- dsl/examples/amazon_reviews_v1.2.yaml

dashboard-hr: ## Launch IBM HR attrition analysis dashboard (v1.2)
	@echo "$(BLUE)Launching HR attrition analytics (v1.2)...$(NC)"
	$(BIN)/streamlit run run_dashboard.py -- dsl/examples/ibm_hr_attrition_v1.2.yaml

dashboard-accidents: ## Launch US traffic accidents analysis dashboard (v1.2)
	@echo "$(BLUE)Launching US accidents analytics (v1.2)...$(NC)"
	$(BIN)/streamlit run run_dashboard.py -- dsl/examples/us_accidents_v1.2.yaml

dashboard-movies: ## Launch TMDB movies analysis dashboard (v1.2)
	@echo "$(BLUE)Launching TMDB movies analytics (v1.2)...$(NC)"
	$(BIN)/streamlit run run_dashboard.py -- dsl/examples/tmdb_movies_v1.2.yaml

dashboard-intrusion: ## Launch network intrusion detection dashboard (v1.2)
	@echo "$(BLUE)Launching network intrusion analytics (v1.2)...$(NC)"
	$(BIN)/streamlit run run_dashboard.py -- dsl/examples/network_intrusion_v1.2.yaml

dashboard-power: ## Launch global power consumption dashboard (v1.2)
	@echo "$(BLUE)Launching power consumption analytics (v1.2)...$(NC)"
	$(BIN)/streamlit run run_dashboard.py -- dsl/examples/power_consumption_v1.2.yaml

dashboard-food: ## Launch global food price inflation dashboard (v1.2)
	@echo "$(BLUE)Launching food price inflation analytics (v1.2)...$(NC)"
	$(BIN)/streamlit run run_dashboard.py -- dsl/examples/food_price_inflation_v1.2.yaml

dashboard-gallery: ## Launch unified dashboard gallery app (all dashboards)
	@echo "$(BLUE)Launching Dashboard Gallery App...$(NC)"
	$(BIN)/streamlit run app.py

##@ Cleaning

clean: ## Remove cache files and build artifacts
	@echo "$(BLUE)Cleaning cache files...$(NC)"
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/ .coverage 2>/dev/null || true
	@echo "$(GREEN)✓ Cache cleaned$(NC)"

clean-data: ## Remove all downloaded and processed data
	@echo "$(YELLOW)Warning: This will delete all data in data/raw, data/processed, and data/metadata$(NC)"
	@echo "Press Ctrl+C to cancel, or wait 5 seconds to continue..."
	@sleep 5
	rm -rf data/raw/* data/processed/* data/metadata/*
	@echo "$(GREEN)✓ Data cleaned$(NC)"

clean-all: clean clean-data ## Clean everything (cache + data)
	@echo "$(GREEN)✓ All cleaned$(NC)"

##@ Documentation

docs: ## Generate documentation (placeholder)
	@echo "$(BLUE)Documentation generation not yet implemented$(NC)"
	@echo "See README.md and docs/ directory for documentation"

##@ Development

dev: install-dev ## Start development mode (install-dev + watch)
	@echo "$(GREEN)Development environment ready!$(NC)"
	@echo "$(BLUE)Available commands:$(NC)"
	@echo "  make dashboard  - Launch dashboard"
	@echo "  make etl        - Run ETL pipeline"
	@echo "  make test       - Run tests"
	@echo "  make check      - Run code quality checks"

watch: ## Watch for file changes and run tests (requires watchdog)
	@echo "$(BLUE)Watching for file changes...$(NC)"
	$(BIN)/watchmedo shell-command \
		--patterns="*.py" \
		--ignore-patterns="*/.venv/*;*/data/*" \
		--recursive \
		--command='make test' \
		.

##@ Git

git-status: ## Show git status and uncommitted changes
	@echo "$(BLUE)Git Status:$(NC)"
	@git status
	@echo ""
	@echo "$(BLUE)Untracked files that might need .gitignore:$(NC)"
	@git status --porcelain | grep "^??" || echo "None"

##@ Information

info: ## Show project information
	@echo "$(BLUE)Project Information$(NC)"
	@echo "Python version: $$($(PYTHON_VENV) --version)"
	@echo "Pip version: $$($(PIP) --version)"
	@echo "Virtual env: $(VENV)"
	@echo ""
	@echo "$(BLUE)Installed Packages:$(NC)"
	@$(PIP) list | grep -E "(pandas|streamlit|plotly|kaggle|pyarrow)" || true
	@echo ""
	@echo "$(BLUE)Data Status:$(NC)"
	@echo "Raw datasets: $$(ls -1 data/raw 2>/dev/null | wc -l | tr -d ' ')"
	@echo "Processed datasets: $$(ls -1 data/processed/*.parquet 2>/dev/null | wc -l | tr -d ' ')"
	@echo "Metadata files: $$(ls -1 data/metadata/*.json 2>/dev/null | wc -l | tr -d ' ')"
