# Technical Requirements Document — Kailash-Ai Android Application

## 1. Document Control

| Field | Value |
|---|---|
| **Document title** | Technical Requirements Document — Kailash-Ai Android Application |
| **Product** | Kailash — Go4Garage internal ML/AI platform |
| **Surface** | Android (phone / tablet native client) |
| **Document type** | TRD (Application level) |
| **Version** | 1.0 |
| **Date** | 2026-07-31 |
| **Status** | Draft — **conditional design for a client that does not exist** |
| **Owner** | TBD |
| **Author** | Go4Garage Documentation Workstream |
| **Reviewers** | TBD (Platform Lead, Security, Mobile Lead if appointed) |
| **Approvers** | TBD |
| **Classification** | Internal — Proprietary |
| **Companion BRD** | `BRD_android_app_kailash_ai.md` (same directory) |
| **Parent product BRD** | `../BRD_kailash_ai.md` |
| **Parent product TRD** | `../TRD_kailash_ai.md` |
| **Source of truth** | `C:\Go4Garage( Eka)\Kailash-Ai\android_app_kailash_ai`, product HEAD commit `40cca17` dated 2026-07-31 |

### 1.1 Status notice

**No Android application exists.** See §11 for the formal existence statement. Sections 2 through 10 are a **conditional technical specification**: they describe what would be built, and to what standard, *if* a decision to build were approved against the criteria in the companion BRD §11.1. Nothing here describes shipped or in-progress work.

### 1.2 Revision History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0 | 2026-07-31 | Documentation Workstream | Initial draft. Records the no-client position and specifies the conditional technical design, including Android-specific delivery-reliability requirements. |

---

## 2. System / Architecture Overview

### 2.1 Current architecture — where Android sits

Kailash today has exactly two runtime tiers: a FastAPI backend and a React 19 web client. There is no third tier. An Android device reaches Kailash by loading the web application in Chrome for Android.

```
  CURRENT STATE (2026-07-31)
  ══════════════════════════

  ┌────────────────────┐  ┌──────────────────┐  ┌────────────────────────────────┐
  │ Android phone/tab  │  │ Desktop browser  │  │ Consumer products              │
  │  ┌──────────────┐  │  │                  │  │ URGAA · GSTSAAS · Ignition ·   │
  │  │ Chrome for   │  │  │ Chrome/Edge/     │  │ ARJUN (KAILASH_AI_URL)         │
  │  │ Android      │  │  │ Firefox/Safari   │  │                                │
  │  │ (mobile web) │  │  │                  │  │                                │
  │  └──────┬───────┘  │  └────────┬─────────┘  └───────────────┬────────────────┘
  │         │          │           │                            │
  │  ┌ ─ ─ ─┴ ─ ─ ─ ┐  │           │                            │
  │  │ NATIVE       │  │           │                            │
  │  │ ANDROID APP  │  │           │                            │
  │  │ ✗ DOES NOT   │  │           │                            │
  │  │   EXIST      │  │           │                            │
  │  └ ─ ─ ─ ─ ─ ─ ─┘  │           │                            │
  └─────────┬──────────┘           │                            │
            │                      │                            │
            └──────────┬───────────┴────────────────────────────┘
                       │  HTTPS
                       ▼
       ┌──────────────────────────────┐       ┌─────────────────────────────┐
       │ Firebase Hosting             │       │ Nginx → FastAPI backend     │
       │ React 19 SPA (build/)        │──────▶│ api.kailash-ai.in           │
       │ project kailash-38268        │       │ 20 departments · 3 guardians│
       └──────────────────────────────┘       │ · 9 platform services       │
                                              └──────────────┬──────────────┘
                                                             ▼
                                          MongoDB 7 · PostgreSQL 16 · Redis 7

       ✗ NO FCM messaging configuration exists (Firebase used for hosting only)
       ✗ NO device-token model exists
       ✗ NO notification dispatch service exists
       ✗ NO Android job exists in .github/workflows/ci.yml
       ✗ NO service worker / web push on the web app either
```

### 2.2 Conditional target architecture

Were an Android client approved, it would slot in as a **third client of the same backend**, adding one new backend capability (push dispatch) plus one Android-specific concern that has no iOS equivalent: **delivery-reliability mitigation against OEM battery management**.

```
  CONDITIONAL TARGET STATE (only if approved)
  ═══════════════════════════════════════════

  ┌────────────────────────────────────────────────────────────────────────────┐
  │                     ANDROID APP (phone / tablet)                           │
  │                                                                            │
  │  ┌──────────────────────────────────────────────────────────────────────┐  │
  │  │  PRESENTATION     Jetpack Compose (or RN/Flutter equivalent)         │  │
  │  │  ── Executive read · Alert feed · Departments · Tasks ──             │  │
  │  │  ── GANESHA chat · Settings (read-only) ──                          │  │
  │  │  Material 3 · dynamic colour · edge-to-edge · predictive back        │  │
  │  │  TalkBack · font scaling · 48dp targets · dark theme                 │  │
  │  └────────────────────────────────┬─────────────────────────────────────┘  │
  │  ┌────────────────────────────────▼─────────────────────────────────────┐  │
  │  │  STATE      ViewModels · StateFlow · navigation graph                 │  │
  │  └────────────────────────────────┬─────────────────────────────────────┘  │
  │  ┌────────────────────────────────▼─────────────────────────────────────┐  │
  │  │  API CLIENT   typed models mirroring ApiResponse envelope             │  │
  │  │  ── auth interceptor (Bearer JWT) · x-request-id · retry/backoff ──   │  │
  │  │  ── typed error mapping: not_found / validation_error / upstream ──   │  │
  │  └───────┬─────────────────┬──────────────────┬────────────────────────┘  │
  │  ┌───────▼──────┐ ┌────────▼─────────┐ ┌──────▼──────────────────────────┐ │
  │  │ ENCRYPTED    │ │ LOCAL CACHE      │ │ FCM SERVICE                     │ │
  │  │ STORAGE      │ │ (read-only)      │ │ token registration · high-      │ │
  │  │ Keystore-    │ │ Room, encrypted, │ │ priority message handling ·     │ │
  │  │ backed       │ │ stale-labelled,  │ │ deep-link routing · channel     │ │
  │  │ JWT · 2FA    │ │ purged on logout │ │ per notification category       │ │
  │  │ backup       │ └──────────────────┘ └──────┬──────────────────────────┘ │
  │  │ excluded     │ ┌──────────────────┐        │                            │
  │  └──────────────┘ │ BIOMETRIC GATE   │ ┌──────▼──────────────────────────┐ │
  │                   │ BiometricPrompt  │ │ ★ OEM BATTERY MITIGATION ★      │ │
  │                   │ device-credential│ │ restriction detection ·         │ │
  │                   │ fallback         │ │ OEM-specific exemption guidance │ │
  │                   └──────────────────┘ │ (Xiaomi/Oppo/Vivo/Realme/       │ │
  │                                        │  Samsung) · fallback signalling │ │
  │                                        └──────┬──────────────────────────┘ │
  └───────────────────────────┬───────────────────┼────────────────────────────┘
                              │ HTTPS · Bearer JWT│ FCM
                              ▼                   ▲
  ┌───────────────────────────────────────────────┼────────────────────────────┐
  │  NGINX (api.kailash-ai.in) → FastAPI BACKEND  │                            │
  │  existing routers: auth · departments · tasks · analytics · dashboard ·    │
  │  conversations · ganesha* · guardians · system_health · automobile         │
  │                                                                            │
  │  ┌──────────────────────────────────────────────────────────────────────┐ │
  │  │  NEW: device registration + channel-agnostic notification dispatch    │─┘
  │  │  device_tokens · notification_preferences · dispatch audit            │
  │  │  channels: email · SMS · web push · FCM                               │
  │  │  ★ per-device delivery tracking + automatic fallback on non-delivery ★│
  │  └──────────────────────────────────────────────────────────────────────┘
  └────────────────────────────────────────────────────────────────────────────┘
```

### 2.3 Architectural principles

