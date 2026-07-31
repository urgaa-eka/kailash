# Technical Requirements Document — Kailash-Ai Web Application

## 1. Document Control

| Field | Value |
|---|---|
| **Document title** | Technical Requirements Document — Kailash-Ai Web Application |
| **Product** | Kailash — Go4Garage internal ML/AI platform |
| **Surface** | Web application (browser client) — `frontend/` in the Kailash repository |
| **Document type** | TRD (Application level) |
| **Version** | 1.0 |
| **Date** | 2026-07-31 |
| **Status** | Draft |
| **Owner** | TBD |
| **Author** | Go4Garage Documentation Workstream |
| **Reviewers** | TBD (Frontend Lead, Security, SRE) |
| **Approvers** | TBD |
| **Classification** | Internal — Proprietary |
| **Companion BRD** | `BRD_web_app_kailash_ai.md` (same directory) |
| **Parent product BRD** | `../BRD_kailash_ai.md` |
| **Parent product TRD** | `../TRD_kailash_ai.md` |
| **Source of truth** | `C:\Go4Garage( Eka)\Kailash-Ai\frontend`, HEAD commit `40cca17` dated 2026-07-31 |

### 1.1 Revision History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0 | 2026-07-31 | Documentation Workstream | Initial draft, derived from `package.json`, `App.js`, `firebase.json` and the on-disk build output |

---

## 2. System / Architecture Overview

### 2.1 Shape

The Kailash web application is a **client-rendered React 19 single-page application** compiled to static assets and served from a CDN. It holds no server-side runtime of its own: every dynamic behaviour is an HTTPS call to the Kailash FastAPI backend. Authentication state is a JWT bearer token; authorisation is enforced server-side and mirrored client-side purely for ergonomics.

Three architectural properties define it:

1. **Static-first delivery.** The production output is a hashed asset bundle plus an `index.html` shell, published to Firebase Hosting with a catch-all rewrite so any deep link resolves to the shell and is routed client-side by React Router.
2. **Server state versus client state separation.** TanStack Query owns everything fetched from the backend (caching, refetch, invalidation); Zustand owns purely local UI state. This keeps the API the single source of truth.
3. **Primitive-based composition.** All interactive UI is composed from Radix UI primitives styled with Tailwind utility classes via `class-variance-authority`, rather than from a heavyweight component framework.

### 2.2 Component diagram

