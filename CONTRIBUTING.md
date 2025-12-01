# Contributing Guide

Thank you for considering contributing to the POC-MarketPredictor-ML project! This guide will help you get started.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Code Standards](#code-standards)
- [Testing Requirements](#testing-requirements)
- [Commit Guidelines](#commit-guidelines)
- [Pull Request Process](#pull-request-process)

---

## Code of Conduct

This project adheres to a code of conduct. By participating, you are expected to uphold this standard:

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Prioritize the project's best interests

---

## Getting Started

### Prerequisites

- **Python 3.10+**
- **Node.js 18+** and npm
- **Git**
- **Docker** (optional, for Prometheus/Grafana)

### Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/KG90-EG/POC-MarketPredictor-ML.git
   cd POC-MarketPredictor-ML
   ```

2. **Install dependencies**:
   ```bash
   # Backend
   pip install -r requirements.txt
   
   # Frontend
   cd frontend
   npm install
   ```

3. **Set up environment variables**:
   ```bash
   # Backend: Create .env file
   cp .env.example .env
   # Add your OPENAI_API_KEY
   
   # Frontend: Create .env.local
   cd frontend
   cp .env.example .env.local
   # Configure VITE_API_URL if needed
   ```

4. **Run the application**:
   ```bash
   # Backend (from project root)
   python3 -m uvicorn trading_fun.server:app --reload
   
   # Frontend (in frontend/)
   npm run dev
   ```

---

## Development Workflow

### Branch Strategy

- `main` - Production-ready code
- Feature branches: `feature/your-feature-name`
- Bug fixes: `fix/issue-description`
- Documentation: `docs/topic`

### Creating a Feature Branch

```bash
git checkout main
git pull origin main
git checkout -b feature/your-feature-name
```

---

## Code Standards

### Python (Backend)

- **Style Guide**: PEP 8
- **Formatter**: Black (line length 127)
- **Linter**: Flake8
- **Type Hints**: Required for public functions

**Format your code**:
```bash
python3 -m black . --line-length 127
python3 -m flake8 . --max-line-length=127
```

**Example**:
```python
from typing import Optional, List

def calculate_signals(data: pd.DataFrame) -> List[dict]:
    \"\"\"
    Calculate trading signals from market data.
    
    Args:
        data: DataFrame with OHLCV data
        
    Returns:
        List of signal dictionaries
    \"\"\"
    # Implementation
    pass
```

### JavaScript/React (Frontend)

- **Style Guide**: Airbnb React/JSX
- **Formatter**: Prettier
- **Linter**: ESLint v9 (flat config)
- **PropTypes**: Required for all components

**Format your code**:
```bash
npm run format
npm run lint
```

**Example**:
```javascript
import PropTypes from 'prop-types'

function MyComponent({ title, count, onAction }) {
  return (
    <div>
      <h2>{title}</h2>
      <button onClick={onAction}>{count}</button>
    </div>
  )
}

MyComponent.propTypes = {
  title: PropTypes.string.isRequired,
  count: PropTypes.number.isRequired,
  onAction: PropTypes.func.isRequired,
}

export default MyComponent
```

### Accessibility

- Use semantic HTML elements
- Include ARIA labels for interactive elements
- Maintain color contrast (WCAG AA: 4.5:1)
- Support keyboard navigation
- Test with screen readers when possible

---

## Testing Requirements

### Backend Tests

Run with pytest:
```bash
pytest tests/ -v
```

**Requirements**:
- Maintain >80% code coverage
- Include unit tests for all new functions
- Mock external API calls
- Test error handling

**Example**:
```python
def test_calculate_rsi():
    data = pd.DataFrame({'close': [100, 102, 101, 103, 105]})
    result = calculate_rsi(data, period=14)
    assert result is not None
    assert len(result) == len(data)
```

### Frontend Tests

Run with Vitest:
```bash
npm run test
```

**Requirements**:
- Test component rendering
- Test user interactions
- Test prop validation
- Mock API calls with MSW or vi.fn()

**Example**:
```javascript
it('renders button and handles click', () => {
  const mockHandler = vi.fn()
  render(<Button onClick={mockHandler}>Click me</Button>)
  
  const button = screen.getByText('Click me')
  fireEvent.click(button)
  
  expect(mockHandler).toHaveBeenCalledOnce()
})
```

---

## Commit Guidelines

We follow **Conventional Commits** format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, no logic change)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```
feat(crypto): add NFT token filtering

Add checkbox to include/exclude NFT tokens from crypto rankings.
Updates CoinGecko API integration to support NFT filtering.

Closes #42
```

```
fix(api): resolve CORS issue for production deployment

Update FastAPI middleware configuration to allow production domain.
Add environment variable for allowed origins.
```

---

## Pull Request Process

### Before Submitting

1. **Update from main**:
   ```bash
   git checkout main
   git pull origin main
   git checkout your-branch
   git rebase main
   ```

2. **Run tests**:
   ```bash
   # Backend
   pytest tests/ -v
   flake8 . --max-line-length=127
   
   # Frontend
   npm run test
   npm run lint
   ```

3. **Update documentation** if needed (README, BACKLOG, etc.)

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Backend tests pass
- [ ] Frontend tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No new warnings generated
```

### Review Process

1. **Automated Checks**: CI must pass (linting, tests)
2. **Code Review**: At least one approval required
3. **Documentation**: Ensure BACKLOG.md is updated if needed
4. **Merge**: Squash and merge to keep history clean

---

## Development Tips

### Debugging

- Backend: Add `import pdb; pdb.set_trace()` for breakpoints
- Frontend: Use React DevTools and browser console
- Check `/docs` endpoint for API documentation
- Use Prometheus/Grafana for performance metrics

### Common Issues

**Backend port already in use**:
```bash
lsof -ti:8000 | xargs kill -9
```

**Frontend port already in use**:
```bash
lsof -ti:5173 | xargs kill -9
```

**Module not found**:
```bash
# Backend: Ensure you're in virtual environment
python3 -m pip install -r requirements.txt

# Frontend: Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

---

## Questions?

- Open an issue on GitHub
- Check existing documentation in `/docs`
- Review the [BACKLOG.md](BACKLOG.md) for planned features

---

Thank you for contributing! 🚀
