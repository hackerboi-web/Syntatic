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
- Group pages require login and show group description plus page cards
- Landing shows group buttons only when logged in
- Groups: Roblox, Discord Bots, Other Websites
- Unimplemented project pages show disabled "coming soon" cards

## Affected Files
- `Syntatic/app.py`
- `Syntatic/pages.py` (new)
- `Syntatic/auth.py` (new blueprint)
- `Syntatic/templates/landing.html` (new)
- `Syntatic/templates/login.html` (new)
- `Syntatic/templates/group.html` (new)
- `Syntatic/templates/page.html` (new placeholder)
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
- `GET /pages/<group>`
- `GET /pages/<group>/<slug>`
- `POST /auth/logout`

## Implementation Steps
1. Add env-based config (`SECRET_KEY`, Supabase URL/key, Discord client id/secret).
2. Create Supabase client helper.
3. Implement user lookup/create and password hashing.
4. Add auth blueprint and templates using global gold-on-violet CSS.
5. Add static `pages.py` with groups, descriptions, and page entries (title, slug, description, implemented flag).
6. Render group buttons on landing only when logged in.
7. Add group pages with description, back button, and page cards (disabled coming soon if not implemented).
8. Add `login_required` decorator and protect group/project pages.

## Risks
- Supabase credentials must not be committed; use env vars.
- Discord OAuth redirect URI must match Wispbyte domain.
- Session cookies need `Secure` in production.

## Validation
- Start app locally, load `/landing`, register, login, logout, Discord flow (with test creds).
- Verify session persists across requests.
- Verify password hash stored, not plaintext.
