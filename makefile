# Makefile for converting BDF to CSV with debug and no-debug options

# Base folders to process
BASE_FOLDERS = ""

# Python script
SCRIPT = main.py

# Python virtual environment directory
VENV_DIR = venv

# Python executable in the virtual environment
PYTHON = $(VENV_DIR)/bin/python

# Default target: convert BDF files to CSV without debug
run: $(VENV_DIR)/bin/activate
	$(PYTHON) $(SCRIPT) --base-folder $(BASE_FOLDERS)

# Target for converting with debug mode
debug: $(VENV_DIR)/bin/activate
	$(PYTHON) $(SCRIPT) --base-folder $(BASE_FOLDERS) --debug

# Install dependencies in a virtual environment
install:
	# Create virtual environment if it doesn't exist
	@echo "Creating virtual environment..."
	python3 -m venv $(VENV_DIR)
	# Install the required packages from requirements.txt
	@echo "Installing dependencies..."
	$(VENV_DIR)/bin/pip install -r requirements.txt

# Uninstall virtual environment by deleting it
uninstall:
	@echo "Deleting virtual environment..."
	rm -rf .$(VENV_DIR)

# Clean log and CSV files if needed
clean:
	rm -f converting.log

# Help message
help:
	@echo "Makefile for converting BDF files to CSV."
	@echo "Usage:"
	@echo "  make run      - Convert BDF to CSV (without debug)"
	@echo "  make debug    - Convert BDF to CSV (with debug)"
	@echo "  make install  - Create a virtual environment and install dependencies"
	@echo "  make uninstall - Delete the virtual environment"
	@echo "  make clean    - Remove log"
	@echo "  make help     - Show this help message"
