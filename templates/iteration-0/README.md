# Iteration 0

A Sprint 0 checklist for setting up a new project repository with version control, a defined branching strategy, and Azure DevOps configuration — capturing localisation requirements — configuring Slack build notifications — defining the initial set of API endpoint PBIs — implementing Scalar OpenAPI documentation — enforcing coding standards — establishing a Mediator Pattern reference implementation — and defining the Minimum Viable Product (MVP) — ensuring consistent practices and a shared delivery scope are in place before development begins.

---

## Objective

- Create and configure a Git repository in Azure DevOps
- Establish a clear, documented branching strategy
- Configure branch protection rules and repository policies
- Set up permissions and access controls
- Ensure all standard repository files are in place and available to the team
- Define and document localisation requirements for the project
- Replace email build notifications with real-time Slack notifications
- Define an initial set of Product Backlog Items (PBIs) for key API endpoints
- Implement Scalar as the OpenAPI documentation tool for the .NET Web API
- Establish and enforce coding standards across local development, version control, and CI
- Establish a production-quality Mediator Pattern reference implementation for decoupled component communication
- Define and agree the Minimum Viable Product (MVP) scope with all stakeholders

Estimated duration: up to 120 minutes.

---

## When to Use

- When kicking off a new software project (Sprint 0 / Iteration 0)
- When inheriting a project that lacks a defined version control strategy
- When standardising repository setup across a team or organisation

---

## Acceptance Criteria

### Repository Setup & Version Control
- A new Git repository is created in Azure DevOps
- Branching strategy is defined and documented
- Branch protection rules and policies are configured
- Documentation is available to the team (in repo and/or project wiki)
- Relevant GitHub Copilot agent skills from the `github/awesome-copilot` curated list have been reviewed and added

### Localisation Requirements
- A list of target languages/locales has been agreed and documented
- Cultural formatting rules (date/time formats, currency, number separators) are specified for each locale
- Key UI/UX elements requiring translation are identified
- Any external dependencies (translation services, libraries, APIs) are captured
- Risks and constraints (e.g., right-to-left support, font/character encoding) are documented

### Slack Build Notifications
- A dedicated Slack channel exists for build updates
- Slack Incoming Webhook URL is created and securely stored
- Azure DevOps Service Hook is configured to trigger on build events (success/failure)
- A test build confirms notifications arrive in the chosen Slack channel
- Email build notifications are disabled to prevent duplication

### API Endpoint PBIs
- A set of PBIs is created in Azure DevOps representing the major API endpoints required by the system
- Each PBI includes a title, description (expressing the user/system need), and acceptance criteria (clear, testable outcomes)
- PBIs are grouped under appropriate Epics (Automation, Integration, Scalability, Reliability)
- PBIs are ready for refinement and estimation by the development team

### Scalar OpenAPI Documentation
- The solution includes the `Scalar.AspNetCore` NuGet package
- An OpenAPI 3.1 document is available at `/openapi/v1.json`
- Scalar UI is accessible at `/scalar` and lists all endpoints
- Scalar UI displays the correct project name and title
- The OpenAPI spec automatically updates as endpoints change
- Documentation includes instructions for accessing `/scalar`
- The solution builds and runs successfully without errors or warnings

### Coding Standards
- `.editorconfig` and `Directory.Build.props` files exist at repo root and define agreed coding rules
- Local formatting and analyzer enforcement work automatically in JetBrains Rider
- A Git pre-commit hook or Lefthook integration prevents non-compliant commits
- Azure DevOps PR validation pipeline fails on style violations, warnings, or test errors
- Coding standards documentation is available in `/docs` and published to the Azure DevOps Wiki
- All developers can restore tools and run `dotnet format --verify-no-changes` locally without manual setup

### Mediator Pattern
- A working Mediator Pattern implementation exists under a shared or core project (e.g., `Fingerprintarr.Core.Mediator`)
- `IMediator`, `IRequest<TResponse>`, and `IRequestHandler<TRequest, TResponse>` abstractions are defined
- A concrete `Mediator` implementation resolves handlers via the DI container
- Mediator and handlers are registered in the application's DI configuration
- An example request and handler demonstrate the pattern in practice
- Unit tests cover mediator dispatch and handler resolution
- Usage conventions and the pattern rationale are documented in `/docs`

### MVP Definition
- MVP scope is agreed by all stakeholders and documented in Azure DevOps
- An initial Product Backlog of prioritised PBIs exists, covering MVP features and integrations
- Assumptions, constraints, and dependencies are captured and visible to the team
- Technical feasibility of the MVP scope has been assessed against available resources and timeline
- MVP Definition document is published to the Azure DevOps Wiki and signed off by stakeholders
- Follow-up backlog items for post-MVP features are created and triaged

---

## Structure Overview

1. Repository Setup & Version Control
2. Localisation Requirements
3. Slack Build Notifications
4. API Endpoint PBIs
5. Scalar OpenAPI Documentation
6. Coding Standards
7. Mediator Pattern
8. MVP Definition

---

## Import Instructions

1. Download `template.csv`
2. Create a new project in Todoist
3. Import from CSV
4. Rename the project to: `Iteration 0 – [Project Name]`
5. Work through the tasks in order, adapting steps to your specific project context

---

## Scalar Integration

To integrate Scalar as the OpenAPI documentation UI for your .NET Web API, add the following registrations to `Program.cs`:

```csharp
// Service registration
builder.Services.AddOpenApi();

// Middleware
app.MapOpenApi();
app.MapScalarApiReference();
```