| # | Principle |
|---|---|
| **AP-1** | **Thin client, thick backend.** No domain logic — no pricing, no GST computation, no orchestration, no model selection — on the device. |
| **AP-2** | **One contract, three clients.** Identical `ApiResponse`-enveloped REST API, identical JWT auth, identical five-role RBAC. No mobile-only business endpoints except device registration. |
| **AP-3** | **Read-cached, never write-cached.** Cached data is display-only, always labelled with retrieval time, never the basis for a write. No offline mutation queue. |
| **AP-4** | **Narrow by design.** Alerting and triage, not parity. |
| **AP-5** | **Assume delivery is unreliable.** Unlike iOS, Android push delivery cannot be assumed. Every alert path must have a defined non-push fallback, and delivery must be measured per OEM. |
| **AP-6** | **Design for the mid-range device.** Performance budgets are set against a 4 GB mid-tier device, not a flagship. |

---

## 3. Technology Stack

### 3.1 Current stack

**None.** No Android technology stack exists because no Android project exists. No language, framework, build system, dependency configuration or signing setup has been chosen.

### 3.2 Conditional framework decision

The choice would be recorded as an Architecture Decision Record before any code is written.

| Option | Fit for Kailash | Assessment |
|---|---|---|
| **Kotlin + Jetpack Compose** | Best native integration (FCM, BiometricPrompt, WorkManager, Material 3 dynamic colour); best performance on budget hardware; no cross-platform reuse; requires Kotlin skills the team does not evidently have | **Preferred if Android-only with a high quality bar and budget-device performance is critical** |
| **React Native (or Expo)** | Reuses the team's existing React 19 and JavaScript expertise (the web app is React); allows **literally shared Zod schemas and TypeScript API models with the web client**; Expo simplifies FCM and build tooling; some friction on deep native work such as OEM battery-exemption intents; heavier runtime on budget devices | **Preferred if both Android and iOS are wanted** — highest reuse of existing skills |
| **Flutter** | Single codebase for both platforms, strong rendering performance; introduces Dart, with no presence in the Go4Garage stack | **Not recommended** — no existing Dart competency to leverage |

**Recommendation, conditional:** given the parent BRD's position that Android would lead any mobile programme and that iOS would likely follow, **React Native with Expo** maximises reuse of the existing React competency and enables shared API schemas across all three clients — directly mitigating the contract-drift risk. If budget-device performance proves the binding constraint, **Kotlin + Compose** is the fallback.

### 3.3 Conditional stack detail — Kotlin / Compose variant

| Layer | Technology |
|---|---|
| Language | Kotlin (current stable) |
| UI | Jetpack Compose with Material 3 |
| Minimum SDK | API 26 (Android 8.0) — reviewed annually |
| Target SDK | Current Google Play policy requirement |
| Architecture | MVVM with ViewModel, StateFlow, Navigation Compose |
| Concurrency | Kotlin Coroutines and Flow |
| Networking | Retrofit with OkHttp; Kotlinx Serialization or Moshi for `ApiResponse` models |
| Dependency injection | Hilt |
| Local storage | Room with SQLCipher (encrypted); DataStore for non-sensitive preferences |
| Credential storage | EncryptedSharedPreferences backed by Android Keystore |
| Biometrics | `androidx.biometric` BiometricPrompt |
| Push | Firebase Cloud Messaging (`firebase-messaging`) |
| Background work | WorkManager (used sparingly — see §5.1 on battery) |
| Build | Gradle with Kotlin DSL; App Bundle (AAB) output |
| Test | JUnit, MockK, Turbine (Flow), Compose UI Test, Espresso |
| Distribution | Managed Google Play (private app) |

### 3.4 Conditional stack detail — React Native / Expo variant

| Layer | Technology |
|---|---|
| Language | TypeScript |
| Framework | React Native with Expo |
| Navigation | React Navigation |
| Server state | TanStack Query — **same library as the web app** |
| Client state | Zustand — **same library as the web app** |
| HTTP | Axios or `fetch` with a shared typed client |
| Schema validation | Zod — **same library as the web app**, enabling shared API schemas |
| Credential storage | `expo-secure-store` (Keystore-backed) |
| Biometrics | `expo-local-authentication` |
| Push | `expo-notifications` over FCM |
| Local storage | `expo-sqlite` with encryption, or WatermelonDB |
| Build | EAS Build; App Bundle output |
| Test | Jest, React Native Testing Library; Maestro or Detox for E2E |
| Distribution | Managed Google Play |

### 3.5 Firebase position

Go4Garage **already uses Firebase**: project `kailash-38268` hosts the web frontend, and the backend carries Firebase Admin SDK configuration (`FIREBASE_PROJECT_ID`, `FIREBASE_STORAGE_BUCKET`, service-account credentials, and a `FIREBASE_DISABLED` kill switch). FCM would therefore be an incremental configuration on an existing project rather than a new vendor relationship — a genuine cost advantage for Android over the iOS APNs path. FCM can also relay to APNs, so a single dispatch implementation could serve both platforms if iOS ever follows.

---

## 4. Functional Requirements

> All requirements in this section are **conditional** — they apply only upon an approved decision to build.