```
  ┌────────────────────────────────────────────────────────────────────────────────┐
  │                              USER'S BROWSER                                    │
  │                                                                                │
  │  ┌──────────────────────────────────────────────────────────────────────────┐  │
  │  │  index.html shell  →  hashed JS/CSS from /static/**                       │  │
  │  └──────────────────────────────────┬───────────────────────────────────────┘  │
  │                                     ▼                                          │
  │  ┌──────────────────────────────────────────────────────────────────────────┐  │
  │  │  REACT 19 APPLICATION  (src/App.js)                                       │  │
  │  │                                                                           │  │
  │  │  ┌─────────────────────┐   ┌──────────────────────────────────────────┐  │  │
  │  │  │ ROUTER              │   │ PROVIDERS                                │  │  │
  │  │  │ react-router-dom 7  │   │ QueryClientProvider (TanStack Query 4)   │  │  │
  │  │  │ ~21 auth routes     │   │ ThemeProvider (next-themes)              │  │  │
  │  │  │ ~35 policy routes   │   │ Auth/session context (src/context/)      │  │  │
  │  │  │ redirects           │   │ Toaster (sonner)                         │  │  │
  │  │  └──────────┬──────────┘   └──────────────────────────────────────────┘  │  │
  │  │             │                                                             │  │
  │  │  ┌──────────▼──────────────────────────────────────────────────────────┐ │  │
  │  │  │ PAGES  src/pages/  (~70 modules)                                    │ │  │
  │  │  │  ── OPERATIONAL ──────────────────────────────────────────────────  │ │  │
  │  │  │  LoginPage · SpiritualKailashDashboard · Departments ·              │ │  │
  │  │  │  DepartmentDetailNew · GaneshaAI · GaneshaChatV2 · Chat ·           │ │  │
  │  │  │  GaneshaAnalytics · Guardians · Tasks · GapsTasksManagement ·       │ │  │
  │  │  │  Analytics · Reports · KnowledgeBase · Users · Settings ·           │ │  │
  │  │  │  AutomobilePricing · ExecutiveDashboard ·                           │ │  │
  │  │  │  InvestorExecutiveDashboard · GSTWebsite · IgnitionApp · Urjaa ·    │ │  │
  │  │  │  TattoosTool · ApplicationsHub                                      │ │  │
  │  │  │  ── POLICY CORPUS (~35) ──────────────────────────────────────────  │ │  │
  │  │  │  PrivacyPolicy · TermsAndConditions · CookiePolicy · GDPR · CCPA ·  │ │  │
  │  │  │  DataRetention · DataBreach · DataTransfer · SubprocessorList ·     │ │  │
  │  │  │  UserRights · SLA · SecurityPolicy · IncidentResponse · PenTest ·   │ │  │
  │  │  │  BugBounty · AccessibilityStatement · Compliance · Transparency ·   │ │  │
  │  │  │  Ethics · CodeOfConduct · … (see Appendix)                          │ │  │
  │  │  └──────────┬──────────────────────────────────────────────────────────┘ │  │
  │  │             │                                                             │  │
  │  │  ┌──────────▼───────────┐  ┌───────────────┐  ┌────────────────────────┐ │  │
  │  │  │ COMPONENTS           │  │ STORES        │  │ SERVICES               │ │  │
  │  │  │ Radix UI (26 pkgs)   │  │ zustand 5     │  │ axios API layer        │ │  │
  │  │  │ + Tailwind + CVA     │  │ UI/local state│  │ src/services/          │ │  │
  │  │  │ framer-motion        │  └───────────────┘  └───────────┬────────────┘ │  │
  │  │  │ three + r3f + drei   │  ┌───────────────┐              │              │  │
  │  │  │ lucide-react icons   │  │ HOOKS / LIB   │              │              │  │
  │  │  │ react-hook-form+zod  │  │ src/hooks/    │              │              │  │
  │  │  │ sonner toasts        │  │ src/lib/      │              │              │  │
  │  │  └──────────────────────┘  └───────────────┘              │              │  │
  │  └────────────────────────────────────────────────────────────┼─────────────┘  │
  └───────────────────────────────────────────────────────────────┼────────────────┘
                                                                  │
                          HTTPS · Authorization: Bearer <JWT>     │
                          JSON · ApiResponse envelope             │
                                                                  ▼
  ┌────────────────────────────────────────────────────────────────────────────────┐
  │  FIREBASE HOSTING (static delivery)          NGINX → KAILASH FastAPI BACKEND   │
  │  project kailash-38268                       api.kailash-ai.in                  │
  │  public: build/                              TLS · rate limit 30 r/s (5 r/s     │
  │  rewrite ** → /index.html                    on auth) · proxy to 127.0.0.1:8000 │
  │  /static/** immutable 1y cache                                                  │
  │  security headers on /**                     MongoDB · PostgreSQL · Redis       │
  └────────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 Rendering and navigation model

- **Entry.** `src/index.js` mounts `App.js` into the shell.
- **Routing.** `react-router-dom` 7.5.1 declares the route table in `App.js`. Deep links work because Firebase Hosting rewrites every unmatched path to `/index.html`.
- **Guarding.** Operational routes are wrapped in a protected-route element; unauthenticated access redirects to `/`. Policy routes are declared outside the guard and render publicly.
- **Redirects.** `/dashboard` and `/applications` both redirect to `/kailash`, preserving older bookmarks.
- **Data.** Pages request data through the Axios-based service layer; TanStack Query caches by key, dedupes in-flight requests and handles refetch on focus.
- **Theme.** `next-themes` toggles a class on the document root; Tailwind's dark variant does the rest.

---

## 3. Technology Stack

### 3.1 Core

| Concern | Technology | Version | Notes |
|---|---|---|---|
| UI library | **React** | 19.0.0 | With `react-dom` 19.0.0 |
| Build | **react-scripts (CRA)** wrapped by **CRACO** | 5.0.1 / 7.1.0 | Scripts: `craco start`, `craco build`, `craco test` |
| Routing | **react-router-dom** | 7.5.1 | Client-side routing for all routes |
| Server state | **@tanstack/react-query** | 4.42.0 | Fetch caching, invalidation, retries |
| Client state | **zustand** | 5.0.8 | Local/UI state stores under `src/stores/` |
| HTTP | **axios** | 1.8.4 | Service layer under `src/services/` |
| Package manager | **yarn** | 1.22.22 | Declared via `packageManager` field |

### 3.2 UI and styling

| Concern | Technology | Version |
|---|---|---|
| Styling | **Tailwind CSS** | 3.4.17 |
| Tailwind utilities | `tailwindcss-animate` 1.0.7, `tailwind-merge` 3.2.0, `class-variance-authority` 0.7.1, `clsx` 2.1.1 | — |
| CSS pipeline | **PostCSS** 8.4.49, **autoprefixer** 10.4.20 | — |
| Primitives | **Radix UI** — accordion, alert-dialog, aspect-ratio, avatar, checkbox, collapsible, context-menu, dialog, dropdown-menu, hover-card, label, menubar, navigation-menu, popover, progress, radio-group, scroll-area, select, separator, slider, slot, switch, tabs, toast, toggle, toggle-group, tooltip (26 packages) | 1.x / 2.x |
| Icons | **lucide-react** | 0.507.0 |
| Animation | **framer-motion** | 12.23.24 |
| 3D / visualisation | **three** 0.160.0, **@react-three/fiber** 8.15.0, **@react-three/drei** 9.100.0 | — |
| Command palette | **cmdk** | 1.1.1 |
| Carousel | **embla-carousel-react** | 8.6.0 |
| Drawer | **vaul** | 1.1.2 |
| Resizable panels | **react-resizable-panels** | 3.0.1 |
| OTP input | **input-otp** | 1.4.2 |
| Toasts | **sonner** | 2.0.3 |
| Theming | **next-themes** | 0.4.6 |
| Dates | **date-fns** 4.1.0, **react-day-picker** 8.10.1 | — |

### 3.3 Forms and validation

| Concern | Technology | Version |
|---|---|---|
| Form state | **react-hook-form** | 7.56.2 |
| Schema validation | **zod** | 3.24.4 |
| Bridge | **@hookform/resolvers** | 5.0.1 |

### 3.4 Platform SDK and tooling

| Concern | Technology | Version |
|---|---|---|
| Firebase client SDK | **firebase** | 11.7.1 |
| Linting | **eslint** 9.23.0, `@eslint/js` 9.23.0, `eslint-plugin-react` 7.37.4, `eslint-plugin-import` 2.31.0, `eslint-plugin-jsx-a11y` 6.10.2, `globals` 15.15.0 | — |
| Browser automation (dev) | **puppeteer** | 24.33.1 |
| Babel plugin | `@babel/plugin-proposal-private-property-in-object` | 7.21.11 |

### 3.5 Explicitly not used

No server-side rendering framework (no Next.js, no Remix). No CSS-in-JS runtime. No Redux. No GraphQL client. No service worker or PWA tooling. No native wrapper (no Capacitor, Cordova, React Native Web or Electron).

---

## 4. Functional Requirements

| ID | Requirement | Acceptance criteria |
|---|---|---|
| **WFR-1** | **Route table.** The application shall declare the full route table in `App.js`, comprising roughly 21 authenticated operational routes, roughly 35 public policy routes, and redirects from `/dashboard` and `/applications` to `/kailash`. Every route shall render a component; no route shall 404 within the app shell. | Programmatically visit every declared route; each renders a component tree; the two redirects resolve to `/kailash`. |
| **WFR-2** | **Deep-link resolution.** Any declared route shall be reachable by direct URL entry or refresh, resolved through the hosting rewrite to `/index.html` and then client-routed. | Load each route by direct URL and hard refresh; no hosting-level 404. |
| **WFR-3** | **Route protection.** Operational routes shall be wrapped in an authentication guard that redirects unauthenticated users to `/`, preserving the intended destination for post-login redirect. Policy routes shall render without a session. | Clear storage, request an operational route — redirected to `/`; log in — landed on the originally requested route. Request a policy route with no session — renders. |
| **WFR-4** | **Session handling.** The client shall obtain a JWT from the backend auth endpoint, attach it as `Authorization: Bearer <token>` on every authenticated request via an Axios interceptor, and on a 401 response shall clear the session and redirect to login rather than retrying indefinitely. | Expire or corrupt the token; the next request produces a clean redirect to login with a user-visible message, not a retry loop. |
| **WFR-5** | **Two-factor challenge.** Where the account has 2FA enabled, the login flow shall present an OTP entry step (the `input-otp` component is available) and accept either a TOTP code or a backup code. | 2FA-enabled login presents the OTP step; a valid code completes login; an invalid code shows an inline error without losing form state. |
| **WFR-6** | **Role-aware rendering.** Navigation items and action controls shall be rendered conditionally on the signed-in user's role and permissions, matching the backend's five-role model. Client-side gating is ergonomic only; it shall not be relied on for security. | For each role, the rendered control set contains no control whose backend call would return an authorisation error. |
| **WFR-7** | **Server-state management.** All backend data shall be fetched through TanStack Query with stable query keys, so that identical concurrent requests are deduped, responses are cached, and mutations invalidate the affected keys. | Two components requesting the same resource produce one network call; a mutation causes dependent views to refresh without a manual reload. |
| **WFR-8** | **Asynchronous state contract.** Every data-driven view shall implement three explicit states: loading (skeleton or spinner with context), empty (an explanatory message, not a blank panel), and error (a message plus a retry affordance). | Force each of the three conditions per major view; all three render distinctly. |
| **WFR-9** | **Form handling.** All user input forms shall use React Hook Form with Zod schema validation, showing inline field-level errors, disabling submit during in-flight requests, and preserving entered values on a failed submission. | Submit each form with invalid data (inline errors, values preserved), with valid data (success toast, state updated), and during a simulated backend failure (error surfaced, values preserved). |
| **WFR-10** | **Notification pattern.** Success, warning and error feedback shall be delivered through the `sonner` toaster with consistent placement, duration and severity styling. | Trigger one of each; verify consistency across at least five different pages. |
| **WFR-11** | **Theming.** The application shall support light and dark themes via `next-themes`, persist the user's choice, respect the system preference on first visit, and render every page correctly in both. | Toggle the theme; reload; the choice persists. Visually inspect a representative page sample in both themes — no unreadable contrast. |
| **WFR-12** | **Department views.** The departments list shall render every department returned by the backend registry, and `/department/:name` shall resolve for each name case-insensitively, rendering a not-found state for unknown names. | List count matches the backend; each detail route loads; an invented name shows the not-found state without a console error. |
| **WFR-13** | **Conversational surfaces.** GANESHA v1, GANESHA v2 and the general chat view shall each submit a prompt, display the composed response, indicate which departments were engaged, and list prior conversations retrieved from the backend. | Submit a prompt on each surface; the response and department attribution render; reload and the conversation persists. |
| **WFR-14** | **Untrusted content rendering.** All model-generated content shall be rendered as text or through a sanitising renderer. `dangerouslySetInnerHTML` shall not be used on any backend- or model-derived content. | Static analysis finds no `dangerouslySetInnerHTML` on model output; a crafted response containing script markup renders inert. |
| **WFR-15** | **Analytics and reports.** Analytics and report views shall support filtering by department and date range, and shall render consistent figures for the same filter across reloads. | Apply filters; figures change coherently; the same filter reproduces the same result. |
| **WFR-16** | **Executive surfaces.** The executive and investor dashboards shall render every tile with either a real value or an explicit "no data" state, never an indefinite loading state. | Load both against an empty dataset and a seeded dataset; verify tile behaviour in both. |
| **WFR-17** | **Responsive layout.** Layouts shall adapt across the defined breakpoints (§5.2) using Tailwind's responsive utilities, with no horizontal overflow of primary content at any supported width and dense tables degrading to a scroll container or card layout below 1024 px. | Render every major view at 1920, 1440, 1280, 1024, 768, 414 and 360 px; check for overflow and clipped controls. |
| **WFR-18** | **Accessibility implementation.** Interactive elements shall be keyboard-operable with a visible focus indicator, have accessible names, use Radix primitives' built-in ARIA semantics rather than hand-rolled equivalents, and expose landmark structure. `eslint-plugin-jsx-a11y` findings shall be treated as errors. | Keyboard-only traversal of the top five journeys succeeds; an automated axe scan of a representative sample reports no Level AA violations. |
| **WFR-19** | **Static build output.** `yarn build` shall produce a deployable bundle in `frontend/build/` containing `index.html`, `asset-manifest.json`, content-hashed assets under `static/`, and the brand assets, with no source maps containing proprietary source published to production. | Inspect the build output; confirm hashed filenames; confirm production source-map policy. |
| **WFR-20** | **Configuration by environment.** The backend base URL and any client-side Firebase configuration shall come from build-time environment variables, not hard-coded values, so the same source builds for local, preview and production. | Change the backend base URL variable and rebuild; the bundle targets the new host with no code edit. |
| **WFR-21** | **No secrets in the client.** The bundle shall contain no AI provider key, no service-account credential, no database connection string and no internal platform token. | Grep the built bundle and source maps for credential patterns; inspect network payloads and browser storage after a full session. Zero findings. |
| **WFR-22** | **Preview and production deployment.** `yarn firebase:preview` shall publish a preview channel and `yarn firebase:deploy` shall publish to production, each building first. | Execute both; the preview URL serves the change; production updates; the previous release remains rollback-able through Firebase Hosting release history. |

---

## 5. Non-Functional Requirements

### 5.1 Performance

| ID | Requirement | Measurement |
|---|---|---|
| WNFR-P1 | First Contentful Paint under **2 s** on a 10 Mbps connection with a mid-range laptop profile. | Lighthouse against production |
| WNFR-P2 | Time to Interactive under **4 s** under the same conditions. | Lighthouse |
| WNFR-P3 | Lighthouse performance score **85 or better** (desktop profile). | Lighthouse |
| WNFR-P4 | Main JavaScript bundle (excluding lazily-loaded chunks) under **500 KB gzipped**; a CI budget shall fail builds that exceed it without written justification. | Bundle analysis in CI |
| WNFR-P5 | Heavy dependencies — `three`, `@react-three/fiber`, `@react-three/drei`, `framer-motion`-heavy surfaces and video-bearing pages — shall be **lazily loaded** and shall not appear in the initial chunk. | Bundle analysis; confirm dynamic import boundaries |
| WNFR-P6 | Hashed static assets shall be served with `Cache-Control: public, max-age=31536000, immutable`; `index.html` shall not be long-cached, so a deploy is picked up on next navigation. | Inspect response headers |
| WNFR-P7 | Brand video assets shall never block first paint; they shall be lazily loaded, `preload="none"`, and use the optimised variant where available. | Network waterfall inspection |
| WNFR-P8 | Cumulative Layout Shift under **0.1**; skeleton placeholders shall reserve final layout dimensions. | Lighthouse / field data |

### 5.2 Browser support and responsive matrix

**Browser matrix**

| Browser | Versions | Support |
|---|---|---|
| Chrome (desktop) | Current, current−1 | Full — primary development target |
| Edge (Chromium) | Current, current−1 | Full |
| Firefox | Current, current−1 | Full |
| Safari (macOS) | Current, current−1 | Full |
| Safari (iOS/iPadOS) | Current, current−1 | Read journeys and core actions |
| Chrome (Android) | Current | Read journeys and core actions |
| Internet Explorer / Opera Mini | Any | **Not supported** |

This matrix is consistent with the declared production browserslist (`>0.2%`, `not dead`, `not op_mini all`) and the development browserslist (`last 1 chrome version`, `last 1 firefox version`, `last 1 safari version`).

**Responsive breakpoints** (Tailwind defaults, as configured)

| Token | Min width | Class of device | Requirement |
|---|---|---|---|
| base | 0 px | Small phone (360 px reference) | Readable, navigable, no horizontal overflow of primary content |
| `sm` | 640 px | Large phone | Single-column layouts; primary actions reachable |
| `md` | 768 px | Tablet portrait | All read journeys complete; dense tables collapse to cards or scroll containers |
| `lg` | 1024 px | Laptop / landscape tablet | Full functionality; multi-column layout begins |
| `xl` | 1280 px | Desktop | Full multi-panel layout |
| `2xl` | 1536 px and above | Large desktop (1920 px reference) | Full layout with constrained max content width |

### 5.3 Security

| ID | Requirement |
|---|---|
| WNFR-S1 | All traffic over HTTPS; Firebase Hosting enforces TLS for the static origin and the backend is reached only over HTTPS. |
| WNFR-S2 | Security headers on every hosted response, as configured in `firebase.json`: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1; mode=block`, `Referrer-Policy: strict-origin-when-cross-origin`, and `Permissions-Policy: camera=(), microphone=(self), geolocation=()`. |
| WNFR-S3 | A Content Security Policy shall be added, restricting `script-src`, `connect-src` (backend origin plus Firebase endpoints only), `img-src` and `frame-ancestors 'none'`. *(Not currently present in `firebase.json` — see §11.)* |
| WNFR-S4 | No secret of any kind in the bundle, source maps, or client storage (WFR-21). The client never holds an AI provider key or the internal platform token. |
| WNFR-S5 | The JWT shall be stored with the shortest practical exposure, cleared on logout and on 401, and never written to a URL, log or analytics payload. |
| WNFR-S6 | All model output and all backend-supplied strings are treated as untrusted and rendered as text or sanitised (WFR-14). |
| WNFR-S7 | Dependency vulnerabilities shall be scanned in CI; critical advisories in production dependencies shall block release. |
| WNFR-S8 | The backend's CORS allow-list shall include only the app's real origins (`kailash-ai.in`, `www.kailash-ai.in`, `kailash-38268.web.app`, `kailash-38268.firebaseapp.com`); the client shall never require a wildcard origin. |
| WNFR-S9 | Client-side role gating is presentation only; every gated action shall be independently rejected by the backend when attempted directly. |
| WNFR-S10 | The `Permissions-Policy` allows microphone to `self` (for voice input) but denies camera and geolocation; any new permission requirement needs a documented justification and a header change. |

