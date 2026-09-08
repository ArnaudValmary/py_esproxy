cur_dir = $(shell pwd)

poetry_version        = $(shell poetry --version)
poetry_env_path       = $(shell poetry env info --path)
poetry_python_version = $(shell poetry run python --version 2>&1)

pytest_test_dir = .pytest_cache
pytest_cov_dir  = htmlcov

project_name = $(shell cat pyproject.toml | grep -E '^name *= *' | head -1 | cut -d = -f 2- | tr -d " ")
project_version = $(shell cat pyproject.toml | grep -E '^version *= *' | cut -d = -f 2- | tr -d " ")

doc:
	@echo -n
	@echo "Poetry     : $(poetry_version)"
	@echo "• env path : $(poetry_env_path)"
	@echo "• Python   : $(poetry_python_version)"
	@echo "Project"
	@echo "• Name     : $(project_name)"
	@echo "• Version  : $(project_version)"
	@echo
	@echo "Targets"
	@echo "• Dependencies"
	@echo "  → deps          : Install default dependencies"
	@echo "  → deps_all      : Install all dependencies"
	@echo "  → deps_clean    : Clean Poetry all dependencies cache and lock file"
	@echo "  → deps_show     : Show dependencies tree"
	@echo "  → deps_show_all : Show all dependencies tree"
	@echo "• Test"
	@echo "  → test          : Run test"
	@echo "  → test_clean    : Clean all test cache directories"
	@echo "• Coverage"
	@echo "  → cov           : Run coverage"
	@echo "  → cov_open      : Run coverage and open result with firefox (in '$(pytest_cov_dir)' directory)"
	@echo "  → cov_clean     : Clean coverage result"
	@echo "• Build & Publish"
	@echo "  → dist          : Build wheel package"
	@echo "  → dist_clean    : Clean package directory"
	@echo "  → publish       : Publish"
	@echo "• Misc"
	@echo "  → clean         : Call all '*_clean' targets"
	@echo "  → force         : Call 'clean', 'deps_all' and 'test' targets"
	@echo

deps_clean:
	poetry env remove --all
	# rm -rf "$(poetry_env_path)"
	rm -f poetry.lock

deps: deps_clean
	poetry install

deps_all: deps_clean
	poetry install --all-groups

deps_show:
	poetry show --tree

deps_show_all:
	poetry show --tree --all-groups

test_clean:
	find . -name "__pycache__" -exec rm -rf "{}" \; || true ; \
	rm -rf $(pytest_test_dir)

test: test_clean
	poetry run pytest --verbose -vvv -r A

cov_clean:
	rm -rf $(pytest_cov_dir) .coverage

cov: cov_clean
	poetry run pytest --cov --cov-report=html:$(pytest_cov_dir)

cov_open: cov
	firefox "file://$(cur_dir)/htmlcov/index.html"

dist_clean:
	rm -rf dist

dist: dist_clean
	poetry build

publish: dist
	poetry publish

clean: deps_clean test_clean cov_clean dist_clean

force: clean deps_all test
