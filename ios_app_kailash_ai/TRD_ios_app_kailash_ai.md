# Technical Requirements Document — Kailash-Ai iOS Application

## 1. Document Control

| Field | Value |
|---|---|
| **Document title** | Technical Requirements Document — Kailash-Ai iOS Application |
| **Product** | Kailash — Go4Garage internal ML/AI platform |
| **Surface** | iOS (iPhone / iPad native client) |
| **Document type** | TRD (Application level) |
| **Version** | 1.0 |
| **Date** | 2026-07-31 |
| **Status** | Draft — **conditional design for a client that does not exist** |
| **Owner** | TBD |
| **Author** | Go4Garage Documentation Workstream |
| **Reviewers** | TBD (Platform Lead, Security, Mobile Lead if appointed) |
| **Approvers** | TBD |
| **Classification** | Internal — Proprietary |
| **Companion BRD** | `BRD_ios_app_kailash_ai.md` (same directory) |
| **Parent product BRD** | `../BRD_kailash_ai.md` |
| **Parent product TRD** | `../TRD_kailash_ai.md` |
| **Source of truth** | `C:\Go4Garage( Eka)\Kailash-Ai\ios_app_kailash_ai`, product HEAD commit `40cca17` dated 2026-07-31 |

### 1.1 Status notice

**No iOS application exists.** See §11 for the formal existence statement. Sections 2 through 10 of this document are a **conditional technical specification**: they describe what would be built, and to what standard, *if* a decision to build were approved against the criteria in the companion BRD §11.1. Nothing in this document should be read as describing shipped or in-progress work.

### 1.2 Revision History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0 | 2026-07-31 | Documentation Workstream | Initial draft. Records the no-client position and specifies the conditional technical design. |

---

## 2. System / Architecture Overview

### 2.1 Current architecture — where iOS sits

Kailash today has exactly two runtime tiers: a FastAPI backend and a React 19 web client. There is no third tier. An iOS device reaches Kailash by loading the web application in mobile Safari.

```
  CURRENT STATE (2026-07-31)
  ══════════════════════════

  ┌──────────────────┐   ┌──────────────────┐   ┌───────────────────────────────┐
  │  iPhone / iPad   │   │  Desktop browser │   │  Consumer products             │
  │  ┌────────────┐  │   │                  │   │  URGAA · GSTSAAS · Ignition ·  │
  │  │  Safari    │  │   │  Chrome/Edge/    │   │  ARJUN (KAILASH_AI_URL)        │
  │  │  (mobile   │  │   │  Firefox/Safari  │   │                                │
  │  │   web)     │  │   │                  │   │                                │
  │  └─────┬──────┘  │   └────────┬─────────┘   └───────────────┬───────────────┘
  │        │         │            │                             │
  │  ┌ ─ ─ ┴ ─ ─ ─┐  │            │                             │
  │  │ NATIVE iOS │  │            │                             │
  │  │ APP        │  │            │                             │
  │  │ ✗ DOES NOT │  │            │                             │
  │  │   EXIST    │  │            │                             │
  │  └ ─ ─ ─ ─ ─ ─┘  │            │                             │
  └────────┬─────────┘            │                             │
           │                      │                             │
           └──────────┬───────────┴─────────────────────────────┘
                      │  HTTPS
                      ▼
        ┌──────────────────────────────┐        ┌────────────────────────────┐
        │  Firebase Hosting            │        │  Nginx → FastAPI backend   │
        │  React 19 SPA (build/)       │───────▶│  api.kailash-ai.in         │
        │  project kailash-38268       │        │  20 departments · 3        │
        └──────────────────────────────┘        │  guardians · 9 services    │
                                                └─────────────┬──────────────┘
                                                              ▼
                                            MongoDB 7 · PostgreSQL 16 · Redis 7

        ✗ NO APNs configuration exists in the backend
        ✗ NO device-token model exists
        ✗ NO notification dispatch service exists
        ✗ NO iOS job exists in .github/workflows/ci.yml
```

### 2.2 Conditional target architecture

Were an iOS client approved, it would slot in as a **third client of the same backend**, adding one new backend capability (push dispatch) and nothing else.

