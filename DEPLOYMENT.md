# PyPI Deployment Guide for BinomoAPI

This guide walks you through deploying BinomoAPI to PyPI (Python Package Index).

## Quick Start

### Prerequisites

1. **Python 3.8+** installed
2. **PyPI account**: Create accounts at:
   - Test PyPI: https://test.pypi.org/account/register/
   - Production PyPI: https://pypi.org/account/register/
3. **API Tokens**: Generate API tokens for both Test PyPI and production PyPI

### Automated Deployment (Recommended)

#### Option 1: Using the deployment script

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Deploy to Test PyPI (for testing)
python deploy.py test

# Deploy to Production PyPI (when ready)
python deploy.py prod
```

#### Option 2: Using batch script (Windows)

```cmd
REM Deploy to Test PyPI
deploy.bat test

REM Deploy to Production PyPI
deploy.bat prod
```

### Manual Deployment

If you prefer to run commands manually:

```bash
# 1. Clean previous builds
rm -rf build/ dist/ *.egg-info/

# 2. Install build tools
pip install build twine

# 3. Build the package
python -m build

# 4. Check the package
python -m twine check dist/*

# 5. Upload to Test PyPI
python -m twine upload --repository testpypi dist/*

# 6. Upload to Production PyPI (when ready)
python -m twine upload dist/*
```

## Configuration Files

The project uses modern Python packaging standards:

### pyproject.toml
- **Main configuration file** following PEP 518/621
- Contains all package metadata, dependencies, and build configuration
- Replaces most functionality of setup.py

### setup.py
- **Minimal compatibility file** for older tools
- Simply calls `setup()` with no arguments
- All configuration is in pyproject.toml

### MANIFEST.in
- **Controls which files are included** in the distribution
- Includes documentation, data files, and excludes test files

### requirements-clean.txt
- **Runtime dependencies only** for the package
- Used in pyproject.toml dependencies section

### requirements-dev.txt
- **Development dependencies** for testing, linting, building
- Install with `pip install -r requirements-dev.txt`

## GitHub Actions (CI/CD)

The project includes automated workflows:

### Tests Workflow (.github/workflows/tests.yml)
- Runs on every push and pull request
- Tests multiple Python versions (3.8-3.11)
- Runs linting, type checking, and build tests

### PyPI Release Workflow (.github/workflows/pypi-release.yml)
- Automatically deploys on GitHub releases
- Manual deployment option via workflow dispatch
- Supports both Test PyPI and production PyPI

### Setting Up GitHub Secrets

For automated deployment, add these secrets to your GitHub repository:

1. Go to your GitHub repository → Settings → Secrets and variables → Actions
2. Add the following secrets:
   - `TEST_PYPI_API_TOKEN`: Your Test PyPI API token
   - `PYPI_API_TOKEN`: Your production PyPI API token

## Version Management

### Updating Version

1. **Update version in pyproject.toml**:
   ```toml
   [project]
   version = "2.1.0"  # Update this
   ```

2. **Update version in BinomoAPI/__init__.py**:
   ```python
   __version__ = "2.1.0"  # Update this
   ```

3. **Create a Git tag**:
   ```bash
   git tag v2.1.0
   git push origin v2.1.0
   ```

### Semantic Versioning

Follow semantic versioning (semver.org):
- **MAJOR** (2.x.x): Breaking changes
- **MINOR** (x.1.x): New features, backward compatible
- **PATCH** (x.x.1): Bug fixes, backward compatible

## Testing Your Package

### Test Installation from Test PyPI

After uploading to Test PyPI:

```bash
# Install from Test PyPI
pip install --index-url https://test.pypi.org/simple/ BinomoAPI

# Test the installation
python -c "import BinomoAPI; print(BinomoAPI.__version__)"
```

### Test Installation from Production PyPI

After uploading to production:

```bash
# Install from PyPI
pip install BinomoAPI

# Test the installation
python -c "import BinomoAPI; print(BinomoAPI.__version__)"
```

## Troubleshooting

### Common Issues

1. **"File already exists" error**:
   - You're trying to upload a version that already exists
   - Update the version number in pyproject.toml and __init__.py

2. **Authentication errors**:
   - Check your API tokens
   - Make sure you're using the correct repository (testpypi vs pypi)

3. **Build errors**:
   - Run `python -m build` to see detailed error messages
   - Check that all required files are present

4. **Import errors after installation**:
   - Check MANIFEST.in to ensure all necessary files are included
   - Verify package structure with `pip show -f BinomoAPI`

### Validation Commands

Before deploying, run these commands to validate:

```bash
# Check package structure
python -c "import BinomoAPI; print(dir(BinomoAPI))"

# Check dependencies
python -c "import BinomoAPI.api; print('API module imported successfully')"

# Validate metadata
python -m twine check dist/*

# Test build
python -m build
```

## Best Practices

1. **Always test on Test PyPI first** before deploying to production
2. **Use semantic versioning** for version numbers
3. **Keep dependencies minimal** in requirements-clean.txt
4. **Update documentation** when adding new features
5. **Run tests locally** before deploying
6. **Use virtual environments** for testing installations

## Support

If you encounter issues:

1. Check the [GitHub Issues](https://github.com/ChipaDevTeam/BinomoAPI/issues)
2. Review the PyPI documentation: https://packaging.python.org/
3. Join our Discord: https://discord.gg/p7YyFqSmAz
