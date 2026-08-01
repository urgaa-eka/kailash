# Business Requirements Document — Kailash-Ai Web Application

## 1. Document Control

| Field | Value |
|---|---|
| **Document title** | Business Requirements Document — Kailash-Ai Web Application |
| **Product** | Kailash — Go4Garage internal ML/AI platform |
| **Surface** | Web application (browser client) — `frontend/` in the Kailash repository |
| **Document type** | BRD (Application level) |
| **Version** | 1.0 |
| **Date** | 2026-07-31 |
| **Status** | Draft |
| **Owner** | TBD |
| **Author** | Go4Garage Documentation Workstream |
| **Reviewers** | TBD (Frontend Lead, Platform Lead, Design, Compliance) |
| **Approvers** | TBD |
| **Classification** | Internal — Proprietary |
| **Parent product BRD** | `../BRD_kailash_ai.md` |
| **Parent product TRD** | `../TRD_kailash_ai.md` |
| **Companion document** | `TRD_web_app_kailash_ai.md` (same directory) |
| **Source of truth** | `C:\Go4Garage( Eka)\Kailash-Ai\frontend`, HEAD commit `40cca17` dated 2026-07-31 |

### 1.1 Revision History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0 | 2026-07-31 | Documentation Workstream | Initial draft, scoped to the web surface only |

---

## 2. Executive Summary

The Kailash web application is the **only human-facing surface of the Kailash platform**. It is a React 19 single-page application that gives Go4Garage staff a browser-based cockpit over the platform's AI departments, guardian orchestration, tasks, analytics, knowledge base and automobile-domain intelligence. Everything a person can do with Kailash, they do here — there is no desktop client, no CLI product, and no mobile app.

The application ships roughly **70 page modules** under `frontend/src/pages/`, split into two distinct families. The first is the **operational cockpit**: roughly 21 authenticated routes including a login gate, the main Kailash dashboard, GANESHA chat (v1 and v2), department listing and per-department detail, tasks, GAPS/task management, analytics, GANESHA analytics, reports, knowledge base, guardians, users, settings, an automobile pricing surface, an executive dashboard, an investor-facing executive dashboard, and product-adjacent views for GST, Ignition, Urjaa and a tattoos tool. The second family is a **published policy and compliance corpus** of roughly 35 static pages — privacy, terms, cookies, disclaimer, acceptable use, intellectual property, DMCA, age restriction, GDPR, CCPA, data retention, data breach, data transfer, sub-processors, user rights, SLA, refund, shipping, warranty, API terms, OEM/SG registration, community and moderator guidelines, code of conduct, ethics, security policy, incident response, penetration testing, bug bounty, accessibility statement, compliance and transparency.

Technically the client is built with Create React App wrapped by CRACO, styled with Tailwind CSS and Radix UI primitives, animated with Framer Motion, and enhanced with a Three.js / react-three-fiber visualisation layer. Server state is managed with TanStack Query, client state with Zustand, forms with React Hook Form and Zod, and HTTP with Axios against the FastAPI backend. It is deployed as static assets to **Firebase Hosting** (project `kailash-38268`) with SPA rewrites, immutable long-lived caching on hashed assets, and a hardened security-header set.

The application has genuinely been built: `frontend/node_modules/` is populated with roughly 1,000 packages and `frontend/build/` contains a compiled bundle including `index.html`, hashed `static/` assets, brand video files and Open Graph imagery.

This BRD covers the web surface only. Backend capability, data model and platform-wide requirements live in the parent product documents.

---

## 3. Business Objectives & Strategic Fit

### 3.1 Why a web app, and why only a web app

Kailash's users are Go4Garage staff performing analytical, supervisory and administrative work: reading dashboards, comparing forecasts, reviewing anomalies, triaging tasks, curating knowledge, and administering users and roles. That work is dense, multi-panel, keyboard-driven and desk-bound. A browser client on a large screen is the correct medium for it, and the absence of a mobile app is a deliberate consequence of that user profile rather than a gap.

The web app also carries a second, non-obvious job: it is where Go4Garage's **published legal and compliance posture** lives. Roughly half the page count is policy content, and it is the artefact an auditor, a partner or an investor would be shown.

### 3.2 Objectives