### 5.4 Availability

| ID | Requirement |
|---|---|
| WNFR-A1 | Static assets served from the Firebase Hosting CDN; target availability **99.9%** for asset delivery. |
| WNFR-A2 | The application shell shall load even when the backend is unreachable, presenting an explicit "backend unavailable" state rather than a blank page. |
| WNFR-A3 | Failed API requests shall retry with exponential backoff a bounded number of times (TanStack Query defaults tuned), then surface an error state with a manual retry. |
| WNFR-A4 | Deployments shall be atomic and instantly reversible through Firebase Hosting release history; rollback target under **15 minutes**. |
| WNFR-A5 | Because `index.html` is not long-cached, a deployed fix reaches users on their next navigation without a forced cache purge. |

### 5.5 Accessibility and compliance

| ID | Requirement |
|---|---|
| WNFR-C1 | **WCAG 2.1 Level AA** target for the operational surface and the policy corpus: contrast ratios, keyboard operability, visible focus, accessible names, landmark structure, and respect for reduced-motion preferences (relevant given Framer Motion and Three.js usage). |
| WNFR-C2 | The published **accessibility statement** page shall accurately describe the current conformance position, including known gaps. |
| WNFR-C3 | **Data residency:** the client stores no personal data beyond the session token and UI preferences. Any client-side persistence of platform data shall be documented in the data-retention policy. |
| WNFR-C4 | **GST/HSN:** the automobile pricing view shall display the HSN code and GST rate used in a computation, and shall never present a derived price without its tax basis. |
| WNFR-C5 | **DISCOM/energy:** where charger or energy figures are displayed, measured and forecast values shall be visually distinguished and forecasts labelled as such. |
| WNFR-C6 | **Cookies and tracking:** the app shall not set non-essential cookies or load third-party trackers without the consent mechanism described in the cookie policy. |
| WNFR-C7 | **SEO scope:** policy pages shall carry correct `title`, `description` and Open Graph tags and be indexable; authenticated operational routes shall be excluded from indexing via `robots` directives. |

