# Artist Interview Invite Email

An AI prompt template for generating concise, persuasive interview invite emails for artists, bands, and their representatives.

---

## Objective

- Produce high-impact invite emails quickly without sounding generic
- Keep message length tight while retaining credibility
- Generate both initial and follow-up outreach copy in one run
- Generate a dedicated variant for agent, manager, and label contacts

---

## When to Use

- When inviting artists or bands into the East Coast FM studio
- When contacting direct artist emails or management contacts
- When you need a fast personalized draft before sending outreach

---

## Inputs

| Variable | Required | Description |
|----------|----------|-------------|
| `{{task_title}}` | Yes | Short heading for the outreach task |
| `{{context}}` | Yes | Recipient, artist, release context, timeframe, and tone guidance |
| `{{priority}}` | Yes | Urgency level used to tune CTA strength |

---

## Output Schema

The prompt returns:

- Three subject line options
- One initial invite email
- One agent or label version of the invite
- One 7-day follow-up email
- Optional short DM version

---

## Usage Instructions

1. Open `prompt.md`.
2. Copy the text in the Prompt section.
3. Replace placeholders with real values.
4. Paste into your AI assistant and run.
5. Use the generated output directly in email outreach.

---

## Worked Example

### Input

- Task title: Invite Northshore Lines for a live studio interview
- Context: Recipient is the management team for Northshore Lines. New single "Static Fires" released this month. Invite them onto Sundown Sessions (East Coast FM, Tuesday 8:00-10:00pm) within the next 4-6 weeks. Keep tone warm and direct.
- Priority: high

### Example Output (abbreviated)

SUBJECT OPTIONS:
1. Live Studio Interview Invite: Northshore Lines on East Coast FM
2. Interview Request for Northshore Lines (Sundown Sessions)
3. East Coast FM Invite: Feature Northshore Lines Live in Studio

INITIAL EMAIL:
Hi The management team,
I am Colin, presenter of Sundown Sessions on East Coast FM in Haddington (Tuesday 8:00-10:00pm). I have been featuring Northshore Lines on the show and would love to invite the band in for a live studio interview around the recent "Static Fires" release. We are passionate about championing new music and giving artists space to share their story, current work, and what comes next. If this is of interest, would the band be available in the next 4-6 weeks?
Best regards,
Colin

AGENT OR LABEL EMAIL:
Hi The management team,
I am reaching out from Sundown Sessions on East Coast FM in Haddington to invite Northshore Lines for a live studio interview supporting the current "Static Fires" release cycle. The show focuses on promoting new music and giving artists editorial space to discuss recent work and upcoming plans. If this fits your campaign schedule, would the band be available for a studio interview in the next 4-6 weeks?
Best regards,
Colin

FOLLOW-UP EMAIL (7 DAYS):
Hi The management team,
Just a quick follow-up on my earlier note. I would still love to invite Northshore Lines into East Coast FM for a live interview on Sundown Sessions. If useful, I can offer flexible dates in the next 4-6 weeks and work around your schedule. Would this be of interest?
Best regards,
Colin
