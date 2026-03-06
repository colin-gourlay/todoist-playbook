# Code Review

A structured checklist for conducting thorough .NET code reviews, covering code hygiene, unit testing conventions, Action file structure, Entity Framework usage, general best practices, clean code principles, SOLID adherence, error handling, and performance considerations — ensuring consistent, high-quality reviews every time.

---

## Objective

- Catch and resolve compilation warnings and StyleCop violations before merge
- Verify that unit tests follow project conventions and provide adequate coverage
- Confirm that each Action is structured with Request, Response, Handler, and Validator
- Validate Entity Framework usage (constraints, `AsNoTracking`, indexing)
- Enforce naming conventions, DRY principles, and SOLID design
- Confirm appropriate error handling, logging practices, and performance patterns

Estimated duration: up to 60 minutes per pull request.

---

## When to Use

- When reviewing a pull request on a .NET project
- When conducting a peer code review or self-review before requesting approval
- When onboarding a new team member and demonstrating code quality standards

---

## Structure Overview

1. Code Hygiene
2. Unit Testing
3. Code Structure
4. Entity Framework
5. General Best Practices
6. General Structure & Readability
7. DRY – Don't Repeat Yourself
8. Method Design
9. Naming Conventions
10. Clean Code & SOLID Principles
11. Testing & Testability
12. Error Handling & Logging
13. Performance Considerations

---

## Section Details

### 1️⃣ Code Hygiene

Ensure the codebase is free of compilation warnings and StyleCop violations before the pull request is approved:

- **Resolve all compilation warnings** – a clean build with zero warnings is required.
- **SA1200** – `using` directives must be alphabetised.
- **SA1028** – the closing curly brace `}` must be on its own line.
- **SA1101** – each method must be documented with appropriate XML comments.

---

### 2️⃣ Unit Testing

#### Builders

Use the builder pattern to construct complex objects for testing (e.g. request objects, entities). Builders should create objects that are easy to modify and extend across test scenarios.

#### Action Testing

Each Action must have unit tests that cover all relevant components:

| Component | What to Test |
|-----------|-------------|
| **Request** | Input to the handler |
| **Handler** | Handler logic |
| **Behaviour** | Logging, transactions, and other side effects |

#### Validator Testing

Each Action must have a dedicated validator test verifying that all input validation rules are correctly applied.

#### Naming Convention

Unit test methods must follow the convention:

```
MethodName_StateUnderTest_ExpectedResult
```

For example: `CreateUser_WithDuplicateEmail_ThrowsValidationException`

---

### 3️⃣ Code Structure

Each Action folder must contain the following files:

| File | Purpose |
|------|---------|
| **Request** | Data passed into the Action |
| **Response** | Data returned after processing |
| **Handler** | Logic that processes the Action |
| **Validator** | Input validation before the Action is processed |

---

### 4️⃣ Entity Framework

- **Consistent validation** – validation constraints must align with the underlying EF model (e.g. if a column has `MaxLength(50)`, the validator must not permit values longer than 50 characters).
- **`AsNoTracking()`** – use `AsNoTracking()` on read-only queries to improve performance.
- **Entity indexing** – review entities to identify columns that would benefit from a database index (frequently queried columns, foreign keys, etc.).

---

### 5️⃣ General Best Practices

- **Global Usings** – leverage global usings to reduce redundant file-level `using` statements.
- **DTO naming** – DTOs must follow the `MapToDto` convention (e.g. `UserMapToDto` instead of `UserDto`).
- **Handler validation** – the Handler must be responsible for implementing validation logic, typically via FluentValidation.
- **`BaseHandler` inheritance** – every Handler must inherit from `BaseHandler` to enforce a consistent pattern and reduce boilerplate.

---

### 6️⃣ General Structure & Readability

- Code is easy to understand without excessive comments
- Functions and methods are named clearly and concisely
- Complex or nested blocks are refactored for clarity
- Files and classes use `.NET` PascalCase naming conventions
- Consistent indentation style is used throughout

---

### 7️⃣ DRY – Don't Repeat Yourself

- No duplicate code blocks — extract repeated logic into methods, classes, or extension methods
- Similar logic is abstracted into reusable functions or components
- Magic numbers and strings are replaced with named constants or enums
- Utility classes and extension methods are used where appropriate

---

### 8️⃣ Method Design

- Methods are small and focused — each method does one thing (Single Responsibility Principle)
- Methods are generally under 20–30 lines
- Method signatures are clear and avoid excessive parameters (consider a model/DTO if needed)
- Methods and classes are loosely coupled to promote testability and maintainability

---

### 9️⃣ Naming Conventions

| Scope | Convention |
|-------|-----------|
| Classes, methods, properties | PascalCase |
| Local variables, parameters | camelCase |
| All identifiers | Meaningful and descriptive — avoid unclear abbreviations |

---

### 🔟 Clean Code & SOLID Principles

#### SOLID

| Principle | Description |
|-----------|------------|
| **S** – Single Responsibility | Each class has one reason to change |
| **O** – Open/Closed | Open for extension; closed for modification |
| **L** – Liskov Substitution | Subtypes are substitutable for their base types |
| **I** – Interface Segregation | No class depends on methods it does not use |
| **D** – Dependency Inversion | Depend on abstractions, not concretions |

#### Additional Checks

- Hardcoded values are replaced with constants or configuration
- Exceptions are caught correctly and not swallowed silently
- `async`/`await` is used correctly — no `Task.Wait()` or `Task.Result` blocking calls

---

### 1️⃣1️⃣ Testing & Testability

- Sufficient unit test coverage, including boundary and edge cases
- Test names are clear and descriptive
- Tests are isolated and independent of each other
- External services and databases are mocked or stubbed in unit tests

---

### 1️⃣2️⃣ Error Handling & Logging

- Appropriate exception types are caught with meaningful messages
- Logging follows a consistent format
- Sensitive data (e.g. passwords, tokens) is excluded from log output

---

### 1️⃣3️⃣ Performance Considerations

- No obvious performance bottlenecks such as expensive operations inside loops
- No memory or database connection leaks
- Appropriate collections and data structures are chosen for the task (e.g. `Dictionary<>` for lookups, `List<>` for ordered sequences)

---

## Import Instructions

1. Download `template.csv`
2. Create a new project in Todoist
3. Import from CSV
4. Rename the project to: `Code Review – [PR / Feature Name]`
5. Work through each section, checking off items as you review the pull request