```
  CONDITIONAL TARGET STATE (only if approved)
  ═══════════════════════════════════════════

  ┌────────────────────────────────────────────────────────────────────────────┐
  │                          iOS APP (iPhone / iPad)                           │
  │                                                                            │
  │  ┌──────────────────────────────────────────────────────────────────────┐  │
  │  │  PRESENTATION       SwiftUI views (or RN/Flutter equivalent)         │  │
  │  │  ── Executive read view · Alert feed · Department list/detail ──     │  │
  │  │  ── Task list/detail · GANESHA chat · Settings (read-only) ──        │  │
  │  │  Dynamic Type · Dark Mode · VoiceOver · Reduce Motion                │  │
  │  └────────────────────────────────┬─────────────────────────────────────┘  │
  │  ┌────────────────────────────────▼─────────────────────────────────────┐  │
  │  │  STATE / VIEW MODELS      observable state · navigation coordinator   │  │
  │  └────────────────────────────────┬─────────────────────────────────────┘  │
  │  ┌────────────────────────────────▼─────────────────────────────────────┐  │
  │  │  API CLIENT       typed models mirroring ApiResponse envelope         │  │
  │  │  ── auth interceptor (Bearer JWT) · x-request-id · retry/backoff ──   │  │
  │  │  ── typed error mapping: not_found / validation_error / upstream ──   │  │
  │  └────────────────────────────────┬─────────────────────────────────────┘  │
  │  ┌──────────────┐ ┌───────────────▼──────────┐ ┌─────────────────────────┐ │
  │  │ KEYCHAIN     │ │ LOCAL CACHE (read-only)  │ │ NOTIFICATION HANDLER    │ │
  │  │ JWT · 2FA    │ │ last-known state, stale- │ │ APNs registration ·     │ │
  │  │ state        │ │ labelled, never authori- │ │ token upload · deep-    │ │
  │  │ kSecAttr     │ │ tative, purged on logout │ │ link routing            │ │
  │  │ AfterFirst   │ └──────────────────────────┘ └──────────┬──────────────┘ │
  │  │ UnlockThis   │ ┌──────────────────────────┐            │                │
  │  │ DeviceOnly   │ │ BIOMETRIC GATE           │            │                │
  │  └──────────────┘ │ LocalAuthentication      │            │                │
  │                   │ Face ID / Touch ID       │            │                │
  │                   │ passcode fallback        │            │                │
  │                   └──────────────────────────┘            │                │
  └────────────────────────────┬──────────────────────────────┼────────────────┘
                               │ HTTPS · Bearer JWT           │ APNs
                               ▼                              ▲
  ┌───────────────────────────────────────────────────────────┼────────────────┐
  │  NGINX (api.kailash-ai.in) → FastAPI BACKEND              │                │
  │  existing routers: auth · departments · tasks · analytics │                │
  │  · dashboard · conversations · ganesha* · guardians ·     │                │
  │  system_health · automobile                               │                │
  │                                                            │                │
  │  ┌──────────────────────────────────────────────────────┐ │                │
  │  │  NEW: device registration + notification dispatch     │─┘                │
  │  │  device_tokens collection · APNs credentials ·        │                  │
  │  │  channel-agnostic dispatcher (email/SMS/web-push/APNs)│                  │
  │  └──────────────────────────────────────────────────────┘                  │
  └────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 Architectural principles for any iOS client

| # | Principle |
|---|---|
| **AP-1** | **Thin client, thick backend.** No domain logic — no pricing, no GST computation, no orchestration, no model selection — is reimplemented on the device. The app renders and interacts; the backend decides. |
| **AP-2** | **One contract, three clients.** The app consumes the identical `ApiResponse`-enveloped REST API the web client uses, with the same JWT auth and the same five-role RBAC. No mobile-only endpoints except device registration. |
| **AP-3** | **Read-cached, never write-cached.** Cached data is for display continuity only, always labelled with its retrieval time, and never the basis for a write. No offline mutation queue. |
| **AP-4** | **Narrow by design.** Alerting and triage, not parity. Every feature beyond that scope requires written justification. |
| **AP-5** | **Secure by default.** Keychain-only credentials, biometric gate, auto-lock on background, certificate pinning, no plaintext persistence, no third-party SDK with data access. |

---

## 3. Technology Stack

### 3.1 Current stack

**None.** There is no iOS technology stack because there is no iOS project. No language, framework, dependency manager, build system or signing configuration has been chosen or configured.

### 3.2 Conditional stack decision

The framework choice would be recorded as an Architecture Decision Record before any code is written. The three candidates, assessed against Go4Garage's actual position:

| Option | Fit for Kailash | Assessment |
|---|---|---|
| **Native Swift / SwiftUI** | Best native integration (APNs, Face ID, widgets, Dynamic Type, VoiceOver); no cross-platform reuse; requires Swift skills the team does not evidently have; requires macOS for all development | **Preferred if iOS-only and quality bar is high** |
| **React Native (or Expo)** | Reuses the team's existing React 19 and JavaScript expertise (the web app is React); shares TypeScript models with the web client; Expo simplifies APNs and build tooling; some native-capability friction | **Preferred if both iOS and Android are wanted** — highest reuse of existing skills |
| **Flutter** | Single codebase for both platforms, strong performance; introduces Dart, a language with no presence in the Go4Garage stack | **Not recommended** — no existing Dart competency to leverage |

**Recommendation, conditional:** if a mobile client is ever built and Android is also wanted (likely, given the Indian device market), **React Native with Expo** maximises reuse of the existing React competency and allows shared TypeScript API models with the web client. If iOS-only with a premium quality bar, **SwiftUI**.

### 3.3 Conditional stack detail — SwiftUI variant

| Layer | Technology |
|---|---|
| Language | Swift 5.9 or later |
| UI | SwiftUI, with UIKit interop only where necessary |
| Minimum deployment target | Current iOS major minus 2 |
| Concurrency | Swift Concurrency (`async`/`await`, structured tasks) |
| Networking | `URLSession` with a typed client layer; `Codable` models mirroring the `ApiResponse` envelope |
| Credential storage | Keychain Services, protection class `kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly` |
| Biometrics | `LocalAuthentication` (`LAContext`), device-passcode fallback |
| Push | `UserNotifications` plus APNs; token registered with the backend |
| Local cache | Core Data or SQLite via GRDB, encrypted, read-only semantics |
| Dependency management | Swift Package Manager |
| Build | Xcode, `xcodebuild` on macOS CI |
| Test | XCTest (unit), XCUITest (UI), plus snapshot testing |
| Distribution | TestFlight (beta), Apple Business Manager custom app (production) |

### 3.4 Conditional stack detail — React Native / Expo variant

| Layer | Technology |
|---|---|
| Language | TypeScript |
| Framework | React Native with Expo (managed or bare, per capability needs) |
| Navigation | React Navigation |
| Server state | TanStack Query — **same library as the web app**, enabling shared query patterns |
| Client state | Zustand — **same library as the web app** |
| HTTP | Axios or `fetch` with a shared typed client |
| Schema validation | Zod — **same library as the web app**, enabling literally shared API schemas |
| Credential storage | `expo-secure-store` (Keychain-backed) |
| Biometrics | `expo-local-authentication` |
| Push | `expo-notifications` over APNs |
| Build | EAS Build (hosted macOS), removing the local-Mac prerequisite |
| Test | Jest plus React Native Testing Library; Detox or Maestro for E2E |
| Distribution | TestFlight, then Apple Business Manager |

The React Native path's decisive advantage is that **Zod schemas, TypeScript API models and TanStack Query keys can be shared with the existing web client**, directly mitigating the contract-drift risk (WTR-1 in the web TRD, IR-8 in the iOS BRD).

---

## 4. Functional Requirements

> All requirements in this section are **conditional** — they apply only upon an approved decision to build.

| ID | Requirement | Acceptance criteria |
|---|---|---|
| **FR-iOS-1** | **Backend contract reuse.** The app shall consume the existing Kailash REST API with no mobile-specific business endpoints, decoding the `ApiResponse` success envelope and the `{ ok: false, error: { code, message, hint }, request_id }` error envelope into typed models, branching on `error.code` and never on `message` text. | Decode fixtures for each documented error code into distinct typed cases; a wording change in `message` causes no behavioural change. |
| **FR-iOS-2** | **Authentication.** The app shall obtain a JWT via the existing auth endpoint, attach it as `Authorization: Bearer <token>` on every authenticated request, refresh or re-authenticate before the 24-hour expiry, and on any 401 shall clear the session and return to the sign-in screen without a retry loop. | Force an expired token; the app returns cleanly to sign-in with a user-visible message; network inspection shows no retry storm. |
| **FR-iOS-3** | **Two-factor challenge.** Where the account has 2FA enabled, the app shall present a native OTP entry supporting TOTP codes and single-use backup codes, with correct keyboard type, autofill from the system where available, and inline error handling that preserves entry state. | 2FA account cannot sign in without a code; an invalid code shows an inline error; a consumed backup code is rejected. |
| **FR-iOS-4** | **Biometric session gate.** After initial sign-in, the app shall gate resumption behind Face ID or Touch ID via `LocalAuthentication`, falling back to the device passcode, and shall auto-lock after a configurable background interval (default 5 minutes). Biometric failure shall never grant access. | Background past the interval; resumption requires biometric or passcode; cancelling the prompt returns to a locked state, not to content. |
| **FR-iOS-5** | **Credential storage.** The JWT and any 2FA state shall be stored exclusively in the iOS Keychain with `kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly` (or stricter), never in `UserDefaults`, never in plaintext files, and never emitted to logs or crash reports. | Filesystem and log inspection on a jailbroken or simulator device finds no token outside the Keychain. |
| **FR-iOS-6** | **APNs registration.** On notification permission grant, the app shall register for remote notifications, obtain the APNs device token, and upload it to the backend device-registration endpoint with the user identity, device identifier and app version. On sign-out it shall deregister the token. | Register on device A; a server-side dispatch reaches device A. Sign out; the same dispatch no longer reaches device A. |
| **FR-iOS-7** | **Notification payloads and deep links.** Push payloads shall carry a typed `category` (anomaly, sla_breach, guardian_escalation, task_assigned, system_incident) and a target identifier. Tapping a notification shall route directly to the corresponding screen with the correct record loaded, from cold start, from background and from foreground. | Test all three app states for each of the five categories; the correct screen loads with the correct record in all fifteen cases. |
| **FR-iOS-8** | **In-context permission requests.** Notification permission shall be requested only after the user has been shown its purpose, never at first launch, and the app shall remain fully functional if denied, offering a route to Settings for later enablement. | Fresh install requests no permission until the user reaches the alerts feature; declining leaves all non-alert functionality intact. |
| **FR-iOS-9** | **Minimal device permissions.** The app shall declare in `Info.plist` only the permissions it actually uses, each with a specific purpose string naming the concrete benefit. At MVP scope, only `NSFaceIDUsageDescription` is required. Camera, microphone, photo library, location, contacts and calendar shall **not** be requested unless a corresponding feature exists. | `Info.plist` audit — every declared usage key maps to a shipped feature. |
| **FR-iOS-10** | **Executive read view.** The app shall present a phone-first summary of platform health — overall status, department status counts, open alerts by severity, and task load — legible at a glance without scrolling on a standard iPhone. | An executive extracts current platform status within 5 seconds on a 6.1-inch device without scrolling. |
| **FR-iOS-11** | **Alert feed and triage.** The app shall list current alerts sorted by severity and recency, allow filtering by severity and department, and support acknowledge, assign, reassign, status change and comment — each reachable in three taps or fewer from a notification tap. | Tap-count measurement for each action from a cold notification; all within budget. |
| **FR-iOS-12** | **Department views.** The app shall list all departments from the backend registry with status, and provide a detail view per department, resolving names case-insensitively and showing a native not-found state for unknown names. | List count matches the backend registry; each detail loads; an invented name shows the not-found state without a crash. |
| **FR-iOS-13** | **Task views.** The app shall list tasks assigned to or relevant to the signed-in user, with detail, status change and comment, reflecting changes to the backend immediately and reconciling optimistic updates against the server response. | Change a status on device; the web client reflects it on refresh; a rejected change reverts the optimistic update with a clear message. |
| **FR-iOS-14** | **GANESHA conversational access.** The app shall submit a prompt to the orchestration endpoint, display the composed response with department attribution, handle long-running responses with a progress state and a timeout, and list prior conversations. | The same prompt returns equivalent content on iOS and web; a slow response shows progress and does not appear frozen; conversations persist across sessions. |
| **FR-iOS-15** | **Role-aware presentation.** The app shall render controls conditionally on the signed-in user's role and permissions, matching the backend's five-role model, and shall present no control whose backend call would be rejected. | For each role, enumerate visible controls and exercise each; zero authorisation errors. |
| **FR-iOS-16** | **Excluded administrative surfaces.** The app shall provide no user administration, no RBAC modification and no platform settings modification, for any role. | Code and UI audit confirms absence for all roles. |
| **FR-iOS-17** | **Offline and degraded behaviour.** With no connectivity, the app shall display last-known cached content clearly labelled with its retrieval time, shall refuse write actions with an explicit message rather than queuing them, and shall never present a blank screen or an indefinite spinner. | Airplane Mode mid-session: cached views show staleness labels; a write attempt is refused clearly; every screen has a defined offline state. |
| **FR-iOS-18** | **Human Interface Guidelines conformance.** The app shall use native navigation patterns, standard system controls, correct safe-area handling (including the Dynamic Island where present), native pull-to-refresh, standard share and back gestures, and shall not imitate another platform's idioms. | HIG review checklist completed and signed off. |
| **FR-iOS-19** | **Dynamic Type and Dark Mode.** All text shall scale with Dynamic Type up to the largest accessibility sizes without truncation, clipping or overlap, and every screen shall render correctly in both light and dark appearance. | Screenshot matrix: every screen at default and largest accessibility text size, in both appearances. |
| **FR-iOS-20** | **VoiceOver support.** Every interactive element shall have an accessible label, value and trait; navigation order shall be logical; and all core journeys shall be completable using VoiceOver alone. | VoiceOver-only traversal completes sign-in, alert triage, department detail and task status change. |
| **FR-iOS-21** | **Device and OS coverage.** The app shall support the current iOS major version and the two preceding majors, on iPhone (small through large) and iPad (at minimum a correct scaled experience, ideally adaptive layout). | Functional pass on the oldest supported OS, the newest OS, one small iPhone, one large iPhone and one iPad. |
| **FR-iOS-22** | **Version compatibility guard.** The app shall send its version to the backend and shall present a blocking upgrade prompt when the backend reports the client version as unsupported, rather than failing in undefined ways against an incompatible contract. | Configure the backend to reject the installed version; the app shows the upgrade prompt and blocks further use. |
| **FR-iOS-23** | **No forked logic.** All pricing, GST/HSN treatment, orchestration, model routing and anomaly scoring shall come from the backend; the app shall not compute or hard-code any of it. | Code review; changing a backend rule changes app behaviour with no app release. |
| **FR-iOS-24** | **Remote sign-out.** A server-side session revocation shall sign the device out on its next request, and the app shall clear Keychain material and cached data on sign-out. | Revoke server-side; the next app request returns to sign-in; filesystem inspection shows no residual token or cached platform data. |

---

## 5. Non-Functional Requirements

> Conditional — applicable only to a built client.

### 5.1 Performance

| ID | Requirement |
|---|---|
| NFR-iOS-P1 | Cold launch to first interactive content under **2 s** on the oldest supported device. |
| NFR-iOS-P2 | Warm launch (biometric unlock to content) under **1 s**. |
| NFR-iOS-P3 | Scrolling in all list views sustains **60 fps** (120 fps on ProMotion displays) with no dropped-frame hitches on a 200-item list. |
| NFR-iOS-P4 | Notification delivery to visible banner within **60 s** of the server-side trigger under normal network conditions. |
| NFR-iOS-P5 | Installed app size under **50 MB** at MVP scope. |
| NFR-iOS-P6 | No measurable battery impact beyond normal foreground use; no background polling — push only. |
| NFR-iOS-P7 | Cellular data use minimised: request only visible data, paginate lists, and never prefetch large payloads on a metered connection. |

### 5.2 Scalability

| ID | Requirement |
|---|---|
| NFR-iOS-S1 | The device-token store shall support one user across multiple devices and one device across sequential users, without cross-delivery of notifications. |
| NFR-iOS-S2 | Notification dispatch shall be batched and rate-limited server-side so that a mass alert event does not overwhelm APNs or the backend. |
| NFR-iOS-S3 | List views shall paginate; no screen shall load an unbounded collection. |
| NFR-iOS-S4 | The app shall function correctly as the department registry grows beyond its current 20 entries, with no hard-coded department list. |

### 5.3 Security

| ID | Requirement |
|---|---|
| NFR-iOS-Sec1 | TLS 1.2 or 1.3 for all network traffic, with App Transport Security enforced and no exceptions in `Info.plist`. |
| NFR-iOS-Sec2 | Certificate pinning against the Kailash API certificate, with a documented rotation procedure so pinning does not become an outage source. |
| NFR-iOS-Sec3 | Credentials exclusively in the Keychain with a device-only, after-first-unlock protection class; nothing sensitive in `UserDefaults`, plists or plaintext files. |
| NFR-iOS-Sec4 | Biometric gate on resume plus auto-lock on background (FR-iOS-4). |
| NFR-iOS-Sec5 | Sensitive screens obscured in the app switcher snapshot. |
| NFR-iOS-Sec6 | Jailbreak detection with a documented policy response (warn, restrict privileged actions, or block) for a client with privileged platform access. |
| NFR-iOS-Sec7 | No third-party analytics, advertising, attribution or session-replay SDK. Crash reporting, if adopted, must not transmit personal or platform data. |
| NFR-iOS-Sec8 | No sensitive value written to `NSLog`, `os_log` at a public level, or crash-report metadata. |
| NFR-iOS-Sec9 | Cached platform data stored encrypted at rest and purged completely on sign-out and on remote revocation. |
| NFR-iOS-Sec10 | Model-generated content rendered as text; no web view rendering of untrusted HTML; any web view used shall disable JavaScript unless a specific need is justified. |
| NFR-iOS-Sec11 | Deep links and universal links validated and authenticated before acting; a link shall never bypass the biometric gate or the auth check. |
| NFR-iOS-Sec12 | For privileged roles, device enrolment in Go4Garage MDM shall be a distribution precondition. |

### 5.4 Availability

| ID | Requirement |
|---|---|
| NFR-iOS-A1 | The app shall launch and present a usable shell even when the backend is unreachable, showing an explicit backend-unavailable state. |
| NFR-iOS-A2 | Failed requests shall retry with bounded exponential backoff, then surface an error state with manual retry — never an infinite spinner. |
| NFR-iOS-A3 | Crash-free session rate **99.5% or better**. |
| NFR-iOS-A4 | A broken release shall be withdrawable and a prior build re-promotable through App Store Connect / Apple Business Manager within **4 hours**. |
| NFR-iOS-A5 | The app shall tolerate additive backend changes (new fields) without crashing; unknown fields are ignored, not fatal. |

### 5.5 Compliance

| ID | Requirement |
|---|---|
| NFR-iOS-C1 | **App Store Review Guidelines** conformance for the chosen distribution channel, including guideline 2.1 (completeness), 4.2 (minimum functionality), 5.1 (privacy), and the business-app provisions if distributed via Apple Business Manager. |
| NFR-iOS-C2 | **App Privacy disclosure** (privacy nutrition label) accurately reflecting all data collected — which at MVP scope should be limited to account identity and diagnostic data, with no tracking. |
| NFR-iOS-C3 | **Data residency:** the app shall persist no personal or platform data beyond the encrypted read cache and Keychain credentials, and shall transmit only to Go4Garage-controlled endpoints. APNs relay metadata (a necessary Apple dependency) shall be disclosed in the sub-processor list. |
| NFR-iOS-C4 | **Accessibility:** VoiceOver, Dynamic Type, sufficient contrast, and Reduce Motion respect — meeting Apple's accessibility expectations and, by extension, the WCAG 2.1 AA spirit applied to the web surface. |
| NFR-iOS-C5 | **GST/HSN:** where the app displays priced automotive values, it shall display the HSN code and GST rate supplied by the backend and shall never compute or infer tax locally. |
| NFR-iOS-C6 | **DISCOM/energy:** where charger or energy values are displayed, forecast values shall be visually distinguished from measured values, matching the parent product requirement. |
| NFR-iOS-C7 | **Export compliance:** the standard encryption exemption declaration shall be completed accurately for App Store Connect. |
| NFR-iOS-C8 | **Retention:** cached platform data on device shall be covered by the published data-retention policy, and the policy shall be updated to describe mobile caching if an app ships. |

### 5.6 Maintainability

| ID | Requirement |
|---|---|
| NFR-iOS-M1 | API models shall be generated from, or validated against, the backend OpenAPI schema — not hand-maintained in parallel. |
| NFR-iOS-M2 | If React Native is chosen, Zod schemas and TypeScript API types shall be **physically shared** with the web client, not duplicated. |
| NFR-iOS-M3 | The app shall be buildable and testable in CI without a developer's local machine (hosted macOS runner or EAS Build). |
| NFR-iOS-M4 | Annual iOS major-version compatibility work shall be an explicitly budgeted maintenance item. |
| NFR-iOS-M5 | The minimum supported iOS version shall be reviewed annually and raised in step with the current-minus-two policy. |

---

## 6. Data Model / Storage

### 6.1 Current state

**No data model exists**, because no application exists. No Core Data model, no SQLite schema, no `UserDefaults` keys, no Keychain items are defined anywhere for Kailash on iOS.

### 6.2 Conditional on-device storage inventory

| Store | Contents | Protection | Lifetime |
|---|---|---|---|
| **Keychain** | JWT session token; refresh state; device identifier | `kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly`; device-only, non-syncing | Until sign-out, expiry or remote revocation |
| **Encrypted local cache** (Core Data / GRDB / SQLite) | Last-known departments, alerts, tasks, executive summary — **read-only, never authoritative** | File protection `NSFileProtectionComplete` | Purged on sign-out; entries expire after a defined TTL |
| **`UserDefaults`** | Non-sensitive preferences only: theme, notification category preferences, last-selected filters, auto-lock interval | None required | Persistent |
| **In-memory** | View-model state, in-flight requests, decoded responses | — | App lifetime |
| **Not stored anywhere** | Passwords, TOTP secrets, backup codes, AI provider keys, the internal platform token, any database credential | — | — |

### 6.3 Backend additions required

An iOS client would require **one new backend capability** — device registration and notification dispatch. Nothing else in the data model changes.

| Entity | Fields | Store |
|---|---|---|
| **DeviceToken** | `id`, `user_id`, `platform` (`ios`/`android`/`web`), `token`, `app_version`, `os_version`, `device_model`, `created_at`, `last_seen_at`, `revoked_at` | MongoDB (new collection, indexed on `user_id` and `token`) |
| **NotificationPreference** | `user_id`, `category`, `enabled`, `min_severity`, `quiet_hours` | MongoDB |
| **NotificationDispatch** | `id`, `user_id`, `device_token_id`, `category`, `target_id`, `payload`, `channel`, `status`, `sent_at`, `error` | MongoDB (audit and delivery tracking) |

**Design requirement:** the dispatcher shall be **channel-agnostic** — a single dispatch record can target email, SMS, web push or APNs. This is deliberate: it means the notification infrastructure delivers value immediately (via email/SMS) without an app, and an app becomes an additional channel rather than a prerequisite. This directly supports milestone IM-3 in the companion BRD.

### 6.4 Caching rules

| Rule | Statement |
|---|---|
| CR-1 | Cached data is display-only. No write action may be derived from, or validated against, a cached value. |
| CR-2 | Every cached view displays its retrieval timestamp when the data is older than a defined freshness threshold. |
| CR-3 | Cache entries expire after a category-specific TTL (alerts: 5 minutes; departments: 1 hour; executive summary: 15 minutes). |
| CR-4 | The entire cache is purged on sign-out, on remote revocation, and on a detected role change. |
| CR-5 | No offline write queue exists. Attempted writes without connectivity are refused with a clear message. |

---

## 7. API & Integration Points

### 7.1 Primary integration — the Kailash backend

An iOS client would consume the **identical API** described in `../TRD_kailash_ai.md` §7, with no mobile-specific business endpoints.

| Aspect | Detail |
|---|---|
| Base URL | `https://api.kailash-ai.in` (production); configurable per build variant |
| Transport | HTTPS, JSON, TLS 1.2/1.3, certificate-pinned |
| Auth | `Authorization: Bearer <JWT>` — same HS256 token, same 24-hour lifetime, same five-role RBAC |
| Correlation | `x-request-id` sent per request; surfaced in error displays for support correlation |
| Envelope | `ApiResponse` on success; `{ ok, error: { code, message, hint }, request_id }` on failure |
| Rate limiting | The proxy enforces 30 r/s general and 5 r/s on auth paths; the client must respect these and back off |

