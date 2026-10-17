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

## Actual Pages

### Decisions
- Orbitix page keeps the full chat UI and model/voice dropdown.
- Other project pages show page content plus a floating chat button that opens an overlay modal; background content is slightly blurred while open.
- Each page has a page-specific system prompt loaded when the page loads.
- Each non-Orbitix page is locked to one primary model with per-page Low/Med/Max thinking levels mapped to configured model IDs.
- Non-Orbitix AI is restricted to page help/info and must not provide code or anything usable against internal or external services.
- Icons live in `Syntatic/icons/`.
- Page content lives in `Syntatic/templates/pages/<group>/<slug>.html`; Python files contain only Python code.
- Overlay chat resets when navigating away, persists on page reload, and auto-saves to Supabase after each response when chat saving is enabled.
- `/load` restores a prior saved conversation and sends it back to the provider as context.
- User settings are stored in Supabase.

### Affected Files
- `Syntatic/pages.py`
- `Syntatic/templates/pages/<group>/<slug>.html`
- `Syntatic/templates/components/chat_overlay.html`
- `Syntatic/chat.py` (new)
- `Syntatic/templates/settings.html` (new)
- `Syntatic/static/gold_violet.css`
- `Syntatic/icons/` (assets added later)

### Routes
- `GET /pages/<group>/<slug>`
- `POST /pages/<group>/<slug>/chat`
- `GET/POST /settings`

### Data Model (Supabase)
`user_settings`:
- `user_id` uuid primary key references users(id)
- `chat_saving_enabled` boolean default false
- `default_thinking_level` text default 'med'

`chat_sessions`:
- `id` uuid primary key
- `user_id` uuid references users(id)
- `page_key` text not null
- `created_at` timestamptz default now()

`chat_messages`:
- `id` uuid primary key
- `session_id` uuid references chat_sessions(id)
- `role` text not null
- `content` text not null
- `created_at` timestamptz default now()

### Implementation Steps
1. Extend `pages.py` with per-page model IDs, thinking levels, system prompts, and template paths.
2. Add page content templates and a shared chat overlay component.
3. Add modal/blur styles to the global CSS.
4. Add chat endpoint that validates page and thinking level, builds the page system prompt, streams responses, and auto-saves when enabled.
5. Add settings page and Supabase-backed user settings.
6. Implement `/load` handling for saved conversations.
7. Keep Orbitix page on the original full chat UI.

### Risks
- Safety is prompt-based and should be reviewed for each page prompt.
- Misconfigured model IDs or thinking levels can break a page’s chat.
- Auto-saving stores user conversations; retention/privacy policy should be defined later.

### Validation
- Open a project page, use the overlay chat, reload, and confirm the conversation persists.
- Navigate away and back; confirm the conversation resets.
- Enable chat saving, send messages, use `/load`, and confirm prior messages restore.
- Change thinking levels and confirm the configured model is used.
- Confirm Orbitix page still supports model/voice selection.
- Confirm landing page has no AI overlay before login.

## Roblox Pages

### Decisions
- Roblox group page uses the existing group template and cards.
- Roblox cosmetic shop is a browse-only page with item cards, Robux price buttons linking to Roblox item pages, and sale status badges.
- Items are manually curated in Supabase, with an optional Python import function for configured Roblox item IDs.
- Shop supports search, filtering, and sorting by status, price, and title.
- Item images use Supabase Storage bucket `roblox-items`, with external URL fallback.
- Sale statuses: `for_sale`, `limited`, `ugc`, `offsale`.
- Realtime updates use a browser Supabase client with anon key and read-only RLS, with page-load fetch as fallback.
- Roblox page chat uses the shared overlay and is restricted to shop help/info.

### Affected Files
- `Syntatic/pages.py`
- `Syntatic/templates/pages/roblox/cosmetic-shop.html` (new)
- `Syntatic/roblox.py` (new)
- `Syntatic/static/gold_violet.css`

