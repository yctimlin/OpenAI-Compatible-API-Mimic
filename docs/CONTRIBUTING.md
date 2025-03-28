# Contributing to OpenAI-Compatible API Mimic

First off, thank you for considering contributing to OpenAI-Compatible API Mimic! It's people like you that make this tool more useful for everyone.

## Code of Conduct

By participating in this project, you are expected to uphold our [Code of Conduct](CODE_OF_CONDUCT.md). Please report unacceptable behavior to the project maintainers.

## How Can I Contribute?

### Reporting Bugs

This section guides you through submitting a bug report for OpenAI-Compatible API Mimic. Following these guidelines helps maintainers and the community understand your report, reproduce the behavior, and find related reports.

* **Use the GitHub issue search** — check if the issue has already been reported.
* **Check if the issue has been fixed** — try to reproduce it using the latest `main` branch.
* **Use the bug report template** — when you create a new issue, you will see a template that you can fill out.

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for OpenAI-Compatible API Mimic, including completely new features and minor improvements to existing functionality.

* **Use the GitHub issue search** — check if the enhancement has already been suggested.
* **Describe the enhancement in detail** — explain what it should do and why it would be useful.
* **Use the feature request template** — when you create a new issue, select the feature request template.

### Pull Requests

* Fill in the required template
* Follow the style guidelines (will be defined soon)
* Include appropriate tests
* Update the documentation as needed
* Keep pull requests focused on a single feature or bugfix
* If you're adding a new feature, consider creating documentation for it

## Development Setup

1. Fork the repository
2. Clone your fork to your local machine
3. Create a new branch for your changes
4. Install the development dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # If we add this in the future
   ```
5. Make your changes
6. Run tests (to be defined)
7. Commit your changes with a descriptive commit message
8. Push your branch to your fork
9. Submit a pull request from your branch to our main branch

## Styleguides

### Git Commit Messages

* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally after the first line

### Python Styleguide

* Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
* Use 4 spaces for indentation
* Include docstrings for all classes and functions
* Prefer explicit over implicit
* Keep functions small and focused

### Testing Styleguide

* Include tests for all new features
* Keep tests simple and clear
* Ensure all tests pass before submitting a pull request

## Additional Notes

### Issue and Pull Request Labels

This section lists the labels we use to help us track and manage issues and pull requests.

* **bug** - Something isn't working
* **documentation** - Improvements or additions to documentation
* **enhancement** - New feature or request
* **good first issue** - Good for newcomers
* **help wanted** - Extra attention is needed
* **invalid** - This doesn't seem right
* **question** - Further information is requested
* **wontfix** - This will not be worked on

Thank you for contributing! 