**Consumed routers:** auth, departments, department_intelligence, tasks, gaps_tasks_crud, dashboard, analytics (summary only), conversations, ganesha (v2 preferred), guardians, system_health, automobile (read only).

**Not consumed:** users, rbac, settings, knowledge_base management, scheduler_api — excluded by FR-iOS-16.

### 7.2 New backend integration required

| Endpoint | Purpose |
|---|---|
| `POST /api/devices/register` | Register an APNs token against the signed-in user |
| `DELETE /api/devices/{id}` | Deregister on sign-out |
| `GET/PUT /api/notifications/preferences` | Per-user, per-category notification preferences |
| Internal dispatch service | Channel-agnostic notification fan-out (email, SMS, web push, APNs) |

**None of this exists today.** The backend has no push infrastructure of any kind.

### 7.3 Third-party integrations

| Integration | Status / requirement |
|---|---|
| **APNs (Apple Push Notification service)** | **Would be required.** Not currently configured anywhere. Requires an APNs authentication key or certificate held in the backend's secret store. |
| **Firebase Cloud Messaging** | Optional alternative to direct APNs (FCM can relay to APNs). Go4Garage already uses Firebase (project `kailash-38268`), so FCM would allow one dispatch path serving both iOS and Android. **Recommended if both platforms are ever built.** |
| **Firebase (other services)** | The backend holds Firebase Admin SDK configuration; the iOS client would need `GoogleService-Info.plist` only if FCM or another Firebase client service is adopted. |
| **TestFlight** | Required for beta distribution. |
| **Apple Business Manager** | Required for private production distribution. |
| **Crash reporting** | Optional. If adopted, it must not transmit personal or platform data (NFR-iOS-Sec7). |
| **Payment gateway** | **Not applicable.** Kailash has no billing surface; no in-app purchase or subscription would exist. |
| **SMS / voice provider** | **Not applicable to the client.** Alerting via SMS is a backend dispatch channel, not an app integration. |
| **Slack** | **Not present** anywhere in Kailash; not proposed. |
| **`KAILASH_AI_URL`-style internal integration** | **Not applicable.** That environment-variable convention is how other Go4Garage *products* (notably ARJUN / `ev-vidya-arjun`) locate the Kailash backend. A first-party iOS client would use its own build-time base-URL configuration against the same host. |
| **Third-party analytics / advertising** | **Prohibited** by NFR-iOS-Sec7. |

---

## 8. Infrastructure & Deployment

### 8.1 Current reality

**Nothing is deployed, because nothing is built.**

| Item | Status |
|---|---|
| Xcode project / workspace | **Does not exist** |
| Source code (any language) | **Does not exist** |
| Bundle identifier | **Not registered** |
| Apple Developer Program membership | **Not held** (unverified — no evidence in this workspace) |
| Apple Business Manager enrolment | **Not held** (unverified) |
| App Store Connect record | **Does not exist** |
| TestFlight build | **Does not exist** |
| Signing certificate / provisioning profile | **Does not exist** |
| APNs authentication key | **Does not exist** |
| iOS CI job | **Does not exist** — `.github/workflows/ci.yml` defines only `lint`, `shared`, `services`, `backend`, `frontend`, `compose-build` |
| macOS build capacity | **Not available** — the observed development environment is Windows 11 |
| `ios_app_kailash_ai/deployed/` | **Empty** |
| `ios_app_kailash_ai/not_deployed/` | **Empty** |

### 8.2 What is deployed for Kailash

For completeness, and to make the contrast explicit:

| Component | Deployment status |
|---|---|
| Backend | Docker/Compose and Vultr VPS tooling present; **live status not verified** from this working copy |
| Frontend | Firebase Hosting configuration present (project `kailash-38268`), built bundle present; **live status not verified** |
| iOS app | **Does not exist** — nothing to deploy |
| Android app | **Does not exist** — nothing to deploy |

