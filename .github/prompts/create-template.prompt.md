# 🎯 Purpose
Create a reusable Todoist template that can be imported via CSV.

# 🧠 Context
This repository provides structured productivity templates.
Templates must:
- Be reusable
- Be consistent
- Support Todoist CSV import

# 📥 Inputs
- Template name
- Purpose
- Sections (optional)

# 📤 Output Requirements
- Valid CSV format
- Header: Section,Task,Labels,Priority,Due Date
- Tasks must be action-oriented
- Logical grouping into sections

# ⚙️ Instructions
- Use clear section names (e.g. Planning, Execution, Review)
- Prefix tasks with verbs (Review, Plan, Identify, etc.)
- Avoid vague tasks (e.g. “Do stuff”)
- Apply labels where appropriate (@deep-work, @admin, @review)
- Use Priority 1–4 where relevant

# 🧪 Example
Input:
Template: Weekly Review

Output:
Section,Task,Labels,Priority,Due Date
Planning,Review last week,@review,2,
Execution,Plan next week,@planning,2,
Review,Identify improvements,@reflection,3,
