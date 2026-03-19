# Code Review Checklist

A language-agnostic, structured checklist for performing thorough code reviews across any repository or technology stack — covering understanding the change, code quality, style, architecture, testing, reliability, security, performance, and operational readiness.

---

## Purpose

This template helps reviewers perform systematic, consistent code reviews. It reduces cognitive load by providing a structured sequence of checks, ensuring that important concerns are not overlooked regardless of the language or framework under review.

---

## When to Use

- When reviewing a pull request
- When reviewing a feature branch before merge
- When conducting a significant refactor review
- When performing a self-review before requesting approval

---

## Philosophy

A good code review focuses on:

- **Correctness** — does the change do what it is supposed to do?
- **Clarity** — is the code easy to read and understand?
- **Maintainability** — will this code be easy to change in the future?
- **Reliability** — does the change handle failure gracefully?
- **Operational readiness** — is the change safe to deploy?

---

## Structure Overview

1. Understand the Change
2. Code Quality
3. Style & Standards
4. Architecture & Design
5. Testing
6. Reliability & Observability
7. Configuration & Security
8. Performance Considerations
9. Deployment & Operations
10. Final Review

---

## Section Details

### 1️⃣ Understand the Change

Before reviewing any code, take time to understand the intent of the change:

- Read the pull request description and any linked issue or ticket
- Confirm the change addresses the stated problem
- Check that the scope of changes is appropriate — no unrelated modifications

---

### 2️⃣ Code Quality

Review the code for common quality issues:

- No TODO or FIXME comments left in the final code
- No hard-coded values or magic numbers
- Meaningful, descriptive variable and method names
- Clear and readable structure
- No duplicate or unnecessary code

---

### 3️⃣ Style & Standards

Confirm the change meets the project's style and standards:

- Linting rules and static analysis pass
- Consistent code formatting
- Naming conventions are followed
- Comments are clear, relevant, and helpful

---

### 4️⃣ Architecture & Design

Evaluate the design of the change:

- The design fits the existing architecture
- Separation of concerns is respected
- Dependencies are appropriate and necessary
- No unnecessary complexity has been introduced

---

### 5️⃣ Testing

Verify test coverage and quality:

- Appropriate tests are included for new behaviour
- Test coverage reflects the risk and complexity of the change
- Tests are meaningful, readable, and maintainable
- Tests would catch regressions if the behaviour breaks

---

### 6️⃣ Reliability & Observability

Check that the change is robust and observable in production:

- Health checks are included where the service requires them
- Logging is meaningful and not excessive or sensitive
- Error handling and failure paths are correctly implemented
- Retry or resilience patterns are applied where appropriate

---

### 7️⃣ Configuration & Security

Ensure the change is secure and correctly configured:

- No secrets, credentials, or tokens are committed to the codebase
- Configuration values are externalised (environment variables, config files, secret stores)
- Environment-specific configuration is handled correctly
- Dependencies are reviewed for known security concerns

---

### 8️⃣ Performance Considerations

Identify potential performance issues:

- No inefficient loops or database queries
- Large objects and data structures are handled efficiently
- Async patterns are used correctly where appropriate

---

### 9️⃣ Deployment & Operations

Confirm the change is safe and ready to deploy:

- Infrastructure changes are included if the code requires them
- Monitoring and alerting are considered for the change
- Backward compatibility is maintained where required
- Migration or phased rollout considerations are documented

---

### 🔟 Final Review

Complete the review and communicate clearly:

- The code is understandable by other engineers on the team
- Constructive feedback has been left in the pull request comments
- The pull request is approved or changes have been requested with clear reasoning

---

## Suggested Workflow

1. Import `template.csv` into Todoist
2. Create a new project named `Code Review – [PR / Feature Name]`
3. Open the pull request alongside the checklist
4. Work through each section in order, checking off items as you go
5. Leave feedback in the GitHub pull request as you identify issues
6. Approve or request changes once all sections are complete

---

## Import Instructions

1. Download `template.csv`
2. Create a new project in Todoist
3. Import from CSV
4. Rename the project to: `Code Review – [PR / Feature Name]`
5. Work through each section, checking off items as you review the pull request