### 8.3 Conditional deployment pipeline

| Stage | Mechanism |
|---|---|
| Prerequisites | Apple Developer Program membership; Apple Business Manager enrolment; bundle identifier registered; APNs key generated; signing certificates and provisioning profiles created |
| Build capacity | Hosted macOS CI runner (GitHub Actions `macos-latest`) or EAS Build if React Native/Expo — avoids a local-Mac dependency |
| CI | New workflow running lint, unit tests, UI tests and a signed archive build on every pull request |
| Versioning | Semantic version plus monotonic build number, injected from CI |
| Beta | TestFlight with a defined internal tester group; release notes mandatory per build |
| Production | Apple Business Manager custom app distribution — **not** the public App Store |
| Rollback | Withdraw the release and re-promote the prior build; target under 4 hours (NFR-iOS-A4) |
| Secret handling | Signing certificates, provisioning profiles and the APNs key stored in the CI secret store; never committed |
| Monitoring | Crash-free session rate, notification delivery rate, version-adoption distribution |

### 8.4 Environment configuration

| Variant | Backend base URL | Distribution |
|---|---|---|
| Debug | `http://localhost:8000` or a developer's Compose backend | Simulator / local device |
| Staging | Staging backend (**does not exist today** — no staging environment is defined for Kailash) | TestFlight internal group |
| Production | `https://api.kailash-ai.in` | Apple Business Manager |

