# Contributing to Sentinel

Thank you for your interest in contributing to the Sentinel Intelligence Platform!

## Development Setup

1. Fork the repository
2. Clone your fork: `git clone <your-fork-url>`
3. Follow the setup instructions in `GETTING_STARTED.md`
4. Create a feature branch: `git checkout -b feature/your-feature-name`

## Code Style

### Python
- Follow PEP 8 guidelines
- Use Black for code formatting: `black .`
- Use isort for import sorting: `isort .`
- Type hints required for all function signatures
- Docstrings required for all public functions (Google style)

### TypeScript/React
- Follow ESLint configuration
- Use Prettier for formatting
- Functional components with hooks
- TypeScript strict mode enabled
- Props interfaces for all components

## Commit Convention

We use Conventional Commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
feat(osint): add certificate transparency log collection
fix(api): correct Neo4j connection error handling
docs(readme): update installation instructions
test(fusion): add multi-INT correlation tests
```

## Pull Request Process

1. Update documentation for any changed functionality
2. Add tests for new features
3. Ensure all tests pass: `pytest` (backend), `npm test` (frontend)
4. Update CHANGELOG.md if applicable
5. Submit PR with clear description of changes

## Testing

### Backend
```bash
cd backend
pytest
pytest --cov=. --cov-report=html
```

### Frontend
```bash
cd frontend
npm test
npm run type-check
```

## Questions?

Open an issue for:
- Bug reports
- Feature requests
- Documentation improvements
- General questions

---

**Classification:** UNCLASSIFIED//FOUO