### 5.6 Maintainability

| ID | Requirement |
|---|---|
| WNFR-M1 | ESLint (react, import, jsx-a11y) shall pass with zero errors; a11y findings shall be errors, not warnings. |
| WNFR-M2 | New UI shall compose existing Radix-plus-Tailwind primitives from `src/components/`; introducing a new UI dependency requires justification. |
| WNFR-M3 | API access shall go through the `src/services/` layer; components shall not call Axios directly. |
| WNFR-M4 | Page modules shall stay under a reasonable size, extracting shared logic into `src/hooks/` and `src/lib/`. |
| WNFR-M5 | The `yarn.lock` file shall be committed and CI shall install with a frozen lockfile. |

---

## 6. Data Model / Storage

### 6.1 The client owns no durable data

The web app is a **stateless view over backend state**. It persists nothing authoritative. All entities — users, departments, tasks, activities, conversations, knowledge, analytics — live in the backend datastores described in `../TRD_kailash_ai.md` §6.

### 6.2 Client-side storage inventory

| Storage | Contents | Lifetime | Sensitivity |
|---|---|---|---|
| **Session/local storage** | JWT session token; possibly the user profile summary for display | Until logout, expiry or 401 | **High** — cleared on logout and on any 401 |
| **Local storage** | Theme preference (`next-themes`) | Persistent | None |
| **Local storage** | UI preferences (collapsed panels, table density, last-selected filters) via Zustand persistence where used | Persistent | Low |
| **In-memory** | TanStack Query cache of fetched server state | Tab lifetime | Medium — never serialised to disk |
| **In-memory** | Zustand UI state | Tab lifetime | None |
| **HTTP cache** | Hashed static assets | One year (immutable) | None |
| **Cookies** | None required by the application itself | — | — |

### 6.3 Data-shape contract

The client consumes the backend's `ApiResponse` envelope and must handle the error envelope `{ ok: false, error: { code, message, hint }, request_id }`. Requirements:

- The client shall branch on `error.code`, not on the human-readable `message`, so message wording can change without breaking behaviour.
- The client shall surface `request_id` in error displays (or at least in the console/error report) so a user can quote it to support and it can be correlated with backend logs.
- Response payloads shall be validated at the boundary with Zod schemas mirroring the backend contract, so that a field rename produces a caught, reported validation failure rather than a silently blank UI (see WR-1 in the companion BRD).