Note: the parent TRD records that **no staging environment exists** for Kailash. A mobile client would create pressure to build one, since testing pre-release mobile builds against production is poor practice. That cost belongs in any business case.

---

## 9. Security & Compliance Requirements

> Conditional — applicable only to a built client. Consolidated here for a security reviewer.

### 9.1 Device and data security

| ID | Control |
|---|---|
| SEC-iOS-1 | Keychain-only credential storage, device-only non-syncing protection class. |
| SEC-iOS-2 | Biometric gate on resume with passcode fallback; auto-lock on background after a configurable interval. |
| SEC-iOS-3 | Encrypted local cache with `NSFileProtectionComplete`; full purge on sign-out and on remote revocation. |
| SEC-iOS-4 | App-switcher snapshot obscured on sensitive screens. |
| SEC-iOS-5 | Jailbreak detection with a documented policy response. |
| SEC-iOS-6 | No sensitive value in logs, crash metadata or analytics payloads. |
| SEC-iOS-7 | Copy/paste of sensitive fields restricted where appropriate. |

### 9.2 Network security

| ID | Control |
|---|---|
| SEC-iOS-8 | TLS 1.2/1.3 only; App Transport Security enforced with no `Info.plist` exceptions. |
| SEC-iOS-9 | Certificate pinning with a documented rotation runbook. |
| SEC-iOS-10 | The client never holds an AI provider key, a Firebase Admin credential or the internal platform token. |
| SEC-iOS-11 | Deep links and universal links authenticated and validated before acting; never a bypass of the auth or biometric gate. |
| SEC-iOS-12 | Respect the backend's proxy rate limits (30 r/s general, 5 r/s auth); implement client-side backoff. |

### 9.3 Application security

| ID | Control |
|---|---|
| SEC-iOS-13 | Model-generated content rendered as text; no untrusted HTML in a web view; JavaScript disabled in any web view unless justified. |
| SEC-iOS-14 | Server-side RBAC is the authorisation boundary; client gating is presentation only. |
| SEC-iOS-15 | No user administration, RBAC change or settings change available in the app for any role. |
| SEC-iOS-16 | Remote sign-out invalidates the device session on next request. |
| SEC-iOS-17 | Minimum-supported-version enforcement prevents an outdated client operating against an incompatible contract. |
| SEC-iOS-18 | Dependency vulnerability scanning in the mobile CI pipeline. |

### 9.4 Distribution and compliance

| ID | Control |
|---|---|
| SEC-iOS-19 | Private distribution via Apple Business Manager; not published to the public App Store. |
| SEC-iOS-20 | Accurate App Privacy disclosure; no tracking; minimal data categories. |
| SEC-iOS-21 | MDM enrolment required for devices used by privileged roles. |
| SEC-iOS-22 | Data-residency position documented, including APNs as an Apple-operated relay in the sub-processor list. |
| SEC-iOS-23 | Export-compliance declaration completed accurately. |
| SEC-iOS-24 | Annual mobile security review, including a penetration test of the client and its API usage. |

---

## 10. Testing Strategy

> Conditional — applicable only to a built client.

### 10.1 Current state

**No iOS tests exist**, because no iOS code exists. The Kailash CI pipeline contains no mobile job of any kind.

### 10.2 Conditional test layers

| Layer | Tooling | Scope |
|---|---|---|
| Unit | XCTest (SwiftUI) or Jest (React Native) | View models, API decoding, error mapping, cache TTL logic, auth state machine |
| Contract | Fixture-driven decoding tests generated from the backend OpenAPI schema | Every endpoint's success and error envelope decodes to the correct typed model |
| UI / integration | XCUITest or Detox/Maestro | Sign-in with and without 2FA, biometric gate, alert triage, task status change, department detail, GANESHA prompt |
| Notification | Simulated APNs payloads across cold, background and foreground states | All five categories deep-link correctly in all three app states |
| Accessibility | XCUITest accessibility audit plus manual VoiceOver traversal | All core journeys VoiceOver-completable; Dynamic Type at maximum size |
| Snapshot | Snapshot testing across device sizes, appearances and text sizes | Layout integrity matrix |
| Security | Static analysis, filesystem and log inspection, jailbroken-device testing, pinning verification | No credential leakage; pinning effective |
| Performance | Instruments (Time Profiler, Allocations, Energy) | Launch time, scroll performance, memory, battery |
| Compatibility | Device farm or physical matrix | Oldest and newest supported iOS; small iPhone, large iPhone, iPad |
| Regression | Full suite in CI on every pull request | No merge on red |

### 10.3 Conditional test requirements

| ID | Requirement |
|---|---|
| TEST-iOS-1 | Contract tests shall decode a fixture for every consumed endpoint, including every documented error code; a backend schema change that breaks decoding shall fail CI. |
| TEST-iOS-2 | Auth tests shall cover valid sign-in, invalid password, 2FA challenge, valid TOTP, backup-code single use, token expiry, 401 handling, biometric success, biometric cancel, biometric unavailable, and remote revocation. |
| TEST-iOS-3 | Notification tests shall verify all five categories across cold start, background and foreground — fifteen cases — each landing on the correct screen with the correct record. |
| TEST-iOS-4 | Role tests shall verify, for each of the five roles, that the visible control set matches the permitted permission set and that no visible control produces an authorisation error. |
| TEST-iOS-5 | Offline tests shall verify staleness labelling, write refusal, and the absence of any silent queue. |
| TEST-iOS-6 | Accessibility tests shall verify VoiceOver completion of all core journeys and layout integrity at the largest Dynamic Type size. |
| TEST-iOS-7 | Security tests shall verify Keychain-only storage, no tokens in logs or the filesystem, effective certificate pinning, app-switcher obscuring, and complete purge on sign-out. |
| TEST-iOS-8 | Performance tests shall assert cold launch under 2 s, warm launch under 1 s, and 60 fps scrolling on the oldest supported device. |
| TEST-iOS-9 | Compatibility tests shall pass on the oldest and newest supported iOS versions across at least three device classes. |
| TEST-iOS-10 | A pre-submission checklist shall verify App Store Review Guideline conformance, App Privacy disclosure accuracy, `Info.plist` purpose-string correctness, and export-compliance declaration. |
| TEST-iOS-11 | Version-guard tests shall verify that an unsupported client version is blocked with an upgrade prompt. |
| TEST-iOS-12 | TestFlight beta shall run for a minimum defined period with a defined tester group before any production promotion. |

