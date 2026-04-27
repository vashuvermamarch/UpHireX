# Postman Testing Guide for UpHireX

This guide extends the previous Postman testing guidance with a deep focus on role-based testing, authentication token management, and end-to-end workflows across multiple user roles. It provides concrete patterns you can adopt against the UpHireX API surface and is designed to be adapted to your exact endpoint catalog.

## 1) Assumptions and goals
- Validate RBAC behavior for Admin, Editor, User, and Guest alike.
- Verify per-endpoint authentication requirements (which token, which role, and expected errors when missing/invalid).
- Exercise end-to-end multi-user workflows (admin creates resources, editor updates, user reads, etc.).
- Enable repeatable, data-driven tests in CI via Newman.

Assumptions about the token flow (adjust to your real auth design):
- The API issues a JWT or opaque token on login via POST {{baseUrl}}/auth/login.
- Login response contains a token (and possibly an expiry). Example: { token: "...", expiresIn: 3600 }.
- All endpoints requiring authentication expect an Authorization: Bearer <token> header, unless you use an API key in a header.
- You may use separate tokens per role for clearer RBAC testing (Admin, Editor, User, Guest).

If you use a different pattern (OAuth2, cookies, API keys), adapt the headers accordingly in the Pre-request scripts described later.

## 2) Role model (RBAC) for UpHireX
- Admin: full access; manage users, roles, resources, configs, and audit endpoints.
- Editor: read/write access to resources; cannot manage users or global settings.
- User: read-access to owned/permitted resources; cannot write or manage users.
- Guest: minimal access; typically public data only, no writes.

This guide assumes endpoints express permissions via roles in the access token or via scopes/claims.

## 3) Endpoints and per-role authentication matrix (example)
Note: Customize this matrix to your actual UpHireX endpoints.

- POST {{baseUrl}}/auth/login
  - Auth needed: None
  - Purpose: obtain a token for a specific role
  - Roles allowed: all (admin, editor, user, guest) via login credentials

- GET {{baseUrl}}/resources
  - Auth needed: Bearer token
  - Roles allowed: Admin, Editor, User (visibility depends on ownership/permissions)
  - Purpose: list resources visible to the caller

- POST {{baseUrl}}/resources
  - Auth needed: Bearer token
  - Roles allowed: Admin, Editor
  - Purpose: create a new resource

- GET {{baseUrl}}/resources/{id}
  - Auth needed: Bearer token
  - Roles allowed: Admin, Editor, User
  - Purpose: view a resource (subject to visibility rules)

- PATCH {{baseUrl}}/resources/{id}
  - Auth needed: Bearer token
  - Roles allowed: Admin, Editor
  - Purpose: update a resource

- DELETE {{baseUrl}}/resources/{id}
  - Auth needed: Bearer token
  - Roles allowed: Admin
  - Purpose: delete a resource

- POST {{baseUrl}}/users
  - Auth needed: Bearer token
  - Roles allowed: Admin
  - Purpose: create a new user (and set initial role)

- POST {{baseUrl}}/users/{id}/roles
  - Auth needed: Bearer token
  - Roles allowed: Admin
  - Purpose: assign/change a user’s role

- GET {{baseUrl}}/admin/reports
  - Auth needed: Bearer token
  - Roles allowed: Admin
  - Purpose: admin-only data access

> Optional: Endpoints that enforce specific scopes/claims. Document required scopes in tests and expected responses (401 vs 403).

## 4) End-to-end workflow patterns (multi-user scenarios)
These scenarios assume you have at least one test account per role and a means to login and obtain a token.

Scenario 1 — Admin onboards a new Editor
- Admin logs in and obtains token_admin
- Admin creates a new user with username: editor_onboard, role: editor
- Expect 201 Created with a new userId

Scenario 2 — Editor creates a resource, User consumes it
- Admin exists but can be omitted if you reuse an editor account
- Editor logs in and obtains token_editor
- Editor creates a resource (POST /resources)
- User logs in and obtains token_user
- User reads the created resource (GET /resources/{id})
- Editor updates the resource (PATCH /resources/{id})
- Admin deletes the resource (DELETE /resources/{id})

Scenario 3 — Unauthorized access tests
- User (or Guest) tries to POST /resources → expect 403 Forbidden or 401 Unauthorized (depending on token presence)
- No token header → expect 401 Unauthorized
- Expired/invalid token → expect 401 Unauthorized

Scenario 4 — Role escalation check
- Admin assigns Editor role to a User
- The same user attempts Editor actions and succeeds
- Verify no escalation for endpoints outside Editor scope

## 5) Postman collection design (recommended structure)
- Environments
  - Base environment with: baseUrl, common headers (optional)
- Authentication strategy (data-driven or per-role)
- Collections and folders (logical grouping):
  - Auth
    - Admin Login
    - Editor Login
    - User Login
  - Users
    - Create User (Admin)
    - Get Users (Admin)
    - Assign Roles (Admin)
  - Resources
    - List Resources (All Authenticated Roles)
    - Create Resource (Admin, Editor)
    - Get Resource (Admin, Editor, User)
    - Update Resource (Admin, Editor)
    - Delete Resource (Admin)
  - Admin
    - Admin-only endpoints (e.g., /admin/reports)
- Data-driven approach
  - data/users.json: list of users with role, username, password
  - data/resources.json: sample payloads for create/update