### 6.4 Caching policy

| Data class | Strategy |
|---|---|
| Reference data (departments, roles, permissions) | Long `staleTime`; invalidate on explicit refresh |
| Operational lists (tasks, activities) | Short `staleTime`; refetch on window focus; invalidate on mutation |
| Analytics aggregates | Medium `staleTime` keyed by filter parameters |
| Conversations | Cached per conversation; appended optimistically on send, reconciled on response |
| User profile / session | Fetched once per session; invalidated on role or profile change |

---

## 7. API & Integration Points

### 7.1 Primary integration — the Kailash backend

The web app's only functional dependency is the Kailash FastAPI backend.

| Aspect | Detail |
|---|---|
| Base URL | Build-time environment variable; production `https://api.kailash-ai.in`, local `http://localhost:8000` |
| Transport | HTTPS, JSON |
| Auth | `Authorization: Bearer <JWT>` (HS256, 24-hour lifetime) |
| Correlation | Optional `x-request-id` on request; echoed on response |
| Envelope | `ApiResponse` on success; typed error envelope on failure |
| Client | Axios 1.8.4 with request/response interceptors in `src/services/` |
| CORS | Backend allow-list includes the production and Firebase hosting origins |

**Consumed router families:** auth, users, rbac, departments, department_intelligence, tasks, gaps_tasks_crud, analytics, dashboard, conversations, knowledge, knowledge_base, live_data, guardians, ganesha (v1, multimodel, orchestrator, v2), shiv_auto_rectify, scheduler_api, system_health, simple_health, automobile.

### 7.2 Firebase integration

| Aspect | Detail |
|---|---|
| SDK | `firebase` 11.7.1 (client) |
| Hosting | Project `kailash-38268`; `public: build`; catch-all rewrite to `/index.html`; caching and security headers as configured |
| Domains | `kailash-38268.web.app`, `kailash-38268.firebaseapp.com`, and the custom domains `kailash-ai.in` / `www.kailash-ai.in` per the backend allow-list |
| Deployment | `yarn firebase:deploy` (production), `yarn firebase:preview` (preview channel) |
| Scope note | The Firebase **Admin** SDK is a backend concern (`FIREBASE_PROJECT_ID`, `FIREBASE_STORAGE_BUCKET`, service-account credentials) and is not exposed to the browser. |

### 7.3 Third-party integrations NOT present in the web client

The following were checked and **not found** in the frontend, and must not be assumed:

| Integration | Status |
|---|---|
| Payment gateway (Razorpay, Stripe, PayU, or any other) | **Absent.** Kailash has no billing surface anywhere. |
| SMS or voice provider called from the browser | **Absent.** Speech capability is a backend service; the client never calls a telephony provider directly. |
| Slack or any chat-ops integration | **Absent.** |
| Push notification service (FCM web push, OneSignal) | **Absent.** No service worker exists, so web push is not possible in the current build. |
| Product analytics (GA4, Mixpanel, PostHog, Amplitude) | **Absent.** No usage instrumentation was found. |
| Error tracking (Sentry, Rollbar, Bugsnag) | **Absent.** No client-side error reporting was found. |
| Session replay / heatmaps | **Absent.** |
| Any direct AI provider call from the browser | **Absent, and correctly so.** All model access is proxied through the backend, so no vendor key is ever exposed client-side. |
| `KAILASH_AI_URL`-style cross-product internal integration | **Not applicable to the client.** That contract is how *other Go4Garage products* reach the Kailash backend; the browser client reaches the same backend directly with its own base-URL variable. |

### 7.4 Asset delivery

Brand assets ship with the build: `favicon.png`, `og-image.png`, `og-image.svg`, `og-background.jpg`, and three video files (`kailash_intro_video.mp4`, `kailash_video_hd.mp4`, `kailash_video_optimized.mp4`). Requirements: video is lazily loaded and never blocks first paint; the optimised variant is preferred; the HD variant is served only on explicit user action or a large-viewport condition.

---

## 8. Infrastructure & Deployment

### 8.1 Build

| Step | Command | Output |
|---|---|---|
| Install | `yarn install` (frozen lockfile in CI) | `node_modules/` |
| Develop | `yarn start` (`craco start`) | Dev server with HMR |
| Build | `yarn build` (`craco build`) | `frontend/build/` — `index.html`, `asset-manifest.json`, hashed `static/`, brand assets |
| Test | `yarn test` (`craco test`) | Wired but no meaningful suite exists today (§11) |
| Lint | ESLint 9 with react/import/jsx-a11y | — |

### 8.2 Hosting configuration (`frontend/firebase.json`)

```
hosting:
  public: "build"
  ignore: ["firebase.json", "**/.*", "**/node_modules/**"]
  rewrites:
    - source: "**"          → destination: "/index.html"     # SPA deep links
  headers:
    - source: "/static/**"  → Cache-Control: public, max-age=31536000, immutable
    - source: "/**"         → X-Content-Type-Options: nosniff
                              X-Frame-Options: DENY
                              X-XSS-Protection: 1; mode=block
                              Referrer-Policy: strict-origin-when-cross-origin
                              Permissions-Policy: camera=(), microphone=(self), geolocation=()
```

### 8.3 Deployment flow

| Path | Mechanism |
|---|---|
| Manual production | `yarn firebase:deploy` — builds then `firebase deploy --only hosting` |
| Manual preview | `yarn firebase:preview` — builds then `firebase hosting:channel:deploy preview`, producing a shareable preview URL |
| Automated | `.github/workflows/deploy-frontend.yml` |
| Verification | `.github/workflows/ci.yml` `frontend` job runs `yarn install` and `yarn build` on every push and pull request |
| Rollback | Firebase Hosting release history — re-activate the prior release |

### 8.4 Environments

| Environment | Serving | Backend target | Status |
|---|---|---|---|
| Local development | `craco start` dev server | `http://localhost:8000` (or a Compose backend) | **Working** — `node_modules/` installed |
| Preview channel | Firebase Hosting preview URL | Production or staging backend | Script exists; usage not verified from this copy |
| Production | Firebase Hosting, project `kailash-38268` | `https://api.kailash-ai.in` | Configuration exists; **live status not verified from this copy** |

### 8.5 What is actually deployed versus not

Being precise, because the parent documents make the same distinction:

- **Built locally: yes.** `frontend/build/` exists with a full compiled asset set, and `node_modules/` is populated with roughly 1,000 packages. The application has demonstrably been installed and built on this machine.
- **Hosting configured: yes.** `firebase.json` is complete and production-shaped, and deploy scripts exist in `package.json`.
- **Currently live: unverified.** Nothing in this working copy proves that `kailash-ai.in` or `kailash-38268.web.app` is currently serving. The backend `.env.example` lists those origins in its CORS allow-list, which indicates intent, not a running deployment.
- **Backend dependency: not verified live.** The app is useless without a reachable backend at the configured base URL; whether `api.kailash-ai.in` is up was not confirmed.