---

## 11. Current Implementation Status

### 11.1 Platform existence statement — iOS

> **No Kailash iOS application exists in code.**
>
> Verified 2026-07-31 at product HEAD commit `40cca17`. The directory `C:\Go4Garage( Eka)\Kailash-Ai\ios_app_kailash_ai\` contains **only two empty subdirectories** — `deployed/` and `not_deployed/` — plus the two documentation files this workstream is producing. There is no application source of any kind.
>
> **Kailash is presently a backend and web-only internal service.** It is Go4Garage's internal ML/AI platform, consumed by other Go4Garage products over HTTP (notably via the `KAILASH_AI_URL` environment-variable convention) and operated by staff through a single React 19 web dashboard. **No dedicated mobile client is planned**, unless the reader decides otherwise on the basis of the decision criteria in the companion BRD §11.1.

### 11.2 Detailed absence audit

| Artefact | Present? |
|---|---|
| `.xcodeproj` / `.xcworkspace` | **No** |
| Swift or Objective-C source files | **No** |
| React Native project (`package.json` with `react-native`, `metro.config.js`, `ios/` folder) | **No** |
| Expo project (`app.json`, `eas.json`) | **No** |
| Flutter project (`pubspec.yaml`, `lib/`, `ios/` folder) | **No** |
| `Info.plist` | **No** |
| Bundle identifier | **No** |
| Entitlements file | **No** |
| `Podfile` / Swift Package manifest | **No** |
| `GoogleService-Info.plist` | **No** |
| Asset catalogue / app icons / launch screen | **No** |
| Localisation files | **No** |
| App Store Connect record | **No** |
| TestFlight build | **No** |
| Provisioning profile / signing certificate | **No** |
| APNs authentication key | **No** |
| Backend device-token model | **No** |
| Backend notification dispatch service | **No** |
| Backend `/api/devices/*` endpoints | **No** |
| iOS job in `.github/workflows/ci.yml` | **No** — the six jobs are `lint`, `shared`, `services`, `backend`, `frontend`, `compose-build` |
| Any mobile-related dependency in `backend/requirements.txt` | **No** |
| macOS build capacity in the development environment | **No** — Windows 11 |

### 11.3 What exists in the product for contrast

| Component | Status |
|---|---|
| **FastAPI backend** | **Built, dependencies installed, run locally.** Roughly 24 API routers, 20 registered department agents, 3 guardian agents, 9 platform services, populated `backend/.venv/`. |
| **React 19 web app** | **Built and compiled.** Roughly 70 page modules, roughly 1,000 installed packages, compiled `frontend/build/` output, Firebase Hosting configuration with SPA rewrites and five security headers. |
| **Docker / Compose / Vultr / Nginx tooling** | **Present.** Live deployment status unverified from this copy. |
| **CI pipeline** | **Present** — six jobs, none mobile. |
| **iOS client** | **Absent.** |

### 11.4 Technical prerequisites before any iOS work could begin

| # | Prerequisite | Current state | Effort class |
|---|---|---|---|
| 1 | Approved business case (BR-iOS-22) | Not started | Governance |
| 2 | Framework ADR (SwiftUI vs React Native vs Flutter) | Not made | Days |
| 3 | Apple Developer Program membership | Not held | Days, plus annual fee |
| 4 | Apple Business Manager enrolment | Not held | Days |
| 5 | macOS build capacity (hosted runner or EAS Build) | Not available | Days, plus recurring cost |
| 6 | Backend device-token model and registration endpoints | **Does not exist** | Weeks |
| 7 | Backend channel-agnostic notification dispatcher | **Does not exist** | Weeks — *and independently valuable without an app* |
| 8 | APNs (or FCM) credentials and configuration | Not configured | Days |
| 9 | Staging environment for pre-release testing | **Does not exist** for Kailash | Weeks |
| 10 | Client-side schema validation shared with the web client | Not implemented on either client | Weeks — *and independently valuable* |
| 11 | Mobile engineering capacity | Not allocated | Ongoing |
| 12 | MDM baseline for privileged roles | Not defined | Weeks |

Items 7 and 10 are worth noting: both are **prerequisites for a mobile client that deliver value even if no mobile client is ever built**. A channel-agnostic notification dispatcher improves alerting today via email and SMS; shared schema validation hardens the web client against contract drift today. These should be built regardless of the mobile decision.

---

## 12. Technical Risks & Dependencies

### 12.1 Risks of the current position

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| TR-iOS-1 | The empty directory is misread as abandoned work. | High | Low | This document plus a README in the directory. |
| TR-iOS-2 | No push infrastructure exists at all, so time-critical alerts depend entirely on whatever email or chat path is in use. | Medium | High | Build the channel-agnostic dispatcher (prerequisite 7) independently of any mobile decision. |
| TR-iOS-3 | Mobile web on iOS Safari degrades untested, creating pressure for a native app that better web testing would have avoided. | Medium | Medium | Keep iOS Safari in the web app's tested matrix; test at 414 px and 360 px each release. |
| TR-iOS-4 | A reactive mobile build is commissioned without prerequisites 6, 7, 9 and 10, producing a fragile client. | Low | High | Enforce the prerequisite list as a gate in the business case. |

### 12.2 Risks that would attach to building

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| TR-iOS-5 | **Contract drift between three clients.** A backend change breaks iOS silently. | High | High | Generate API models from the OpenAPI schema; contract tests in CI; version guard (FR-iOS-22); share Zod schemas if React Native is chosen. |
| TR-iOS-6 | **No macOS build capacity** in a Windows development environment. | High | High | Hosted macOS CI runner or EAS Build; budget it explicitly. |
| TR-iOS-7 | **No staging environment** forces pre-release mobile testing against production. | High | High | Build a staging environment as a prerequisite; do not test mobile builds against production data. |
| TR-iOS-8 | **Apple review or policy change** blocks or delays release. | Medium | Medium | Private distribution via Apple Business Manager; pre-submission guideline checklist. |
| TR-iOS-9 | **Annual iOS major-version churn** imposes recurring cost with no feature value. | High | Medium | Budget maintenance explicitly; hold to the current-minus-two support policy; reassess the app annually against usage KPIs. |
| TR-iOS-10 | **Certificate pinning becomes an outage source** when the API certificate rotates. | Medium | High | Pin to the intermediate CA rather than the leaf, or pin multiple certificates; document and rehearse rotation. |
| TR-iOS-11 | **Platform credentials on personal devices** widen the breach surface. | Medium | High | Keychain-only, biometric gate, auto-lock, remote revocation, MDM for privileged roles, jailbreak policy. |
| TR-iOS-12 | **Notification fatigue** degrades alert response. | High | Medium | Severity thresholds, per-category preferences, quiet hours, digest batching. |
| TR-iOS-13 | **Framework lock-in** — the wrong choice among SwiftUI, React Native and Flutter. | Medium | Medium | Decide by ADR against explicit criteria; weight Android intent and existing React competency heavily. |
| TR-iOS-14 | **Scope creep toward web parity** turns a narrow triage client into a second full product. | High | High | Hard scope boundary (FR-iOS-16, §5.3 of the BRD); written justification for every addition. |
| TR-iOS-15 | **Cached stale data misleads a decision** — an operator acts on an out-of-date anomaly list. | Medium | High | Mandatory staleness labelling (CR-2), short TTLs (CR-3), refusal of writes derived from cache (CR-1). |
| TR-iOS-16 | **Two release cadences diverge**, with the app lagging backend capability. | Medium | Medium | Minimum-supported-version enforcement; additive-change tolerance (NFR-iOS-A5); coordinated release planning. |

### 12.3 Dependencies

| Dependency | Type | Criticality | Note |
|---|---|---|---|
| Kailash backend API | Internal | **Critical** | The app is useless without it |
| Backend push infrastructure | Internal | **Critical** | **Does not exist**; must be built first |
| Staging environment | Internal | High | **Does not exist**; needed for safe pre-release testing |
| Apple Developer Program | External | **Critical** | Not held |
| Apple Business Manager | External | **Critical** for private distribution | Not held |
| APNs | External | **Critical** for the core value proposition | Not configured |
| macOS build capacity | External | **Critical** | Not available |
| Firebase / FCM | External | Optional | Already in use for hosting; could serve as a unified push path for iOS and Android |
| Xcode and the Apple toolchain | External | **Critical** | Annual major-version churn |
| Chosen framework ecosystem | External | High | SwiftUI, React Native or Flutter — each with its own upgrade cadence |
| Mobile engineering capacity | Internal | **Critical** | Not allocated |

---

## 13. Appendix

### 13.1 Parent and sibling documents

| Document | Location | Relationship |
|---|---|---|
| **`BRD_kailash_ai.md`** | `../BRD_kailash_ai.md` | Parent product BRD — platform-wide business requirements |
| **`TRD_kailash_ai.md`** | `../TRD_kailash_ai.md` | Parent product TRD — the backend architecture, data model and API any client consumes |
| `BRD_ios_app_kailash_ai.md` | Same directory | Companion business requirements, including the decision criteria for building |
| `BRD_web_app_kailash_ai.md` / `TRD_web_app_kailash_ai.md` | `../web_app_kailash_ai/` | The one Kailash client that exists |
| `BRD_android_app_kailash_ai.md` / `TRD_android_app_kailash_ai.md` | `../android_app_kailash_ai/` | Sibling surface — records the equivalent no-app position for Android |

### 13.2 Directory contents, verbatim

```
ios_app_kailash_ai/
├── deployed/                    (empty — no build has ever been deployed)
├── not_deployed/                (empty — no build exists to be pending)
├── BRD_ios_app_kailash_ai.md
└── TRD_ios_app_kailash_ai.md    ← this document
```

### 13.3 Recommended `Info.plist` usage keys at MVP scope

| Key | Required? | Purpose string guidance |
|---|---|---|
| `NSFaceIDUsageDescription` | **Yes** | "Kailash uses Face ID to unlock your session without re-entering your password." |
| `NSCameraUsageDescription` | No | Only if a platform-level document-capture feature is added |
| `NSMicrophoneUsageDescription` | No | Only if voice input to GANESHA is added |
| `NSPhotoLibraryUsageDescription` | No | Not needed at MVP scope |
| `NSLocationWhenInUseUsageDescription` | No | Kailash has no location-dependent feature |
| `NSContactsUsageDescription` | No | Never required |
| `NSCalendarsUsageDescription` | No | Never required |

Requesting any permission without a shipped feature that uses it is an App Review rejection risk and a privacy-posture failure.

### 13.4 Notification category specification (conditional)

| Category | Trigger | Severity gate | Deep link target |
|---|---|---|---|
| `anomaly` | Anomaly service score above threshold | Configurable per user | Alert detail |
| `sla_breach` | SLA breach detected | Always | Alert detail |
| `guardian_escalation` | SHIV or GANESHA escalates | Always | Guardian detail |
| `task_assigned` | Task assigned to the signed-in user | Always | Task detail |
| `system_incident` | System-health incident | Always | System health |

### 13.5 Glossary

| Term | Meaning |
|---|---|
| **APNs** | Apple Push Notification service |
| **ATS** | App Transport Security — iOS enforcement of secure connections |
| **Keychain** | iOS secure credential storage |
| **Dynamic Type** | User-controlled system text sizing that apps must respect |
| **HIG** | Apple Human Interface Guidelines |
| **TestFlight** | Apple's beta distribution service |
| **Apple Business Manager** | Apple's private organisational app distribution channel |
| **MDM** | Mobile Device Management |
| **EAS Build** | Expo Application Services hosted build service |
| **ADR** | Architecture Decision Record |
| **`ApiResponse`** | The Kailash standard response envelope |

### 13.6 Open technical questions

1. Does Go4Garage hold an Apple Developer Program membership and Apple Business Manager enrolment?
2. Should the channel-agnostic notification dispatcher be built now, independent of any mobile decision? (Recommended: yes.)
3. Should client-side schema validation be added to the web client now, so that a future second client inherits it? (Recommended: yes.)
4. Should a staging environment be created for Kailash regardless of the mobile question?
5. If a mobile client is ever built, is FCM preferable to direct APNs given Firebase is already in the stack and Android would likely follow?
6. Which framework, and does Android intent change the answer?
7. What is the MDM baseline for devices holding a privileged Kailash session?
8. Given no macOS capacity exists, is EAS Build (implying React Native/Expo) effectively the deciding constraint?