| ID | Requirement | Acceptance criteria |
|---|---|---|
| **FR-AND-1** | **Backend contract reuse.** The app shall consume the existing Kailash REST API with no mobile-specific business endpoints, decoding the `ApiResponse` success envelope and the `{ ok: false, error: { code, message, hint }, request_id }` error envelope into typed models, branching on `error.code` and never on `message` text. | Decode fixtures for each documented error code into distinct typed cases; a wording change in `message` causes no behavioural change. |
| **FR-AND-2** | **Authentication.** The app shall obtain a JWT via the existing auth endpoint, attach it as `Authorization: Bearer <token>` on every authenticated request, refresh or re-authenticate before the 24-hour expiry, and on any 401 shall clear the session and return to sign-in without a retry loop. | Force an expired token; the app returns cleanly to sign-in; network inspection shows no retry storm. |
| **FR-AND-3** | **Two-factor challenge.** Where 2FA is enabled, the app shall present an OTP entry supporting TOTP codes and single-use backup codes, with the correct keyboard type, SMS autofill where applicable, and inline error handling that preserves entry state. | 2FA account cannot sign in without a code; invalid code shows an inline error; a consumed backup code is rejected. |
| **FR-AND-4** | **Biometric session gate.** After initial sign-in, the app shall gate resumption behind BiometricPrompt (fingerprint, face or device credential), and shall auto-lock after a configurable background interval (default 5 minutes). Biometric failure or cancellation shall never grant access. | Background past the interval; resumption requires biometric or device credential; cancelling returns to a locked state. |
| **FR-AND-5** | **Credential storage.** The JWT and any 2FA state shall be stored exclusively in Keystore-backed encrypted storage, never in plain `SharedPreferences`, never in plaintext files, never in logcat, and **shall be excluded from Android Auto Backup and Google cloud backup**. | Filesystem, logcat and `bmgr`-triggered backup inspection finds no token in the clear; `android:allowBackup` behaviour verified via backup rules. |
| **FR-AND-6** | **FCM registration.** On notification permission grant, the app shall obtain the FCM registration token and upload it to the backend device-registration endpoint with user identity, device model, OEM, OS version and app version. It shall handle token rotation, and deregister on sign-out. | Register on device A; a server-side dispatch reaches device A. Rotate the token; dispatch still reaches the device. Sign out; dispatch no longer reaches it. |
| **FR-AND-7** | **Notification channels.** The app shall create a distinct Android notification channel per category (anomaly, sla_breach, guardian_escalation, task_assigned, system_incident), each with an appropriate importance level, so users can tune categories individually via system settings. | Inspect system notification settings; five channels present with correct names and importance. |
| **FR-AND-8** | **Notification payloads and deep links.** Push payloads shall carry a typed `category` and target identifier. Tapping shall route directly to the corresponding screen with the correct record loaded, from cold start, from background and from foreground. | Test all three app states for each of the five categories — fifteen cases — all landing correctly. |
| **FR-AND-9** | **★ OEM battery-restriction detection and mitigation.** The app shall detect when it is subject to battery optimisation or OEM background restriction, shall present OEM-aware guidance directing the user to the correct settings screen (Xiaomi/MIUI Autostart, Oppo/ColorOS and Realme background management, Vivo/FuntouchOS high background power consumption, Samsung "Never sleeping apps", plus the generic `REQUEST_IGNORE_BATTERY_OPTIMIZATIONS` flow), and shall report its restriction state to the backend so the dispatcher can select a fallback channel. | On a Xiaomi and an Oppo device with default settings: restriction is detected, guidance appears, the correct settings screen opens, and the backend records the restriction state. |
| **FR-AND-10** | **★ Delivery-assurance fallback.** Where the backend does not receive a delivery acknowledgement within a defined window, or where a device is known to be restricted, it **shall automatically dispatch the same alert via a secondary channel (email or SMS)**. Alerts shall never depend solely on push. | Suppress push on a test device; the alert arrives by the fallback channel within the defined window; the dispatch audit records both attempts. |
| **FR-AND-11** | **In-context permission requests.** `POST_NOTIFICATIONS` (Android 13+) shall be requested only after the user has been shown its purpose, never at first launch, with a rationale UI before the system dialog, and the app shall remain fully usable if denied. | Fresh install requests no permission until the user reaches the alerts feature; declining leaves all non-alert functionality intact. |
| **FR-AND-12** | **Minimal permissions.** The manifest shall declare only permissions actually used. At MVP scope: `INTERNET`, `ACCESS_NETWORK_STATE`, `POST_NOTIFICATIONS`, `USE_BIOMETRIC`, and optionally `RECEIVE_BOOT_COMPLETED` for FCM token restoration. **No camera, microphone, location, storage, contacts or SMS-read permission** unless a corresponding feature ships. | Manifest audit — every declared permission maps to a shipped feature; Play Console permissions declaration is consistent. |
| **FR-AND-13** | **Executive read view.** The app shall present a phone-first summary of platform health — overall status, department status counts, open alerts by severity, task load — legible at a glance without scrolling on a standard phone. | An executive extracts current platform status within 5 seconds on a mid-range device. |
| **FR-AND-14** | **Alert feed and triage.** The app shall list alerts sorted by severity and recency, filterable by severity and department, supporting acknowledge, assign, reassign, status change and comment — each reachable in three taps or fewer from a notification tap. | Tap-count measurement for each action from a cold notification. |
| **FR-AND-15** | **Department views.** The app shall list all departments from the backend registry with status and provide a detail view per department, resolving names case-insensitively and showing a native not-found state for unknown names. | List count matches the backend registry; each detail loads; an invented name shows the not-found state without a crash. |
| **FR-AND-16** | **Task views.** The app shall list tasks assigned to or relevant to the signed-in user with detail, status change and comment, reflecting changes to the backend immediately and reconciling optimistic updates against the server response. | Change a status on device; the web client reflects it on refresh; a rejected change reverts the optimistic update with a clear message. |
| **FR-AND-17** | **GANESHA conversational access.** The app shall submit a prompt to the orchestration endpoint, display the composed response with department attribution, handle long-running responses with a progress state and timeout, and list prior conversations. | The same prompt returns equivalent content on Android and web; a slow response shows progress and does not appear frozen (no ANR). |
| **FR-AND-18** | **Role-aware presentation.** The app shall render controls conditionally on the signed-in user's role and permissions, matching the backend's five-role model, presenting no control whose backend call would be rejected. | For each role, enumerate visible controls and exercise each; zero authorisation errors. |
| **FR-AND-19** | **Excluded administrative surfaces.** The app shall provide no user administration, no RBAC modification and no platform settings modification, for any role. | Code and UI audit confirms absence for all roles. |
| **FR-AND-20** | **Offline and degraded behaviour.** With no connectivity, the app shall display last-known cached content clearly labelled with its retrieval time, refuse write actions with an explicit message rather than queuing them, and never present a blank screen or an indefinite spinner. Given intermittent Indian coverage, transient loss shall be handled without losing screen state. | Airplane Mode mid-session: cached views show staleness labels; a write attempt is refused clearly; toggling connectivity does not reset navigation state. |
| **FR-AND-21** | **Material Design 3 conformance.** The app shall use Material 3 components, support dynamic colour on Android 12+, render edge-to-edge with correct window insets, support the predictive back gesture, follow system light/dark theme, and use standard navigation patterns. | Material Design review checklist completed; the app looks and behaves native on a Pixel and on a heavily-skinned OEM device. |
| **FR-AND-22** | **Font scaling and accessibility.** All text shall respect system font scaling to the largest setting without truncation, clipping or overlap; all touch targets shall be at least 48 dp; all interactive elements shall have TalkBack content descriptions; and reduced-motion settings shall be respected. | Screenshot matrix at default and maximum font scale; TalkBack traversal completes all core journeys. |
| **FR-AND-23** | **Device and OS coverage.** The app shall support the minimum SDK through the current target SDK, on phones (5.5-inch through 6.8-inch) and tablets, across at least the top five OEM skins in the user base. | Functional pass on minimum SDK, target SDK, one budget device, one mid-range device, one flagship, one tablet, and five OEM skins. |
| **FR-AND-24** | **Version compatibility guard.** The app shall send its version to the backend and shall present a blocking upgrade prompt when the backend reports the client version as unsupported. | Configure the backend to reject the installed version; the app shows the upgrade prompt and blocks further use. |
| **FR-AND-25** | **No forked logic.** All pricing, GST/HSN treatment, orchestration, model routing and anomaly scoring shall come from the backend; the app shall not compute or hard-code any of it. | Code review; changing a backend rule changes app behaviour with no app release. |
| **FR-AND-26** | **Remote sign-out.** A server-side session revocation shall sign the device out on next request, and the app shall clear encrypted storage and cached data on sign-out. | Revoke server-side; the next request returns to sign-in; storage inspection shows no residual token or cached platform data. |

---

## 5. Non-Functional Requirements

> Conditional — applicable only to a built client.

### 5.1 Performance

| ID | Requirement |
|---|---|
| NFR-AND-P1 | Cold launch to first interactive content under **3 s on a mid-range 4 GB device** (and under 2 s on a flagship). Budgets are set against mid-range hardware, not flagships. |
| NFR-AND-P2 | Warm launch (biometric unlock to content) under **1.5 s** on mid-range hardware. |
| NFR-AND-P3 | Scrolling in all list views sustains **60 fps** on mid-range hardware (higher on high-refresh displays) with no jank on a 200-item list. |
| NFR-AND-P4 | **ANR rate under 0.47%** and **crash rate under 1.09%** — the Google Play Console bad-behaviour thresholds. No blocking work on the main thread. |
| NFR-AND-P5 | Notification delivery to visible notification within **60 s** of server-side trigger on an unrestricted device. |
| NFR-AND-P6 | Download size under **30 MB** and installed size under **80 MB** at MVP scope; App Bundle splits used to minimise per-device download. |
| NFR-AND-P7 | Memory footprint under **200 MB** on a 4 GB device; no memory leaks across navigation cycles. |
| NFR-AND-P8 | **No background polling.** Push only, with WorkManager used sparingly and never for periodic network work — polling is both battery-hostile and actively suppressed by OEM skins. |
| NFR-AND-P9 | Cellular data use minimised: request only visible data, paginate every list, never prefetch large payloads on a metered connection, and respect the Data Saver setting. |

### 5.2 Scalability and device coverage

| ID | Requirement |
|---|---|
| NFR-AND-S1 | The device-token store shall support one user across multiple devices and one device across sequential users, without cross-delivery. |
| NFR-AND-S2 | Notification dispatch shall be batched and rate-limited server-side so a mass alert event does not overwhelm FCM or the backend. |
| NFR-AND-S3 | List views shall paginate; no screen shall load an unbounded collection. |
| NFR-AND-S4 | The app shall function correctly as the department registry grows beyond its current 20 entries, with no hard-coded department list. |
| NFR-AND-S5 | The app shall function on screen sizes from small phone through 10-inch tablet, and shall not break on foldables (correct configuration-change handling, no state loss on fold/unfold). |

### 5.3 Security

