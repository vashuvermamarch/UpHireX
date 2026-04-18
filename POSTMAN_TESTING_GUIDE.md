# 🧪 Uphirex API — Complete Postman Testing Guide

**Base URL:** `http://localhost:8000/api/v1/`

> ⚠️ **IMPORTANT:** Follow the steps **IN EXACT ORDER**. Each step depends on data from previous steps. Skipping steps will cause errors.

---

## 🏁 Pre-Requisites

### 1. Start the Django Server
```bash
cd d:\uphirex
python manage.py runserver
```

### 2. Postman Setup
- Create a new **Collection** called `Uphirex API`
- Create these **Collection Variables** (you'll fill them as you go):

| Variable | Description |
|---|---|
| `base_url` | `http://localhost:8000/api/v1` |
| `access_token` | JWT access token (from login) |
| `refresh_token` | JWT refresh token (from login) |
| `user_id` | Your user's UUID (from login) |
| `user2_id` | Second user's UUID |
| `access_token_2` | Second user's access token |
| `access_token_admin` | Admin user's access token |
| `admin_user_id` | Admin user's UUID |
| `org_id` | Organization UUID |
| `profile_id` | Profile UUID |
| `skill_id` | Skill UUID |
| `skill_id_2` | Second Skill UUID |
| `job_id` | Job UUID |
| `application_id` | Application UUID |
| `connection_id` | Connection UUID |
| `chat_room_id` | Chat room UUID |
| `message_id` | Message UUID |
| `notification_id` | Notification UUID |

---

## 📋 Testing Flow Overview

```
Step 1:  Health Check
Step 2:  Signup User 1 (job_seeker)
Step 3:  Verify Signup (OTP)
Step 4:  Login User 1
Step 5:  Get Current User (/auth/me/)
Step 6:  Signup + Verify + Login User 2
Step 7:  Create Admin via Django Shell
Step 8:  Login as Admin
Step 9:  Profile APIs
Step 10: Skills (Admin creates)
Step 11: User Skills
Step 12: Organizations
Step 13: Jobs
Step 14: Job Skills
Step 15: Saved Jobs
Step 16: Applications
Step 17: Application Reviews
Step 18: Connections
Step 19: Chat
Step 20: Notifications
Step 21: File Uploads
Step 22: Courses
Step 23: User Management
Step 24: Logout
```

---

## PHASE 1: Authentication (Steps 1–8)

---

### ✅ Step 1 — Health Check (API Root)

| Field | Value |
|---|---|
| **Method** | `GET` |
| **URL** | `http://localhost:8000/` |
| **Auth** | None |

**Expected Response** (200 OK):
```json
{
  "success": true,
  "message": "Welcome to Uphirex API v1",
  "endpoints": ["/api/v1/auth/signup/", "..."]
}
```

> 💡 If this fails, your server isn't running. Run `python manage.py runserver`.

---

### ✅ Step 2 — Signup (User 1 — Job Seeker)

| Field | Value |
|---|---|
| **Method** | `POST` |
| **URL** | `{{base_url}}/auth/signup/` |
| **Auth** | None |
| **Body Type** | raw → JSON |

**Request Body:**
```json
{
  "username": "testseeker",
  "email": "testseeker@example.com",
  "password": "Test@12345",
  "displayName": "Test Seeker",
  "role": "job_seeker"
}
```

**Expected Response** (200 OK):
```json
{
  "success": true,
  "message": "OTP sent successfully.",
  "data": {
    "email": "testseeker@example.com",
    "otp": "123456"
  }
}
```

> 🔑 **SAVE the `otp` value** from the response! You need it for the next step.  
> In dev mode, the OTP is returned directly in the response (not sent via email).

---

### ✅ Step 3 — Verify Signup (OTP)

| Field | Value |
|---|---|
| **Method** | `POST` |
| **URL** | `{{base_url}}/auth/verify_signup/` |
| **Auth** | None |
| **Body Type** | raw → JSON |

**Request Body:**
```json
{
  "email": "testseeker@example.com",
  "otp": "PASTE_OTP_FROM_STEP_2"
}
```

**Expected Response** (201 Created):
```json
{
  "success": true,
  "message": "Signup verified.",
  "data": {
    "user": {
      "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
      "username": "testseeker",
      "email": "testseeker@example.com",
      "role": "job_seeker"
    },
    "signup_token": "..."
  }
}
```

> ⚠️ The OTP expires in **5 minutes** (300 seconds). If you get "Invalid or expired OTP", go back to Step 2 and signup again to get a fresh OTP.

---

### ✅ Step 4 — Login (User 1)

| Field | Value |
|---|---|
| **Method** | `POST` |
| **URL** | `{{base_url}}/auth/login/` |
| **Auth** | None |
| **Body Type** | raw → JSON |

**Request Body:**
```json
{
  "email": "testseeker@example.com",
  "password": "Test@12345"
}
```

**Expected Response** (200 OK):
```json
{
  "success": true,
  "message": "Login successful.",
  "data": {
    "user": {
      "id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
    },
    "refresh": "eyJ...",
    "access": "eyJ..."
  }
}
```

> 🔑 **SAVE THESE VALUES** as Postman variables:
> - `access_token` ← `data.access`
> - `refresh_token` ← `data.refresh`
> - `user_id` ← `data.user.id`
>
> **Pro Tip**: Add this to the request's **Tests** tab to auto-save:
> ```javascript
> if (pm.response.code === 200) {
>     var json = pm.response.json();
>     pm.collectionVariables.set("access_token", json.data.access);
>     pm.collectionVariables.set("refresh_token", json.data.refresh);
>     pm.collectionVariables.set("user_id", json.data.user.id);
> }
> ```

---

### ✅ Step 5 — Get Current User (`/auth/me/`)

| Field | Value |
|---|---|
| **Method** | `GET` |
| **URL** | `{{base_url}}/auth/me/` |
| **Auth Tab** | Type: **Bearer Token** → Token: `{{access_token}}` |

**Expected Response** (200 OK):
```json
{
  "success": true,
  "message": "Authenticated user.",
  "data": {
    "id": "...",
    "username": "testseeker",
    "role": "job_seeker"
  }
}
```

> ⚠️ If you get **401 Unauthorized**, your access token is expired or incorrect. Go back to Step 4 and login again.

---

### ✅ Step 6 — Create User 2 (Repeat Steps 2–4 for Second User)

You need a second user for testing connections, chat, etc.

**6a. Signup User 2:**
```json
{
  "username": "testseeker2",
  "email": "testseeker2@example.com",
  "password": "Test@12345",
  "displayName": "Test Seeker Two",
  "role": "job_seeker"
}
```

**6b. Verify User 2** — use the OTP from 6a response.

**6c. Login User 2** and save:
- `access_token_2` ← `data.access`
- `user2_id` ← `data.user.id`

---

### ✅ Step 7 — Create an Admin User (via Django Shell)

> ⚠️ **Admin and HR accounts cannot be created purely through the API.** You need to use the Django shell.

Open a **new terminal** and run:
```bash
cd d:\uphirex
python manage.py shell
```

Then execute:
```python
from authapp.models import User
admin = User.objects.create_superuser(
    username='adminuser',
    email='admin@example.com',
    password='Admin@12345',
    displayName='Admin User',
    role='admin'
)
admin.email_verified = True
admin.save()
print(f"Admin created: {admin.id}")
exit()
```

---

### ✅ Step 8 — Login as Admin

| Field | Value |
|---|---|
| **Method** | `POST` |
| **URL** | `{{base_url}}/auth/login/` |
| **Body Type** | raw → JSON |

```json
{
  "email": "admin@example.com",
  "password": "Admin@12345"
}
```

🔑 **Save** `access_token_admin` and `admin_user_id` from the response.

> 💡 Keep all 3 tokens saved — you'll switch between them:
> - `access_token` → Job Seeker 1
> - `access_token_2` → Job Seeker 2
> - `access_token_admin` → Admin

---

## PHASE 2: Profiles & Skills (Steps 9–11)

> From here on, use **Bearer Token** auth header for every request:  
> `Authorization: Bearer {{access_token}}` (switch token based on which user you're testing as)

---

### ✅ Step 9 — Profile APIs

**9a. Get My Profile** (auto-creates if doesn't exist)

| Field | Value |
|---|---|
| **Method** | `GET` |
| **URL** | `{{base_url}}/profiles/me/` |
| **Auth** | Bearer `{{access_token}}` |

🔑 **Save** `profile_id` ← `data.user` (this is the user UUID, which is the profile PK)

**9b. Update My Profile**

| Field | Value |
|---|---|
| **Method** | `PATCH` |
| **URL** | `{{base_url}}/profiles/{{profile_id}}/` |
| **Auth** | Bearer `{{access_token}}` |

```json
{
  "headline": "Full Stack Developer",
  "summary": "3+ years of experience in Django and React",
  "location": "Mumbai, India",
  "current_company": "TechCorp",
  "total_experience": 3,
  "availability_status": "active"
}
```

**9c. List All Profiles**

| Field | Value |
|---|---|
| **Method** | `GET` |
| **URL** | `{{base_url}}/profiles/` |
| **Auth** | Bearer `{{access_token}}` |

**9d. View Another User's Profile** (triggers profile view tracking)

| Field | Value |
|---|---|
| **Method** | `GET` |
| **URL** | `{{base_url}}/profiles/{{user2_id}}/` |
| **Auth** | Bearer `{{access_token}}` |

> 📝 User 2 must have a profile first. Login as User 2 and hit `GET /profiles/me/` to auto-create it.

**9e. Get Profile Views** (who viewed my profile)

| Field | Value |
|---|---|
| **Method** | `GET` |
| **URL** | `{{base_url}}/profiles/{{user2_id}}/views/` |
| **Auth** | Bearer `{{access_token_2}}` ← must be the profile owner |

---

### ✅ Step 10 — Skills (Admin Only for Create)

**10a. Create a Skill** (use Admin token)

| Field | Value |
|---|---|
| **Method** | `POST` |
| **URL** | `{{base_url}}/skills/` |
| **Auth** | Bearer `{{access_token_admin}}` |

```json
{
  "name": "Python",
  "category": "Programming Language"
}
```

🔑 **Save** `skill_id` ← `data.id`

**10b. Create another Skill**
```json
{
  "name": "Django",
  "category": "Web Framework"
}
```

🔑 **Save** `skill_id_2` ← `data.id`

**10c. List All Skills** (any authenticated user)

| Field | Value |
|---|---|
| **Method** | `GET` |
| **URL** | `{{base_url}}/skills/` |
| **Auth** | Bearer `{{access_token}}` |

---

### ✅ Step 11 — User Skills

**11a. Add a Skill to My Profile** (as Job Seeker)

| Field | Value |
|---|---|
| **Method** | `POST` |
| **URL** | `{{base_url}}/user-skills/` |
| **Auth** | Bearer `{{access_token}}` |

```json
{
  "skill": "{{skill_id}}",
  "proficiency_level": "intermediate"
}
```

**11b. List My Skills**

| Field | Value |
|---|---|
| **Method** | `GET` |
| **URL** | `{{base_url}}/user-skills/` |
| **Auth** | Bearer `{{access_token}}` |

**11c. Get Skills of a Specific User**

| Field | Value |
|---|---|
| **Method** | `GET` |
| **URL** | `{{base_url}}/user-skills/user/{{user_id}}/` |
| **Auth** | Bearer `{{access_token}}` |

---

## PHASE 3: Organizations (Step 12)

---

### ✅ Step 12 — Organizations (Admin/HR Only for Create)

**12a. Create Organization** (use Admin token)

| Field | Value |
|---|---|
| **Method** | `POST` |
| **URL** | `{{base_url}}/organizations/` |
| **Auth** | Bearer `{{access_token_admin}}` |

```json
{
  "name": "TechCorp Solutions",
  "industry": "Information Technology",
  "location": "Mumbai, India",
  "description": "Leading IT solutions company"
}
```

🔑 **Save** `org_id` ← `data.id`

**12b. List Organizations** (any authenticated user)

| Field | Value |
|---|---|
| **Method** | `GET` |
| **URL** | `{{base_url}}/organizations/` |
| **Auth** | Bearer `{{access_token}}` |

**12c. Get Organization Details**

| Field | Value |
|---|---|
| **Method** | `GET` |
| **URL** | `{{base_url}}/organizations/{{org_id}}/` |
| **Auth** | Bearer `{{access_token}}` |

**12d. Update Organization** (Admin only)

| Field | Value |
|---|---|
| **Method** | `PATCH` |
| **URL** | `{{base_url}}/organizations/{{org_id}}/` |
| **Auth** | Bearer `{{access_token_admin}}` |

```json
{
  "description": "Leading IT solutions company in India"
}
```

---

## PHASE 4: Jobs (Steps 13–15)

---

### ✅ Step 13 — Job Posts (Admin/HR for Create)

**13a. Create a Job** (use Admin token)

| Field | Value |
|---|---|
| **Method** | `POST` |
| **URL** | `{{base_url}}/jobs/` |
| **Auth** | Bearer `{{access_token_admin}}` |

```json
{
  "title": "Senior Python Developer",
  "description": "Looking for experienced Python developers",
  "requirements": "3+ years Python, Django experience",
  "salary_range": "12L - 18L",
  "location": "Mumbai, India",
  "remote": true,
  "status": "open"
}
```

🔑 **Save** `job_id` ← `data.id`

> 📝 The `organization_id` is auto-set from the logged-in user's `organization_id` field. If the admin user isn't linked to an org, it will be `null` — that's OK.

**13b. List All Jobs** (merges internal + Adzuna external)

| Field | Value |
|---|---|
| **Method** | `GET` |
| **URL** | `{{base_url}}/jobs/` |
| **Auth** | Bearer `{{access_token}}` |

> 💡 Add query parameters for search: `{{base_url}}/jobs/?search=python&location=mumbai`

**13c. Get Job Details**

| Field | Value |
|---|---|
| **Method** | `GET` |
| **URL** | `{{base_url}}/jobs/{{job_id}}/` |
| **Auth** | Bearer `{{access_token}}` |

**13d. Update Job** (owner or admin)

| Field | Value |
|---|---|
| **Method** | `PATCH` |
| **URL** | `{{base_url}}/jobs/{{job_id}}/` |
| **Auth** | Bearer `{{access_token_admin}}` |

```json
{
  "salary_range": "15L - 22L"
}
```

---

### ✅ Step 14 — Job Skills (Link Skills to Jobs)

**14a. Add Required Skill to a Job** (Admin/HR)

| Field | Value |
|---|---|
| **Method** | `POST` |
| **URL** | `{{base_url}}/job-skills/` |
| **Auth** | Bearer `{{access_token_admin}}` |

```json
{
  "job": "{{job_id}}",
  "skill": "{{skill_id}}",
  "is_required": true
}
```

**14b. List Job Skills**

| Field | Value |
|---|---|
| **Method** | `GET` |
| **URL** | `{{base_url}}/job-skills/` |
| **Auth** | Bearer `{{access_token_admin}}` |

---

### ✅ Step 15 — Saved Jobs

**15a. Save/Bookmark a Job** (as Job Seeker)

| Field | Value |
|---|---|
| **Method** | `POST` |
| **URL** | `{{base_url}}/jobs/{{job_id}}/save_job/` |
| **Auth** | Bearer `{{access_token}}` |

*(No body needed)*

**15b. List My Saved Jobs**

| Field | Value |
|---|---|
| **Method** | `GET` |
| **URL** | `{{base_url}}/jobs/saved/` |
| **Auth** | Bearer `{{access_token}}` |

**15c. Unsave a Job**

| Field | Value |
|---|---|
| **Method** | `DELETE` |
| **URL** | `{{base_url}}/jobs/{{job_id}}/unsave_job/` |
| **Auth** | Bearer `{{access_token}}` |

---

## PHASE 5: Applications (Steps 16–17)

---

### ✅ Step 16 — Job Applications (Job Seeker Only for Create)

**16a. Apply to a Job** (as Job Seeker — User 1)

| Field | Value |
|---|---|
| **Method** | `POST` |
| **URL** | `{{base_url}}/applications/` |
| **Auth** | Bearer `{{access_token}}` |

```json
{
  "job": "{{job_id}}",
  "cover_letter": "I am very interested in this position...",
  "resume_url": "https://example.com/resume.pdf"
}
```

🔑 **Save** `application_id` ← `data.id`

> ⚠️ Only `job_seeker` role can apply. If you use the admin token, you'll get a **403 Forbidden**.

**16b. List My Applications** (as Job Seeker)

| Field | Value |
|---|---|
| **Method** | `GET` |
| **URL** | `{{base_url}}/applications/` |
| **Auth** | Bearer `{{access_token}}` |

**16c. List All Applications** (as Admin — sees all)

| Field | Value |
|---|---|
| **Method** | `GET` |
| **URL** | `{{base_url}}/applications/` |
| **Auth** | Bearer `{{access_token_admin}}` |

**16d. Update Application Status** (Admin/HR only)

| Field | Value |
|---|---|
| **Method** | `PATCH` |
| **URL** | `{{base_url}}/applications/{{application_id}}/update_status/` |
| **Auth** | Bearer `{{access_token_admin}}` |

```json
{
  "status": "reviewed"
}
```

> Valid statuses: `pending`, `reviewed`, `accepted`, `rejected`

---

### ✅ Step 17 — Application Reviews (Admin/HR Only)

**17a. Leave a Review on an Application**

| Field | Value |
|---|---|
| **Method** | `POST` |
| **URL** | `{{base_url}}/application-reviews/` |
| **Auth** | Bearer `{{access_token_admin}}` |

```json
{
  "application": "{{application_id}}",
  "note": "Strong candidate. Good Python skills. Schedule for interview."
}
```

**17b. List All Reviews**

| Field | Value |
|---|---|
| **Method** | `GET` |
| **URL** | `{{base_url}}/application-reviews/` |
| **Auth** | Bearer `{{access_token_admin}}` |

---

## PHASE 6: Connections (Step 18)

---

### ✅ Step 18 — Connections (Networking)

**18a. Send Connection Request** (User 1 → User 2)

| Field | Value |
|---|---|
| **Method** | `POST` |
| **URL** | `{{base_url}}/connections/` |
| **Auth** | Bearer `{{access_token}}` |

```json
{
  "receiver": "{{user2_id}}"
}
```

🔑 **Save** `connection_id` ← `data.id`

**18b. List My Connections**

| Field | Value |
|---|---|
| **Method** | `GET` |
| **URL** | `{{base_url}}/connections/` |
| **Auth** | Bearer `{{access_token}}` |

**18c. View Pending Connections** (as User 2 — the receiver)

| Field | Value |
|---|---|
| **Method** | `GET` |
| **URL** | `{{base_url}}/connections/pending/` |
| **Auth** | Bearer `{{access_token_2}}` |

**18d. Accept Connection** (as User 2 — receiver only)

| Field | Value |
|---|---|
| **Method** | `POST` |
| **URL** | `{{base_url}}/connections/{{connection_id}}/accept/` |
| **Auth** | Bearer `{{access_token_2}}` |

*(No body needed)*

> ⚠️ Only the **receiver** can accept/reject. Using the sender's token will return **403 Forbidden**.

**18e. Reject Connection** (alternative to accept)
```
POST {{base_url}}/connections/{{connection_id}}/reject/
Auth: Bearer {{access_token_2}}
```

**18f. Block Connection** (either participant)
```
POST {{base_url}}/connections/{{connection_id}}/block/
Auth: Bearer {{access_token}} OR {{access_token_2}}
```

---

## PHASE 7: Chat (Step 19)

---

### ✅ Step 19 — Chat System

**19a. Create a Direct Message Chat** (User 1 with User 2)

| Field | Value |
|---|---|
| **Method** | `POST` |
| **URL** | `{{base_url}}/chat/direct/` |
| **Auth** | Bearer `{{access_token}}` |

```json
{
  "user_id": "{{user2_id}}"
}
```

🔑 **Save** `chat_room_id` ← `data.id`

**19b. Create a Group Chat**

| Field | Value |
|---|---|
| **Method** | `POST` |
| **URL** | `{{base_url}}/chat/` |
| **Auth** | Bearer `{{access_token}}` |

```json
{
  "type": "group",
  "name": "Project Team Chat",
  "participant_ids": ["{{user2_id}}"]
}
```

**19c. List My Chat Rooms**

| Field | Value |
|---|---|
| **Method** | `GET` |
| **URL** | `{{base_url}}/chat/` |
| **Auth** | Bearer `{{access_token}}` |

**19d. Send a Message**

| Field | Value |
|---|---|
| **Method** | `POST` |
| **URL** | `{{base_url}}/chat/{{chat_room_id}}/send_message/` |
| **Auth** | Bearer `{{access_token}}` |

```json
{
  "content": "Hello! How are you?",
  "message_type": "text"
}
```

🔑 **Save** `message_id` ← `data.id`

**19e. Get Messages in a Room**

| Field | Value |
|---|---|
| **Method** | `GET` |
| **URL** | `{{base_url}}/chat/{{chat_room_id}}/messages/` |
| **Auth** | Bearer `{{access_token}}` |

**19f. Get Chat Participants**

| Field | Value |
|---|---|
| **Method** | `GET` |
| **URL** | `{{base_url}}/chat/{{chat_room_id}}/participants/` |
| **Auth** | Bearer `{{access_token}}` |

**19g. Mark Messages as Read** (as User 2)

| Field | Value |
|---|---|
| **Method** | `POST` |
| **URL** | `{{base_url}}/chat/{{chat_room_id}}/mark_read/` |
| **Auth** | Bearer `{{access_token_2}}` |

```json
{
  "message_ids": ["{{message_id}}"]
}
```

---

## PHASE 8: Notifications (Step 20)

---

### ✅ Step 20 — Notifications

> 📝 Notifications are typically generated by other actions (profile views, applications, etc.). You can create test notifications via the Django admin panel at `http://localhost:8000/admin/`.

**20a. List My Notifications**

| Field | Value |
|---|---|
| **Method** | `GET` |
| **URL** | `{{base_url}}/notifications/` |
| **Auth** | Bearer `{{access_token}}` |

**20b. Get Unread Count**

| Field | Value |
|---|---|
| **Method** | `GET` |
| **URL** | `{{base_url}}/notifications/unread_count/` |
| **Auth** | Bearer `{{access_token}}` |

**20c. Mark a Notification as Read** (if you have a notification_id)

| Field | Value |
|---|---|
| **Method** | `POST` |
| **URL** | `{{base_url}}/notifications/{{notification_id}}/mark_read/` |
| **Auth** | Bearer `{{access_token}}` |

**20d. Mark All Notifications as Read**

| Field | Value |
|---|---|
| **Method** | `POST` |
| **URL** | `{{base_url}}/notifications/mark_all_read/` |
| **Auth** | Bearer `{{access_token}}` |

---

## PHASE 9: File Uploads (Step 21)

---

### ✅ Step 21 — File Upload

> ⚠️ **This endpoint requires `multipart/form-data`, NOT JSON.** Change the body type in Postman!

**21a. Upload a File**

| Field | Value |
|---|---|
| **Method** | `POST` |
| **URL** | `{{base_url}}/files/` |
| **Auth** | Bearer `{{access_token}}` |
| **Body Type** | **form-data** (NOT raw JSON!) |

| Key | Type | Value |
|---|---|---|
| `file` | **File** | Select a file from your computer |
| `entity_type` | Text | `resume` |
| `entity_id` | Text | `{{user_id}}` |

> 🚨 Make sure the Body type dropdown says **form-data**. If you send this as JSON, you'll get "No file provided."

**21b. List My Uploaded Files**

| Field | Value |
|---|---|
| **Method** | `GET` |
| **URL** | `{{base_url}}/files/` |
| **Auth** | Bearer `{{access_token}}` |

---

## PHASE 10: Courses (Step 22)

---

### ✅ Step 22 — Course Search (YouTube API)

| Field | Value |
|---|---|
| **Method** | `GET` |
| **URL** | `{{base_url}}/courses/?query=python&max_results=5` |
| **Auth** | Bearer `{{access_token}}` |

> ⚠️ This requires a valid **YouTube Data API key** configured in your `.env` file. If not configured, you'll get an empty result or an error.

---

## PHASE 11: User Management & Cleanup (Steps 23–24)

---

### ✅ Step 23 — User Management (Admin Only)

**23a. List All Users** (Admin/HR only)

| Field | Value |
|---|---|
| **Method** | `GET` |
| **URL** | `{{base_url}}/users/` |
| **Auth** | Bearer `{{access_token_admin}}` |

**23b. User Lookup by ID**

| Field | Value |
|---|---|
| **Method** | `GET` |
| **URL** | `{{base_url}}/auth/user/{{user2_id}}/` |
| **Auth** | Bearer `{{access_token}}` |

**23c. Update a User** (Admin)

| Field | Value |
|---|---|
| **Method** | `PATCH` |
| **URL** | `{{base_url}}/users/{{user2_id}}/` |
| **Auth** | Bearer `{{access_token_admin}}` |

```json
{
  "displayName": "Updated Name"
}
```

**23d. Deactivate a User** (Admin only — soft delete)

| Field | Value |
|---|---|
| **Method** | `DELETE` |
| **URL** | `{{base_url}}/users/{{user2_id}}/` |
| **Auth** | Bearer `{{access_token_admin}}` |

---

### ✅ Step 24 — Logout

| Field | Value |
|---|---|
| **Method** | `POST` |
| **URL** | `{{base_url}}/auth/logout/` |
| **Auth** | Bearer `{{access_token}}` |

```json
{
  "refresh": "{{refresh_token}}"
}
```

---

## 🚨 Common Errors & Fixes

| Error | Cause | Fix |
|---|---|---|
| `401 Unauthorized` | Missing or expired access token | Login again to get a fresh token |
| `403 Forbidden` | Wrong role (e.g., job_seeker trying to create a job) | Switch to Admin/HR token |
| `403 "Account not active"` | HR user needs admin activation | Use Django admin to set `is_active=True` |
| `400 "Invalid or expired OTP"` | OTP expired (5 min limit) | Re-do signup to get a new OTP |
| `400 "Email already exists"` | Duplicate signup | Use a different email or login instead |
| `400 "Already applied to this job"` | Duplicate application | Each user can only apply once per job |
| `400 "Connection already exists"` | Duplicate connection request | Check existing connections first |
| `400 "No file provided"` | File upload sent as JSON | Change body type to **form-data** |
| `404 Not Found` | Wrong UUID in URL | Double-check the ID you saved |
| `405 Method Not Allowed` | Wrong HTTP method | Check the method (GET/POST/PATCH/DELETE) |

---

## 🎯 Quick Reference: Which Token to Use

| Action | Token |
|---|---|
| Signup, Verify, Login | ❌ No token needed |
| Browse jobs, profiles, skills | `access_token` (any user) |
| Create jobs, organizations, skills | `access_token_admin` |
| Apply to jobs | `access_token` (job_seeker only) |
| Review applications, update status | `access_token_admin` |
| Accept/reject connections | Token of the **receiver** |
| Send chat messages | Token of any **participant** |
| Upload files | Any authenticated user |
| Manage users (list/update/delete) | `access_token_admin` |
