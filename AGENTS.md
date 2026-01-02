# Agent Instructions for FastAPI Enterprise AI Gateway

This document provides guidelines for AI agents working on this codebase.

##  Development Workflow

1.  **Understand the Goal**: Carefully read the user's request to understand the requirements.
2.  **Explore the Code**: Use tools like `list_files` and `read_file` to understand the relevant parts of the codebase. Pay special attention to the modular structure in the `src` directory.
3.  **Formulate a Plan**: Create a clear, step-by-step plan using `set_plan`.
4.  **Implement Changes**: Write and modify the code, following the existing patterns and conventions.
5.  **Run Tests**: After making changes, run the test suite to ensure nothing has broken.
6.  **Update Documentation**: If you add or modify a feature, update the `README.md` to reflect the changes.

## Testing

The project uses `pytest` for testing. To run the full test suite, use the following command:

```bash
pytest
```

Ensure all existing tests pass and add new tests for any new functionality you introduce.

## Documentation

The primary user-facing documentation is the `README.md` file. It should always be kept up-to-date with the latest features, setup instructions, and API endpoints.

After implementing a new feature, please take a moment to update the following sections in `README.md`:
-   Core Features
-   Advanced Features
-   Security (if applicable)
-   Setup (if environment variables or dependencies change)
-   API Endpoints & Usage

## Committing and Submitting

When you are ready to submit your work, use a descriptive commit message that clearly explains the changes you made.