| ID | Requirement |
|---|---|
| NFR-AND-Sec1 | TLS 1.2/1.3 for all traffic; cleartext traffic disabled via a network security configuration (`cleartextTrafficPermitted="false"`). |
| NFR-AND-Sec2 | Certificate pinning against the Kailash API certificate via the network security configuration, with a documented rotation procedure so pinning does not become an outage source. |
| NFR-AND-Sec3 | Credentials exclusively in Keystore-backed encrypted storage; nothing sensitive in plain `SharedPreferences`, files or logs. |
| NFR-AND-Sec4 | **Backup exclusion** — `android:allowBackup` configured with explicit backup rules excluding all credential and cached platform data, so tokens never leave the device via Google backup. |
| NFR-AND-Sec5 | Biometric gate on resume plus auto-lock on background (FR-AND-4). |
| NFR-AND-Sec6 | `FLAG_SECURE` set on screens displaying sensitive platform data, preventing screenshots and obscuring the recents-screen thumbnail. |
| NFR-AND-Sec7 | Root detection with a documented policy response (warn, restrict privileged actions, or block) for a client with privileged platform access. |
| NFR-AND-Sec8 | Code shrinking and obfuscation via R8/ProGuard on release builds, with mapping files retained for crash symbolication. |
| NFR-AND-Sec9 | No third-party analytics, advertising, attribution or session-replay SDK. Crash reporting, if adopted, must not transmit personal or platform data. |
| NFR-AND-Sec10 | Nothing sensitive written to logcat in release builds; logging stripped or gated by build type. |
| NFR-AND-Sec11 | Local cache encrypted at rest (SQLCipher or equivalent) and purged completely on sign-out and remote revocation. |
| NFR-AND-Sec12 | Model-generated content rendered as text; no WebView rendering of untrusted HTML; if a WebView is used at all, JavaScript disabled unless specifically justified. |
| NFR-AND-Sec13 | Deep links and App Links validated and authenticated before acting; a link shall never bypass the biometric gate or the auth check. Exported components minimised and protected. |
| NFR-AND-Sec14 | Signing key stored in a secure key management system (Play App Signing plus a protected upload key); never committed. |
| NFR-AND-Sec15 | For privileged roles, device enrolment in Go4Garage MDM shall be a distribution precondition. |

### 5.4 Availability

| ID | Requirement |
|---|---|
| NFR-AND-A1 | The app shall launch and present a usable shell even when the backend is unreachable, showing an explicit backend-unavailable state. |
| NFR-AND-A2 | Failed requests shall retry with bounded exponential backoff, then surface an error state with manual retry — never an infinite spinner and never an ANR. |
| NFR-AND-A3 | Crash-free session rate **99.5% or better**; ANR-free session rate within Play thresholds. |
| NFR-AND-A4 | A broken release shall be haltable mid-rollout and a prior version re-promotable within **4 hours**; staged rollout is mandatory. |
| NFR-AND-A5 | The app shall tolerate additive backend changes (new fields) without crashing; unknown fields are ignored, not fatal. |
| NFR-AND-A6 | **Notification delivery shall not be a single point of failure** — the fallback channel requirement (FR-AND-10) is an availability requirement, not merely a feature. |

### 5.5 Compliance

| ID | Requirement |
|---|---|
| NFR-AND-C1 | **Google Play policy** conformance for the chosen track: target API level requirement, Data Safety declaration, permissions declarations, and any provisions applying to private/enterprise apps. |
| NFR-AND-C2 | **Data Safety declaration** accurately reflecting all data collected — at MVP scope limited to account identity and diagnostic data, with **no data sharing and no tracking**. |
| NFR-AND-C3 | **Data residency:** the app shall persist no personal or platform data beyond the encrypted read cache and Keystore credentials, and shall transmit only to Go4Garage-controlled endpoints. **FCM relay metadata (a necessary Google dependency) shall be disclosed in the published sub-processor list**, alongside Firebase Hosting which is already a sub-processor. |
| NFR-AND-C4 | **Accessibility:** TalkBack support, font scaling to the largest setting, sufficient contrast, 48 dp minimum touch targets, and respect for reduced-motion — meeting Android accessibility expectations and, by extension, the WCAG 2.1 AA spirit applied to the web surface. |
| NFR-AND-C5 | **GST/HSN:** where the app displays priced automotive values, it shall display the HSN code and GST rate supplied by the backend and shall never compute or infer tax locally. |
| NFR-AND-C6 | **DISCOM/energy:** where charger or energy values are displayed, forecast values shall be visually distinguished from measured values, matching the parent product requirement. |
| NFR-AND-C7 | **Retention:** cached platform data on device shall be covered by the published data-retention policy, and the policy shall be updated to describe mobile caching if an app ships. |
| NFR-AND-C8 | **Export compliance and encryption declarations** completed accurately in the Play Console. |

### 5.6 Maintainability

| ID | Requirement |
|---|---|
| NFR-AND-M1 | API models shall be generated from, or validated against, the backend OpenAPI schema — not hand-maintained in parallel. |
| NFR-AND-M2 | If React Native is chosen, Zod schemas and TypeScript API types shall be **physically shared** with the web client, not duplicated. |
| NFR-AND-M3 | The app shall be buildable and testable in CI without a developer's local machine. |
| NFR-AND-M4 | Annual target-API-level compliance work shall be an explicitly budgeted maintenance item. |
| NFR-AND-M5 | The minimum SDK shall be reviewed annually against actual user-base distribution. |
| NFR-AND-M6 | Per-OEM notification delivery rates shall be monitored continuously, not measured once at launch. |

---

## 6. Data Model / Storage

### 6.1 Current state

**No data model exists**, because no application exists. No Room schema, no `SharedPreferences` keys, no DataStore definitions, no Keystore aliases are defined anywhere for Kailash on Android.

### 6.2 Conditional on-device storage inventory

| Store | Contents | Protection | Lifetime |
|---|---|---|---|
| **Keystore-backed encrypted storage** (EncryptedSharedPreferences / expo-secure-store) | JWT session token; refresh state; device identifier | Hardware-backed Keystore where available; **excluded from backup** | Until sign-out, expiry or remote revocation |
| **Encrypted Room database** (SQLCipher) | Last-known departments, alerts, tasks, executive summary — **read-only, never authoritative** | Encrypted at rest; excluded from backup | Purged on sign-out; entries expire per TTL |
| **DataStore / SharedPreferences** | Non-sensitive preferences: theme, notification category preferences, last-selected filters, auto-lock interval, OEM-guidance-shown flag | None required | Persistent |
| **In-memory** | ViewModel state, in-flight requests, decoded responses | — | Process lifetime |
| **Not stored anywhere** | Passwords, TOTP secrets, backup codes, AI provider keys, the internal platform token, any database credential | — | — |

### 6.3 Backup exclusion

Android's Auto Backup is enabled by default and will silently upload app data to the user's Google Drive unless configured otherwise. Requirement: explicit backup rules shall **exclude** the encrypted credential store and the cache database. This is an Android-specific hazard with no iOS equivalent and must be verified by test, not assumed.

### 6.4 Backend additions required

An Android client would require **one new backend capability** — device registration and notification dispatch — with Android-specific fields for delivery reliability.

| Entity | Fields | Store |
|---|---|---|
| **DeviceToken** | `id`, `user_id`, `platform` (`android`/`ios`/`web`), `token`, `app_version`, `os_version`, `device_model`, **`oem`**, **`battery_restricted`**, `created_at`, `last_seen_at`, `revoked_at` | MongoDB (new collection, indexed on `user_id` and `token`) |
| **NotificationPreference** | `user_id`, `category`, `enabled`, `min_severity`, `quiet_hours`, `fallback_channel` | MongoDB |
| **NotificationDispatch** | `id`, `user_id`, `device_token_id`, `category`, `target_id`, `payload`, `channel`, `status`, `sent_at`, **`acknowledged_at`**, **`fallback_dispatched`**, `error` | MongoDB (audit, delivery tracking and per-OEM analytics) |

The bolded fields exist specifically to support the Android delivery-reliability requirements (FR-AND-9, FR-AND-10) and the per-OEM delivery KPI. They have no iOS counterpart.

**Design requirement:** the dispatcher shall be **channel-agnostic** — a single dispatch record can target email, SMS, web push or FCM, with automatic fallback on non-acknowledgement. This is deliberate: the notification infrastructure delivers value immediately (via email and SMS) without any app, and an app becomes an additional channel rather than a prerequisite.

### 6.5 Caching rules