| # | Objective | How the web app serves it |
|---|---|---|
| **WO-1** | **Make platform capability usable without engineering.** | Every department, guardian and analytics capability reachable through a UI, so non-engineers exercise the platform directly rather than filing tickets. |
| **WO-2** | **Give leadership a single operational picture.** | Executive dashboard, investor executive dashboard, analytics and reports consolidate portfolio health in one place. |
| **WO-3** | **Make the AI conversational and explainable.** | GANESHA chat (v1 and v2) plus GANESHA analytics let a user ask, see which departments answered, and inspect orchestration behaviour. |
| **WO-4** | **Turn the knowledge layer into a curatable asset.** | The knowledge base view makes the RAG corpus visible and maintainable by domain SMEs. |
| **WO-5** | **Provide the administrative control plane.** | Users, RBAC and settings administration performed in-browser by an admin, not by a database edit. |
| **WO-6** | **Surface automobile-domain commercial intelligence.** | The automobile pricing view exposes the pricing engine, market data and GST treatment to commercial staff. |
| **WO-7** | **Publish and maintain Go4Garage's compliance posture.** | Roughly 35 policy pages covering privacy, data protection, security, community and commercial terms. |
| **WO-8** | **Present the platform credibly to investors and partners.** | Investor executive dashboard plus branded video and Open Graph assets in the build output. |
| **WO-9** | **Cost-efficient delivery.** | Static hosting on a CDN with immutable caching keeps the human surface effectively free to serve relative to backend compute. |

### 3.3 Strategic fit

The parent BRD identifies Kailash's value as leverage across the Go4Garage portfolio. The web app is where that leverage becomes visible to the business: a forecast is only worth what a manager does with it, and an anomaly is only worth the investigation it triggers. The web app converts platform capability into organisational action, and it does so with zero marginal infrastructure cost per user.

---

## 4. Target Users / Personas / Stakeholders

### 4.1 Personas and their journeys

| Persona | Primary journey in the web app | Key routes |
|---|---|---|
| **Operations manager** | Log in → dashboard → scan department status → open a flagged department → create or reassign a task → track it to closure | `/`, `/kailash`, `/departments`, `/department/:name`, `/tasks`, `/management` |
| **Business analyst** | Log in → analytics → filter and compare → open reports → export a view for a stakeholder | `/analytics`, `/reports`, `/ganesha-analytics` |
| **Executive** | Log in → executive dashboard → portfolio-level rollups → drill into a single metric | `/dashboard/executive`, investor executive dashboard |
| **Platform / AI engineer** | Log in → GANESHA chat v2 → test an orchestration → check guardians → inspect system health | `/ganesha`, `/ganesha-v2`, `/chat`, `/guardians` |
| **Domain SME** | Log in → knowledge base → review ingested knowledge and digests → flag stale content | `/knowledge-base` |
| **Commercial / pricing staff** | Log in → automobile pricing → price a part or vehicle → review GST/HSN treatment | `/automobile` |
| **Administrator** | Log in → users → create or deactivate an account → assign a role → adjust settings | `/users`, `/settings` |
| **Compliance officer / external reviewer** | Reach a policy page directly by URL → read the current position → cite it | `/privacy`, `/gdpr-compliance`, `/data-retention`, `/security-policy`, `/transparency`, and roughly 30 others |
| **Consumer-product engineer** | Log in → view the platform they depend on → check department and system health before blaming their own service | `/kailash`, `/guardians`, health views |

### 4.2 Stakeholders

| Stakeholder | Interest in the web app |
|---|---|
| Go4Garage leadership | Executive and investor dashboards; the platform's public face |
| Platform engineering | The surface they must keep in sync with backend API changes |
| Design | Visual consistency across roughly 70 pages built with Radix and Tailwind |
| Compliance / Legal | Currency and accuracy of the roughly 35 policy pages |
| Finance | Hosting cost (currently minimal — static CDN) |
| Consumer-product teams | Visibility into the shared platform's health |

### 4.3 Access model

The application is **not** a public product. Access requires an account provisioned by an administrator, authenticated at `/`, with role-based visibility thereafter. Policy pages are the exception — they are reachable without authentication, by design, since their purpose is to be citable.

---

## 5. Scope

### 5.1 In scope

**Authenticated operational surface**

- Login gate at `/` with session establishment and, where enabled, a two-factor challenge.
- Main dashboard at `/kailash` (with `/dashboard` and `/applications` redirecting to it).
- Departments list at `/departments` and per-department detail at `/department/:name`.
- GANESHA conversational surfaces: `/ganesha`, `/ganesha-v2`, `/chat`.
- GANESHA analytics at `/ganesha-analytics`.
- Guardians view at `/guardians`.
- Tasks at `/tasks` and GAPS/task management at `/management`.
- Analytics at `/analytics` and reports at `/reports`.
- Knowledge base at `/knowledge-base`.
- Users administration at `/users` and settings at `/settings`.
- Automobile pricing at `/automobile`.
- Executive dashboard at `/dashboard/executive`, plus the investor-facing executive dashboard.
- Product-adjacent views: `/gst`, `/ignition`, `/urjaa`, `/tattoos`.

**Public policy surface (roughly 35 pages)**

