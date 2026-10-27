# SYNTATIC — COMPLETE PROJECT PLAN
Generated: 2026‑10‑27
Stack: Python / Flask / Jinja2 / Supabase / Discord OAuth / Stripe / Cloudflare / Wispbyte Hosting
Purpose: Full blueprint for the entire Syntatic project hub including AI, Discord Bots, Roblox & Business Pages

## TABLE OF CONTENTS
1. GLOBAL UI & NAVIGATION
2. MAIN HUB PAGES
3. ORBITIX AI SYSTEM
4. DISCORD BOTS + DASHBOARDS
5. SYNPASS VERIFICATION SYSTEM
6. ROBLOX PROJECTS
7. BUSINESS PAGES
8. STORAGE & LIMIT RULES
9. SECURITY RULES
10. DEPLOYMENT NOTES

---
# 1. GLOBAL UI & NAVIGATION
✅ Shared across ALL pages
- Sidebar: Hidden by default on mobile; toggle button fixed bottom‑right; slides in from left; overlay blurs background; desktop always visible
- Theme: Gold (#E6C030) + Violet (#6B21B3) dark theme
- Login: Discord OAuth only; show avatar / name / logout button at sidebar bottom
- Auto‑save: Drafts locally + Supabase where applicable
- Skeleton loading, error toasts, escape to close sidebar
- No raw admin IDs exposed; admin list stored only in .env

---
# 2. MAIN HUB PAGES
## Path: / (Home)
- Logged Out: Brand intro, login button, ratings carousel, footer
- Logged In: Welcome message, avatar, quick actions, Sentivel status widget
## Path: /login
- Discord OAuth redirect page
## Path: /faq
- Searchable expandable Q&A grouped by categories
## Path: /about
- Mission, version, team, roadmap, feature voting
## Path: /contact
- Discord link + contact / bug report / security report forms
## Path: /security
- Best practices, credential leak recovery, data protection info
## Path: /status
- Sentivel iframe + component‑by‑component uptime status

---
# 3. ORBITIX AI SYSTEM
## Pages
### /ai
- AI hub overview: quick access cards, plan info, storage usage counter
### /ai/chat
- Unified chat interface: Text Chat / TTS / STT / File Analysis tabs
- Model selector, message bubbles, edit / regenerate / copy / delete
- Chat history sidebar: new, rename, search, delete, pin, archive
- Secure code handling: code extracted → encrypted → stored; generic message shown instead
### /ai/plans
- Four tiers: Free / Plus / Pro / Max
- Monthly ↔ Yearly toggle; current plan highlighted
### /ai/checkout
- Stripe checkout flow; summary + confirmation; redirect back to /ai

## Storage Rules
- Free Tier: Max 5 saved conversations; total 1 000 messages (500 user / 500 AI)
- Load old chat → restores full chronological history and counts toward limit
- Auto‑save ON by default; limit reached prompt: "You've reached your storage limit — upgrade or delete older conversations"
- Context recall: Scan saved history before new response to inject relevant context
- Secure code message: "This content has been securely packaged and stored for you. It is encrypted at rest and can only be viewed or downloaded from this active session. If you navigate away, it will be automatically relocated to a secure archive location."

---
# 4. DISCORD BOTS + DASHBOARDS
## Bot List
1. Chat Revive
2. Secret Shop (Private — your servers only; public view‑only)
3. Secret Sounds (Private — your servers only; public view‑only)
4. Invite Tracker
5. Server Setup
6. Server Info + Moderation
7. Tax Casino
8. Ask AI
9. Custom Commands
10. Auto Responder
11. Anti Attack (AA: Anti‑raid / Anti‑nuke / Anti‑spam / Honeypot)
12. SynPass (Verification Bot)

## Routes
- /discord — Bots Hub (grid, search, order custom bot, SynPass status)
- /discord/order — Custom Bot Enquiry Form
- /discord/{botname} — Per‑Bot Dashboard

## Per‑Bot Dashboard Tabs (ALL bots follow this structure)
1. 📌 Overview: Bot name, status, stats, Sentivel uptime, recent activity
2. ⚙️ Configuration: Bot‑specific toggles, channels, thresholds (public read‑only)
3. 📊 Analytics: 7d / 30d / 1yr / Lifetime graphs
4. 🔧 Commands: Toggle slash / prefix / logging / permissions (NOT full command list)
5. 💳 Subscription: Show all plans, highlight current plan, upgrade buttons
6. 🆘 Support: Links to status / Discord / FAQ + contact form

## Access Rules
- Public: Can view dashboard
- Non‑admin clicking save/edit: Instant blocked message
- Admin IDs stored only in .env; never exposed to frontend
- Bots hosted separately; dashboard ≠ bot host; Sentivel used for uptime tracking

---
# 5. SYNPASS VERIFICATION SYSTEM
## Route: /discord/synpass
- Only visible to server owners / admins
- Pending verifications list, verified users, logs, settings

## Verification Flow
1. User clicks "Verify Server" button
2. Backend generates one‑time URL valid for 5 minutes
3. Cloudflare triple bot check before activation
4. User adds SynPass bot (minimal permissions only; cannot join servers for user)
5. System confirms bot present → auto redirect back
6. Dashboard access unlocked for that server

⚠️ Important: Bot never joins servers automatically; only confirms presence

---
# 6. ROBLOX PROJECTS
## Routes
- /roblox — Roblox Hub
- /roblox/{gamename} — Individual Game Page

## Roblox Hub Content
- Game cards grid (thumbnail, name, status, description)
- Group overview: name, icon, member count, owner, social links
- Global stats: total visits, total currency in circulation, online players
- Announcements + upcoming updates teaser

## Individual Game Page Content
- Game Info: Banner, description, version, last updated, credits, play link
- Update Log: Reverse chronological; Added / Improved / Fixed
- Upcoming Updates: Planned / In Progress / Under Consideration
- Game Data: Total currency circulation, active players, server count, economy trends
- Player Lookup: Search username → public profile (playtime, balance, inventory, achievements — NO private data)

---
# 7. BUSINESS PAGES
## Route: /shems‑bar
- Purpose: In‑person venue + online pre‑order for collection
- Sections: Info (hours / location / contact), Menu, Online Order, Bundles / Add‑ons, Reviews, FAQ

## Route: /shems‑cards
- Purpose: Custom cards & invitations (order/enquiry based)
- Sections: Info, Gallery / Products, Custom Order Form, Add‑ons, FAQ

## Route: /booth (PS Naylor Photobooth)
- Purpose: Time‑based booking
- Pricing: £250 = 2 hours (prints included); +£50 per extra hour
- Optional Add‑ons: USB copy, Guest Book
- Sections: Info, Gallery, Calendar Booking, Packages / Add‑ons, FAQ

## Route: /naylorized‑creations
- Purpose: Custom art commissions
- Sections: Info, Portfolio Gallery, Commission Tiers, Enquiry Form, Add‑ons, Queue Status, FAQ

---
# 8. STORAGE & LIMIT RULES
- Supabase stores user chats, orders, verification logs, analytics data
- .env stores: DISCORD_CLIENT_ID, DISCORD_CLIENT_SECRET, SECRET_KEY, ADMIN_USER_IDS, GROQ_API_KEY, STRIPE_KEYS
- Never commit .env to GitHub
- Chat limits reset / managed by plan; higher plans increase limits
- Code storage: Temporary rotating encrypted GitHub storage; moved/removed when leaving active session

---
# 9. SECURITY RULES
- All POST / edit requests server‑side checked against .env admin list
- Discord OAuth only; no manual password login
- Cloudflare for bot protection on SynPass verification links
- Environment variables loaded via python‑dotenv
- No private Discord IDs / API keys rendered to frontend
- Log unauthorized edit attempts
- Code encrypted at rest; decrypted only during active viewing session

---
# 10. DEPLOYMENT NOTES
- Host: Wispbyte
- Backend: Flask + Python
- Templates: Jinja2 (separate folders per page)
- Database: Supabase
- Payments: Stripe
- Uptime: Sentivel
- Bot Hosting: Separate (NOT on Flask dashboard)
- CSS: External style.css only; inline only for testing

ignore the orbitix folder, unless you need anything from it/would like to use smth from it and then refine it.

urls and other stuff:

