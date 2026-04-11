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
