# Contributing to AutoLaTeX

First off, thank you for considering contributing to AutoLaTeX!

## Table of Contents

- [How Can I Contribute?](#how-can-i-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Your First Code Contribution](#your-first-code-contribution)
  - [Pull Requests](#pull-requests)
- [Pull Request Process](#pull-request-process)
  - [Step-by-Step Guide](#step-by-step-guide)
  - [Pull Request Guidelines](#pull-request-guidelines)
    - [⚠️ Important Note on README ⚠️](#️-important-note-on-readmemd-️)
- [Style Guidelines](#style-guidelines)
  - [Python Style Guide](#python-style-guide)
  - [Git Commit Messages](#git-commit-messages)
- [License](#license)


## How Can I Contribute?

### Reporting Bugs

This section guides you through submitting a bug report for AutoLaTeX. Following these guidelines helps maintainers and the community understand your report, reproduce the behavior, and find related reports.

**Before Submitting A Bug Report:**
- Check the [issues](https://github.com/gallandarakhneorg/autolatex2/issues) to see if the problem has already been reported.
- Perform a cursory search to see if the problem has been fixed in a newer version.

**How Do I Submit A (Good) Bug Report?**
Bugs are tracked as [GitHub issues](https://guides.github.com/features/issues/). Create an issue on the project repository and provide the following information:

- **Use a clear and descriptive title** for the issue to identify the problem.
- **Describe the exact steps which reproduce the problem** in as many details as possible.
- **Provide specific examples to demonstrate the steps**. Include links to files or GitHub projects, or copy/pasteable snippets, which you use in those examples.
- **Describe the behavior you observed after following the steps** and point out what exactly is the problem with that behavior.
- **Explain which behavior you expected to see instead and why.**
- **Include details about your configuration and environment.**
  - Which version of AutoLaTeX are you using?
  - What's the name and version of the OS you're using?
  - Are you running AutoLaTeX in a virtual machine? If so, which VM software are you using and which operating systems and versions are used for the host and the guest?

### Suggesting Enhancements

This section guides you through submitting an enhancement suggestion for AutoLaTeX, including completely new features and minor improvements to existing functionality.

**Before Submitting An Enhancement Suggestion:**
- Check the [issues](https://github.com/gallandarakhneorg/autolatex2/issues) to see if the enhancement has already been suggested.
- Perform a cursory search to see if the enhancement has already been implemented in a newer version.

**How Do I Submit A (Good) Enhancement Suggestion?**
Enhancement suggestions are tracked as [GitHub issues](https://guides.github.com/features/issues/). Create an issue on the project repository and provide the following information:

- **Use a clear and descriptive title** for the issue to identify the suggestion.
- **Provide a step-by-step description of the suggested enhancement** in as many details as possible.
- **Provide specific examples to demonstrate the steps**.
- **Describe the current behavior** and **explain which behavior you expected to see instead** and why.
- **Explain why this enhancement would be useful** to most AutoLaTeX users.

### Your First Code Contribution

### Pull Requests

The primary method of contributing to AutoLaTeX is through GitHub Pull Requests. Please follow the detailed process outlined below.

## Pull Request Process

### Step-by-Step Guide

1. **Fork the repository** to your own GitHub account.
2. **Clone the forked repository** to your local machine:
   ```bash
   git clone https://github.com/YOUR_USERNAME/autolatex2.git
   cd autolatex2
   ```
3. **Make your changes** following the style guidelines.
4. **Commit your changes** with a clear commit message (see guidelines below).
5. **Push your branch** to your forked repository:
   ```bash
   git push origin feature/your-feature-name
   ```
6. **Open a Pull Request** against the `master` branch of the main repository.
7. **Fill out the Pull Request template** with all required information.
8. **Wait for review** - a maintainer will review your PR and may request changes.

### Pull Request Guidelines

- **Keep pull requests focused** on a single change. If you want to fix multiple issues, please submit separate PRs.
- **Write detailed descriptions** explaining what your PR does and why.
- **Update documentation** if you're changing functionality or adding new features.
- **Add tests** for any new code (if the project has a testing framework).
- **Ensure all tests pass** before submitting the PR.
- **Link related issues** in your PR description using keywords like "Fixes #123" or "Resolves #456".
- **Request a review** from a maintainer after making requested changes.

### ⚠️ Important Note on README ⚠️

**DO NOT edit the `README` file directly.** The `README` is automatically generated from the `docs/autolatex.md` file (in Markdown format). Any changes to the project's main documentation should be made by editing `docs/autolatex.md`. After updating the Markdown file, the `README` will be regenerated during the release process.

If you need to update the project's documentation:
1. Edit `docs/autolatex.md` with your changes.
2. Test your changes locally by converting the Markdown to text (using `pandoc -s -t plain docs/autolatex.md -o README`).
2. On Unix: Test your changes locally by converting the Markdown to Unix ROFF man page (using `pandoc -s -t man docs/autolatex.md -o README.1; man -l README.1`).
3. If possible, include both the Markdown and the regenerated README in your pull request, but not the Unix ROFF man page.

Other documentation files (such as this CONTRIBUTING.md) can be edited directly.

## Style Guidelines

### Python Style Guide

AutoLaTeX follows the [PEP 8](https://peps.python.org/pep-0008/) style guide for Python code. Additionally:

- Use types everywhere, as well as, object-oriented annotations.
- Use descriptive variable names (e.g., `document_path` instead of `dp`).
- Add docstrings to all public or protected functions, classes, and methods following the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) for docstrings.
- Use type hints where appropriate to improve code readability and maintainability.

### Git Commit Messages

- Use the present tense ("Add feature" not "Added feature").
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...").
- Limit the first line to 50 characters or less.
- Reference issues and pull requests liberally after the first line.

## License

By contributing to AutoLaTeX, you agree that your contributions will be licensed under the [GNU General Public License v2.0](https://github.com/gallandarakhneorg/autolatex2/blob/master/COPYING) (or later version at the discretion of the maintainers) that covers the AutoLaTeX project.
