# Uphirex – Postman Testing Guide

A step-by-step guide to test every API endpoint in Postman.

**Base URL:** `http://127.0.0.1:8000/api/v1`

---

## 🔧 Postman Setup

### 1. Create an Environment

Go to **Environments → New** and create `Uphirex Local` with these variables:

| Variable | Initial Value |
|---|---|
| `base_url` | `http://127.0.0.1:8000/api/v1` |
| `access_token` | *(leave blank – auto-filled on login)* |
| `refresh_token` | *(leave blank – auto-filled on login)* |
| `user_id` | *(leave blank – auto-filled on login)* |

### 2. Set Authorization (Global)

For every request **except** signup/verify/login, go to the **Authorization** tab and set:

*   **Type:** Bearer Token
*   **Token:** `{{access_token}}`

Or set this once at the **Collection level** so all requests inherit it.

---

## 📋 Test Flow (Recommended Order)

Follow this exact order to test the full platform end-to-end:

---

## 1. Authentication

### 1.1 Signup

```
POST {{base_url}}/auth/signup/
```

**Body (JSON):**
```json
{
  "username": "testuser",
  "email": "testuser@example.com",
  "password": "Test@1234",
  "displayName": "Test User",
  "role": "job_seeker",
  "phone": "9876543210"
}
```

**Expected:** `200 OK` – Returns success message. Check your **email** (or terminal if in development) to retrieve the OTP.

---

### 1.2 Verify Signup

```
POST {{base_url}}/auth/verify_signup/
```

**Body (JSON):**
```json
{
  "email": "testuser@example.com",
  "otp": "PASTE_OTP_HERE"
}
```

**Expected:** `201 Created` – User created, returns `signup_token`.

---

### 1.3 Login

```
POST {{base_url}}/auth/login/
```

**Body (JSON):**
```json
{
  "email": "testuser@example.com",
  "password": "Test@1234"
}
```

**Expected:** `200 OK` – Returns `access` and `refresh` tokens.

**⚡ Auto-save tokens (Tests tab script):**
```javascript
var data = pm.response.json();
if (data.success) {
    pm.environment.set("access_token", data.data.access);
    pm.environment.set("refresh_token", data.data.refresh);
    pm.environment.set("user_id", data.data.user.id);
}
```

---

### 1.4 Get Current User

```
GET {{base_url}}/auth/me/
```

**Auth:** Bearer `{{access_token}}`

**Expected:** `200 OK` – Your user profile.

---

### 1.5 User Lookup

```
GET {{base_url}}/auth/user/{{user_id}}/
```

**Expected:** `200 OK` – User data for that ID.

---

### 1.6 Logout

```
POST {{base_url}}/auth/logout/
```

**Body (JSON):**
```json
{
  "refresh": "{{refresh_token}}"
}
```

**Expected:** `200 OK` – Token revoked.

> ⚠️ **Don't test this yet** — you need the token for the remaining tests. Test logout last.

---

## 2. Organizations

### 2.1 Create Organization (HR/Admin only)

First, login as admin (`admin@example.com`) or create an HR user.

```
POST {{base_url}}/organizations/
```

**Body (JSON):**
```json
{
  "name": "Uphirex Technologies",
  "description": "AI-powered hiring platform",
  "website": "https://uphirex.com",
  "industry": "Technology",
  "location": "Bangalore, India",
  "size": "50-200",
  "is_verified": true
}
```

**Expected:** `201 Created`

---

### 2.2 List Organizations

```
GET {{base_url}}/organizations/
```

**Expected:** `200 OK` – List of all orgs.

---

### 2.3 Get Single Organization

```
GET {{base_url}}/organizations/{org_id}/
```

---

## 3. Profiles & Skills

### 3.1 Get My Profile

```
GET {{base_url}}/profiles/me/
```

**Expected:** `200 OK` – Auto-creates profile if one doesn't exist.

---

### 3.2 Update Profile

