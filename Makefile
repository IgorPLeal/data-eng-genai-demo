.PHONY: lint format test package clean

lint:
	black --check src/ tests/
	flake8 src/ tests/

format:
	black src/ tests/

test:
	pytest tests/ -v

package:
	python -m build

clean:
	rm -rf dist/ build/ *.egg-info src/*.egg-info