This exposes the OpenAPI specification at `/openapi/v1.json` and the interactive Scalar UI at `/scalar`.

To restrict Scalar to development and test environments only:

```csharp
if (app.Environment.IsDevelopment() || app.Environment.IsEnvironment("Test"))
{
    app.MapOpenApi();
    app.MapScalarApiReference();
}
```

Install the required NuGet package first:

```
dotnet add package Scalar.AspNetCore
```

---

## Task Notes

### Create and add `.github/copilot-instructions.md`

Use the GitHub Copilot coding agent to generate this file automatically. Navigate to [github.com/copilot/agents](https://github.com/copilot/agents), select the repository, and paste the following prompt:

```
Your task is to "onboard" this repository to Copilot coding agent by adding a .github/copilot-instructions.md file in the repository that contains information describing how a coding agent seeing it for the first time can work most efficiently.

You will do this task only one time per repository and doing a good job can SIGNIFICANTLY improve the quality of the agent's work, so take your time, think carefully, and search thoroughly before writing the instructions.

<Goals>
- Reduce the likelihood of a coding agent pull request getting rejected by the user due to
generating code that fails the continuous integration build, fails a validation pipeline, or
having misbehavior.
- Minimize bash command and build failures.
- Allow the agent to complete its task more quickly by minimizing the need for exploration using grep, find, str_replace_editor, and code search tools.
</Goals>

<Limitations>
- Instructions must be no longer than 2 pages.
- Instructions must not be task specific.
</Limitations>

<WhatToAdd>

Add the following high level details about the codebase to reduce the amount of searching the agent has to do to understand the codebase each time:
<HighLevelDetails>

- A summary of what the repository does.
- High level repository information, such as the size of the repo, the type of the project, the languages, frameworks, or target runtimes in use.
</HighLevelDetails>

Add information about how to build and validate changes so the agent does not need to search and find it each time.
<BuildInstructions>

- For each of bootstrap, build, test, run, lint, and any other scripted step, document the sequence of steps to take to run it successfully as well as the versions of any runtime or build tools used.
- Each command should be validated by running it to ensure that it works correctly as well as any preconditions and postconditions.
- Try cleaning the repo and environment and running commands in different orders and document errors and misbehavior observed as well as any steps used to mitigate the problem.
- Run the tests and document the order of steps required to run the tests.
- Make a change to the codebase. Document any unexpected build issues as well as the workarounds.
- Document environment setup steps that seem optional but that you have validated are actually required.
- Document the time required for commands that failed due to timing out.
- When you find a sequence of commands that work for a particular purpose, document them in detail.
- Use language to indicate when something should always be done. For example: "always run npm install before building".
- Record any validation steps from documentation.
</BuildInstructions>

List key facts about the layout and architecture of the codebase to help the agent find where to make changes with minimal searching.
<ProjectLayout>

- A description of the major architectural elements of the project, including the relative paths to the main project files, the location
of configuration files for linting, compilation, testing, and preferences.
- A description of the checks run prior to check in, including any GitHub workflows, continuous integration builds, or other validation pipelines.
- Document the steps so that the agent can replicate these itself.
- Any explicit validation steps that the agent can consider to have further confidence in its changes.
- Dependencies that aren't obvious from the layout or file structure.
- Finally, fill in any remaining space with detailed lists of the following, in order of priority: the list of files in the repo root, the
contents of the README, the contents of any key source files, the list of files in the next level down of directories, giving priority to the more structurally important and snippets of code from key source files, such as the one containing the main method.
</ProjectLayout>
</WhatToAdd>

<StepsToFollow>
- Perform a comprehensive inventory of the codebase. Search for and view:
- README.md, CONTRIBUTING.md, and all other documentation files.
- Search the codebase for build steps and indications of workarounds like 'HACK', 'TODO', etc.
- All scripts, particularly those pertaining to build and repo or environment setup.
- All build and actions pipelines.
- All project files.
- All configuration and linting files.
- For each file:
- think: are the contents or the existence of the file information that the coding agent will need to implement, build, test, validate, or demo a code change?
- If yes:
   - Document the command or information in detail.
   - Explicitly indicate which commands work and which do not and the order in which commands should be run.
   - Document any errors encountered as well as the steps taken to workaround them.
- Document any other steps or information that the agent can use to reduce time spent exploring or trying and failing to run bash commands.
- Finally, explicitly instruct the agent to trust the instructions and only perform a search if the information in the instructions is incomplete or found to be in error.
</StepsToFollow>
   - Document any errors encountered as well as the steps taken to work-around them.
```

Source: [GitHub Docs — Add repository instructions](https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions)

---

### Add relevant agent skills from the github/awesome-copilot curated list

Browse the curated skill list at [github.com/github/awesome-copilot](https://github.com/github/awesome-copilot) and identify any agent skills (instructions, prompts, or tool configurations) that are relevant to this project's stack and workflows. Add the applicable skills to `.github/copilot-instructions.md` or the appropriate configuration location documented in each skill's README.

---

### Register OpenAPI and Scalar services in Program.cs

Add the following registrations to `Program.cs`:

```csharp
// Service registration
builder.Services.AddOpenApi();

// Middleware
app.MapOpenApi();
app.MapScalarApiReference();
```

This exposes the OpenAPI specification at `/openapi/v1.json` and the interactive Scalar UI at `/scalar`. Scope both calls inside a development/test environment check if you do not want them active in production:

```csharp
if (app.Environment.IsDevelopment() || app.Environment.IsEnvironment("Test"))
{
    app.MapOpenApi();
    app.MapScalarApiReference();
}
```