| Rule | Statement |
|---|---|
| CR-1 | Cached data is display-only. No write may be derived from, or validated against, a cached value. |
| CR-2 | Every cached view displays its retrieval timestamp when older than a defined freshness threshold. |
| CR-3 | Cache entries expire per category TTL (alerts: 5 minutes; departments: 1 hour; executive summary: 15 minutes). |
| CR-4 | The entire cache is purged on sign-out, on remote revocation, and on a detected role change. |
| CR-5 | No offline write queue exists. Writes without connectivity are refused with a clear message. |
| CR-6 | The cache is excluded from Android backup. |

---

## 7. API & Integration Points

### 7.1 Primary integration — the Kailash backend

An Android client would consume the **identical API** described in `../TRD_kailash_ai.md` §7, with no mobile-specific business endpoints.

| Aspect | Detail |
|---|---|
| Base URL | `https://api.kailash-ai.in` (production); configurable per build variant |
| Transport | HTTPS, JSON, TLS 1.2/1.3, certificate-pinned via network security config |
| Auth | `Authorization: Bearer <JWT>` — same HS256 token, same 24-hour lifetime, same five-role RBAC |
| Correlation | `x-request-id` sent per request; surfaced in error displays for support correlation |
| Envelope | `ApiResponse` on success; `{ ok, error: { code, message, hint }, request_id }` on failure |
| Rate limiting | The proxy enforces 30 r/s general and 5 r/s on auth paths; the client must respect these and back off |

**Consumed routers:** auth, departments, department_intelligence, tasks, gaps_tasks_crud, dashboard, analytics (summary only), conversations, ganesha (v2 preferred), guardians, system_health, automobile (read only).

**Not consumed:** users, rbac, settings, knowledge_base management, scheduler_api — excluded by FR-AND-19.

### 7.2 New backend integration required

| Endpoint | Purpose |
|---|---|
| `POST /api/devices/register` | Register an FCM token with OEM and restriction state |
| `PATCH /api/devices/{id}/restriction` | Report a change in battery-restriction state |
| `DELETE /api/devices/{id}` | Deregister on sign-out |
| `GET/PUT /api/notifications/preferences` | Per-user, per-category preferences including fallback channel |
| `POST /api/notifications/{id}/ack` | Client acknowledgement of delivery, enabling fallback logic |
| Internal dispatch service | Channel-agnostic fan-out with acknowledgement tracking and automatic fallback |

**None of this exists today.** The backend has no push infrastructure of any kind.

### 7.3 Third-party integrations

| Integration | Status / requirement |
|---|---|
| **Firebase Cloud Messaging (FCM)** | **Would be required.** Not currently configured. **Advantage: Firebase project `kailash-38268` already exists** for hosting and the backend already carries Firebase Admin SDK configuration — FCM would be an incremental configuration, not a new vendor relationship. FCM can also relay to APNs, serving a future iOS client from one dispatch implementation. |
| **Google Play Console / managed Google Play** | Required for private distribution. |
| **Play App Signing** | Required; upload key held in the CI secret store. |
| **Cloud device farm** (Firebase Test Lab, or equivalent) | Strongly recommended for the fragmentation test matrix. Firebase Test Lab is again incremental on the existing Firebase relationship. |
| **Crash reporting** | Optional. If adopted, must not transmit personal or platform data (NFR-AND-Sec9). Firebase Crashlytics would be the path of least resistance but requires a data-flow assessment against NFR-AND-C3. |
| **SMS provider** | **Backend-side only**, as a notification fallback channel. Not an app integration — the app never calls a telephony provider directly. |
| **Payment gateway / Google Play Billing** | **Not applicable.** Kailash has no billing surface; no in-app purchase or subscription would exist. |
| **Slack** | **Not present** anywhere in Kailash; not proposed. |
| **`KAILASH_AI_URL`-style internal integration** | **Not applicable.** That environment-variable convention is how other Go4Garage *products* (notably ARJUN / `ev-vidya-arjun`) locate the Kailash backend. A first-party Android client would use its own build-variant base-URL configuration against the same host. |
| **Third-party analytics / advertising** | **Prohibited** by NFR-AND-Sec9. |

---

## 8. Infrastructure & Deployment

### 8.1 Current reality

**Nothing is deployed, because nothing is built.**

| Item | Status |
|---|---|
| Gradle project (`build.gradle`, `settings.gradle`, `gradlew`) | **Does not exist** |
| Kotlin or Java source | **Does not exist** |
| `AndroidManifest.xml` | **Does not exist** |
| Application ID | **Not registered** |
| `res/` resources, icons, themes | **Do not exist** |
| React Native / Expo / Flutter project | **Does not exist** |
| `google-services.json` | **Does not exist** |
| Signing keystore | **Does not exist** |
| Google Play Console record | **Does not exist** |
| App Bundle (AAB) | **Does not exist** |
| Release track (internal / closed / production) | **Does not exist** |
| FCM configuration | **Not configured** (Firebase project exists for hosting only) |
| Android CI job | **Does not exist** — `.github/workflows/ci.yml` defines only `lint`, `shared`, `services`, `backend`, `frontend`, `compose-build` |
| `android_app_kailash_ai/deployed/` | **Empty** |
| `android_app_kailash_ai/not_deployed/` | **Empty** |

### 8.2 What is deployed for Kailash

For completeness, and to make the contrast explicit:

| Component | Deployment status |
|---|---|
| Backend | Docker/Compose and Vultr VPS tooling present; **live status not verified** from this working copy |
| Frontend | Firebase Hosting configuration present (project `kailash-38268`), built bundle present; **live status not verified** |
| Android app | **Does not exist** — nothing to deploy |
| iOS app | **Does not exist** — nothing to deploy |

### 8.3 Conditional deployment pipeline

| Stage | Mechanism |
|---|---|
| Prerequisites | Play Console developer account; managed Google Play channel; application ID registered; FCM configured on project `kailash-38268`; signing keystore created and secured; Play App Signing enrolled |
| Build capacity | Standard Linux CI runners (no macOS requirement — a genuine advantage over iOS); Gradle build producing a signed App Bundle, or EAS Build if React Native |
| CI | New workflow running lint (ktlint/detekt or ESLint), unit tests, instrumentation tests and a signed AAB build on every pull request |
| Versioning | Semantic `versionName` plus monotonic `versionCode`, injected from CI |
| Internal testing | Play Console internal testing track — fastest turnaround, defined tester group |
| Closed testing | Closed track across at least five OEM skins before production |
| Production | Managed Google Play private app with **staged rollout** (5% → 20% → 50% → 100%) and defined halt criteria on crash/ANR rate |
| Rollback | Halt rollout and re-promote the prior release; target under 4 hours |
| Secret handling | Keystore, upload key and `google-services.json` in the CI secret store; never committed |
| Monitoring | Crash-free rate, ANR rate, **per-OEM notification delivery rate**, version-adoption distribution, Android vitals |

### 8.4 Environment configuration

| Build variant | Backend base URL | Distribution |
|---|---|---|
| `debug` | `http://localhost:8000` or a developer's Compose backend (requires a cleartext exception limited to debug) | Emulator / local device |
| `staging` | Staging backend (**does not exist today** — no staging environment is defined for Kailash) | Internal testing track |
| `release` | `https://api.kailash-ai.in` | Managed Google Play |

Note: the parent TRD records that **no staging environment exists** for Kailash. A mobile client would create pressure to build one, since testing pre-release mobile builds against production is poor practice. That cost belongs in any business case.

### 8.5 Device test matrix (conditional)

Unlike iOS, Android requires an explicit device matrix. Minimum viable coverage:

| Class | Examples | Purpose |
|---|---|---|
| Budget | 4 GB RAM, entry SoC, Android 8–11 | Performance floor validation |
| Mid-range | 6 GB RAM, mid SoC, Android 12–13 | The realistic primary target |
| Flagship | 8 GB+, current Android | Upper bound and new-API behaviour |
| **Xiaomi / Redmi (MIUI/HyperOS)** | Any | **Battery-restriction testing** |
| **Oppo / Realme (ColorOS)** | Any | **Battery-restriction testing** |
| **Vivo (FuntouchOS)** | Any | **Battery-restriction testing** |
| **Samsung (One UI)** | Any | **Battery-restriction testing** plus largest install base |
| Pixel (stock) | Any | Reference behaviour |
| Tablet | 10-inch | Layout adaptation |
| Foldable | Any | Configuration-change handling |

