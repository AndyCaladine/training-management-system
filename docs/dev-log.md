# 🧠 Dev Log

## 11-04-2026 — Student Profile Enhancements

### 🧩 Context
Extending student profile to support real-world organisational data (department, job title, cohort)

### ✅ What went well
- Successfully added department, job title, cohort fields
- End-to-end flow working (form → backend → DB)
- Cohort auto-generation implemented cleanly

### ⚠️ Challenges
- Data not saving from frontend
- JS not binding values correctly to form submission

### 🔧 How I fixed it
- Added debug logging in Flask
- Verified request.form values
- Fixed missing input name attributes

### 🎯 What I learned
- Always validate full data flow: UI → backend → DB
- Debug logs save time vs guessing
- Frontend issues can silently break backend logic

### 🚀 Impact
Student records now support richer organisational data and align more closely with real-world training systems.

## 11-04-2026 — Employer Registration + System Refactor Prep

### 🧩 Context  
Building out employer-side foundations and preparing the system for a larger structural refactor.

---

### 🚀 What we did
- Built full Employer Contact Registration flow
- Introduced:
  - employer access codes
  - domain-based email validation concept
  - proper employer contact structure (treated as real users, not just a company name)
- Expanded demo dataset:
  - more realistic student journeys
  - varied exam results (fail, booked, passed, full completion)
- Refactored database schema:
  - separated `employers` from `employer_contacts`
  - introduced assignment model (`employer_student_assignments`)
  - added groundwork for GDPR-related fields and locking logic
- Created `demo-access.md` (dev + demo support doc)
- Began restructuring frontend for scalability

---

### 🐛 What broke (because of course it did)
- SQL typo (`eac.id,,`) → classic midnight chaos
- Random word `"understood"` inserted into SQL (??? brain.exe stopped working)
- Flash message typo: `"Em[loyer"` → peak professionalism
- Signature styling disappeared (font mismatch between Mac → Linux)
- Access code validation styling inconsistent (CSS override issue)
- Employer flow only partially wired compared to student flow (expected during refactor)

---

### 🧠 What we learned
- Schema changes ripple HARD through UI and logic
- JavaScript duplication is becoming a real problem
- CSS needs structure before it becomes unmanageable
- System fonts are not reliable → use web fonts
- Splitting “company” vs “contact” was 100% the right decision
- Debugging late at night = 50% real bugs, 50% spelling mistakes

---

### 🔧 Next Steps
- Refactor JavaScript into modular files
- Refactor CSS into base / components / pages
- Complete employer access code + domain validation flow
- Implement employer dashboard properly
- Fix student → employer contact linking in workflows
- Consider turning `demo-access.md` into a live UI page

---

### 💬 Dev Note
“Everything worked perfectly… until I improved it.”

Also: never trust code written after 11:30pm.

---

## 12-04-2026 — Refactor, QA, and System Consistency

### 🧩 Context  
Major refactor of CSS and JavaScript structure followed by a full QA pass of the student dashboard and key workflows.

---

### ✅ What went well
- Successfully refactored CSS into `base`, `components`, and `pages`
- Moved JavaScript into shared utilities and page-specific controllers
- Standardised form, button, and card usage across templates
- Completed full QA pass on student dashboard
- Identified and resolved multiple UI and UX inconsistencies quickly due to improved structure

---

### ⚠️ Challenges
- Refactor initially broke multiple UI elements (navigation, forms, buttons)
- Missing or incorrect classes caused inconsistent styling across pages
- Dashboard default state logic showed all sections instead of summary view
- Form inputs behaved inconsistently due to conflicting CSS rules
- Some issues appeared in multiple places (e.g. add/edit forms)

---

### 🔧 How I fixed it
- Enforced consistent use of shared classes (`learning-form`, `btn-primary`, etc.)
- Removed conflicting CSS rules (e.g. `max-width` on date inputs)
- Fixed navigation visibility by explicitly setting header text colours
- Updated dashboard JS to correctly initialise hidden sections
- Standardised card variants using semantic classes (contact, security, declarations)
- Applied fixes once and reused across similar templates to avoid duplication

---

### 🎯 What I learned
- Most issues after a refactor are **consistency problems, not logic problems**
- A clean structure makes debugging significantly faster
- Missing classes are one of the most common sources of UI bugs
- Fixing patterns (not just individual bugs) prevents repeat issues
- There is a clear difference between “making it work” and “making it consistent”

---

### 🧠 Product Thinking
- Identified several improvements that should not be rushed and instead logged as backlog items:
  - Agreement workflow and status logic refinement
  - Student agreement signing path after admin registration
  - Highlighting changes in the change summary panel
  - Improving learning record validation (planned vs hours)
  - Structuring password fields into a dedicated security section
- Began separating **immediate fixes vs future enhancements**

---

### 🚀 Impact
- Student dashboard now passes QA testing
- UI is significantly more consistent and maintainable
- Forms and components behave predictably across the system
- Codebase is now structured in a way that supports future scaling and feature development

---

### 🔄 Next Steps
- Commit refactor and QA fixes to GitHub
- Raise backlog issues for workflow and UX improvements
- Begin QA testing of employer-side functionality
- Continue refining system workflows rather than just UI

## 18-04-2026 - Change Details – Employer Email Handling Refactor

### Summary
Refactored the employer change details flow to improve usability, align with real-world system behaviour, and remove unnecessary complexity from the user interface.