- Core legal: terms and conditions, privacy policy, cookie policy, disclaimer, acceptable use, intellectual property, DMCA, age restriction.
- Data protection: GDPR compliance, CCPA compliance, data retention, data breach, data transfer, sub-processor list, user rights.
- Commercial: SLA, refund policy, shipping policy, warranty policy, API terms, OEM/SG registration.
- Community: community guidelines, moderator guidelines, code of conduct, ethics.
- Security: security policy, incident response, penetration testing, bug bounty.
- Assurance: accessibility statement, compliance, transparency.

**Cross-cutting**

- Role-aware navigation and view gating consistent with backend RBAC.
- Responsive layout across desktop, laptop and tablet breakpoints, with tablet-usable read paths.
- Light/dark theming.
- Toast notifications and consistent form validation.
- Branded assets: intro/HD/optimised video, Open Graph image set, favicon.
- Static deployment to Firebase Hosting with SPA rewrites, caching and security headers.

### 5.2 Out of scope

- **Any native mobile application.** See §10.2. The web app is responsive; it is not packaged for an app store.
- **A Progressive Web App with offline capability.** No service worker or manifest-driven install flow is in scope for v1 (see §11 for the considered position).
- **Public self-service signup, billing or payment collection.** No payment gateway exists anywhere in Kailash.
- **A public marketing website.** Go4Garage's marketing presence is a separate property; only the policy corpus here is publicly reachable.
- **Direct database or model-provider access from the browser.** All data flows through the backend API; the client never holds an AI vendor key.
- **Server-side rendering.** The app is a client-rendered SPA served from static hosting.
- **Rich text/document authoring.** Knowledge ingestion is a backend script path, not an in-browser editor, in v1.
- **Real-time collaborative editing.** Not a requirement for this user base.

---

## 6. Business Requirements