The four bolded OEM rows exist solely because of the notification-suppression problem and represent recurring test cost with no iOS equivalent.

---

## 9. Security & Compliance Requirements

> Conditional — applicable only to a built client. Consolidated here for a security reviewer.

### 9.1 Device and data security

| ID | Control |
|---|---|
| SEC-AND-1 | Keystore-backed encrypted credential storage; nothing sensitive in plain `SharedPreferences` or files. |
| SEC-AND-2 | **Backup exclusion** for all credential and cached platform data — verified by test, not assumed. |
| SEC-AND-3 | Biometric gate on resume via BiometricPrompt with device-credential fallback; auto-lock on background. |
| SEC-AND-4 | `FLAG_SECURE` on sensitive screens, preventing screenshots and obscuring recents thumbnails. |
| SEC-AND-5 | Root detection with a documented policy response. |
| SEC-AND-6 | Encrypted local cache; full purge on sign-out and remote revocation. |
| SEC-AND-7 | R8/ProGuard shrinking and obfuscation on release builds; mapping files retained securely for symbolication. |
| SEC-AND-8 | No sensitive value in logcat in release builds. |

### 9.2 Network security

| ID | Control |
|---|---|
| SEC-AND-9 | Network security configuration with `cleartextTrafficPermitted="false"` for release builds. |
| SEC-AND-10 | Certificate pinning via network security config, pinned to the intermediate CA (not the leaf) with a documented rotation runbook. |
| SEC-AND-11 | The client never holds an AI provider key, a Firebase Admin credential or the internal platform token. |
| SEC-AND-12 | Deep links and App Links validated and authenticated; exported components minimised and permission-protected; a link never bypasses the auth or biometric gate. |
| SEC-AND-13 | Respect the backend's proxy rate limits (30 r/s general, 5 r/s auth); implement client-side backoff. |

### 9.3 Application security

| ID | Control |
|---|---|
| SEC-AND-14 | Model-generated content rendered as text; no WebView rendering of untrusted HTML; JavaScript disabled in any WebView unless justified. |
| SEC-AND-15 | Server-side RBAC is the authorisation boundary; client gating is presentation only. |
| SEC-AND-16 | No user administration, RBAC change or settings change available in the app for any role. |
| SEC-AND-17 | Remote sign-out invalidates the device session on next request. |
| SEC-AND-18 | Minimum-supported-version enforcement prevents an outdated client operating against an incompatible contract. |
| SEC-AND-19 | Dependency vulnerability scanning in the mobile CI pipeline. |

### 9.4 Distribution and compliance

| ID | Control |
|---|---|
| SEC-AND-20 | Private distribution via managed Google Play; **not** a public Play Store listing. |
| SEC-AND-21 | Play App Signing enrolled; upload key in secure CI storage; keystore never committed. |
| SEC-AND-22 | Accurate Data Safety declaration; no data sharing, no tracking; minimal data categories. |
| SEC-AND-23 | MDM enrolment required for devices used by privileged roles. |
| SEC-AND-24 | Data-residency position documented, including **FCM as a Google-operated relay** in the published sub-processor list. |
| SEC-AND-25 | Target-API-level compliance maintained per Google Play policy. |
| SEC-AND-26 | Annual mobile security review, including a penetration test of the client and its API usage, with attention to Android-specific attack surface (exported components, deep links, backup, root). |

---

## 10. Testing Strategy

> Conditional — applicable only to a built client.

### 10.1 Current state

**No Android tests exist**, because no Android code exists. The Kailash CI pipeline contains no mobile job of any kind.

### 10.2 Conditional test layers

| Layer | Tooling | Scope |
|---|---|---|
| Unit | JUnit + MockK + Turbine (Kotlin), or Jest (React Native) | ViewModels, API decoding, error mapping, cache TTL logic, auth state machine |
| Contract | Fixture-driven decoding tests generated from the backend OpenAPI schema | Every endpoint's success and error envelope decodes to the correct typed model |
| UI / instrumentation | Compose UI Test / Espresso, or Maestro/Detox | Sign-in with and without 2FA, biometric gate, alert triage, task status change, department detail, GANESHA prompt |
| **Notification delivery** | Real-device testing per OEM with simulated FCM payloads | All five categories deep-link correctly across cold/background/foreground; **delivery verified on each major OEM skin with default battery settings** |
| **OEM battery restriction** | Manual and scripted testing on Xiaomi, Oppo, Vivo, Realme, Samsung | Restriction detected; correct settings screen opens; backend records state; fallback fires |
| Accessibility | Accessibility Scanner, Espresso accessibility checks, manual TalkBack | All core journeys TalkBack-completable; maximum font scale renders correctly |
| Screenshot | Paparazzi or equivalent | Layout integrity across device sizes, themes and font scales |
| Security | Static analysis, filesystem and logcat inspection, backup-content inspection, rooted-device testing, pinning verification | No credential leakage; backup exclusion effective |
| Performance | Android Studio Profiler, Macrobenchmark, Android vitals | Cold launch, scroll jank, memory, ANR — **measured on a mid-range device** |
| Compatibility | Cloud device farm across the §8.5 matrix | Minimum SDK through target SDK; five OEM skins; tablet; foldable |
| Regression | Full suite in CI on every pull request | No merge on red |

### 10.3 Conditional test requirements

| ID | Requirement |
|---|---|
| TEST-AND-1 | Contract tests shall decode a fixture for every consumed endpoint, including every documented error code; a backend schema change that breaks decoding shall fail CI. |
| TEST-AND-2 | Auth tests shall cover valid sign-in, invalid password, 2FA challenge, valid TOTP, backup-code single use, token expiry, 401 handling, biometric success, biometric cancel, biometric unavailable, and remote revocation. |
| TEST-AND-3 | Notification tests shall verify all five categories across cold start, background and foreground — fifteen cases — each landing on the correct screen with the correct record. |
| TEST-AND-4 | **★ OEM delivery tests shall verify notification arrival on at least Xiaomi, Oppo, Vivo, Realme and Samsung devices with default (unmodified) battery settings**, and shall record the per-OEM delivery rate. |
| TEST-AND-5 | **★ Fallback tests shall verify that a suppressed or unacknowledged push results in a secondary-channel dispatch within the defined window.** |
| TEST-AND-6 | Role tests shall verify, for each of the five roles, that the visible control set matches the permitted permission set and that no visible control produces an authorisation error. |
| TEST-AND-7 | Offline tests shall verify staleness labelling, write refusal, absence of any silent queue, and no state loss on transient connectivity change. |
| TEST-AND-8 | Accessibility tests shall verify TalkBack completion of all core journeys, maximum font-scale layout integrity, and 48 dp minimum touch targets. |
| TEST-AND-9 | Security tests shall verify Keystore-only credential storage, no tokens in logcat or the filesystem, **backup exclusion**, effective certificate pinning, `FLAG_SECURE` behaviour, and complete purge on sign-out. |
| TEST-AND-10 | Performance tests shall assert cold launch under 3 s, 60 fps scrolling and memory under 200 MB **on a mid-range 4 GB device**, and shall assert ANR and crash rates within Play thresholds. |
| TEST-AND-11 | Compatibility tests shall pass across the §8.5 device matrix, including tablet and foldable configuration changes. |
| TEST-AND-12 | A pre-submission checklist shall verify Play policy conformance, Data Safety declaration accuracy, permissions declarations, target API level, and export-compliance declaration. |
| TEST-AND-13 | Version-guard tests shall verify that an unsupported client version is blocked with an upgrade prompt. |
| TEST-AND-14 | Internal and closed testing tracks shall run for a defined minimum period across at least five OEM skins before any production promotion, with staged-rollout halt criteria defined in advance. |

---

## 11. Current Implementation Status

### 11.1 Platform existence statement — Android

