# HextgenAI Take-Home Assignment: Permission-Aware Operations Agent
## Complete Engineering Session & Project Summary Report

**Date:** November 10, 2026  
**Repository:** https://github.com/kjeevankumar/Permission-Aware-Operations-Agent.git  
**Branch:** `main`  
**Author:** K Jeevan Kumar  

---

### Executive Summary

Over this engineering session, we designed, built, tested, and shipped the **Permission-Aware Operations Agent** platform from the ground up to production readiness. The system is a secure, multi-tenant healthcare database operations platform built with a high-performance **FastAPI backend** and a modern **React SaaS frontend**.

---

### 1. Key Accomplishments & Deliverables

#### A. Backend Architecture & Database Foundation (FastAPI + SQLAlchemy 2.0)
- **11 Relational Database Tables**:
  - `hospitals` (Tenant isolation root)
  - `users`, `roles`, `permissions`, `role_permissions`, `user_roles`, `user_permission_overrides`
  - `inventory_items` (Stock & batch tracking with compound indexes)
  - `bills` (Financial invoices strictly preventing deletion)
  - `pending_operations` (Two-phase staged mutations with 15-minute TTL)
  - `audit_log` (Write-ahead immutable transaction log with before/after state diffs)
- **Database Migrations**: Initialized Alembic migration (`alembic/versions/0001_initial_tables.py`).
- **Deterministic & Idempotent Seed Dataset (`random.seed(42)`)**:
  - **2 Hospitals**: Metro Health General Hospital (Mumbai) and St. Jude Memorial Hospital (Bangalore).
  - **14 Pre-seeded Users** (7 per hospital) with distinct roles and operational constraints.
  - **1,240 Inventory Records** (620 per hospital, exceeding requirement of 600) with low-stock alerts, 30-day expiry windows, and an adversarial prompt injection test record.
  - **550 Billing Invoices** spread realistically over 90 days.
  - **Zero initial audit logs** (ensuring true runtime logging).

#### B. Security & Architectural Invariants
1. **Strict Hospital Tenant Isolation**:
   - Every business table contains an indexed `hospital_id`.
   - Tenant identity is derived authoritatively from the verified JWT token and database lookup.
   - Forged client headers or query parameters attempting cross-tenant access are strictly ignored.
2. **Fine-Grained RBAC & Dynamic Constraints**:
   - Pharmacist updates capped at `max_rows: 500`.
   - Billing Manager discounts capped at `max_discount_pct: 10%`.
   - Front Desk restricted to viewing own-initiated records (`scope: own_records`).
   - Admin holds full privileges (`max_discount_pct: 100%`, `max_rows: 10000`).
3. **User-Specific Permission Overrides**:
   - Specific privileges can be granted or revoked per user without modifying shared roles.
4. **No Financial Deletions**:
   - `bills.delete` permission does not exist. Only status updates or approved discounts are allowed.
5. **Two-Phase Preview & Confirmation Workflow**:
   - Mutating or high-impact operations calculate dry-run before/after diffs, stage them with a 15-minute TTL, and require same-tenant authorized confirmation before atomic execution.
   - Operations impacting >50 records trigger an explicit high-risk UI safeguard dialog.

#### C. Authentication & Swagger OAuth2 Fix
- Resolved Swagger UI OAuth2 authentication by exposing standard `POST /api/v1/auth/token` (`application/x-www-form-urlencoded`), while retaining clean JSON `POST /api/v1/auth/login` for the web client.
- Secure password hashing using Bcrypt (12 salt rounds) and standard Bearer JWT issuance.

#### D. Modern React SaaS Frontend (`frontend/`)
- Built using **React 18**, **Vite**, **Tailwind CSS**, and **Lucide Icons**.
- **Login Screen**: Includes clean authentication with a one-click quick demo role switcher for all 10 demo users.
- **Operations Dashboard**: Real-time statistics, low-stock alerts, recent activity feed.
- **AI Operations Assistant**: Interactive chat interface supporting all 4 structured response schemas:
  - *Direct Answer*: Structured operational query responses.
  - *Clarification Request*: Resolving ambiguous references (e.g. Dr. Ravi Sharma vs Pharmacist Ravi Kumar).
  - *Permission Denied Refusal*: Clear rejection cards when constraints/RBAC are violated.
  - *Two-Phase Preview*: Interactive diff card with countdown timer and Confirm / Reject buttons.
- **Data Explorers**: Filterable and searchable views for Inventory, Bills & Invoices, User Access & Overrides, and Immutable Audit Logs.

#### E. Automated Testing Suite (Pytest)
- **26 passed out of 26 tests** validating database connectivity, schema integrity, password hashing, seed volumes, JWT security, cross-tenant isolation barriers, and RBAC constraint enforcement.

#### F. Git Repository & Documentation
- Initialized and pushed 103 clean files to:
  `https://github.com/kjeevankumar/Permission-Aware-Operations-Agent.git`
- Comprehensive, production-grade `README.md` with system diagrams, quickstart guides, demo credentials table, and API specifications.

---

### 2. Demo User Credentials Reference

Demo Password for all accounts: `HospitalDemo2026!`

| Hospital | Username | Role | Purpose / Special Capability |
| :--- | :--- | :--- | :--- |
| Metro Health | `admin.metro` | Admin | Full admin access, up to 100% discount, user overrides |
| Metro Health | `billing.metro` | Billing Manager | Financial invoices, discount strictly capped at 10% |
| Metro Health | `pharma.metro` | Pharmacist | Inventory stock updates capped at 500 records |
| Metro Health | `frontdesk.metro`| Front Desk | Bill creation, view own records only |
| Metro Health | `doctor.metro` | Doctor | Read-only inventory and bills lookup |
| Metro Health | `ravi.sharma` | Doctor, Admin | Dual-role user; tests name ambiguity |
| Metro Health | `ravi.kumar` | Pharmacist | Pharmacist user; tests name ambiguity |
| St. Jude Memorial | `admin.jude` | Admin | Isolated St. Jude administration |
| St. Jude Memorial | `billing.jude` | Billing Manager | St. Jude billing management |
| St. Jude Memorial | `pharma.jude` | Pharmacist | St. Jude pharmacy management |
| St. Jude Memorial | `frontdesk.jude` | Front Desk | St. Jude front desk admissions |
| St. Jude Memorial | `doctor.jude` | Doctor | St. Jude attending doctor |
| St. Jude Memorial | `ravi.patel` | Billing Mgr, Front Desk | Cross-hospital identity; tests tenant isolation |
| St. Jude Memorial | `dr.anand` | Doctor, Billing Mgr | Dual clinical & financial reviewer |

---

### 3. Quick Run Commands

**Run Backend:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
# Access Swagger UI: http://localhost:8000/docs
```

**Run Frontend:**
```bash
cd frontend
npm run dev
# Access Web App: http://localhost:5173
```

**Run Tests:**
```bash
pytest -v
# 26 passed in ~1.5s
```