```
PATCH {{base_url}}/profiles/me/
```

**Body (JSON):**
```json
{
  "headline": "Full Stack Developer | Django | React",
  "location": "Mumbai, India",
  "current_company": "Uphirex Technologies",
  "experience_years": 3,
  "availability_status": "open_to_work",
  "linkedin_url": "https://linkedin.com/in/testuser",
  "github_url": "https://github.com/testuser",
  "portfolio_url": "https://testuser.dev"
}
```

---

### 3.3 Create a Skill (Admin only)

```
POST {{base_url}}/skills/
```

**Body (JSON):**
```json
{
  "name": "Python",
  "category": "Programming Language"
}
```

---

### 3.4 Add Skill to My Profile

```
POST {{base_url}}/user-skills/
```

**Body (JSON):**
```json
{
  "skill": "SKILL_UUID_HERE",
  "proficiency_level": "advanced"
}
```

---

### 3.5 View Profile (triggers view tracking)

```
GET {{base_url}}/profiles/{other_user_profile_id}/
```

---

### 3.6 See Who Viewed My Profile

```
GET {{base_url}}/profiles/{my_profile_id}/views/
```

---

## 4. Connections

### 4.1 Send Connection Request

```
POST {{base_url}}/connections/
```

**Body (JSON):**
```json
{
  "receiver": "OTHER_USER_UUID"
}
```

---

### 4.2 View Pending Requests

```
GET {{base_url}}/connections/pending/
```

---

### 4.3 Accept Connection (login as receiver)

```
POST {{base_url}}/connections/{connection_id}/accept/
```

---

### 4.4 Reject Connection

```
POST {{base_url}}/connections/{connection_id}/reject/
```

---

### 4.5 Block Connection

```
POST {{base_url}}/connections/{connection_id}/block/
```

---

### 4.6 List All Connections

```
GET {{base_url}}/connections/
```

---

## 5. Jobs

### 5.1 Create Job Post (HR/Admin only)

Login as admin or HR user first.

```
POST {{base_url}}/jobs/
```

**Body (JSON):**
```json
{
  "title": "Senior Backend Developer",
  "description": "We are looking for a Senior Backend Developer with 3+ years Django experience.",
  "requirements": "Python, Django, PostgreSQL, REST APIs, Docker",
  "location": "Bangalore, India",
  "salary_range": "15-25 LPA",
  "employment_type": "full_time",
  "remote": true,
  "status": "active"
}
```

---

### 5.2 List All Jobs (internal + Adzuna merged)

```
GET {{base_url}}/jobs/
```

**With filters:**
```
GET {{base_url}}/jobs/?search=python&location=bangalore
```

---

### 5.3 Save a Job

```
POST {{base_url}}/jobs/{job_id}/save_job/
```

---

### 5.4 View Saved Jobs

```
GET {{base_url}}/jobs/saved/
```

---

### 5.5 Unsave a Job

```
DELETE {{base_url}}/jobs/{job_id}/unsave_job/
```

---

## 6. Applications

### 6.1 Apply for a Job (Job Seeker only)

```
POST {{base_url}}/applications/
```

**Body (JSON):**
```json
{
  "job": "JOB_UUID_HERE",
  "cover_letter": "I am excited to apply for this position...",
  "resume_url": "/media/resumes/resume_xxx.pdf"
}
```

---

### 6.2 View My Applications

```
GET {{base_url}}/applications/
```

---

### 6.3 Update Application Status (HR/Admin)

```
PATCH {{base_url}}/applications/{app_id}/update_status/
```

**Body (JSON):**
```json
{
  "status": "shortlisted"
}
```

Valid statuses: `pending`, `reviewed`, `shortlisted`, `rejected`, `accepted`

---

### 6.4 Add Application Review (HR/Admin)

```
POST {{base_url}}/application-reviews/
```

**Body (JSON):**
```json
{
  "application": "APPLICATION_UUID",
  "rating": 4,
  "notes": "Strong technical skills. Schedule interview."
}
```

