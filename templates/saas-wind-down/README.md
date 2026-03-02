# SaaS Wind-Down

A comprehensive checklist for safely and cleanly winding down a Software as a Service (SaaS) subscription — covering data export, integration revocation, security cleanup, billing cancellation, device uninstall, community unfollowing, and account closure.

This template is the counterpart to the [SaaS Spin-Up](../saas-spin-up/) template and mirrors its structure in reverse.

---

## Objective

- Preserve all data before losing access
- Revoke all API access and integrations to prevent orphaned connections
- Cancel billing cleanly to avoid unexpected charges
- Remove the tool from all devices and workflows
- Close out the community and social presence built around the tool
- Archive knowledge and lessons learned for future reference
- Close the account securely and completely

Estimated duration: 60–90 minutes (may span multiple days depending on data volume).

---

## When to Use

- When cancelling a paid SaaS subscription
- When a free tier tool is being deprecated or no longer needed
- When offboarding a tool from a team or organisation
- When a better alternative has been found

---

## Structure Overview

1. Decision & Pre-Wind-Down Planning
2. Data Export & Backup
3. Revoke Integrations & API Access
4. Security Cleanup
5. Cancel Billing & Subscription
6. Uninstall from Devices
7. Community & Social Cleanup
8. Update Documentation & Knowledge Base
9. Account Closure

---

## Important Notes

- **Complete data export before cancelling the subscription** — access may be revoked immediately on cancellation
- **Check notice periods** — some enterprise plans require 30–90 days notice
- **Revoke API keys before deleting the account** — to avoid any dangling authorisations in connected systems
- **Verify backup integrity** — open and confirm exported files are complete before proceeding

---

## Import Instructions

1. Download `template.csv`
2. Create a new project in Todoist
3. Import from CSV
4. Rename project to: `SaaS Wind-Down – [Tool Name]`
5. Work through sections in order — do not skip the data export step