| ID | Requirement | Priority | Verification |
|---|---|---|---|
| **WBR-1** | The web app **shall be the complete human interface to Kailash** — every capability an authenticated user is entitled to exercise shall be reachable through the UI without recourse to `curl`, the OpenAPI page, or direct database access. | Must | Walk the permission matrix; for each granted permission, identify the UI route that exercises it. Any permission with no UI path is a defect. |
| **WBR-2** | The web app **shall gate all operational content behind authentication**, redirecting unauthenticated users to the login route, while leaving the policy corpus publicly reachable by design. | Must | Request each operational route with no session — all redirect to `/`. Request each policy route with no session — all render. |
| **WBR-3** | The web app **shall render only what the signed-in user's role permits**, hiding or disabling actions the backend would reject, so that a `viewer` never sees a control that will fail. | Must | Log in as each of the five roles; capture the visible navigation and action set; confirm no visible control produces an authorisation error when used. |
| **WBR-4** | The web app **shall present department status and detail for every registered department**, with a detail view reachable at a stable per-department URL. | Must | The count of departments listed equals the backend registry count; `/department/:name` resolves for each; an unknown name shows a friendly not-found state, not a blank screen or crash. |
| **WBR-5** | The web app **shall provide a conversational interface to GANESHA** that shows the user's question, the composed answer, and which departments were engaged, with conversation history retrievable across sessions. | Must | Ask a multi-department question; the response names the departments engaged; log out and back in; the conversation is still listed. |
| **WBR-6** | The web app **shall provide task and GAPS management** — create, view, assign, update status and close — with changes persisted and reflected on the dashboard. | Must | Create a task, assign it, close it; confirm dashboard counts update and the item appears in the activity trail. |
| **WBR-7** | The web app **shall provide analytics and reporting views** that render populated data for the current period and support filtering by department and by date range. | Must | Load analytics against a seeded dataset; apply a department and date filter; confirm the rendered figures change consistently with the filter. |
| **WBR-8** | The web app **shall provide an executive dashboard and an investor-facing dashboard** that summarise platform and portfolio health in a form presentable without further explanation. | Must | An executive-role user reaches both views and every tile renders a real value or an explicit "no data" state — never a spinner that never resolves or a raw error. |
| **WBR-9** | The web app **shall surface the knowledge base**, showing what knowledge exists, how recent it is, and which department it belongs to. | Should | Open the knowledge base; entries display department attribution and a date; the newest dated digest is visible. |
| **WBR-10** | The web app **shall provide user and role administration** — create, view, update, deactivate users and assign roles — restricted to administrator roles. | Must | An admin performs the full lifecycle; a non-admin cannot reach the view or perform the action. |
| **WBR-11** | The web app **shall provide the automobile pricing surface**, returning a priced result with the market adjustment and the applicable HSN/GST treatment shown to the user. | Should | Price a representative part; the result displays base price, adjustment, HSN code and GST amount. |
| **WBR-12** | The web app **shall publish the full policy corpus** — at minimum privacy, terms, cookies, disclaimer, acceptable use, intellectual property, DMCA, age restriction, GDPR, CCPA, data retention, data breach, data transfer, sub-processors, user rights, SLA, refund, shipping, warranty, API terms, community guidelines, moderator guidelines, code of conduct, ethics, security policy, incident response, penetration testing, bug bounty, accessibility statement, compliance, and transparency — each at a stable, linkable URL. | Must | Every listed route returns substantive content at a permanent URL. |
| **WBR-13** | Each policy page **shall carry a visible effective date and an owning function**, and shall be reviewed at least annually. | Should | Inspect each page for a date and owner; maintain a review register. |
| **WBR-14** | The web app **shall be usable on the browsers Go4Garage staff actually use** — the two most recent major versions of Chrome, Edge, Firefox and Safari on desktop, and current mobile Safari and Chrome for read-only access. | Must | Execute the core journey matrix (§7.6 of the companion TRD) on each supported browser. |
| **WBR-15** | The web app **shall be responsive from 1920 px down to 768 px for full functionality, and shall remain readable and navigable down to 360 px** for consultation on a phone, with no horizontal scrolling of primary content. | Must | Test at 1920, 1440, 1280, 1024, 768, 414 and 360 px; confirm no clipped controls or horizontal overflow on primary content. |
| **WBR-16** | The web app **shall meet WCAG 2.1 Level AA** for the authenticated operational surface and the public policy corpus — keyboard operability, visible focus, sufficient contrast, correct labelling and landmark structure. | Should | Automated audit (axe or Lighthouse) reports no Level AA violations on a representative page sample; manual keyboard-only traversal completes the core journeys. |
| **WBR-17** | The web app **shall load fast enough not to obstruct work** — first contentful paint under 2 s and interactive under 4 s on a typical office connection, with static assets served immutably from a CDN. | Should | Lighthouse performance run against the production deployment; verify `Cache-Control: public, max-age=31536000, immutable` on hashed assets. |
| **WBR-18** | The web app **shall communicate state honestly** — every asynchronous view shall render a loading state, an empty state and an error state, and shall never leave a user staring at an indefinite spinner or a blank panel. | Must | Force a slow response, an empty dataset and a backend error on each major view; confirm all three states render. |
| **WBR-19** | The web app **shall never expose secrets to the browser** — no AI provider key, no service-account credential, no database connection string shall appear in the bundle, in network payloads or in client storage. | Must | Grep the production bundle for credential patterns; inspect network traffic and browser storage after a full session. Expect zero findings. |
| **WBR-20** | The web app **shall be deployable as an immutable static build with a single documented command**, and any deployment shall be reversible to the previous version. | Must | Run the documented deploy command from a clean checkout; confirm the live site updates; roll back and confirm restoration. |
| **WBR-21** | The web app **shall present a coherent Go4Garage/Kailash brand** across all pages — consistent typography, colour, spacing and iconography, with light and dark modes both complete. | Should | Design review across a representative sample of both page families in both themes. |
| **WBR-22** | The web app **shall support the platform's SEO and social-preview needs for its public policy pages only**, with correct titles, descriptions and Open Graph imagery, while keeping authenticated surfaces out of search indexes. | Should | Inspect meta tags and Open Graph assets on policy pages; confirm authenticated routes are excluded from indexing. |

---

## 7. Success Metrics / KPIs

### 7.1 Adoption

| KPI | Definition | Target |
|---|---|---|
| Weekly active internal users | Distinct authenticated users per week | Growing to cover the full intended staff group |
| Route coverage | Share of the roughly 21 authenticated routes visited at least monthly | 80% or better — unvisited routes are candidates for removal |
| Self-service rate | Share of routine platform questions answered in-app rather than by asking an engineer | 80% or better |
| Executive dashboard usage | Distinct leadership users per month | Every intended leadership user at least monthly |

### 7.2 Experience and quality

| KPI | Definition | Target |
|---|---|---|
| First contentful paint | Lighthouse FCP on the production deployment | Under 2 s |
| Time to interactive | Lighthouse TTI | Under 4 s |
| Lighthouse performance score | Production, desktop profile | 85 or better |
| Lighthouse accessibility score | Production, representative sample | 90 or better |
| WCAG 2.1 AA violations | Automated audit findings | 0 on audited pages |
| Client-side error rate | Uncaught JavaScript errors per 1,000 sessions | Under 5 |
| Broken-state incidents | Views rendering an indefinite spinner or blank panel, reported per month | 0 |

### 7.3 Reach and compatibility