### What Was Done
- Implemented employer change details functionality
- Introduced initial email domain restriction logic using `employer_allowed_domains`
- Built dynamic email handling (username + domain split)
- Integrated live summary updates for employer fields

### Issue Identified
The email domain dropdown was not behaving as expected in the UI despite:
- Correct database relationships
- Valid domain data being returned
- Template logic appearing correct

Additionally, the approach introduced:
- unnecessary complexity for end users
- increased validation overhead
- potential confusion during demos

### Solution
Refactored the employer email field to be **read-only**:
- Removed editable email username and domain fields from the UI
- Displayed the full email address as a disabled input
- Updated helper text to clarify that email is organisation-managed
- Simplified backend logic by removing email update handling for employer users

### Outcome
- Cleaner and more intuitive user experience
- Reduced validation and edge case complexity
- Behaviour now aligns with real-world systems where employer emails are centrally controlled
- Retained domain restriction logic in the database for future enhancement

### Lessons Learned
- Building the "full solution" first helped validate the data model and relationships
- Not all technically correct solutions are appropriate for the user experience
- Simplicity often leads to better usability, especially for demo and portfolio applications

### Next Steps
- Begin development of Employer Dashboard
- Implement employer → student visibility
- Introduce approval workflows for submissions (timesheets, learning records, reviews)

## 19-04-2026 - Employer Dashboard v1

### Summary
Built the first proper version of the employer dashboard and aligned it with the refactored dashboard design system already used elsewhere in the application.

### What Was Done
- Replaced the employer dashboard placeholder with a real dashboard route and template
- Pulled employer-linked students into the dashboard from the database
- Added grouped summary panels for:
  - Student Overview
  - Outstanding Actions
  - Exam Progress
  - Compliance Attention
- Reused the existing dashboard card layout and table wrapper styles
- Corrected student status display to use `registration_status`
- Updated employer dashboard statuses to use the existing `status-badge` design system

### Issues Identified
- Initial dashboard cards were stacking badly and did not match the rest of the app
- Student statuses were incorrectly showing as inactive
- Early badge markup did not match the project’s existing badge CSS system

### Solution
- Reworked the employer dashboard template to reuse the established dashboard selector card structure
- Fixed the route logic to calculate active students correctly using `registration_status`
- Updated the table status badges to use the existing reusable badge classes:
  - `status-badge approved`
  - `status-badge submitted`
  - `status-badge planned`

### Outcome
- Employer dashboard now feels consistent with the wider application
- Student list is readable and visually aligned with the design system
- Top-level dashboard panels now better reflect employer workflows and future reporting needs

### Lessons Learned
- Reusing the existing design system gives a more polished result than creating one-off layouts
- It is important to match HTML class names to the CSS architecture already in place
- Building grouped dashboard panels creates a better foundation for future filtered workflows than simple standalone stat cards

### Next Steps
- Wire real values into the remaining employer dashboard panels
- Add drill-down / filtered views from dashboard cards
- Build employer-side student detail view

## 23-04-2026 – UI Refactor & Keystone Branding

Today focused on a full UI refactor and introducing consistent branding across the application.

### Keystone Branding

Created a name and identity for the application: **Keystone** with the tagline *“The foundation behind every milestone.”*

Designed a logo and favicon and integrated them into the application:

* Added logo to the main navigation bar
* Added favicon across the site
* Updated layout so the logo, system title, and user controls sit on a single aligned row

### Design System & Colour Refactor

Introduced a centralised design system using CSS variables.

* Created a `variables.css` file to hold:

  * Core brand colours
  * Backgrounds
  * Borders
  * Text colours
  * Shadows
  * Border radius values

* Refactored existing CSS to use variables instead of hardcoded values across:

  * Navigation
  * Cards
  * Buttons
  * Badges
  * Tables
  * Forms
  * Filters

This allows the application to be rebranded in future by updating a single file rather than multiple CSS files.

### Layout Improvements

* Reworked the navbar to:

  * Use a fixed height for consistency
  * Properly align logo, title, and user menu
  * Match the Keystone dark theme (#01081a)

* Moved the system title into the navbar and removed the duplicate header bar

### Component Consistency

Standardised UI components to align with the new design system:

* **Cards**

  * Unified spacing, shadows, and border styling
  * Improved dashboard readability

* **Buttons**

  * Introduced consistent hover, active, and focus states
  * Aligned primary/secondary actions with brand colours

* **Badges**

  * Refactored status indicators to use muted, consistent tones
  * Reduced visual noise and improved hierarchy

* **Tables**

  * Updated headers, hover states, and borders
  * Improved readability and alignment with card styles

* **Forms**

  * Standardised inputs, focus states, and layout
  * Improved accessibility and visual consistency

* **Filters**

  * Simplified filter controls
  * Introduced subtle active states
  * Removed heavy styling to better support data-first views

### Navigation & User Menu Fixes

Resolved multiple issues with the user dropdown menu:

* Fixed dropdown incorrectly affecting navbar height
* Restored proper absolute positioning so the menu floats correctly
* Added a small hover buffer to prevent menu flickering when moving cursor
* Fixed link styling so menu items display correctly as stacked options
* Reintroduced clear hover feedback for menu items

### Outcome

The application now has:

* A consistent visual identity (Keystone)
* A scalable design system
* Cleaner, more professional UI
* Easier maintainability for future changes

This moves the project from a styled prototype towards a production-quality interface.