### Routes
- `GET /pages/roblox/cosmetic-shop`
- `GET /api/roblox/items`
- `POST /api/roblox/import` (optional manual trigger)

### Data Model (Supabase)
`roblox_items`:
- `id` uuid primary key
- `title` text not null
- `description` text
- `image_url` text
- `robux_price` integer
- `roblox_item_url` text not null
- `sale_status` text not null
- `item_type` text
- `created_at` timestamptz default now()
- `updated_at` timestamptz default now()

### Implementation Steps
1. Add Roblox cosmetic shop page entry and template.
2. Create `roblox_items` table and RLS read policy.
3. Create Supabase Storage bucket `roblox-items`.
4. Implement item fetch, search, filter, and sort in the page.
5. Add Supabase Realtime subscription for item changes.
6. Implement optional Python import function for configured item IDs.
7. Add Roblox AI overlay system prompt.

### Risks
- Roblox public API fields and availability may change.
- Realtime requires exposing an anon key; RLS must remain read-only.
- Client-side filtering may need pagination for large catalogs.

### Validation
- Load shop, verify items render with status badges and price buttons.
- Test search/filter/sort.
- Update an item in Supabase and verify realtime update.
- Run optional import and verify imported items.
- Confirm page chat remains scoped to shop help.

## Discord Bot Dashboards

### Decisions
- Discord bot dashboards are per-bot pages under the Discord Bots group.
- Dashboard access requires Discord OAuth2 and only shows guilds the user can manage and where the bot is present.
- Configuration is stored per guild in each bot's own Supabase database.
- The website reads and updates guild config; bots fetch config through a shared API using bot API key plus guild ID.
- Bots cache config and invalidate it when settings change.
- If a bot is disabled for a guild, it leaves the server and deletes that guild's stored messages/config.
- Each bot has its own command list, toggles, configs, rules, and automated message schedules.
- Features can depend on other bots; a feature stays disabled unless its required bot is present and enabled.
- Automated message schedules store cron-like times and target channels.

### Affected Files
- `Syntatic/pages.py`
- `Syntatic/templates/pages/discord-bots/<bot-slug>.html`
- `Syntatic/discord_bots.py` (new)
- `Syntatic/static/gold_violet.css`

### Routes
- `GET /pages/discord-bots/<bot-slug>`
- `GET /api/discord/guilds`
- `GET /api/discord/bots/<bot-slug>/guilds/<guild_id>/config`
- `POST /api/discord/bots/<bot-slug>/guilds/<guild_id>/config`

### Data Model (Per Bot Supabase)
`guild_configs`:
- `guild_id` text primary key
- `enabled` boolean default true
- `commands` jsonb
- `command_configs` jsonb
- `rules` jsonb
- `automated_messages` jsonb
- `updated_at` timestamptz default now()

`guild_messages`:
- `id` uuid primary key
- `guild_id` text not null
- `channel_id` text
- `message_id` text
- `created_at` timestamptz default now()

### Implementation Steps
1. Add one dashboard page per bot in `pages.py`.
2. Implement Discord OAuth guild fetching and intersection with bot guilds.
3. Create shared API routes for reading and updating guild config.
4. Build dashboard UI for settings, command toggles, configs, rules, and schedules.
5. Add dependency checks for cross-bot features.
6. Implement bot-side fetch/cache/invalidation and disable cleanup behavior.
7. Keep each bot's command set configured separately.

### Risks
- Per-bot databases require consistent schema and migrations.
- Guild permissions and bot membership must be validated on every config request.
- Invalidating stale bot caches can be delayed.
- Cross-bot dependencies can create circular feature requirements.

### Validation
- Log in with Discord and verify only manageable shared guilds appear.
- Change a setting and confirm the bot fetches the updated config.
- Disable a bot for a guild and confirm cleanup behavior.
- Verify command toggles and automated schedules persist.
- Test a feature that depends on another bot.

## Uptime Page