| KPI | Definition | Target |
|---|---|---|
| Supported-browser pass rate | Core journeys passing on each browser in the support matrix | 100% |
| Responsive defects | Layout defects reported at any supported breakpoint | 0 open at release |
| Tablet read-path success | Core read journeys completable on a 768 px viewport | 100% |

### 7.4 Delivery and operations

| KPI | Definition | Target |
|---|---|---|
| Build success rate | Green `yarn build` runs in CI | 95% or better |
| Deploy frequency | Frontend deployments per month | At least fortnightly during active development |
| Rollback time | Time to restore the previous version | Under 15 minutes |
| Bundle size regression | Increase in main bundle size per release | Under 5% without written justification |
| Policy currency | Policy pages reviewed within 12 months | 100% |

---

## 8. Assumptions & Constraints

### 8.1 Assumptions

| # | Assumption | If false |
|---|---|---|
| WA-1 | Users work primarily on desktop or laptop browsers on office or home broadband. | Mobile-first redesign and offline capability become necessary. |
| WA-2 | The backend API contract is stable, versioned, and changes are communicated before release. | The SPA breaks on backend deploys; contract testing becomes mandatory. |
| WA-3 | Firebase Hosting remains the deployment target and satisfies performance and residency expectations. | Hosting migration required (self-hosted CDN or alternative provider). |
| WA-4 | Users have modern evergreen browsers; no Internet Explorer or legacy support is required. | Polyfill and transpilation targets widen; bundle size grows. |
| WA-5 | The policy corpus is drafted and maintained by Legal/Compliance, not by engineering. | Engineering absorbs unbudgeted content maintenance. |
| WA-6 | No offline access is needed because all data is live platform state. | A service worker and caching strategy must be designed. |
| WA-7 | Session-based JWT auth in the browser is acceptable for an internal tool on trusted networks. | Stronger client-side session protections and shorter token lifetimes are required. |
| WA-8 | The Three.js visualisation layer is a differentiator worth its bundle cost. | It should be lazy-loaded or removed. |

### 8.2 Constraints

| # | Constraint | Nature |
|---|---|---|
| WC-1 | Build toolchain is Create React App 5.0.1 via CRACO — a maintenance-mode path for a React 19 application. | Technical debt |
| WC-2 | Client-rendered SPA only; no SSR, so public policy pages rely on client rendering for crawlers. | Architectural |
| WC-3 | Static hosting means all dynamic behaviour requires a live backend; there is no server-side fallback. | Architectural |
| WC-4 | The design system is Radix primitives plus Tailwind — component choices must stay within it for consistency. | Design |
| WC-5 | Roughly 70 page modules with a small team means consistency must be enforced by shared components, not by discipline alone. | Resource |
| WC-6 | Bundle weight is influenced by Three.js, Framer Motion, the Firebase client SDK and 26 Radix packages. | Performance |
| WC-7 | Content in the policy corpus has legal significance; engineering must not edit it unilaterally. | Governance |
| WC-8 | Yarn 1.22.22 is the declared package manager; lockfile discipline is required. | Tooling |

---

## 9. Risks & Mitigations

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| WR-1 | **Backend contract change breaks the SPA silently** — a renamed field yields a blank panel rather than an error. | High | High | Typed API client with runtime validation (Zod is already a dependency); contract tests in CI; explicit error states (WBR-18). |
| WR-2 | **Bundle bloat degrades load time** as pages and dependencies accumulate. | High | Medium | Route-level code splitting; lazy-load the Three.js and video-heavy surfaces; enforce a bundle-size budget in CI. |
| WR-3 | **CRA maintenance mode** leaves the build path unsupported and slow. | Medium | Medium | Plan a Vite migration; keep CRACO customisation minimal so migration cost stays bounded. |
| WR-4 | **Inconsistent UX across roughly 70 pages** built at different times by different hands. | High | Medium | Shared component library; design review gate on new pages; visual regression testing. |
| WR-5 | **Policy pages drift out of date** and misrepresent the actual position. | Medium | High | Effective date and owner on every page (WBR-13); annual review register; Legal sign-off in the release checklist. |
| WR-6 | **Accessibility regressions** despite `eslint-plugin-jsx-a11y` being present but not build-blocking. | High | Medium | Promote a11y lint findings to errors; add an automated audit to CI; manual keyboard testing before release. |
| WR-7 | **Client-side auth token exposure** through XSS or careless storage. | Medium | High | Strict security headers (already configured), no `dangerouslySetInnerHTML` on untrusted content, short token lifetime, sanitise any rendered model output. |
| WR-8 | **Rendered model output as an injection vector** — an LLM answer containing markup or a link that executes or misleads. | Medium | High | Treat all model output as untrusted; sanitise before render; never render it as raw HTML. |
| WR-9 | **Backend outage renders the app useless** with no graceful message. | Medium | Medium | A global offline/backend-unreachable banner; retry with backoff; cached last-known values where safe and clearly labelled as stale. |
| WR-10 | **Search engines index authenticated routes** or, conversely, fail to index policy pages because they are client-rendered. | Medium | Low–Medium | `robots` directives excluding app routes; verify policy-page indexing with Search Console; consider prerendering the policy corpus if indexing proves unreliable. |
| WR-11 | **Firebase Hosting dependency** — outage or policy change at the hosting provider. | Low | Medium | Build output is portable static assets; document an alternative hosting path. |
| WR-12 | **Video and image assets inflate the deployment** and slow first load. | Medium | Low | Serve video lazily and only where it adds value; keep it out of the critical path; compress aggressively (an optimised variant already exists). |
| WR-13 | **Role gating implemented only in the UI** creates a false sense of security. | Medium | High | Treat UI gating as ergonomics only; the backend remains the enforcement point; test that hidden actions are also server-rejected. |
| WR-14 | **Tablet and small-screen users hit unusable dense tables.** | Medium | Medium | Responsive table patterns (card collapse or horizontal scroll containers) at the breakpoints in WBR-15. |