### 8.6 PWA position

The application is **not** a Progressive Web App: there is no service worker, no web app manifest and no install flow, and consequently no offline capability and no web push. This is consistent with the user model (desk-bound staff on connected networks) but should be an explicit recorded decision rather than an omission. If PWA capability is later adopted, the minimum scope would be a manifest with icons and theme colour, a service worker caching the app shell and hashed static assets, an explicit offline read scope (last-known dashboard and department state, clearly labelled as stale), and a versioning strategy that avoids serving a stale shell after deploy.

---

## 9. Security & Compliance Requirements

### 9.1 Client security controls

| ID | Control |
|---|---|
| WSEC-1 | HTTPS only for both static delivery and backend calls. |
| WSEC-2 | Security headers enforced at the hosting layer (see WNFR-S2). |
| WSEC-3 | **Content Security Policy to be added**, restricting `default-src 'self'`, `connect-src` to the backend origin and Firebase endpoints, `frame-ancestors 'none'`, and eliminating inline script where the build permits. |
| WSEC-4 | JWT cleared on logout, on expiry and on any 401; never placed in a URL, log line or analytics payload. |
| WSEC-5 | No AI provider credential, service-account key or internal platform token in the bundle, source maps or client storage. |
| WSEC-6 | All model output and backend strings rendered as text or sanitised; no `dangerouslySetInnerHTML` on untrusted content. |
| WSEC-7 | External links rendered with `rel="noopener noreferrer"` when opened in a new context. |
| WSEC-8 | File uploads (where present) validated for type and size client-side as a usability measure, with the backend as the enforcement point. |
| WSEC-9 | Dependency vulnerability scanning in CI; critical advisories in production dependencies block release. |
| WSEC-10 | Production source maps either not published or access-restricted, to avoid disclosing proprietary source. |
| WSEC-11 | Microphone access (permitted to `self` by the Permissions-Policy) requested only on explicit user action, with a clear in-UI indication when active. |
| WSEC-12 | Client-side role gating never treated as an authorisation boundary. |

### 9.2 Compliance requirements specific to the web surface

| ID | Requirement |
|---|---|
| WSEC-13 | The policy corpus shall be publicly reachable at stable URLs, each carrying an effective date and an owning function. |
| WSEC-14 | The cookie policy shall accurately reflect what the app stores; if only essential storage is used, that shall be stated plainly rather than implying a consent regime that does not exist. |
| WSEC-15 | The accessibility statement shall reflect the real, measured conformance position including known gaps — not an aspirational claim. |
| WSEC-16 | The sub-processor list shall include Firebase Hosting (Google) as the static-hosting sub-processor, and any model providers reached via the backend on behalf of the user. |
| WSEC-17 | Where the UI displays GST-bearing amounts, the HSN code and rate used shall be shown alongside (WNFR-C4). |
| WSEC-18 | Where the UI displays energy or charger figures, forecast values shall be visually distinguished from measured values (WNFR-C5). |
| WSEC-19 | Authenticated routes shall be excluded from search indexing; policy routes shall be indexable. |
| WSEC-20 | No third-party tracker shall be added without a corresponding cookie-policy update and, where required, a consent mechanism. |

---

## 10. Testing Strategy

### 10.1 Test layers

| Layer | Tooling | Scope |
|---|---|---|
| Static analysis | ESLint 9 (react, import, jsx-a11y) | Correctness, import hygiene, accessibility rules |
| Type/schema safety at the boundary | Zod schemas at the API layer | Backend contract drift caught at runtime and in tests |
| Component tests | React Testing Library via `craco test` | Shared primitives, forms, state rendering |
| Integration tests | React Testing Library with a mocked API layer | Page-level behaviour: loading, empty, error, success |
| End-to-end | Puppeteer 24.33.1 (already a dev dependency) | Top journeys against a running backend |
| Accessibility | axe automated scan plus manual keyboard traversal | WCAG 2.1 AA |
| Performance | Lighthouse CI plus a bundle-size budget | FCP, TTI, CLS, bundle weight |
| Visual regression | Screenshot comparison (Puppeteer-based) | Consistency across roughly 70 pages in both themes |
| Cross-browser | Manual or cloud grid against the §5.2 matrix | Core journeys per browser |
| Build verification | CI `frontend` job (`yarn install` plus `yarn build`) | **This is the only frontend gate that exists today** |

### 10.2 Test requirements

| ID | Requirement |
|---|---|
| WTEST-1 | Every shared component in `src/components/` shall have a component test covering its states and keyboard interaction. |
| WTEST-2 | Every data-driven page shall have integration tests for all four states: loading, empty, error, populated. |
| WTEST-3 | Route-protection tests shall assert that each operational route redirects when unauthenticated and each policy route renders when unauthenticated. |
| WTEST-4 | Role-based rendering tests shall assert, for each of the five roles, that the rendered control set matches the permitted permission set. |
| WTEST-5 | API-contract tests shall validate every response shape against its Zod schema; a shape mismatch fails the build. |
| WTEST-6 | Error-handling tests shall cover 401 (clean redirect to login), 403 (authorisation message), 404 (not-found state), 5xx (retryable error state) and network failure (offline banner). |
| WTEST-7 | End-to-end journeys shall cover, at minimum: login (with and without 2FA); dashboard load; department list to department detail; GANESHA prompt to response; task create-assign-close; analytics filter; user administration; and one policy page load. |
| WTEST-8 | Accessibility scans shall run in CI on a representative page sample; Level AA violations fail the build. |
| WTEST-9 | Lighthouse CI shall enforce performance, accessibility and best-practice thresholds against a preview deployment. |
| WTEST-10 | A bundle-size budget shall fail builds exceeding the WNFR-P4 limit. |
| WTEST-11 | Responsive tests shall capture each major view at the seven reference widths and flag horizontal overflow. |
| WTEST-12 | A secret-scan step shall assert that no credential pattern appears in the built bundle. |
| WTEST-13 | Cross-browser journeys shall be executed before each release against the §5.2 matrix. |

### 10.3 Current gating reality

Today, CI runs `yarn install` and `yarn build` for the frontend and nothing else. **The bundle is verified to compile; it is not verified to behave.** Every requirement in §10.2 is therefore a gap to close, and WTEST-2, WTEST-5, WTEST-7 and WTEST-8 are the highest-value first steps.

---

## 11. Current Implementation Status

*Assessed 2026-07-31 against `C:\Go4Garage( Eka)\Kailash-Ai\frontend`, HEAD `40cca17`.*

### 11.1 Platform existence statement — WEB

