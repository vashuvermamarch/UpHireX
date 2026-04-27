# Uphirex – Role-Based Testing Guide

This guide focuses on testing the **interaction workflows** between different user roles: **Admin**, **HR Manager**, and **Job Seeker**.

## 🛠️ Postman Setup for Multiple Roles

To test how users interact, you should simulate multiple users logged in at once.

### 1. Recommended Environments
Create three separate Postman Environments:
*   `Uphirex - Admin`
*   `Uphirex - HR Manager`
*   `Uphirex - Job Seeker`

Each environment should contain these variables:
| Variable | Description |
|---|---|
| `base_url` | `http://127.0.0.1:8000/api/v1` |
| `access_token` | The JWT access token (auto-filled) |
| `user_id` | The UUID of the logged-in user (auto-filled) |
| `org_id` | The UUID of the organization (for HR/Admin) |

### 2. Multi-Role Token Script
In the **Tests** tab of your Login request, use this script to automatically update the active environment:
```javascript
var data = pm.response.json();
if (data.success) {
    pm.environment.set("access_token", data.data.access);
    pm.environment.set("user_id", data.data.user.id);
    if (data.data.user.organization_id) {
        pm.environment.set("org_id", data.data.user.organization_id);
    }
}
```

---

## 🔄 End-to-End Workflow Scenario

### Phase 1: Platform Setup (Admin Role)
*Goal: Create the organization and skills needed for the platform.*

1.  **Login as Admin** (`admin@example.com`)
    `POST {{base_url}}/auth/login/`
2.  **Create an Organization**
    `POST {{base_url}}/organizations/`
    *Note: Save the returned `id` as `org_id` in your HR environment.*
3.  **Create Skills**
    `POST {{base_url}}/skills/`
    *Example: Create "Python", "Django", "React".*

### Phase 2: Hiring Setup (HR Manager Role)
*Goal: Post a job as an employer.*

1.  **Login as HR**
    *Ensure the user has `role: "hr"` and is linked to the `org_id`.*
2.  **Create a Job Post**
    `POST {{base_url}}/jobs/`
    ```json
    {
      "title": "Senior Backend Developer",
      "description": "Looking for a Django expert.",
      "organization": "{{org_id}}",
      "requirements": "3+ years Python/Django",
      "location": "Bangalore",
      "salary_range": "20-30 LPA"
    }
    ```
    *Note: Save the returned `id` as `job_id` for testing.*

### Phase 3: Job Application (Job Seeker Role)
*Goal: Create a profile and apply for the job.*

1.  **Login as Job Seeker**
2.  **Add Skills to Profile**
    `POST {{base_url}}/user-skills/`
3.  **Apply for Job**
    `POST {{base_url}}/applications/`
    ```json
    {
      "job": "{{job_id}}",
      "cover_letter": "I have extensive experience with Django REST Framework."
    }
    ```
    *Note: Save the returned `id` as `app_id`.*

### Phase 4: Recruitment & Communication (HR Role)
*Goal: Review the candidate and start a conversation.*

1.  **Review Application**
    `POST {{base_url}}/application-reviews/`
    ```json
    {
      "application": "{{app_id}}",
      "rating": 5,
      "notes": "Candidate matches all requirements."
    }
    ```
2.  **Shortlist Candidate**
    `PATCH {{base_url}}/applications/{{app_id}}/update_status/`
    ```json
    { "status": "shortlisted" }
    ```
3.  **Start a Chat**
    `POST {{base_url}}/chat/direct/`
    ```json
    { "user_id": "{{job_seeker_id}}" }
    ```

---

## 🔐 Authentication & Role Requirements

| Feature | Endpoint | Method | Required Role |
|---|---|---|---|
| **Manage Skills** | `/skills/` | POST/DELETE | `admin` |
| **Manage Orgs** | `/organizations/` | POST/PATCH | `admin` |
| **Post Job** | `/jobs/` | POST | `hr`, `admin` |
| **Apply for Job** | `/applications/` | POST | `job_seeker` |
| **Review App** | `/application-reviews/` | POST | `hr`, `admin` |
| **Update Status** | `/applications/{id}/update_status/` | PATCH | `hr`, `admin` |
| **AI Resume Gen** | `/ai/assistant/` | POST | `job_seeker`, `admin` |

---

## 🛡️ RBAC Security Testing (Fail Cases)

Test these to ensure your API security is working:

1.  **Job Seeker creating a Job:**
    *   `POST /api/v1/jobs/` using a Job Seeker token.
    *   **Expected Result:** `403 Forbidden`.
2.  **HR creating an Admin Skill:**
    *   `POST /api/v1/skills/` using an HR token.
    *   **Expected Result:** `403 Forbidden`.
3.  **Anonymous User viewing applications:**
    *   `GET /api/v1/applications/` without any token.
    *   **Expected Result:** `401 Unauthorized`.