> **No Kailash Android application exists in code.**
>
> Verified 2026-07-31 at product HEAD commit `40cca17`. The directory `C:\Go4Garage( Eka)\Kailash-Ai\android_app_kailash_ai\` contains **only two empty subdirectories** — `deployed/` and `not_deployed/` — plus the two documentation files this workstream is producing. There is no application source of any kind.
>
> **Kailash is presently a backend and web-only internal service.** It is Go4Garage's internal ML/AI platform, consumed by other Go4Garage products over HTTP (notably via the `KAILASH_AI_URL` environment-variable convention) and operated by staff through a single React 19 web dashboard. **No dedicated mobile client is planned**, unless the reader decides otherwise on the basis of the decision criteria in the companion BRD §11.1.

### 11.2 Detailed absence audit

| Artefact | Present? |
|---|---|
| `build.gradle` / `build.gradle.kts` / `settings.gradle` / `gradle.properties` / `gradlew` | **No** |
| Kotlin or Java source files | **No** |
| `AndroidManifest.xml` | **No** |
| Application ID | **No** |
| `res/` directory, icons, themes, strings | **No** |
| React Native project (`package.json` with `react-native`, `metro.config.js`, `android/` folder) | **No** |
| Expo project (`app.json`, `eas.json`) | **No** |
| Flutter project (`pubspec.yaml`, `lib/`, `android/` folder) | **No** |
| `google-services.json` | **No** |
| ProGuard / R8 rules | **No** |
| Signing keystore | **No** |
| Google Play Console record | **No** |
| App Bundle (AAB) or APK | **No** |
| Release track (internal / closed / production) | **No** |
| FCM messaging configuration | **No** — Firebase project `kailash-38268` exists for hosting only |
| Backend device-token model | **No** |
| Backend notification dispatch service | **No** |
| Backend `/api/devices/*` endpoints | **No** |
| Android job in `.github/workflows/ci.yml` | **No** — the six jobs are `lint`, `shared`, `services`, `backend`, `frontend`, `compose-build` |
| Any mobile-related dependency in `backend/requirements.txt` | **No** |
| Service worker or web push on the web app (the cheaper alternative) | **No** — also absent |

### 11.3 What exists in the product for contrast

| Component | Status |
|---|---|
| **FastAPI backend** | **Built, dependencies installed, run locally.** Roughly 24 API routers, 20 registered department agents, 3 guardian agents, 9 platform services, populated `backend/.venv/`. |
| **React 19 web app** | **Built and compiled.** Roughly 70 page modules, roughly 1,000 installed packages, compiled `frontend/build/` output, Firebase Hosting configuration with SPA rewrites and five security headers. |
| **Firebase relationship** | **Exists** — project `kailash-38268` for hosting, Firebase Admin SDK configuration in the backend. **This lowers the barrier to FCM specifically.** |
| **Docker / Compose / Vultr / Nginx tooling** | **Present.** Live deployment status unverified from this copy. |
| **CI pipeline** | **Present** — six jobs, none mobile. |
| **Android client** | **Absent.** |

### 11.4 Technical prerequisites before any Android work could begin

| # | Prerequisite | Current state | Effort class |
|---|---|---|---|
| 1 | Approved business case (BR-AND-24) | Not started | Governance |
| 2 | **PWA alternative evaluated and rejected** — Chrome for Android supports installability and web push | Not evaluated | Days — **and should be done first** |
| 3 | Framework ADR (Kotlin/Compose vs React Native vs Flutter) | Not made | Days |
| 4 | Google Play Console developer account | Not held (unverified) | Days |
| 5 | Managed Google Play private distribution channel | Not established | Days |
| 6 | FCM configuration on project `kailash-38268` | Not configured | Hours — **low barrier, project exists** |
| 7 | Backend device-token model and registration endpoints | **Does not exist** | Weeks |
| 8 | Backend channel-agnostic notification dispatcher with acknowledgement and fallback | **Does not exist** | Weeks — *and independently valuable without an app* |
| 9 | Staging environment for pre-release testing | **Does not exist** for Kailash | Weeks |
| 10 | Client-side schema validation shared with the web client | Not implemented on either client | Weeks — *and independently valuable* |
| 11 | Signing keystore and secure key management | Not created | Days |
| 12 | Device test matrix / cloud device farm access | Not established | Days, plus recurring cost |
| 13 | Mobile engineering capacity | Not allocated | Ongoing |
| 14 | MDM baseline for privileged roles | Not defined | Weeks |

Items 8 and 10 deserve emphasis: both are **prerequisites for a mobile client that deliver value even if no mobile client is ever built**. A channel-agnostic dispatcher with fallback improves alerting today via email and SMS; shared schema validation hardens the web client against contract drift today. Both should be built regardless of the mobile decision.

Item 2 deserves equal emphasis and is Android-specific: **Chrome for Android supports both PWA installability and web push**. Adding a service worker and manifest to the existing React app would deliver the two genuine native benefits — an app icon and push notifications — at a fraction of the cost of a native client, from a codebase the team already maintains. This should be exhausted before a native build is contemplated.

---

## 12. Technical Risks & Dependencies

### 12.1 Risks of the current position

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| TR-AND-1 | The empty directory is misread as abandoned work. | High | Low | This document plus a README in the directory. |
| TR-AND-2 | No push infrastructure exists at all, so time-critical alerts depend entirely on whatever email or chat path is in use. | Medium | High | Build the channel-agnostic dispatcher (prerequisite 8) independently of any mobile decision. |
| TR-AND-3 | Mobile web on Chrome for Android degrades untested, creating pressure for a native app that better web testing would have avoided. | Medium | Medium | Keep Chrome for Android in the web app's tested matrix; test at 414 px and 360 px on a mid-range device each release. |
| TR-AND-4 | The cheaper PWA path is never evaluated, and a native build is commissioned that a service worker would have obviated. | Medium | Medium | Make PWA evaluation a mandatory gate in the business case (prerequisite 2). |
| TR-AND-5 | A reactive mobile build is commissioned without prerequisites 7, 8, 9 and 10, producing a fragile client. | Low | High | Enforce the prerequisite list as a gate. |

### 12.2 Risks that would attach to building

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| TR-AND-6 | **★ OEM battery optimisation silently suppresses notifications**, defeating the app's primary justification on precisely the devices most common in India. | **High** | **High** | High-priority FCM messages; restriction detection and OEM-specific exemption guidance (FR-AND-9); **mandatory secondary-channel fallback (FR-AND-10)**; per-OEM delivery-rate monitoring as a permanent KPI. |
| TR-AND-7 | **Device fragmentation** produces defects visible only on specific OEM skins or Android versions. | **High** | Medium | Cloud device-farm testing across the §8.5 matrix; per-model crash and ANR monitoring; staged rollout with halt criteria. |
| TR-AND-8 | **Performance floor on budget devices** — an app tuned on a flagship is unusable on a 4 GB mid-range phone. | High | Medium | Set all budgets against a mid-range reference device (NFR-AND-P1); profile on that device. |
| TR-AND-9 | **ANR and crash rates breach Play Console bad-behaviour thresholds**, harming distribution even on a private track. | Medium | Medium | Main-thread discipline; monitor against the 0.47% ANR threshold; profile on budget hardware. |
| TR-AND-10 | **Android Auto Backup silently exfiltrates credentials** to Google Drive if backup rules are not configured. | Medium | **High** | Explicit backup exclusion (SEC-AND-2), verified by test (TEST-AND-9), not assumed. |
| TR-AND-11 | **Contract drift between three clients** — a backend change breaks Android silently. | High | High | Generate API models from the OpenAPI schema; contract tests in CI; version guard (FR-AND-24); share Zod schemas if React Native is chosen. |
| TR-AND-12 | **No staging environment** forces pre-release mobile testing against production. | High | High | Build a staging environment as a prerequisite. |
| TR-AND-13 | **Annual target-API-level policy** forces recurring compatibility work with no feature value. | High | Medium | Budget maintenance explicitly; reassess the app annually against usage KPIs. |
| TR-AND-14 | **Certificate pinning becomes an outage source** on certificate rotation. | Medium | High | Pin the intermediate CA, or pin multiple certificates; document and rehearse rotation. |
| TR-AND-15 | **Platform credentials on personal devices**, with Android's more open filesystem and sideloading culture widening exposure. | Medium | High | Keystore-backed storage, backup exclusion, biometric gate, auto-lock, remote revocation, root detection, MDM for privileged roles. |
| TR-AND-16 | **Notification fatigue** trains users to dismiss pushes. | High | Medium | Per-category channels (FR-AND-7), severity thresholds, quiet hours, digest batching. |
| TR-AND-17 | **Scope creep toward web parity** turns a narrow triage client into a second full product. | High | High | Hard scope boundary (FR-AND-19, BRD §5.3); written justification for every addition. |
| TR-AND-18 | **Cached stale data misleads a decision** — an operator acts on an out-of-date anomaly list. | Medium | High | Mandatory staleness labelling (CR-2), short TTLs (CR-3), refusal of writes derived from cache (CR-1). |
| TR-AND-19 | **Intermittent Indian network coverage** produces a poor experience without careful offline and retry design. | High | Medium | Explicit offline states (FR-AND-20), bounded retry with backoff, small payloads, pagination, no state loss on connectivity change. |
| TR-AND-20 | **Framework lock-in** — the wrong choice among Kotlin/Compose, React Native and Flutter. | Medium | Medium | Decide by ADR against explicit criteria; weight existing React competency and iOS intent heavily. |

### 12.3 Dependencies

| Dependency | Type | Criticality | Note |
|---|---|---|---|
| Kailash backend API | Internal | **Critical** | The app is useless without it |
| Backend push infrastructure with fallback | Internal | **Critical** | **Does not exist**; must be built first |
| Staging environment | Internal | High | **Does not exist**; needed for safe pre-release testing |
| Firebase Cloud Messaging | External | **Critical** for the core value proposition | Not configured — **but the Firebase project already exists**, lowering the barrier |
| Google Play Console | External | **Critical** | Not held |
| Managed Google Play | External | **Critical** for private distribution | Not established |
| Cloud device farm | External | High | Needed for the fragmentation matrix |
| **OEM battery-management behaviour** | External | **Critical and uncontrollable** | The single largest technical risk; changes without notice per OEM per OS version |
| Android SDK / Gradle toolchain | External | **Critical** | Annual churn |
| Chosen framework ecosystem | External | High | Kotlin/Compose, React Native or Flutter — each with its own cadence |
| Mobile engineering capacity | Internal | **Critical** | Not allocated |

---

## 13. Appendix

### 13.1 Parent and sibling documents

| Document | Location | Relationship |
|---|---|---|
| **`BRD_kailash_ai.md`** | `../BRD_kailash_ai.md` | Parent product BRD — platform-wide business requirements |
| **`TRD_kailash_ai.md`** | `../TRD_kailash_ai.md` | Parent product TRD — the backend architecture, data model and API any client consumes |
| `BRD_android_app_kailash_ai.md` | Same directory | Companion business requirements, including the decision criteria for building |
| `BRD_web_app_kailash_ai.md` / `TRD_web_app_kailash_ai.md` | `../web_app_kailash_ai/` | The one Kailash client that exists |
| `BRD_ios_app_kailash_ai.md` / `TRD_ios_app_kailash_ai.md` | `../ios_app_kailash_ai/` | Sibling surface — records the equivalent no-app position for iOS |

### 13.2 Directory contents, verbatim

```
android_app_kailash_ai/
├── deployed/                        (empty — no build has ever been deployed)
├── not_deployed/                    (empty — no build exists to be pending)
├── BRD_android_app_kailash_ai.md
└── TRD_android_app_kailash_ai.md    ← this document
```

### 13.3 Conditional manifest permissions at MVP scope

| Permission | Required? | Justification |
|---|---|---|
| `INTERNET` | **Yes** | All functionality is backend-served |
| `ACCESS_NETWORK_STATE` | **Yes** | Offline-state detection (FR-AND-20) |
| `POST_NOTIFICATIONS` (API 33+) | **Yes** | Alert delivery — the app's primary justification |
| `USE_BIOMETRIC` | **Yes** | Session unlock (FR-AND-4) |
| `RECEIVE_BOOT_COMPLETED` | Optional | FCM token restoration after reboot |
| `REQUEST_IGNORE_BATTERY_OPTIMIZATIONS` | Conditional | Only if the generic exemption flow is used; **note this permission attracts Play policy scrutiny and must be justified** |
| `CAMERA` | **No** | Only if platform-level document capture is added |
| `RECORD_AUDIO` | **No** | Only if voice input to GANESHA is added |
| `READ_EXTERNAL_STORAGE` / `READ_MEDIA_*` | **No** | Not needed at MVP scope |
| `ACCESS_FINE_LOCATION` / `ACCESS_COARSE_LOCATION` | **No** | Kailash has no location-dependent feature |
| `READ_CONTACTS` / `READ_SMS` | **No** | Never required |

Declaring an unused permission is a Play policy risk and a privacy-posture failure.

### 13.4 Notification category and channel specification (conditional)

| Category | Channel importance | Trigger | Deep link target |
|---|---|---|---|
| `anomaly` | High | Anomaly service score above threshold | Alert detail |
| `sla_breach` | High | SLA breach detected | Alert detail |
| `guardian_escalation` | High | SHIV or GANESHA escalates | Guardian detail |
| `task_assigned` | Default | Task assigned to the signed-in user | Task detail |
| `system_incident` | High | System-health incident | System health |

All high-importance categories require the FR-AND-10 fallback path.

### 13.5 OEM battery-restriction reference (conditional)

| OEM / Skin | Mechanism | User action required |
|---|---|---|
| Xiaomi / Redmi / Poco (MIUI, HyperOS) | Autostart and battery saver restrictions | Enable Autostart; set battery saver to "No restrictions" |
| Oppo / Realme (ColorOS) | Background power management, startup manager | Allow background running; allow auto-launch |
| Vivo / iQOO (FuntouchOS, OriginOS) | High background power consumption whitelist | Allow high background power; allow auto-start |
| Samsung (One UI) | "Sleeping apps" / "Deep sleeping apps" | Add to "Never sleeping apps" |
| Huawei (EMUI) | Protected apps / launch management | Manage manually; enable auto-launch |
| Generic Android | Doze and App Standby buckets | `REQUEST_IGNORE_BATTERY_OPTIMIZATIONS` prompt |

The app must detect its restriction state and route users to the correct screen per OEM — a maintenance burden that grows with each new OEM and OS release.

### 13.6 Glossary

| Term | Meaning |
|---|---|
| **FCM** | Firebase Cloud Messaging — Google's push notification service |
| **AAB** | Android App Bundle — Play's required publishing format |
| **ANR** | Application Not Responding — a Play Console bad-behaviour metric |
| **API level** | Android SDK version identifier (API 26 = Android 8.0) |
| **BiometricPrompt** | Android's unified biometric authentication API |
| **Material 3 / Material You** | Google's current design system, including dynamic colour |
| **Managed Google Play** | Google's private organisational app distribution channel |
| **Doze / App Standby** | Android's built-in background restriction mechanisms |
| **OEM battery management** | Vendor-specific background restrictions beyond stock Android |
| **R8 / ProGuard** | Android code shrinking and obfuscation |
| **Play App Signing** | Google-managed app signing key custody |
| **MDM** | Mobile Device Management |
| **ADR** | Architecture Decision Record |
| **`ApiResponse`** | The Kailash standard response envelope |

### 13.7 Open technical questions

1. Does Go4Garage hold a Google Play Console developer account, and is managed Google Play available?
2. **Should the PWA route be evaluated and costed first?** Chrome for Android supports installability and web push; a service worker on the existing React app would deliver both native benefits at a fraction of the cost. (Strongly recommended.)
3. Should the channel-agnostic notification dispatcher with acknowledgement and fallback be built now, independent of any mobile decision? (Recommended: yes.)
4. Should client-side schema validation be added to the web client now, so a future second client inherits it? (Recommended: yes.)
5. Should a staging environment be created for Kailash regardless of the mobile question?
6. Given FCM can relay to APNs, should a single dispatch implementation be designed to serve both platforms from the outset?
7. Which framework — and given the parent BRD's position that Android would lead any mobile programme with iOS following, does that favour React Native for cross-platform reuse?
8. What is the realistic OEM distribution across Go4Garage staff devices, and what would per-OEM notification testing cost annually?
9. What is the MDM baseline for devices holding a privileged Kailash session?