### Decisions
- Uptime page is login-required.
- External cron calls a Flask health endpoint every minute.
- Store check results in Supabase with service name, status, latency, and timestamp.
- Display current status, recent history, and rolling total uptime percentage.

### Affected Files
- `Syntatic/templates/pages/other-websites/uptime.html` (new)
- `Syntatic/uptime.py` (new)

### Routes
- `GET /pages/other-websites/uptime`
- `POST /api/uptime/check`
- `GET /api/uptime/history`

### Data Model (Supabase)
`uptime_checks`:
- `id` uuid primary key
- `service_name` text not null
- `status` text not null
- `latency_ms` integer
- `checked_at` timestamptz default now()

### Implementation Steps
1. Add uptime page entry and template.
2. Implement health checks for configured services.
3. Store results and calculate rolling uptime percentage.
4. Add cron-compatible endpoint.
5. Add realtime or polling refresh.

### Risks
- External cron must be configured on Wispbyte.
- Service endpoints may be unreachable from the host.

### Validation
- Trigger checks manually and verify results.
- Confirm uptime percentage calculation.
- Verify page refreshes status.

## Invite Page

### Decisions
- Invite page is login-required.
- It generates and manages Discord bot invite links for guilds the user can manage and where each bot is present.
- Invites are stored in Supabase with bot, guild, creator, and created timestamp.

### Affected Files
- `Syntatic/templates/pages/discord-bots/invite.html` (new)
- `Syntatic/invites.py` (new)

### Routes
- `GET /pages/discord-bots/invite`
- `POST /api/invites`
- `DELETE /api/invites/<id>`

### Data Model (Supabase)
`bot_invites`:
- `id` uuid primary key
- `bot_slug` text not null
- `guild_id` text not null
- `created_by` uuid references users(id)
- `invite_url` text not null
- `created_at` timestamptz default now()

### Implementation Steps
1. Add invite page entry and template.
2. Fetch manageable shared guilds.
3. Generate invite URLs per bot and guild.
4. Store and list invites.
5. Add revoke support.

### Risks
- Discord permission checks must be revalidated server-side.
- Invite URLs can be shared beyond intended users.

### Validation
- Generate an invite and verify it opens Discord.
- Revoke and verify removal.
- Confirm only manageable guilds appear.

## Request Page

### Decisions
- Request page is login-required.
- It collects custom bot order requirements and creates a Stripe checkout session.
- Stripe webhook marks the order paid.
- Orders are stored in a separate Supabase database/table accessible only to the owner.
- New orders send a Discord webhook notification and optional email.

### Affected Files
- `Syntatic/templates/pages/discord-bots/request.html` (new)
- `Syntatic/orders.py` (new)
- `Syntatic/templates/pages/admin/orders.html` (new)

### Routes
- `GET /pages/discord-bots/request`
- `POST /api/orders`
- `POST /api/stripe/webhook`
- `GET /admin/orders`

### Data Model (Supabase)
`custom_orders`:
- `id` uuid primary key
- `user_id` uuid references users(id)
- `requirements` text not null
- `status` text default 'pending'
- `stripe_session_id` text
- `stripe_payment_intent_id` text
- `created_at` timestamptz default now()

### Implementation Steps
1. Add request form and order creation.
2. Create Stripe checkout session server-side.
3. Handle webhook and mark order paid.
4. Send Discord/email notification.
5. Add admin-only orders page.

### Risks
- Webhook signature verification is required.
- Admin access must be strictly enforced.
- Payment and order state can desync.

### Validation
- Submit a request and complete checkout.
- Verify webhook updates order status.
- Verify notification is sent.
- Verify admin-only access.

## Additional Project Pages

### Decisions
- Add `shes-bar`, `nalorized-creations`, `shems-cards-and-invitations`, and `naylor-photobooth` as project pages under Other Websites.
- Each page has its own content template and overlay chat.
- Each page is login-required and uses a page-specific system prompt and locked model.
- Additional pages can be added later through `pages.py`.

