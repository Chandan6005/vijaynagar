# Workspace

## Overview

pnpm workspace monorepo using TypeScript, plus a Django ePaper web application.

## Stack

- **Monorepo tool**: pnpm workspaces
- **Node.js version**: 24
- **Package manager**: pnpm
- **TypeScript version**: 5.9
- **API framework**: Express 5
- **Database**: PostgreSQL + Drizzle ORM (Node.js), SQLite (Django)
- **Validation**: Zod (`zod/v4`), `drizzle-zod`
- **API codegen**: Orval (from OpenAPI spec)
- **Build**: esbuild (CJS bundle)

## Artifacts

### ePaper - Digital Newspaper (`artifacts/epaper`)
- **Framework**: Django 5.2 (Python 3.11)
- **Database**: SQLite (at `artifacts/epaper/db.sqlite3`)
- **Startup**: `bash /home/runner/workspace/artifacts/epaper/start.sh`
- **Port**: 25153
- **Admin credentials**: username=`admin`, password=`admin123`

#### Features
- Public homepage — browse and read all published newspaper editions
- PDF viewer embedded in browser (`<object>` tag)
- Search editions by title or description
- Admin login at `/admin-login/` (staff/superuser required)
- Admin dashboard at `/admin-dashboard/` — manage all editions
- Upload PDF newspapers with optional cover image
- Edit and delete editions
- Publish/unpublish toggle

#### Key URLs
- `/` — Homepage (public)
- `/admin-login/` — Admin login
- `/admin-dashboard/` — Edition management (admin only)
- `/admin-dashboard/upload/` — Upload new edition (admin only)
- `/edition/<id>/` — Read a specific edition (public)
- `/django-admin/` — Django default admin (superuser)

## Key Commands

- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- `pnpm --filter @workspace/api-server run dev` — run API server locally

See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details.