---

## 7. Chat

### 7.1 Create Direct Chat

```
POST {{base_url}}/chat/direct/
```

**Body (JSON):**
```json
{
  "user_id": "OTHER_USER_UUID"
}
```

---

### 7.2 Create Group Chat

```
POST {{base_url}}/chat/
```

**Body (JSON):**
```json
{
  "type": "group",
  "name": "Project Discussion",
  "participant_ids": ["UUID_1", "UUID_2"]
}
```

---

### 7.3 Send a Message

```
POST {{base_url}}/chat/{room_id}/send_message/
```

**Body (JSON):**
```json
{
  "content": "Hey, are you available for a quick call?",
  "message_type": "text"
}
```

---

### 7.4 Get Messages

```
GET {{base_url}}/chat/{room_id}/messages/
```

---

### 7.5 Mark Messages as Read

```
POST {{base_url}}/chat/{room_id}/mark_read/
```

**Body (JSON):**
```json
{
  "message_ids": ["MSG_UUID_1", "MSG_UUID_2"]
}
```

---

### 7.6 List Participants

```
GET {{base_url}}/chat/{room_id}/participants/
```

---

### 7.7 List My Chat Rooms

```
GET {{base_url}}/chat/
```

---

### 7.8 WebSocket Test (use Postman WebSocket tab)

```
ws://127.0.0.1:8000/ws/chat/{room_id}/
```

**Send message payload:**
```json
{
  "type": "chat_message",
  "content": "Hello from WebSocket!",
  "message_type": "text",
  "file_url": ""
}
```

**Send read receipt:**
```json
{
  "type": "read_receipt",
  "message_id": "MESSAGE_UUID"
}
```

---

## 8. Notifications

### 8.1 List My Notifications

```
GET {{base_url}}/notifications/
```

**With filters:**
```
GET {{base_url}}/notifications/?is_read=false
GET {{base_url}}/notifications/?type=connection_request
```

---

### 8.2 Mark One as Read

```
POST {{base_url}}/notifications/{notif_id}/mark_read/
```

---

### 8.3 Mark All as Read

```
POST {{base_url}}/notifications/mark_all_read/
```

---

### 8.4 Get Unread Count

```
GET {{base_url}}/notifications/unread_count/
```

**Expected:**
```json
{ "success": true, "message": "Unread count.", "data": { "count": 5 } }
```

---

## 9. File Uploads

### 9.1 Upload a File

```
POST {{base_url}}/files/
```

**Body Type:** `form-data`

| Key | Type | Value |
|---|---|---|
| `file` | File | Select a file from your machine |
| `entity_type` | Text | `resume` |
| `entity_id` | Text | *(optional UUID)* |

---

### 9.2 List My Uploads

```
GET {{base_url}}/files/
```

---

## 10. Courses (YouTube)

### 10.1 Search Courses

```
GET {{base_url}}/courses/?query=python django tutorial
```

**With max results:**
```
GET {{base_url}}/courses/?query=machine+learning&max_results=10
```

> ⚠️ Requires `YOUTUBE_API_KEY` in `.env`

---

## 11. 🤖 AI Assistant

The unified AI endpoint. ONE endpoint, THREE capabilities.

### 11.1 Generate a Resume

```
POST {{base_url}}/ai/assistant/
```

**Body (JSON):**
```json
{
  "message": "Create a resume for a backend developer",
  "job_title": "Senior Backend Developer"
}
```

**Expected Response:**
```json
{
  "success": true,
  "message": "AI response ready.",
  "data": {
    "intent": "resume_generate",
    "message": "Resume generated successfully.",
    "corrections": [],
    "resume_text": "# John Doe\n## Senior Backend Developer\n...",
    "pdf_url": "/media/resumes/resume_abc123_20260422_xyz.pdf",
    "pdf_required": true
  }
}
```

