# Uphirex API Documentation

**Base API URL:** `http://localhost:8000/api/v1/`
**WebSocket URL:** `ws://localhost:8000/ws/chat/<room_id>/`

## Contents
1. [Authentication & Authorization](#1-authentication--authorization)
2. [Organizations](#2-organizations)
3. [Profiles & Skills](#3-profiles--skills)
4. [Connections (Networking)](#4-connections-networking)
5. [Jobs](#5-jobs)
6. [Applications](#6-applications)
7. [Chat (Real-time)](#7-chat-real-time)
8. [Notifications](#8-notifications)
9. [Files (Uploads)](#9-files-uploads)
10. [Courses](#10-courses)

---

## Standardized Response Format

Every API endpoint responds with a standardized JSON wrapper:

```json
{
  "success": true, // or false
  "message": "Human readable message describing the result.",
  "data": { ... } // (Optional) The requested resource or objects
}
```

---

## 1. Authentication & Authorization

All protected routes require an HTTP header containing the JWT Access Token.
**Header Format:** `Authorization: Bearer <your_access_token>`

Roles: `job_seeker` (default), `hr` (requires admin activation), `admin`.

### Signup
*   **POST** `/auth/signup/`
*   **Body:** `{ "username": "...", "email": "...", "password": "...", "displayName": "...", "role": "job_seeker" }`
*   **Response:** Expect an OTP (sent to email) for verification.

### Verify Signup (OTP)
*   **POST** `/auth/verify_signup/`
*   **Body:** `{ "email": "...", "otp": "123456" }`
*   **Response:** JWT signup token and user data.

### Login
*   **POST** `/auth/login/`
*   **Body:** `{ "email": "...", "password": "..." }`
*   **Response:** 
    ```json
    {
      "success": true,
      "message": "Login successful.",
      "data": {
        "user": { ... },
        "refresh": "<refresh_token>",
        "access": "<access_token>"
      }
    }
    ```

### Logout
*   **POST** `/auth/logout/` (Auth required)
*   **Body:** `{ "refresh": "<refresh_token>" }`

### Current User Profile
*   **GET** `/auth/me/` (Auth required)
*   **Response:** Your full `User` object.

### User Lookup
*   **GET** `/auth/user/<user_id>/` (Auth required)

### Manage Users (HR/Admin Only)
*   **CRUD** `/users/` — List, edit, deactivate users.

---

## 2. Organizations

Manage teams and companies.

*   **GET** `/organizations/` (Auth required) — List all organizations.
*   **GET** `/organizations/{id}/` (Auth required) — Get details of a specific organization.
*   **POST** `/organizations/` (HR/Admin only) — Create a new organization.
*   **PUT/PATCH** `/organizations/{id}/` (HR/Admin only) — Update an organization.
*   **DELETE** `/organizations/{id}/` (Admin only) — Delete an organization.

---

## 3. Profiles & Skills

*   **GET** `/profiles/me/` (Auth required) — Get or create your own profile.
*   **GET** `/profiles/` (Auth required) — List all professional profiles.
*   **GET** `/profiles/{id}/` (Auth required) — Fetch specific profile details (automatically tracks that you viewed them).
*   **GET** `/profiles/{id}/views/` (Owner/Admin only) — See everyone who has viewed this profile (up to 50 recent).
*   **PUT/PATCH** `/profiles/{id}/` (Owner only) — Update headline, location, status, etc.
*   **CRUD** `/skills/` (Create requires Admin) — Manage platform-wide skill dictionary.
*   **CRUD** `/user-skills/` (Auth required) — Manage your personal skills and proficiency levels.
*   **GET** `/user-skills/user/{user_id}/` (Auth required) — Fetch a specific user's skills.

---

## 4. Connections (Networking)

Send, accept, and block networking connections.

*   **GET** `/connections/` (Auth required) — List all your connections (sent or received).
*   **POST** `/connections/` (Auth required) — Send a connection request.
    *   **Body:** `{ "receiver": "<user_uuid>" }`
*   **GET** `/connections/pending/` (Auth required) — List connections waiting for you to accept.
*   **POST** `/connections/{id}/accept/` (Receiver only) — Accept request.
*   **POST** `/connections/{id}/reject/` (Receiver only) — Reject request.
*   **POST** `/connections/{id}/block/` (Participant) — Block the user.

---

## 5. Jobs

Job discovery, posting, and saving.

*   **GET** `/jobs/` (Auth required) — List jobs. Merges internal DB jobs with **Adzuna API** external jobs! (Flagged via `source` field). Supports query parameters `?search=dev&location=london`.
*   **GET** `/jobs/{id}/` (Auth required) — Job details.
*   **POST** `/jobs/` (HR/Admin only) — Post a new job for your organization.
*   **PUT/PATCH** `/jobs/{id}/` (Owner/Admin only) — Update a job.
*   **DELETE** `/jobs/{id}/` (Admin only) — Delete a job.
*   **CRUD** `/job-skills/` (HR/Admin) — Manage required skills linked to jobs (`is_required` flag available).

### Saved Jobs
*   **POST** `/jobs/{id}/save_job/` (Auth required) — Bookmark a job.
*   **DELETE** `/jobs/{id}/unsave_job/` (Auth required) — Un-bookmark.
*   **GET** `/jobs/saved/` (Auth required) — List all your saved jobs.

---

## 6. Applications

*   **POST** `/applications/` (Job Seeker only) — Apply to a job.
    *   **Body:** `{ "job": "<job_uuid>", "cover_letter": "...", "resume_url": "..." }`
*   **GET** `/applications/` (Auth required)
    *   Job Seekers: See all jobs they've applied for.
    *   HR/Admin: See all applications across the platform.
*   **PATCH** `/applications/{id}/update_status/` (HR/Admin only)
    *   **Body:** `{ "status": "shortlisted" }` (or `rejected`, `accepted`, etc.)
*   **CRUD** `/application-reviews/` (HR/Admin only) — Leave private HR reviews/notes on candidates' applications.

---

## 7. Chat (Real-time)

Supports DM, Group Chat, and WebSockets.

### REST Endpoints
*   **GET** `/chat/` (Auth required) — List chat rooms you belong to, sorted by `last_message_at`.
*   **POST** `/chat/` (Auth required) — Create a group chat.
    *   **Body:** `{ "type": "group", "name": "Team Chat", "participant_ids": ["uuid-1", "uuid-2"] }`
*   **POST** `/chat/direct/` (Auth required) — Init or fetch a DM.
    *   **Body:** `{ "user_id": "<other_user_uuid>" }`
*   **GET** `/chat/{room_id}/messages/` (Participant) — Fetch up to 100 recent messages.
*   **GET** `/chat/{room_id}/participants/` (Participant) — List who is in the room and their `last_seen`.
*   **POST** `/chat/{room_id}/send_message/` (Participant) — Send a REST message.
*   **POST** `/chat/{room_id}/mark_read/` (Participant) — Bulk mark messages as read.
    *   **Body:** `{ "message_ids": ["uuid-1", "uuid-2"] }`

### WebSockets (Channels)
**URL:** `ws://localhost:8000/ws/chat/<room_id>/`
*(You must authenticate the socket connection via JWT—handling depends on frontend auth middleware, or standard Django Session auth if browsing from the same domain).*

**Sending a Message Payload (JSON):**
```json
{
  "type": "chat_message",
  "content": "Hello team!",
  "message_type": "text",
  "file_url": "" 
}
```

**Sending a Read Receipt Payload (JSON):**
```json
{
  "type": "read_receipt",
  "message_id": "<message_uuid>"
}
```

---

## 8. Notifications

*   **GET** `/notifications/` (Auth required)
*   **POST** `/notifications/{id}/mark_read/` (Auth required)
*   **POST** `/notifications/mark_all_read/` (Auth required)
*   **GET** `/notifications/unread_count/` (Auth required) — Quick stats check.

---

## 9. Files (Uploads)

A generic service to upload images, resumes, and attachments.

*   **POST** `/files/` (Auth required) — Requires `multipart/form-data`.
    *   `file`: The actual binary file.
    *   `entity_type` (Optional string): Context (e.g. "resume", "chat_attachment").
    *   `entity_id` (Optional string): Linked object UUID.
*   **GET** `/files/` (Auth required) — See your past uploads (Admins see all).

---

## 10. Courses

*   **GET** `/courses/?query=python` (Auth required)
    *   Searches the **YouTube Data API** for Playlists matching the query.
    *   Normalizes standard YouTube playlists into platform "Courses".
    *   Supports `&max_results=...` query param.
