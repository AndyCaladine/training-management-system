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