---

## 10. Current Implementation Status

*Assessed 2026-07-31 against `C:\Go4Garage( Eka)\Kailash-Ai\frontend`, HEAD `40cca17`.*

### 10.1 Does the web app exist in code?

**Yes.** This is the one Kailash client surface that is genuinely built, compiled and demonstrably run locally.

| Item | Status | Evidence |
|---|---|---|
| Source tree | **Present** | `frontend/src/` with `components/`, `pages/`, `services/`, `stores/`, `hooks/`, `context/`, `data/`, `lib/`, `styles/`, plus `App.js`, `index.js` and stylesheets |
| Page modules | **Present — roughly 70** | `frontend/src/pages/` includes the operational views and the full policy corpus, with dedicated CSS modules for several (Analytics, Chat, Departments, Executive, GaneshaAI, GaneshaChat, GaneshaChatV2, Reports, Settings, Tasks, Urjaa, Users, LegalPages, DepartmentDetail) |
| Routing | **Present** | `App.js` defines roughly 21 authenticated routes plus roughly 35 policy routes, with redirects from `/dashboard` and `/applications` to `/kailash` |
| Dependencies installed | **Confirmed** | `frontend/node_modules/` populated with roughly 1,000 entries |
| Production build | **Confirmed** | `frontend/build/` contains `index.html`, `asset-manifest.json`, hashed `static/`, `favicon.png`, `og-image.png`, `og-image.svg`, `og-background.jpg`, and three video files (`kailash_intro_video.mp4`, `kailash_video_hd.mp4`, `kailash_video_optimized.mp4`) |
| Hosting configuration | **Present** | `frontend/firebase.json` with SPA rewrite, immutable static caching and a full security-header set |
| Deploy scripts | **Present** | `yarn firebase:deploy` and `yarn firebase:preview` in `package.json` |
| CI coverage | **Present** | The `frontend` job in `.github/workflows/ci.yml` runs `yarn install` and `yarn build`; `deploy-frontend.yml` exists |
| Lint tooling | **Present** | ESLint 9.23.0 with react, import and `jsx-a11y` plugins |

### 10.2 Platform existence statement — WEB

> **The Kailash web application EXISTS in code and has been built.** It is a React 19 single-page application located at `Kailash-Ai/frontend/`, with an installed dependency tree and a compiled production bundle present on disk. It is the platform's only human-facing client. There is no native mobile counterpart — see `../ios_app_kailash_ai/BRD_ios_app_kailash_ai.md` and `../android_app_kailash_ai/BRD_android_app_kailash_ai.md`, both of which record that no mobile client exists or is planned.

### 10.3 Not verified or not present

| Item | Honest status |
|---|---|
| **Live production deployment** | `firebase.json` targets project `kailash-38268`, and `backend/.env.example` lists `kailash-ai.in`, `www.kailash-ai.in`, `kailash-38268.web.app` and `kailash-38268.firebaseapp.com` as allowed origins. **Whether the site is currently live was not verified from this working copy.** |
| **PWA capability** | No service worker, no web app manifest, no install prompt found. The app is not installable and has no offline capability. |
| **Automated frontend tests** | `craco test` is wired as a script, but no meaningful test suite was found under `frontend/src/`. CI verifies that the bundle builds, not that it behaves. |
| **Accessibility conformance** | `eslint-plugin-jsx-a11y` is installed; there is no evidence of a formal WCAG audit or of a11y findings being build-blocking. |
| **Performance measurement** | No Lighthouse budget, bundle-size budget or performance regression gate found in CI. |
| **Code splitting** | Not verified. With Three.js, Framer Motion, 26 Radix packages and the Firebase client SDK in the dependency set, route-level splitting matters; no evidence of it was found in the configuration reviewed. |
| **Policy page currency** | Roughly 35 policy pages exist as components. Whether each carries an effective date and a named owner, and when each was last legally reviewed, was not verified. |
| **Analytics / RUM** | No product analytics or real-user-monitoring integration was found in the client. |
| **Error tracking** | No client-side error reporting service (Sentry or equivalent) was found. |
| **Design system documentation** | Radix plus Tailwind are used consistently as dependencies, but no Storybook or documented component inventory was found. |