> **The web application EXISTS in code and has been built locally.** It is a React 19 SPA at `Kailash-Ai/frontend/` with roughly 70 page modules, a complete route table, an installed `node_modules/` tree of roughly 1,000 packages, and a compiled production bundle in `frontend/build/`. It is the only human-facing Kailash client. No native iOS or Android client exists — see `../ios_app_kailash_ai/TRD_ios_app_kailash_ai.md` and `../android_app_kailash_ai/TRD_android_app_kailash_ai.md`.

### 11.2 Verified present

| Item | Evidence |
|---|---|
| React 19 application source | `frontend/src/` with `App.js`, `index.js`, `components/`, `pages/`, `services/`, `stores/`, `hooks/`, `context/`, `data/`, `lib/`, `styles/` |
| Roughly 70 page modules | `frontend/src/pages/` — operational views plus roughly 35 policy pages, with dedicated CSS for Analytics, Chat, Departments, DepartmentDetail, Executive, ExecutiveDashboard, GaneshaAI, GaneshaChat, GaneshaChatV2, Reports, Settings, Tasks, Urjaa, Users and LegalPages |
| Complete route table | `App.js` — roughly 21 authenticated routes, roughly 35 policy routes, redirects from `/dashboard` and `/applications` |
| Full dependency set | `package.json` — React 19, CRACO, Tailwind, 26 Radix packages, TanStack Query, Zustand, Axios, Framer Motion, Three.js stack, React Hook Form plus Zod, sonner, next-themes, firebase, lucide-react, date-fns, cmdk, embla, vaul, input-otp, react-resizable-panels |
| Installed dependencies | `frontend/node_modules/` — roughly 1,000 entries |
| Compiled production build | `frontend/build/` — `index.html`, `asset-manifest.json`, `static/`, `favicon.png`, `og-image.png`, `og-image.svg`, `og-background.jpg`, three MP4 brand videos |
| Hosting configuration | `frontend/firebase.json` — public dir, SPA rewrite, immutable static caching, five security headers |
| Deploy scripts | `firebase:deploy`, `firebase:preview` in `package.json` |
| CI build gate | `frontend` job in `.github/workflows/ci.yml`; `deploy-frontend.yml` present |
| Lint toolchain | ESLint 9.23.0 with react, import and jsx-a11y plugins |
| Browserslist targets | Production `>0.2%`, `not dead`, `not op_mini all`; development last-1 Chrome/Firefox/Safari |
| E2E-capable tooling | `puppeteer` 24.33.1 as a dev dependency |

### 11.3 Absent or unverified

| Item | Status |
|---|---|
| **Live deployment** | Not verified from this copy. Configuration and allow-listed origins exist; running status unknown. |
| **Frontend test suite** | `craco test` is wired; **no meaningful test files were found** under `frontend/src/`. The only frontend CI gate is that the bundle compiles. |
| **Content Security Policy** | **Not present** in `firebase.json`. Five other security headers are configured; CSP is the notable omission. |
| **Service worker / manifest / PWA** | **Absent.** No offline capability, no installability, no web push. |
| **Code splitting** | Not evidenced in the configuration reviewed. With Three.js, Framer Motion, 26 Radix packages, the Firebase SDK and video assets, this is a material performance concern. |
| **Bundle-size or performance budget** | **Absent** from CI. |
| **Accessibility gate** | `jsx-a11y` is installed but there is no evidence its findings are build-blocking, and no formal audit was found. |
| **Client error tracking** | **Absent.** No Sentry or equivalent. |
| **Product analytics / RUM** | **Absent.** No usage instrumentation. |
| **Design system documentation** | No Storybook or documented component inventory found. |
| **API response validation** | Zod is a dependency (used for forms); no evidence it is applied to API responses, leaving the app exposed to silent backend contract drift. |
| **Robots / indexing directives** | Not verified; authenticated-route exclusion and policy-page indexability unconfirmed. |
| **Source-map policy for production** | Not verified. |

### 11.4 Summary

The web client is **feature-complete and instrumentation-poor**. The build works, the hosting configuration is genuinely well-hardened (five security headers and correct caching semantics are better than most internal tools manage), and the dependency choices are coherent. The credible technical gaps are, in priority order: no runtime API contract validation, no test coverage beyond "it compiles", no CSP, no code splitting despite a heavy dependency graph, and no error or usage telemetry.

---

## 12. Technical Risks & Dependencies

### 12.1 Technical risks

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| WTR-1 | **Silent backend contract drift.** A renamed or removed field produces an undefined value that renders as a blank panel with no error anywhere. | High | High | Validate every API response with Zod at the service-layer boundary; fail loudly and report; add contract tests to CI. |
| WTR-2 | **No behavioural test coverage.** CI proves the bundle compiles, nothing more; regressions reach production undetected. | High | High | Implement WTEST-2, WTEST-5 and WTEST-7 as the first tranche; gate pull requests on them. |
| WTR-3 | **Missing Content Security Policy** leaves XSS mitigation dependent on React's escaping alone. | Medium | High | Add a CSP to `firebase.json` headers; start in report-only mode, then enforce. |
| WTR-4 | **Initial bundle weight** from Three.js, Framer Motion, 26 Radix packages, the Firebase SDK and MP4 assets. | High | Medium | Route-level `React.lazy` splitting; dynamic import for the 3D and video surfaces; enforce a CI bundle budget. |
| WTR-5 | **CRA/CRACO in maintenance mode** — slow builds, ageing transitive dependencies, no first-party React 19 alignment. | Medium | Medium | Plan a Vite migration; keep CRACO overrides minimal to bound the migration cost. |
| WTR-6 | **No error telemetry** — client failures are invisible until a user complains. | High | Medium | Add a client error reporter with release and route context; alert on error-rate spikes. |
| WTR-7 | **Accessibility regressions** as roughly 70 pages evolve without a gate. | High | Medium | Promote `jsx-a11y` findings to errors; add axe scanning to CI; commission a baseline audit. |
| WTR-8 | **Model output rendering as an XSS or phishing vector.** | Medium | High | Render as text or sanitise; never `dangerouslySetInnerHTML` on model output; add a test with a crafted malicious response. |
| WTR-9 | **Token handling in browser storage** exposed to any successful XSS. | Medium | High | Shortest practical token lifetime; CSP; clear on 401 and logout; consider moving to an httpOnly cookie flow if the backend can support it. |
| WTR-10 | **Backend unavailability produces a broken experience** rather than an explained one. | Medium | Medium | Global backend-unreachable banner; bounded retry with backoff; clearly-labelled stale cached values where safe. |
| WTR-11 | **Visual and behavioural inconsistency** across roughly 70 pages built at different times. | High | Medium | Component inventory; design review gate; visual regression testing. |
| WTR-12 | **Policy corpus is code** — legally significant content maintained in JSX by engineers. | Medium | Medium | Legal sign-off in the release checklist; effective date and owner on each page; consider moving the corpus to a content source. |
| WTR-13 | **Yarn 1 (classic) is legacy** and is the declared package manager. | Low | Low | Bundle the package-manager upgrade with the build-tool migration (WTR-5). |
| WTR-14 | **Firebase Hosting single dependency** for delivery. | Low | Medium | Build output is portable static assets; document an alternative hosting path. |
| WTR-15 | **Dead routes accumulate** — product-adjacent views (`/gst`, `/ignition`, `/urjaa`, `/tattoos`) may no longer belong in the Kailash dashboard. | Medium | Low | Add usage analytics; review route inventory quarterly; remove or migrate unused surfaces. |

