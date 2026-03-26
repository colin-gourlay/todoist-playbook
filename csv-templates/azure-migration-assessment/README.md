# Azure Migration Assessment

A structured assessment and planning checklist for migrating an on-premises application stack — .NET Framework backend, Angular frontend, and SQL Server database — to Microsoft Azure.

---

## Objective

- Understand the current estate, dependencies, and migration blockers
- Define the target Azure architecture per component
- Make explicit, justified decisions on hosting, database, identity, and networking
- Produce a phased delivery plan with rollback considerations
- Ensure the target solution is secure, observable, resilient, and supportable in Azure

Estimated duration: 8 hours (spread across multiple working sessions).

---

## When to Use

- When planning the migration of an on-premises application to Microsoft Azure
- When the current stack includes .NET Framework (including end-of-support versions such as 4.6), Angular, and SQL Server
- As a structured framework to drive architecture, DevOps, and engineering conversations before committing to a migration approach
- When aligning a migration plan with the Azure Well-Architected Framework and Cloud Adoption Framework

---

## Structure Overview

1. **Estate Discovery & Current-State Assessment** — Inventory components, dependencies, and non-functional requirements; run Azure Migrate and SQL assessment tooling
2. **Migration Strategy Decisions** — Determine rehost, replatform, or refactor/modernise for each layer
3. **Backend Assessment (.NET Framework 4.6)** — Identify blockers, upgrade path decisions, config/secret handling, and resiliency patterns
4. **Frontend Assessment (Angular)** — Confirm version compatibility, hosting model, build pipeline, and deployment approach
5. **Database Assessment & Migration Planning** — Validate SQL compatibility with Azure targets; plan schema, data, and cutover
6. **Azure Landing Zone & Environment Design** — Subscription strategy, naming, RBAC, networking, policy, and governance foundations
7. **Target Architecture Design** — Document preferred hosting per tier, ingress strategy, WAF, and produce architecture diagram
8. **Identity, Secrets & Security** — Entra ID integration, Key Vault, managed identities, private endpoints, and compliance
9. **Observability & Operations** — Application Insights, distributed tracing, SLOs, runbooks, and release health probes
10. **DevOps, IaC & Release Management** — CI/CD pipelines, environment promotion, release patterns, and drift control
11. **Data Migration & Cutover Planning** — Migration type decision, rehearsal migrations, cutover window, validation, and rollback
12. **Performance, Resilience & Scalability** — Performance baseline, scaling approach, retry logic, and DR validation
13. **Cost & Licensing** — Run cost estimates, licensing options, PaaS vs IaaS trade-offs, and cost controls
14. **Risks, Assumptions & Open Questions** — Document blockers, unknowns, and assign owners for resolution

---

## Import Instructions

1. Download `template.csv`
2. Create a new project in Todoist
3. Import from CSV
4. Rename the project to: `Azure Migration Assessment – [Application Name]`
5. Work through each section in order, adapting tasks to your specific application and organisational context

---

## Deliverables

When all sections are complete, you should have:

- Current-state architecture summary and dependency map
- Target Azure architecture diagram
- Hosting recommendation per component (backend, frontend, database)
- Security and identity approach
- Landing zone and environment prerequisites
- Migration backlog with phased work items
- Cutover and rollback strategy
- Costed options and recommendation
- Key risks, assumptions, and open questions register

---

## References

- [Azure Cloud Adoption Framework](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/)
- [Azure Well-Architected Framework](https://learn.microsoft.com/en-us/azure/well-architected/)
- [Azure Migrate](https://learn.microsoft.com/en-us/azure/migrate/migrate-services-overview)
- [Azure Database Migration Service](https://learn.microsoft.com/en-us/azure/dms/dms-overview)
- [Azure Landing Zones](https://learn.microsoft.com/en-us/azure/cloud-adoption-framework/ready/landing-zone/)
- [App Service Migration Assistant](https://azure.microsoft.com/en-us/products/app-service/migration-tools/)
