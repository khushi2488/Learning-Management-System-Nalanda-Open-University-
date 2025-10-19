# Contributing to Learning Management System 🤝

First off, thank you for considering contributing to the Learning Management System for Nalanda Open University! It's people like you that make this platform a great tool for digital education.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Pull Request Process](#pull-request-process)

---

## 📜 Code of Conduct

This project and everyone participating in it is governed by our commitment to fostering an open and welcoming environment. By participating, you are expected to uphold this code. Please be respectful, constructive, and considerate in all interactions.

### Our Standards

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

---

## 🌟 How Can I Contribute?

There are many ways to contribute to this project:

### 1. Reporting Bugs 🐛
Found a bug? Help us improve by reporting it! See the [Reporting Bugs](#reporting-bugs) section below.

### 2. Suggesting Features ✨
Have an idea for a new feature? We'd love to hear it! Check out [Suggesting Enhancements](#suggesting-enhancements).

### 3. Writing Code 💻
Want to fix a bug or implement a feature? Follow our [Development Workflow](#development-workflow).

### 4. Improving Documentation 📚
Documentation improvements are always welcome, from fixing typos to adding new guides.

---

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.8 or higher
- Git
- A text editor or IDE (VS Code, PyCharm, etc.)
- Basic knowledge of Django and Python

### Setting Up Your Development Environment

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR-USERNAME/Learning-Management-System-Nalanda-Open-University-.git
   cd Learning-Management-System-Nalanda-Open-University-
   ```

3. **Add the upstream repository:**
   ```bash
   git remote add upstream https://github.com/ShailjaVerma18/Learning-Management-System-Nalanda-Open-University-.git
   ```

4. **Create a virtual environment:**
   ```bash
   # On Windows
   python -m venv venv
   venv\Scripts\activate

   # On macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

5. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

6. **Set up the database:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsuperuser
   ```

7. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

---

## 🔄 Development Workflow

### Creating a New Branch

Always create a new branch for your work:

```bash
git checkout -b feature/your-feature-name
```

### Making Changes

1. Make your changes in your feature branch
2. Write or update tests as needed
3. Ensure your code follows our style guidelines
4. Test your changes thoroughly
5. Update documentation if necessary

### Keeping Your Fork Updated

Regularly sync your fork with the upstream repository:

```bash
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

---


## 💬 Commit Message Guidelines

Write clear and meaningful commit messages following this format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, missing semicolons, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples:

```
feat(courses): add course search functionality

Implemented search feature allowing users to search courses by title,
description, and instructor name. Added search form to course listing
page with real-time filtering.

Closes #123
```

```
fix(assignments): resolve submission deadline validation bug

Fixed issue where assignments could be submitted after deadline.
Added proper timezone handling and validation checks.

Fixes #456
```

---

## 🔀 Pull Request Process

### Before Submitting

1. Ensure your code follows our style guidelines
2. Update documentation if you've changed functionality
3. Add or update tests as necessary
4. Verify all tests pass
5. Update the README.md if needed
6. Ensure your branch is up to date with main

### Submitting a Pull Request

1. **Push your changes** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create a Pull Request** on GitHub with a clear title and description

3. **Fill out the PR template** with all relevant information:
   - Description of changes
   - Related issue numbers
   - Type of change (bug fix, new feature, etc.)
   - Testing performed
   - Screenshots (if applicable)

4. **Wait for review** - maintainers will review your PR and may request changes

5. **Address feedback** - make any requested changes and push updates

6. **Celebrate!** 🎉 Once approved, your PR will be merged


## 🏆 Recognition

Contributors will be:
- Listed in the README.md contributors section
- Mentioned in release notes for significant contributions
- Given credit in code comments for major features

---

## 📞 Getting Help

If you need help with your contribution:

- **GitHub Discussions:** Ask questions and discuss ideas
- **Issues:** Tag your question with the `question` label
- **Email:** Reach out to the maintainers

---

## 📚 Additional Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Python PEP 8 Style Guide](https://www.python.org/dev/peps/pep-0008/)
- [Git Documentation](https://git-scm.com/doc)
- [GitHub Flow Guide](https://guides.github.com/introduction/flow/)

---

<div align="center">
<p><strong>Thank you for contributing! 🎉</strong></p>
<p><em>Together, we're building better educational tools</em></p>
</div>

[⬆️ Back to Top](#contributing-to-learning-management-system-)