### 12.2 External dependencies

| Dependency | Criticality | Failure impact |
|---|---|---|
| Kailash backend API | **Critical** | The app renders a shell and nothing else |
| Firebase Hosting | **Critical** | The app is unreachable |
| React 19 and the React ecosystem | High | Upgrade friction; ecosystem lag on a very recent major |
| Radix UI (26 packages) | High | UI primitives are load-bearing; a breaking change is broad |
| Tailwind CSS 3.4 | High | All styling |
| TanStack Query 4 | High | All server-state handling; v5 migration is a future cost |
| Axios | Medium | Replaceable with `fetch` |
| Three.js / react-three-fiber / drei | Medium | Visualisation only; degrade gracefully if removed |
| Framer Motion | Medium | Animation only |
| Firebase client SDK | Medium | Client-side Firebase features |
| npm registry | High | Build reproducibility; mitigate with a committed lockfile and frozen installs |
| GitHub Actions | Medium | Manual build and deploy required if unavailable |

### 12.3 Internal dependencies

| Dependency | Note |
|---|---|
| Backend `ApiResponse` envelope | The client's entire error and success handling is built on it; changes are breaking |
| Backend RBAC model | Client role gating mirrors the five-role model; role changes require coordinated frontend updates |
| Backend CORS allow-list | Adding a new frontend origin requires a backend configuration change |
| Department registry | The departments list and per-department routes derive from it |
| Brand assets | Video and OG imagery are shipped in the build; asset changes are frontend releases |

---

## 13. Appendix

### 13.1 Parent and sibling documents

| Document | Location | Relationship |
|---|---|---|
| **`BRD_kailash_ai.md`** | `../BRD_kailash_ai.md` | Parent product BRD — platform-wide business requirements |
| **`TRD_kailash_ai.md`** | `../TRD_kailash_ai.md` | Parent product TRD — backend architecture, data model and API this client consumes |
| `BRD_web_app_kailash_ai.md` | Same directory | Companion business requirements for this surface |
| `BRD_ios_app_kailash_ai.md` / `TRD_ios_app_kailash_ai.md` | `../ios_app_kailash_ai/` | Sibling surface — records that no iOS client exists |
| `BRD_android_app_kailash_ai.md` / `TRD_android_app_kailash_ai.md` | `../android_app_kailash_ai/` | Sibling surface — records that no Android client exists |

### 13.2 Frontend directory layout

```
frontend/
├── src/
│   ├── App.js              # route table, providers, guards
│   ├── App.css
│   ├── index.js            # mount point
│   ├── index.css           # Tailwind entry
│   ├── components/         # Radix + Tailwind composed UI
│   ├── pages/              # ~70 page modules (operational + policy corpus)
│   ├── services/           # Axios API layer
│   ├── stores/             # Zustand stores
│   ├── hooks/              # shared hooks
│   ├── context/            # React context providers
│   ├── data/               # static/reference data
│   ├── lib/                # utilities
│   └── styles/             # shared styles
├── build/                  # compiled output (present)
│   ├── index.html · asset-manifest.json · static/
│   ├── favicon.png · og-image.png · og-image.svg · og-background.jpg
│   └── kailash_intro_video.mp4 · kailash_video_hd.mp4 · kailash_video_optimized.mp4
├── node_modules/           # installed (~1,000 entries)
├── package.json
├── firebase.json
└── yarn.lock
```

### 13.3 Full route inventory

**Authenticated (roughly 21):** `/` (login) · `/kailash` · `/departments` · `/department/:name` · `/ganesha` · `/ganesha-v2` · `/chat` · `/ganesha-analytics` · `/guardians` · `/tasks` · `/management` · `/analytics` · `/reports` · `/knowledge-base` · `/users` · `/settings` · `/automobile` · `/dashboard/executive` · `/gst` · `/ignition` · `/urjaa` · `/tattoos`
**Redirects:** `/dashboard` → `/kailash` · `/applications` → `/dashboard` → `/kailash`

**Public policy (roughly 35):** `/terms` · `/privacy` · `/cookie-policy` · `/disclaimer` · `/acceptable-use` · `/intellectual-property` · `/dmca` · `/age-restriction` · `/gdpr-compliance` · `/ccpa-compliance` · `/data-retention` · `/data-breach` · `/data-transfer` · `/subprocessors` · `/user-rights` · `/sla` · `/refund-policy` · `/shipping-policy` · `/warranty-policy` · `/api-terms` · `/oemsg` · `/community-guidelines` · `/moderator-guidelines` · `/code-of-conduct` · `/ethics` · `/security-policy` · `/incident-response` · `/penetration-testing` · `/bug-bounty` · `/accessibility` · `/compliance` · `/transparency`

### 13.4 Recommended CSP starting point

```
Content-Security-Policy:
  default-src 'self';
  script-src 'self';
  style-src 'self' 'unsafe-inline';               # Tailwind-generated inline styles
  img-src 'self' data: https:;
  media-src 'self';
  font-src 'self' data:;
  connect-src 'self' https://api.kailash-ai.in https://*.googleapis.com https://*.firebaseio.com;
  frame-ancestors 'none';
  base-uri 'self';
  form-action 'self';
```

Deploy in `Content-Security-Policy-Report-Only` mode first, collect violations, then enforce.

### 13.5 Open technical questions

1. Is the Firebase-hosted site live, on which domain, and at which commit?
2. Should API responses be validated with Zod at the boundary — and who owns keeping those schemas in step with the backend?
3. What is the agreed main-bundle budget, and which surfaces get lazily loaded first?
4. Should production source maps be published, and if so with what access control?
5. When does the CRA to Vite migration start, and is the Yarn upgrade bundled with it?
6. Which error-tracking and analytics providers are acceptable given the data-residency position in `../TRD_kailash_ai.md` NFR-C3?
7. Is the online-only (non-PWA) position permanent, and should it be recorded as an explicit architectural decision?
8. Should the policy corpus remain as JSX components, or move to a content source that Legal can edit without a code deploy?
