---
name: frontend-designs
description: Generate modern, production-ready UI components and pages for the Spendly expense tracker. Trigger this skill whenever the user says "design the ___ page", "create UI for ____", "build component for ____", or "redesign/improve ____". This skill produces clean, responsive, fintech-quality interfaces with consistent design patterns, proper spacing, meaningful icons, and modular code. Always use this skill for any UI/component creation in Spendly — don't just output code snippets, use the full skill workflow.
disable-model-invocation: true
---

# Spendly UI Component Generator

A skill for designing and building production-ready UI components and pages for the Spendly expense tracker app.

## Core Capability

This skill generates complete, high-quality user interfaces that are:
- **Modern & polished** — fintech-style design with clean aesthetics
- **Responsive** — mobile-first, works on all screen sizes
- **Usable** — clear hierarchy, meaningful icons, intuitive flows
- **Consistent** — matches Spendly's existing design system
- **Production-ready** — clean code, modular components, minimal boilerplate

## When to Use This Skill

Use this skill whenever the user wants to create, redesign, or improve any UI in Spendly:
- `"design the dashboard page"`
- `"create UI for expense categories"`
- `"build a transaction detail component"`
- `"redesign the navigation header"`
- `"improve the login form"`

If the user asks for any page, component, or interface in Spendly, this skill should be consulted.

## Input

The user provides:
- **Component/page name** (required) — what are we building? (e.g., "expense list", "settings page", "category selector")
- **Constraints** (optional) — any specific requirements (e.g., "mobile-only", "dashboard widget", "inline form")
- **Data context** (optional) — what data does it display? (e.g., "list of 20 transactions with categories")
- **References** (optional) — existing designs, screenshots, or design patterns to match

## Output Structure

Every generated component includes:

### 1. Design Brief
- **Layout overview** — main sections and their purposes
- **Key UX decisions** — why we made specific choices (spacing, hierarchy, interactions)
- **Design rationale** — how this fits into Spendly's broader design system

### 2. UI Code
- **HTML structure** — clean, semantic, no unnecessary nesting
- **CSS styling** — modular, uses CSS variables, follows 8px grid
- **Icons** — lucide-react icons where appropriate (for React), or inline SVG icons (for HTML)
- **Responsive behavior** — mobile-first approach, clear breakpoints

### 3. Design Quality Checklist
- Modern SaaS fintech aesthetic
- Proper spacing and visual hierarchy
- Subtle colors and shadows (no harsh contrasts)
- Rounded corners (8px default, 12px for cards)
- Consistent padding/margins (multiples of 8px)
- Good contrast for accessibility

### 4. Code Quality
- Minimal boilerplate — no bloated framework code
- Modular components — easy to customize and reuse
- CSS variables for theming — colors, spacing, typography
- Mobile-responsive — tested at multiple breakpoints
- Clean and readable — well-organized, commented where needed

## Design System

### Colors
- **Primary**: Clean, modern blues and teals (fintech standard)
- **Neutrals**: Grays for secondary text and borders
- **Semantic**: Green (success), red (danger), amber (warning)
- **Backgrounds**: White primary, light gray secondary, subtle tertiary
- No bright or saturated colors — keep it professional

### Typography
- **Headlines**: 18–24px, 500 weight (bold but not heavy)
- **Body**: 14–16px, 400 weight
- **Labels**: 12–13px, 400 weight
- Font family: System fonts (San Francisco, Segoe UI) for performance

### Spacing
- **Base unit**: 8px grid
- **Common gaps**: 8px, 12px, 16px, 24px, 32px
- **Card padding**: 16px (1rem)
- **Section spacing**: 24–32px vertical

### Components
- **Cards**: White bg, 0.5px gray border, 8px radius, subtle shadow
- **Buttons**: 36px height, 8px radius, soft shadows on hover
- **Inputs**: 40px height, light gray bg, 8px radius, clear focus state
- **Icons**: 20–24px size, muted gray or brand color
- **Badges**: Subtle background with semantic color, 6px padding, 4px radius

### Shadows
- **Subtle**: `0 1px 3px rgba(0,0,0,0.1)`
- **Medium**: `0 4px 12px rgba(0,0,0,0.08)`
- **Focus**: `0 0 0 3px rgba(59,130,246,0.1)` (blue)
- Never harsh or dark shadows — keep it light and professional

## Design Rules

1. **Minimal, clean fintech aesthetic** — think modern banking apps, not colorful startups
2. **8px grid system** — all spacing and sizing follows this rule
3. **Rounded corners** — 8px default, 12px for prominent cards, avoid harsh corners
4. **Soft shadows** — subtle depth, never overwhelming
5. **Consistent spacing** — no random margins or padding
6. **Meaningful icons** — only use icons that clarify, not decorate
7. **Clear hierarchy** — font size, weight, and color guide the eye
8. **Avoid clutter** — whitespace is a design element, use it generously
9. **Mobile-first** — design for small screens first, scale up

## Consistency Rule

Every design must match Spendly's existing design patterns. Before generating, check:
- What colors are used in existing pages?
- What's the button style? Input style? Card style?
- What icons are already in use?
- What's the overall tone?

**If unclear**, ask the user for:
- Screenshots of existing Spendly pages
- Links to the project repo
- Color palette or design tokens
- Existing component examples

## What NOT to Do

❌ Don't generate dated or generic UI  
❌ Don't dump unstructured code without explanation  
❌ Don't use harsh colors, bright gradients, or busy patterns  
❌ Don't ignore spacing and alignment  
❌ Don't create one-off styles — use system patterns  
❌ Don't ignore mobile responsiveness  
❌ Don't use random icon libraries — stick to lucide/heroicons  
❌ Don't build components that don't fit the existing design  

## Workflow

1. **Clarify the request** — what exactly are we building?
2. **Ask for context** — existing designs, data, constraints
3. **Design brief** — explain the layout and UX decisions
4. **Generate code** — clean, modular, production-ready
5. **Test cases** — show how it works with real data
6. **Iterate** — refine based on user feedback

## Example Trigger Phrases

- "Design the expense detail page"
- "Create a category filter component"
- "Build the transaction list UI"
- "Improve the dashboard cards"
- "Design a date picker for Spendly"
- "Create the expense form"
- "Build an empty state component"
- "Design the settings page"

---

## Implementation Workflow

1. **Clarify the request**
   - What component/page is being built?
   - Are there any specific constraints or data requirements?
   - Should this match existing Spendly designs?

2. **Design brief**
   - Explain the layout and key sections
   - Describe UX decisions and rationale
   - Show how this fits into the broader app

3. **Generate code**
   - Provide clean, production-ready HTML + CSS
   - Use CSS variables for consistency
   - Include responsive design (mobile-first)
   - Add meaningful icons (emoji or lucide-react)

4. **Visual mockup**
   - Show the component rendered in context
   - Demonstrate with real-world data
   - Highlight responsive behavior

5. **Iterate based on feedback**
   - Adjust spacing, colors, or layout as needed
   - Refine design based on user input
   - Ensure consistency with existing patterns

## Example: Dashboard Page

The dashboard demonstrates the skill in action:
- **4 summary cards** showing total spent, expense count, daily average, largest expense
- **Donut chart** breaking down spending by category with legend
- **Recent transactions list** with icons, names, dates, and amounts
- **Responsive grid** that adapts from 2-column to 1-column on mobile
- **Clean CSS** using variables for colors, spacing, typography
- **Fintech aesthetics** with soft shadows, rounded corners, proper hierarchy

All of this follows the design system: 8px grid, semantic colors, subtle shadows, and meaningful spacing.