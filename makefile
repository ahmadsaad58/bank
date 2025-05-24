# --- Configuration Variables ---
ENV_NAME = bank
PYTHON_VERSION = 3.13.2
APP_SCRIPT = app.py
REQUIREMENTS_FILE = requirements.txt
CONDA_ENV_FILE = environment.yml

.PHONY: all setup install run test lint clean clean-env help

# --- Default Target ---
all: setup install run

# --- Environment Management ---

# setup: Creates or updates the Conda environment
# Prioritizes CONDA_ENV_FILE if it exists, otherwise creates from scratch.
setup:
	@echo "Setting up Conda environment: $(ENV_NAME)..."
	@if [ -f $(CONDA_ENV_FILE) ]; then \
		conda env create -f $(CONDA_ENV_FILE) || conda env update -f $(CONDA_ENV_FILE); \
	else \
		conda create -n $(ENV_NAME) python=$(PYTHON_VERSION) -y; \
	fi
	@echo "Conda environment $(ENV_NAME) setup complete."

# install: Installs Python dependencies into the active Conda environment
install:
	@echo "Installing Python dependencies from $(REQUIREMENTS_FILE)..."
	conda run -n $(ENV_NAME) pip install -r $(REQUIREMENTS_FILE)
	@echo "Dependencies installed."

# update-dependencies: Exports the current environment to CONDA_ENV_FILE
update-dependencies:
	@echo "Exporting current Conda environment to $(CONDA_ENV_FILE)..."
	conda env export -n $(ENV_NAME) --no-builds > $(CONDA_ENV_FILE)
	pip freeze > $(REQUIREMENTS_FILE)
	@echo "Environment exported."

# --- Code Execution ---

# run: Runs the main application script
run:
	@echo "Running $(APP_SCRIPT)..."
	conda run -n $(ENV_NAME) python $(APP_SCRIPT)

# test: Runs tests using pytest
test:
	@echo "Running tests in $(TEST_PATH)..."
	conda run -n $(ENV_NAME) pytest $(TEST_PATH)

# lint: Runs a linter (flake8, black --check, isort --check-only)
lint:
	@echo "Running linter/formatter check..."
	conda run -n $(ENV_NAME) flake8 .
	conda run -n $(ENV_NAME) black --check .
	conda run -n $(ENV_NAME) isort --check-only .

# format: Formats code using black (in-place) and sorts imports using isort
format:
	conda run -n $(ENV_NAME) black .
	conda run -n $(ENV_NAME) isort .

# --- Cleanup ---
clean:
	@echo "Cleaning up build artifacts and caches..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .pytest_cache/
	rm -rf build/ dist/ *.egg-info/
	@echo "Cleanup complete."

# --- Help ---
help:
	@echo "Usage: make [command]"
	@echo ""
	@echo "Common commands:"
	@echo "  all           : Runs setup, install, and then run (default)"
	@echo "  setup         : Creates or updates the Conda environment"
	@echo "  install       : Installs dependencies from $(REQUIREMENTS_FILE)"
	@echo "  update-env-file: Exports current environment to $(CONDA_ENV_FILE)"
	@echo "  run           : Executes the main application script ($(APP_SCRIPT))"
	@echo "  test          : Runs tests using pytest ($(TEST_PATH))"
	@echo "  lint          : Runs code linter (e.g., flake8)"
	@echo "  format        : Formats code using black"
	@echo "  clean         : Removes Python cache files and build artifacts"
	@echo "  clean-env     : Removes the Conda environment ($(ENV_NAME))"
	@echo "  help          : Displays this help message"