### 10.4 Summary judgement

The web app is **substantially complete as a feature surface and materially under-instrumented as a product**. It has the pages, the routing, the design primitives, a working build and a hardened hosting configuration. What it lacks is the measurement layer: no frontend tests, no accessibility gate, no performance budget, no error tracking, no usage analytics. Those gaps do not stop it working; they stop anyone knowing whether it works well.

---

## 11. Roadmap / Milestones

### 11.1 Near term (0 to 3 months) — *instrument and verify*

| # | Milestone | Success criterion |
|---|---|---|
| WN-1 | **Confirm and document the live deployment.** Establish whether the Firebase-hosted site is live and at which commit. | A dated deployment record naming URL, commit and owner. |
| WN-2 | **Add client-side error tracking.** Capture uncaught errors with release and route context. | Errors visible in a dashboard within one minute of occurrence. |
| WN-3 | **Establish the state contract.** Ensure every asynchronous view renders loading, empty and error states (WBR-18). | Audit sheet covering all roughly 21 authenticated routes, all three states present. |
| WN-4 | **Promote accessibility linting to build-blocking** and run a baseline axe audit on a representative page sample. | Zero new a11y lint errors merge; baseline audit report published. |
| WN-5 | **Set performance and bundle budgets in CI.** | A pull request exceeding the bundle budget fails the build. |
| WN-6 | **Verify the browser support matrix** against the core journey list. | Signed-off compatibility matrix. |
| WN-7 | **Policy corpus audit.** Add an effective date and owning function to every policy page; build a review register. | 100% of policy pages dated and owned. |

### 11.2 Mid term (3 to 9 months) — *harden and refine*

| # | Milestone | Success criterion |
|---|---|---|
| WM-1 | **Route-level code splitting**, lazy-loading the Three.js and video-heavy surfaces. | Main bundle materially smaller; TTI under 4 s. |
| WM-2 | **Frontend test suite** — component tests for shared primitives plus end-to-end coverage of the top five journeys (Puppeteer is already a dev dependency). | Journeys run in CI on every pull request. |
| WM-3 | **Typed, validated API client** using Zod schemas shared with backend contracts. | A backend field rename fails CI rather than producing a blank panel in production. |
| WM-4 | **Responsive refinement for tablet**, especially dense analytics tables. | All core read journeys complete cleanly at 768 px. |
| WM-5 | **Component inventory and design documentation.** | A documented shared component set; new pages composed from it. |
| WM-6 | **Usage analytics** (privacy-respecting, internal-only) to identify unvisited routes. | Route coverage KPI measurable; dead routes identified for removal. |
| WM-7 | **WCAG 2.1 AA conformance** on the operational surface and the policy corpus. | Independent audit reports no Level AA violations. |

### 11.3 Long term (9 to 24 months) — *modernise*

| # | Milestone | Success criterion |
|---|---|---|
| WL-1 | **Migrate off CRA/CRACO** to a maintained build toolchain. | Faster builds, no functional regression, no visual regression. |
| WL-2 | **Decide the PWA question explicitly.** Either implement a service worker with a defined offline read scope and installability, or formally record that the app remains online-only. | A written decision, implemented or recorded. |
| WL-3 | **Consider prerendering or static generation for the policy corpus** so it is reliably indexable and instantly loadable without the SPA shell. | Policy pages served as prerendered HTML with correct meta and Open Graph tags. |
| WL-4 | **Real-time platform state** via streaming or subscriptions for dashboards and GANESHA responses. | Dashboards update without a manual refresh; chat streams tokens. |
| WL-5 | **In-browser knowledge curation**, allowing SMEs to add and correct knowledge without a backend script. | An SME completes an ingestion end to end in the UI. |

---

## 12. Appendix

### 12.1 Parent product documents

This application-level BRD narrows the Kailash platform requirements to the web surface. The authoritative product-level documents are:

