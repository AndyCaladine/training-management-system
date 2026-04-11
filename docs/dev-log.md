# 🧠 Dev Log

## 2026-04-11 — Student Profile Enhancements

### ✅ What went well
- Successfully added department, job title, cohort fields
- End-to-end flow working (form → backend → DB)
- Cohort auto-generation implemented cleanly

### ⚠️ Challenges
- Data not saving from frontend
- JS not binding values correctly to form submission

### 🔧 Solution
- Added debug logging in Flask
- Verified request.form values
- Fixed missing input name attributes

### 🎯 What I learned
- Always validate full data flow: UI → backend → DB
- Debug logs save time vs guessing
- Frontend issues can silently break backend logic
