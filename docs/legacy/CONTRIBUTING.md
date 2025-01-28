# Contributing to Project Olympus

## Development Process

1. **Fork & Clone**
   - Fork the repository
   - Clone your fork locally

2. **Branch**
   - Create a branch for your feature/fix
   - Use descriptive branch names (e.g., `feature/add-rag-caching`, `fix/memory-leak`)

3. **Development**
   - Follow the [Key Principles](README.md#key-principles)
   - Write tests for new functionality
   - Keep changes focused and atomic

4. **Code Quality**
   - Run formatters before committing:
     ```bash
     black olympus tests
     isort olympus tests
     ```
   - Run type checking:
     ```bash
     mypy olympus
     ```
   - Run linting:
     ```bash
     flake8 olympus tests
     ```
   - Ensure all tests pass:
     ```bash
     pytest
     ```

5. **Documentation**
   - Update relevant documentation
   - Add docstrings to new functions/classes
   - Update README if needed

6. **Pull Request**
   - Submit PR against main branch
   - Include clear description of changes
   - Reference any related issues

## Commit Messages

Follow the conventional commits specification:
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `test:` Adding/updating tests
- `refactor:` Code changes that neither fix bugs nor add features
- `perf:` Performance improvements
- `chore:` Other changes that don't modify src or test files

## Code Style

- Follow Google Python Style Guide
- Use type hints
- Write descriptive docstrings
- Keep functions focused and small
- Use meaningful variable names
- Avoid deep nesting
- Prioritize readability