### Affected Files
- `Syntatic/pages.py`
- `Syntatic/templates/pages/other-websites/shes-bar.html` (new)
- `Syntatic/templates/pages/other-websites/nalorized-creations.html` (new)
- `Syntatic/templates/pages/other-websites/shems-cards-and-invitations.html` (new)
- `Syntatic/templates/pages/other-websites/naylor-photobooth.html` (new)

### Routes
- `GET /pages/other-websites/<slug>`

### Implementation Steps
1. Add page entries and templates.
2. Add page-specific prompts and model config.
3. Reuse shared overlay chat.
4. Add navigation links from group page.

### Risks
- Page content and branding need manual authoring.
- Overlay prompts must be reviewed per page.

### Validation
- Load each page and verify content.
- Verify overlay chat works.
- Verify page navigation.

## Stripe Payments

### Decisions
- Stripe checkout sessions are generated server-side in Python.
- Use one generic `orders` table for all purchase types.
- Products and prices are configured in Supabase and can be added over time.
- Orbitix has no payments initially, but can use the same order model later.
- Webhooks fulfill orders and update status.

### Affected Files
- `Syntatic/payments.py` (new)
- `Syntatic/templates/checkout.html` (new)
- `Syntatic/static/gold_violet.css`

### Routes
- `POST /api/checkout`
- `POST /api/stripe/webhook`
- `GET /orders`

### Data Model (Supabase)
`products`:
- `id` uuid primary key
- `name` text not null
- `description` text
- `price_cents` integer not null
- `currency` text default 'usd'
- `active` boolean default true
- `created_at` timestamptz default now()

`orders`:
- `id` uuid primary key
- `user_id` uuid references users(id)
- `product_id` uuid references products(id)
- `product_type` text not null
- `status` text default 'pending'
- `stripe_session_id` text
- `stripe_payment_intent_id` text
- `amount_cents` integer not null
- `currency` text not null
- `created_at` timestamptz default now()
- `updated_at` timestamptz default now()

### Implementation Steps
1. Add Stripe configuration from environment.
2. Implement checkout session creation.
3. Implement webhook verification and fulfillment.
4. Add orders history page.
5. Add product management entries.
6. Reuse order flow for custom bot requests.

### Risks
- Webhook endpoint must be public and verified.
- Payment state and order state can desync.
- Product pricing changes need careful handling.

### Validation
- Create checkout and complete test payment.
- Verify webhook updates order.
- Verify orders history.
- Test failed/canceled checkout handling.

## Additional Features

### Decisions
- Add an admin dashboard for orders, users, and uptime.
- Add audit logging for config and payment changes.
- Add global search across pages and items.
- Add notification preferences in settings.
- Add backups/export for user data.
- Add analytics events for page views and purchases.

### Affected Files
- `Syntatic/admin.py` (new)
- `Syntatic/templates/admin/dashboard.html` (new)
- `Syntatic/analytics.py` (new)

### Routes
- `GET /admin`
- `GET /admin/users`
- `GET /admin/orders`
- `GET /admin/uptime`
- `POST /api/analytics/event`

### Data Model (Supabase)
`audit_logs`:
- `id` uuid primary key
- `user_id` uuid references users(id)
- `action` text not null
- `target_type` text
- `target_id` text
- `created_at` timestamptz default now()

`analytics_events`:
- `id` uuid primary key
- `user_id` uuid references users(id)
- `event_name` text not null
- `metadata` jsonb
- `created_at` timestamptz default now()

### Implementation Steps
1. Add admin-only dashboard.
2. Add audit logging to config and payment actions.
3. Add analytics event endpoint.
4. Add user data export.
5. Add notification preference settings.

### Risks
- Admin routes require strict authorization.
- Analytics can grow quickly and need retention.
- Audit logs must not store secrets.

### Validation
- Verify admin access restrictions.
- Verify audit entries are created.
- Verify analytics events are stored.
- Verify data export.
