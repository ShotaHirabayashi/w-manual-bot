# Claude Code Usage Guide (Django Project Oriented)

This file provides usage guidelines for Claude Code (claude.ai/code) when working within this repository.

---

## Repository Overview

This workspace contains Django-based applications and services. Each directory represents an individual Django project or app.

---

## Important Notes

- **[MANDATORY]** Use **English** for all thinking and communication. Use **Japanese only for the final output** if required.
- Always **ultrathink** before acting.
- At the end of each task, review any TODOs and ensure everything is complete and clean.

---

## File Structure & Claude Code Conventions

When working with Claude Code, please follow the structure below:

- Long prompts must be saved in the `.claude/prompts/` directory and referenced from there.
- Unused or temporary intermediate files created during thinking or processing should be saved in `.claude/tmp/`.

---

### File Creation and Editing Rules

- All newly created files must be placed **inside the Django project folder**.
- Temporary working files must be saved in `.claude/tmp/`.
- **Do not create or edit files outside** the Django project scope.
- Even final output should initially be saved to `.claude/tmp/` and reviewed before moving into production.

---

## Development Environment

All Django projects in this workspace use **Python virtual environments** (`venv`) for local development.

- Use `source .venv/bin/activate` to activate the environment.
- Refer to each project's `README.md` for specific setup and command instructions.

---

## Claude Temporary File Policy

- All temporary or intermediate files generated during Claude sessions must be placed in `.claude/tmp/`.
- Final deliverables should also be initially saved to `.claude/tmp/`, and moved only after review.

---

## Naming, Dependencies & Font Policy

- **Naming Convention**: Use lowercase snake_case or kebab-case for directory names.
- **Dependency Management**:
  - `backend/requirements` should be modularized (e.g., `base.txt`, `dev.txt`, `prod.txt`).
  - `frontend/` should use `package.json` and `npx` where applicable.
- **Font Management**: Store custom fonts in `frontend/public/fonts` and load using `@next/font/local`.

---

## Django (Python) Coding Guidelines

### 2.1 Coding Style

- Use **Google-style docstrings** for functions, classes, and modules.
- Include **type hints** wherever possible.
- Remove unused imports and variables.
- Recommended line length: **88 characters** (Black's default).

### 2.2 Django Best Practices

- Write code with **maintainability in mind**; avoid overly complex logic and include comments where necessary.
- Always create new apps using:

  ```bash
  python3 manage.py startapp <app_name>
  ```

- **Project structure**: Organize by domain under an `apps/` directory.
- **Models**:
  - Use snake_case for field names.
  - Always define `on_delete` behavior.
  - Implement `__str__` method.
- **Templates**:
  - Use inheritance and common layouts.
  - Always include `{% static %}` and `{% csrf_token %}` where appropriate.
- **Forms & Serializers**:
  - Validate thoroughly.
  - In DRF, organize serializers into `serializers.py`.
- **Security**:
  - Use the Django ORM to avoid raw SQL.
  - Protect against XSS/CSRF.
  - Always hash passwords and sensitive data.

### 2.3 Django Anti-patterns

Avoid the following:

- Placing business logic inside views.
- Writing complex logic directly in templates.
- Using raw SQL unnecessarily or over-nesting queries.
- Ignoring security measures (e.g., CSRF/XSS).
- Poor test coverage.

### 2.4 Error Handling & Logging

- Customize HTTP error pages (e.g., 404/500) using `handler404`, `handler500`, and dedicated templates.
- For business logic, define custom exceptions inheriting from `django.core.exceptions` and catch them in views.

### 2.5 Middleware Policy

- Keep middleware responsibilities **isolated and modular**.
- Insert custom middleware **immediately after official Django middleware** in the `MIDDLEWARE` list.

### 2.6 Authentication & User Management

- Use `django-allauth` for:
  - Password reset flows
  - Email verification
  - Account registration/login

---

## App Structure in `apps/`

- Apps in `apps/` should be organized by **functional domain**, using snake_case names.
- Each app should include:
  - `models.py`
  - `views.py`
  - `forms.py`
  - `serializers.py`
  - `urls.py`
  - `tests.py`
- Follow the **Fat models / Fat services** pattern. Keep views thin.

---

## Database Migration Rules

- Run and commit migrations **per feature or schema update**.
- Before running `makemigrations`, always check for pending changes:

  ```bash
  python manage.py makemigrations --check --dry-run
  ```

---

## Static & Media File Handling

- Define `STATICFILES_DIRS`, `MEDIA_URL`, and `MEDIA_ROOT` clearly.
- Avoid using `runserver` for serving production static/media.
- Use `collectstatic` only for production build pipelines.

---

## Testing Policy

- Place all tests under a `tests/` directory and organize them by module.
- Write unit tests for:
  - Models and their constraints
  - Forms and serializer validation
  - Views and API endpoints
  - Admin interfaces

---

## Claude Collaboration Best Practices

1. Before asking Claude for help, provide **context** about the app’s responsibilities and location (e.g., `apps/account/ handles user registration`).
2. Store long prompts in `.claude/prompts/` and link them by file path.
3. Ask Claude to output **proposals or drafts** into `.claude/tmp/` first, not directly into the codebase.
4. Always review Claude-generated content before applying. Use Git to track diffs.
5. 🧠 Keep It Simple for Claude 
- When writing code or prompts for Claude to review, **prioritize clarity and simplicity**.
- Avoid overly abstract logic, unnecessary indirection, or cryptic variable names.  
- The easier your intent is to understand, the more useful Claude’s responses will be.

---

## Security Policy (Django-Specific)

- Do **not** hardcode secrets or credentials. Use `.env` and `django-environ`.
- Always set `DEBUG = False` in production.
- Change default `admin/` URL to a custom one for security.
- Use Django’s `SECURE_*` settings for SSL enforcement in production.