📥 **Download the PDF:** Open `http://127.0.0.1:8000{pdf_url}` in your browser.

---

### 11.2 Improve / Review a Resume

```
POST {{base_url}}/ai/assistant/
```

**Body (JSON):**
```json
{
  "message": "Review my resume and suggest improvements",
  "resume": "John Doe\nBackend Developer\n3 years experience in Python and Django.\nWorked at XYZ company.\nSkills: Python, Django, SQL",
  "job_title": "Senior Backend Developer"
}
```

**Expected Response:**
```json
{
  "success": true,
  "message": "AI response ready.",
  "data": {
    "intent": "resume_improve",
    "message": "Resume reviewed successfully.",
    "corrections": [
      "Add quantifiable achievements (e.g., 'Reduced API response time by 40%')",
      "Include a professional summary at the top",
      "Expand skills section with specific frameworks and tools",
      "Add education details"
    ],
    "resume_text": "",
    "pdf_url": "",
    "pdf_required": false
  }
}
```

---

### 11.3 Career Chat / Advice

```
POST {{base_url}}/ai/assistant/
```

**Body (JSON):**
```json
{
  "message": "What skills should I learn to become a full stack developer in 2026?"
}
```

**Expected Response:**
```json
{
  "success": true,
  "message": "AI response ready.",
  "data": {
    "intent": "career_chat",
    "message": "To become a full stack developer in 2026, focus on...",
    "corrections": [],
    "resume_text": "",
    "pdf_url": "",
    "pdf_required": false
  }
}
```

---

### 11.4 More AI Test Messages

Try these to see intent detection in action:

| Message | Expected Intent |
|---|---|
| `"Build me a resume"` | `resume_generate` |
| `"Make a resume for data scientist"` | `resume_generate` |
| `"Write my resume"` | `resume_generate` |
| `"Fix my resume"` | `resume_improve` |
| `"Check my resume for errors"` | `resume_improve` |
| `"Optimize my resume for ATS"` | `resume_improve` |
| `"How do I prepare for an interview?"` | `career_chat` |
| `"What salary should I expect as a fresher?"` | `career_chat` |
| `"Tips for switching from QA to development"` | `career_chat` |

---

## 🧪 Quick Smoke Test Checklist

Run through this after a fresh server start:

- [ ] `POST /auth/signup/` → check email for OTP
- [ ] `POST /auth/verify_signup/` → verify OTP
- [ ] `POST /auth/login/` → get tokens
- [ ] `GET /auth/me/` → see user data
- [ ] `GET /profiles/me/` → see profile
- [ ] `POST /jobs/` → create a job (as admin)
- [ ] `GET /jobs/` → list jobs
- [ ] `POST /applications/` → apply to a job
- [ ] `POST /chat/direct/` → create a DM
- [ ] `POST /chat/{id}/send_message/` → send a message
- [ ] `POST /ai/assistant/` → career chat
- [ ] `POST /ai/assistant/` → generate resume (check PDF download)
- [ ] `POST /ai/assistant/` → improve resume (check corrections)
- [ ] `POST /auth/logout/` → revoke token

---

## 🔑 Testing Different Roles

Create users with different roles to test RBAC:

| Role | Signup `role` value | Activation |
|---|---|---|
| Job Seeker | `"job_seeker"` | Active immediately |
| HR | `"hr"` | Requires admin activation via `/admin/` |
| Admin | — | Created via `python manage.py createsuperuser` |

### Role Permissions Summary

| Endpoint | job_seeker | hr | admin |
|---|---|---|---|
| AI Resume features | ✅ | ❌ | ✅ |
| AI Career chat | ✅ | ✅ | ✅ |
| Create job post | ❌ | ✅ | ✅ |
| Apply to job | ✅ | ❌ | ❌ |
| Review applications | ❌ | ✅ | ✅ |
| Create organization | ❌ | ✅ | ✅ |
| Delete anything | ❌ | ❌ | ✅ |
