# Contributing to BinomoAPI

## Support
donate in paypal: [Paypal.me](https://paypal.me/ChipaCL?country.x=CL&locale.x=en_US) <br> 
help us in patreon: [Patreon](https://patreon.com/VigoDEV?utm_medium=unknown&utm_source=join_link&utm_campaign=creatorshare_creator&utm_content=copyLink) <br>
👉 [Join us on Discord](https://discord.gg/p7YyFqSmAz) <br>
[Get our services here](https://chipa.tech/shop/) <br>
[Let us create your bot here](https://chipa.tech/product/create-your-bot/) <br>
[Contact us in Telegram](https://t.me/ChipaDevTeam)

Thank you for your interest in contributing to BinomoAPI! This guide will help you get started with contributing to the project.

## 🌟 How to Contribute

### 1. Setting Up Development Environment

1. Fork the repository
2. Clone your fork:
```bash
git clone https://github.com/your-username/BinomoAPI.git
cd BinomoAPI
```

3. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Unix/macOS
venv\Scripts\activate     # Windows
```

4. Install dependencies:
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Making Changes

1. Create a new branch:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes
3. Run tests:
```bash
pytest tests/
```

4. Format code:
```bash
black .
isort .
```

5. Run linting:
```bash
flake8 .
mypy .
```

### 3. Submitting Changes

1. Commit your changes:
```bash
git add .
git commit -m "feat: add new feature"
```

2. Push to your fork:
```bash
git push origin feature/your-feature-name
```

3. Create a Pull Request

## 📝 Coding Standards

### Python Code Style

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use type hints
- Maximum line length: 88 characters
- Use descriptive variable names

### Example Code Style

```python
from typing import Dict, Optional

class TradingClient:
    """
    Trading client implementation.
    
    Attributes:
        api_key: API authentication key
        demo_mode: Whether to use demo account
    """
    
    def __init__(
        self,
        api_key: str,
        demo_mode: bool = True
    ) -> None:
        self.api_key = api_key
        self.demo_mode = demo_mode
    
    async def execute_trade(
        self,
        asset: str,
        amount: float,
        direction: str
    ) -> Dict[str, any]:
        """
        Execute a trading operation.
        
        Args:
            asset: Trading asset name
            amount: Trade amount
            direction: Trade direction
            
        Returns:
            Dict containing trade result
            
        Raises:
            TradeError: If trade execution fails
        """
        # Implementation
```

### Documentation Standards

- Use Google-style docstrings
- Document all public APIs
- Include type hints
- Provide usage examples

### Testing Standards

- Write unit tests for all new features
- Maintain test coverage above 80%
- Use pytest fixtures
- Mock external dependencies

Example test:
```python
import pytest
from BinomoAPI import BinomoAPI

@pytest.fixture
def api_client():
    return BinomoAPI(
        auth_token="test_token",
        device_id="test_device",
        demo=True
    )

def test_place_call_option(api_client):
    result = await api_client.place_call_option(
        asset="EUR/USD",
        duration_seconds=60,
        amount=1.0
    )
    assert result["status"] == "success"
```

## 🎯 Pull Request Guidelines

### PR Title Format

Use conventional commits format:
- `feat: add new feature`
- `fix: resolve bug issue`
- `docs: update documentation`
- `test: add tests`
- `refactor: improve code structure`

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Testing
Describe testing done

## Screenshots
If applicable

## Related Issues
Fixes #issue_number
```

### Review Process

1. Code review by maintainers
2. CI checks must pass
3. Documentation must be updated
4. Tests must be included
5. Changes must be rebased on main

## 🚀 Development Workflow

### 1. Feature Development

1. Create issue describing feature
2. Discuss implementation approach
3. Create feature branch
4. Implement feature
5. Add tests
6. Update documentation
7. Submit PR

### 2. Bug Fixes

1. Create issue with reproduction steps
2. Create fix branch
3. Implement fix
4. Add regression test
5. Submit PR

### 3. Documentation Updates

1. Identify documentation needs
2. Create documentation branch
3. Update documentation
4. Submit PR

## 📚 Project Structure

```
BinomoAPI/
├── BinomoAPI/
│   ├── __init__.py
│   ├── api.py
│   ├── exceptions.py
│   ├── models.py
│   └── utils/
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   └── test_utils.py
├── docs/
│   ├── index.md
│   └── api-reference.md
├── examples/
│   └── basic_usage.py
└── setup.py
```

## 🔍 Code Review Process

### Review Checklist

- [ ] Code follows style guide
- [ ] Tests are included
- [ ] Documentation is updated
- [ ] Changes are backwards compatible
- [ ] Error handling is appropriate
- [ ] Performance impact is considered

### Review Comments

- Be constructive
- Explain reasoning
- Provide examples
- Be respectful

## 🎉 Recognition

### Contributors

- All contributors are listed in CONTRIBUTORS.md
- Significant contributors become maintainers
- Active contributors get special recognition

### Rewards

- Recognition in release notes
- Contributor badges
- Community spotlight

## 📅 Release Process

### Version Numbers

Follow semantic versioning:
- MAJOR.MINOR.PATCH
- Example: 1.2.3

### Release Checklist

1. Update version number
2. Update CHANGELOG.md
3. Create release branch
4. Run full test suite
5. Build documentation
6. Create GitHub release
7. Deploy to PyPI

## 🤝 Community Guidelines

### Communication

- Be respectful
- Stay professional
- Help others
- Share knowledge

### Support

- Use GitHub issues for bugs
- Use discussions for questions
- Join Discord community
- Follow Stack Overflow guidelines

## 📝 License

BinomoAPI is MIT licensed. By contributing, you agree to license your contributions under the same terms.

Thank you for contributing to BinomoAPI! 🎉