| Document | Location |
|---|---|
| **`BRD_kailash_ai.md`** | `../BRD_kailash_ai.md` — product-level business requirements for the whole Kailash platform |
| **`TRD_kailash_ai.md`** | `../TRD_kailash_ai.md` — product-level technical requirements, including the backend API this client consumes |

Its direct companion is **`TRD_web_app_kailash_ai.md`** in this same directory.

The sibling application surfaces are documented in `../ios_app_kailash_ai/` and `../android_app_kailash_ai/`; both record that no native client exists.

### 12.2 Route inventory

**Authenticated operational routes (roughly 21)**

| Route | View |
|---|---|
| `/` | Login |
| `/kailash` | Main Kailash dashboard (target of `/dashboard` and `/applications` redirects) |
| `/departments` | Departments list |
| `/department/:name` | Department detail |
| `/ganesha` | GANESHA AI |
| `/ganesha-v2` | GANESHA chat v2 |
| `/chat` | Chat |
| `/ganesha-analytics` | GANESHA analytics |
| `/guardians` | Guardians |
| `/tasks` | Tasks |
| `/management` | GAPS/task management |
| `/analytics` | Analytics |
| `/reports` | Reports |
| `/knowledge-base` | Knowledge base |
| `/users` | User administration |
| `/settings` | Settings |
| `/automobile` | Automobile pricing |
| `/dashboard/executive` | Executive dashboard |
| `/gst` | GST product view |
| `/ignition` | Ignition product view |
| `/urjaa` | Urjaa view |
| `/tattoos` | Tattoos tool |

**Public policy routes (roughly 35)**

`/terms` · `/privacy` · `/cookie-policy` · `/disclaimer` · `/acceptable-use` · `/intellectual-property` · `/dmca` · `/age-restriction` · `/gdpr-compliance` · `/ccpa-compliance` · `/data-retention` · `/data-breach` · `/data-transfer` · `/subprocessors` · `/user-rights` · `/sla` · `/refund-policy` · `/shipping-policy` · `/warranty-policy` · `/api-terms` · `/oemsg` · `/community-guidelines` · `/moderator-guidelines` · `/code-of-conduct` · `/ethics` · `/security-policy` · `/incident-response` · `/penetration-testing` · `/bug-bounty` · `/accessibility` · `/compliance` · `/transparency`

### 12.3 Browser support matrix (business view)

| Browser | Platform | Support level |
|---|---|---|
| Chrome (current and current−1) | Windows, macOS, Linux | Full — primary |
| Edge (current and current−1) | Windows | Full |
| Firefox (current and current−1) | Windows, macOS, Linux | Full |
| Safari (current and current−1) | macOS | Full |
| Safari | iOS/iPadOS (current and current−1) | Read paths and core journeys |
| Chrome | Android (current) | Read paths and core journeys |
| Internet Explorer | Any | Not supported |

The `package.json` production browserslist target is `>0.2%`, `not dead`, `not op_mini all`, which is consistent with this matrix.

### 12.4 Responsive breakpoints (business view)

| Breakpoint | Class of device | Expectation |
|---|---|---|
| 1920 px and above | Large desktop | Full multi-panel layout |
| 1440 px | Desktop | Full functionality |
| 1280 px | Small desktop / large laptop | Full functionality |
| 1024 px | Laptop / landscape tablet | Full functionality; denser layout |
| 768 px | Tablet portrait | All read journeys; write journeys usable |
| 414 px | Large phone | Consultation and simple actions |
| 360 px | Small phone | Readable and navigable; no horizontal overflow |

### 12.5 Glossary

| Term | Meaning |
|---|---|
| **SPA** | Single-page application — client-rendered, routed in the browser |
| **PWA** | Progressive Web App — installable, offline-capable web application (not implemented) |
| **CRA / CRACO** | Create React App, and the configuration override layer wrapping it |
| **GANESHA** | The orchestrating guardian agent; the conversational entry point in the UI |
| **GAPS** | The task/gap management concept surfaced at `/management` |
| **Policy corpus** | The roughly 35 public legal, compliance and security pages |
| **WCAG 2.1 AA** | The accessibility conformance level targeted |

### 12.6 Open questions for the document owner

1. Is the Firebase-hosted site live today, and at which domain — `kailash-ai.in` or the `web.app` default?
2. Who owns the content of the policy corpus, and when was each page last legally reviewed?
3. Should authenticated routes be explicitly excluded from search indexing, and are policy pages currently indexed?
4. Are the product-adjacent views (`/gst`, `/ignition`, `/urjaa`, `/tattoos`) intended to remain in the Kailash dashboard, or migrate to their own products?
5. Is offline access ever required, or is the online-only position permanent?
6. What is the accepted budget for main bundle size, given the Three.js and video assets?
7. Is a formal WCAG 2.1 AA audit commissioned, and by when?
