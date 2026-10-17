# Syntatic Landing + Auth Plan

## Goal
Add a `/landing` page to the main Syntatic app with server-side login state, username/password auth backed by Supabase, Discord OAuth login, and static page categories.

## Decisions
- Landing route: `/landing` (alias-friendly; root can redirect later)
- Session: Flask server-side session with `SECRET_KEY` from env
- Database: Supabase
- Email auth: username + password, hashed with `werkzeug.security`
- Discord auth: OAuth2, store `discord_id` on user row
- Page groups: static config in `Syntatic/pages.py` (display categories only)

## Affected Files
- `Syntatic/app.py`
- `Syntatic/pages.py` (new)
- `Syntatic/auth.py` (new blueprint)
- `Syntatic/templates/landing.html` (new)
- `Syntatic/templates/login.html` (new)
- `Syntatic/templates/register.html` (new)
- `Syntatic/static/gold_violet.css` (reuse)

## Data Model (Supabase)
`users`:
- `id` uuid primary key
- `username` text unique not null
- `email` text
- `password_hash` text nullable
- `discord_id` text unique nullable
- `created_at` timestamptz default now()

## Routes
- `GET /landing`
- `GET/POST /auth/login`
- `GET/POST /auth/register`
- `GET /auth/discord`
- `GET /auth/discord/callback`
- `POST /auth/logout`

## Implementation Steps
1. Add env-based config (`SECRET_KEY`, Supabase URL/key, Discord client id/secret).
2. Create Supabase client helper.
3. Implement user lookup/create and password hashing.
4. Add auth blueprint and templates using global gold-on-violet CSS.
5. Add static `pages.py` with categories and page entries.
6. Render categories on landing page; show login/logout state.
7. Protect future pages via session check (helper `login_required`).

## Risks
- Supabase credentials must not be committed; use env vars.
- Discord OAuth redirect URI must match Wispbyte domain.
- Session cookies need `Secure` in production.

## Validation
- Start app locally, load `/landing`, register, login, logout, Discord flow (with test creds).
- Verify session persists across requests.
- Verify password hash stored, not plaintext.