- Tokens per role (optional)
  - TOKEN_ADMIN, TOKEN_EDITOR, TOKEN_USER, TOKEN_GUEST stored in environment or via data-driven login steps
- Per-request metadata
  - If you want per-request role scoping, include a field requiredRole in the data file and a small pre-request script to attach the correct token.

## 6) Data-driven testing and token management approaches
You have three practical approaches. Pick one that aligns with your CI strategy and security constraints.

Approach A — Per-iteration login (recommended for realism in CI)
- data.json contains: role, username, password, baseUrl, requiredRole
- A dedicated login request runs at the start of each iteration to fetch a role-specific token and stores it in an environment variable (TOKEN_ADMIN, TOKEN_EDITOR, etc.)
- All subsequent requests use the role-specific token via Authorization: Bearer {{TOKEN_ADMIN}} (or the corresponding role).

Approach B — Pre-fetched tokens in data (simple for local testing)
- data.json includes tokens per role: token_admin, token_editor, token_user
- Requests set Authorization header from the appropriate token field in the data row using a small pre-request script.
- Tokens must be refreshed periodically in CI.

Approach C — Hybrid with role mapping (flexible and CI-friendly)
- Run per-role login steps to populate token variables into collection/environment variables, then map those tokens to role-specific requests via a pre-request script.

Tip: Use a pre-request script to set the Authorization header based on a requiredRole field in the data row:

```js
// Example Pre-request Script (data-driven)
const requiredRole = (pm.iterationData.get("requiredRole") || "admin").toLowerCase();
const tokenVar = `TOKEN_${requiredRole.toUpperCase()}`;
const token = pm.environment.get(tokenVar);
if (token) {
  pm.request.headers.upsert({ key: "Authorization", value: `Bearer ${token}` });
} else {
  // Optional: fall back to a default token or fail clearly
  pm.test("token for role " + requiredRole + " is present", () => {
    throw new Error("Missing token for role: " + requiredRole);
  });
}
```

## 7) Starter data files (templates)
Data file template (data.json example):
```json
[
  {"role":"admin","username":"admin1","password":"admin-pass","baseUrl":"https://api.uphirex.local","requiredRole":"admin"},
  {"role":"editor","username":"editor1","password":"editor-pass","baseUrl":"https://api.uphirex.local","requiredRole":"editor"},
  {"role":"user","username":"user1","password":"user-pass","baseUrl":"https://api.uphirex.local","requiredRole":"user"}
]
```

Login helper data (optional) for first-iteration login results are stored in environment vars:
```json
{
  "token_admin": "<jwt-token-for-admin>",
  "token_editor": "<jwt-token-for-editor>",
  "token_user": "<jwt-token-for-user>"
}
```

Environment example (environment.json):
```json
{
  "baseUrl": "https://api.uphirex.local",
  "TOKEN_ADMIN": "<token>",
  "TOKEN_EDITOR": "<token>",
  "TOKEN_USER": "<token>"
}
```

## 8) Per-endpoint tests (examples you can copy)
- Admin and Editor write access tests for resources
  - status 201 on POST /resources for Admin and Editor
  - status 200 on GET /resources and GET /resources/{id}
  - status 200 on PATCH /resources/{id} for Admin/Editor
  - status 403/401 for User attempting POST/PATCH/DELETE when not allowed
- User read tests
  - status 200 on GET /resources/{id} if allowed
  - status 403/401 on unauthorized reads
- Auth tests
  - Login succeeds for admin/editor/user
  - Access without token returns 401
  - Access with invalid token returns 401

## 9) CI integration with Newman (quick start)
- Install: npm install -g newman
- Run a collection with environment and data files:
  newman run collection.json -e environment.json -d data.json --reporters cli,json --reporter-json-export results.json

GitHub Actions example (simplified):
```yaml
name: API Tests
on: [push]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - name: Install Newman
        run: npm install -g newman
      - name: Run Postman tests
        env:
          BASE_URL: ${{ secrets.BASE_URL }}
        run: newman run collection.json -e environment.json -d data.json --reporters cli,json --reporter-json-export results.json
```

Note: Do not log sensitive tokens in build logs. Use CI secrets for credentials and limit what is printed.

## 10) Security and hygiene
- Isolate test data from production data; prefer sandbox/test environments where possible.
- Never commit real secrets; leverage CI secret stores.
- Clean up test-created data if endpoints support deletion.
- Use short-lived tokens and rotate test credentials regularly.

## 11) Quick-start plan (2-hour starter)
- Step 1: Define roles and the exact endpoints you want to cover; draft a RBAC matrix tailored to UpHireX.
- Step 2: Create a Postman collection skeleton with folders for Auth, Users, Resources, Admin.
- Step 3: Implement login requests for Admin, Editor, User; capture tokens into TOKEN_ADMIN, TOKEN_EDITOR, TOKEN_USER in environment.
- Step 4: Implement a subset of tests (read/write for Resources, user creation/role assignment for Admin).
- Step 5: Add a data.json with 2-3 roles and a couple of resources.
- Step 6: Run tests locally via Postman or Newman; iterate on test coverage.
- Step 7: Wire into CI with a simple Newman run and a results artifact for reporting.

If you share your exact endpoint list, roles, and your current auth approach, I’ll tailor this guide into a concrete, drop-in Postman collection skeleton (requests, pre-request scripts, tests), plus concrete data.json and environment.json that you can drop into your repo.
