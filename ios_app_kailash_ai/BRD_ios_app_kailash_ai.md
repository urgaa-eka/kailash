# Business Requirements Document — Kailash-Ai iOS Application

## 1. Document Control

| Field | Value |
|---|---|
| **Document title** | Business Requirements Document — Kailash-Ai iOS Application |
| **Product** | Kailash — Go4Garage internal ML/AI platform |
| **Surface** | iOS (iPhone / iPad native client) |
| **Document type** | BRD (Application level) |
| **Version** | 1.0 |
| **Date** | 2026-07-31 |
| **Status** | Draft |
| **Owner** | TBD |
| **Author** | Go4Garage Documentation Workstream |
| **Reviewers** | TBD (Platform Lead, Mobile Lead if appointed, Security, Compliance) |
| **Approvers** | TBD |
| **Classification** | Internal — Proprietary |
| **Parent product BRD** | `../BRD_kailash_ai.md` |
| **Parent product TRD** | `../TRD_kailash_ai.md` |
| **Companion document** | `TRD_ios_app_kailash_ai.md` (same directory) |
| **Source of truth** | `C:\Go4Garage( Eka)\Kailash-Ai\ios_app_kailash_ai`, product HEAD commit `40cca17` dated 2026-07-31 |

### 1.1 Revision History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0 | 2026-07-31 | Documentation Workstream | Initial draft. Records the current no-native-client position and defines conditional requirements should that position be revisited. |

---

## 2. Executive Summary

### 2.1 The headline finding

**There is no Kailash iOS application.** No Swift, Objective-C, React Native, Expo or Flutter project exists in this repository for Kailash, and none is currently planned. The directory `ios_app_kailash_ai/` contains exactly two empty placeholder subdirectories — `deployed/` and `not_deployed/` — and nothing else. There is no Xcode project, no `Info.plist`, no bundle identifier, no App Store Connect record, no TestFlight build and no provisioning profile.

This is a **deliberate consequence of what Kailash is**, not an oversight. Kailash is Go4Garage's internal ML/AI platform — the shared AI engine behind URGAA, GSTSAAS, Ignition and ARJUN. It is explicitly not a product sold to customers. Its human users are Go4Garage staff performing analytical and supervisory work: reading multi-panel dashboards, comparing forecasts, triaging anomalies, curating knowledge, and administering users and roles. That work belongs on a large screen with a keyboard. Kailash is, by design, a **backend and web-only service**.

### 2.2 What this document is for

A BRD for an application that does not exist has three legitimate jobs, and this document does all three:

1. **Record the position unambiguously**, so that no future reader, auditor, investor or new engineer mistakes an empty directory for lost work or an unshipped commitment.
2. **State the decision criteria** — what would have to become true for an iOS client to be justified.
3. **Pre-specify the business requirements** that would apply *if* that threshold were ever crossed, so a future decision starts from an informed position rather than a blank page.

Every numbered requirement in §6 is therefore **conditional**: it takes effect only upon an approved decision to build an iOS client. Until then the requirements are dormant, and the operative requirement is BR-iOS-0 in §6.1.

### 2.3 The alternative that already exists

Go4Garage staff who need Kailash on an iPhone or iPad are not without recourse. The Kailash web application (`../web_app_kailash_ai/`) is a responsive React 19 SPA, and mobile Safari on iOS is in its supported browser matrix for read journeys and core actions. A user on an iPad can reach the dashboard, departments, tasks and analytics today. What they cannot do is install an app icon, receive a push notification, work offline, or use device capabilities such as the camera for document capture. Those four gaps are the entirety of what a native iOS client would add — and §4 assesses whether any of them is worth an app.

---

## 3. Business Objectives & Strategic Fit

### 3.1 The strategic question

The parent BRD sets out Kailash's objectives: be the single AI engine for the Go4Garage portfolio, insulate product teams from AI vendor churn, accumulate an automotive data moat, provide an operations cockpit, encode Indian regulatory knowledge, reduce AI time-to-market, be operationally credible, and build toward a licensable Automobile-LLM.

An iOS client advances **none of them directly**. It is a delivery channel for objective O-4 (the operations cockpit) only, and that objective is already served by the web app. The strategic question is therefore narrow: *is there a class of Kailash work that must happen away from a desk, frequently enough and urgently enough to justify a second client codebase, an Apple Developer Program membership, an App Store review relationship and an ongoing maintenance burden?*

On the evidence in this repository, the answer today is no.

### 3.2 Assessment of candidate justifications

| Candidate justification | Assessment | Verdict |
|---|---|---|
| **Executives want dashboards on their phone** | The executive and investor dashboards are read-only summary views. Mobile Safari renders them today. A native app adds an icon, not a capability. | Not sufficient |
| **Push notifications for anomalies and SLA breaches** | Genuinely useful — but email, SMS or a chat integration delivers the same alert without an app. Web push would need a service worker, which the web app also lacks today. | Addressable more cheaply |
| **Offline access in the field** | Kailash data is live platform state; a stale forecast or a stale anomaly list is close to useless and potentially misleading. | Not sufficient |
| **Camera capture for document AI** | The strongest technical argument. The `document-ai` service ingests PDFs, and a phone camera is a natural capture device. But this capture need belongs to the *consumer products* (URGAA certifications, GSTSAAS invoices, Ignition RC documents), which have their own mobile surfaces, not to the internal platform. | Belongs to consumer products |
| **Voice input for GANESHA using device speech** | The `speech` service exists, and the web app's Permissions-Policy already allows microphone to `self`. Browser speech APIs cover this. | Addressable on web |
| **Biometric authentication (Face ID) for a privileged internal tool** | A real security ergonomics gain, but it does not on its own justify a client. WebAuthn provides platform-authenticator support in Safari. | Addressable on web |
| **Presenting the platform to investors on an iPad** | The investor executive dashboard renders in mobile Safari; an app adds polish, not function. | Not sufficient |

### 3.3 Objectives, conditional on a future decision

Were an iOS client ever approved, its objectives would be:

| # | Objective |
|---|---|
| **IO-1** | Deliver time-critical platform alerts (anomalies, SLA breaches, guardian escalations) to on-call staff wherever they are, with one-tap navigation to context. |
| **IO-2** | Give leadership a genuinely mobile-native read experience of the executive dashboard, designed for a phone rather than reflowed from a desktop layout. |
| **IO-3** | Enable fast triage away from a desk — acknowledge, assign, comment, escalate — without requiring a laptop. |
| **IO-4** | Use device capability where it adds real value: biometric unlock, native notifications, and camera capture *if* a platform-level capture use case emerges. |
| **IO-5** | Do all of the above without forking business logic — the app is a client of the same backend contract, never a second implementation. |

### 3.4 Strategic fit conclusion

An iOS client is a **channel investment, not a capability investment**. Kailash's strategic priorities per the parent BRD are the Automobile-LLM moat, consumer-product integration, durable retrieval and production hardening. A mobile client competes for the same scarce engineering attention while advancing none of those. The recommended position is: **do not build; revisit only against the explicit criteria in §11.1.**

---

## 4. Target Users / Personas / Stakeholders

### 4.1 Current position

**There are no iOS app users, because there is no iOS app.** All Kailash users are web users. Users who access the web app from an iPhone or iPad are served by the responsive web surface documented in `../web_app_kailash_ai/BRD_web_app_kailash_ai.md`.

### 4.2 Prospective personas, conditional on a future decision

| Persona | Mobile need | Would an app help? |
|---|---|---|
| **On-call platform engineer** | Receive an alert that Kailash is degraded or a guardian escalated; assess severity; acknowledge | **Yes** — push notification and one-tap context are genuinely native strengths |
| **Operations manager (in the field)** | Check a department's status; reassign an urgent task; see today's anomalies | **Partly** — the responsive web app covers reading; native would improve action speed |
| **Executive** | Glance at portfolio health between meetings | **Marginal** — a phone-optimised read view, but mobile Safari already renders it |
| **Business analyst** | Deep multi-panel analysis, filtering, export | **No** — this is desktop work by nature |
| **Domain SME** | Curate knowledge, review digests | **No** — long-form reading and editing work |
| **Administrator** | User and role administration | **No** — and arguably should not be possible from a phone on security grounds |
| **Compliance officer / external reviewer** | Read a policy page and cite it | **No** — policy pages are public web URLs by design |

Of seven personas, exactly one has an unambiguous native need, and that need (alerting) is satisfiable by channels that do not require an app.

### 4.3 Stakeholders in the decision

| Stakeholder | Interest |
|---|---|
| Go4Garage leadership | Whether the investment is justified against the moat roadmap |
| Platform engineering | Second codebase, second release cadence, contract-drift risk across two clients |
| Security / Compliance | Device-level data exposure, MDM posture, App Store distribution of an internal tool |
| Finance | Apple Developer Program membership, mobile engineering capacity, ongoing OS-version maintenance |
| Consumer-product teams | Whether platform mobile effort would be better spent on *their* customer-facing apps |

---

## 5. Scope

### 5.1 Current scope

**Empty.** There is no iOS application in scope. This document's scope is limited to recording the position and pre-specifying conditional requirements.

### 5.2 Conditional in-scope (if an iOS client is ever approved)

- **Authentication** — email and password against the Kailash backend, TOTP two-factor challenge, and biometric unlock (Face ID / Touch ID) for session resumption.
- **Push notifications via APNs** for anomaly alerts, SLA breaches, guardian escalations, task assignments and system-health incidents, with deep links into the relevant screen.
- **Read surfaces** — executive dashboard, department list and detail, task list and detail, anomaly and alert feed, system health, redesigned for a phone rather than reflowed.
- **Focused write actions** — acknowledge an alert, assign or reassign a task, change task status, add a comment.
- **GANESHA conversational access** — ask a question, read the composed answer, see which departments were engaged.
- **Role-aware presentation** consistent with the backend's five-role model.
- **Session security** — Keychain-stored credentials, biometric gate, automatic lock on backgrounding, remote sign-out.
- **Internal distribution** — Apple Business Manager custom app distribution or Ad Hoc/enterprise distribution, with TestFlight for pre-release.
- **iPad support** — at minimum a well-behaved scaled experience; ideally an adaptive layout using the larger canvas.

### 5.3 Conditional out-of-scope

- **Public App Store listing.** Kailash is internal; the app would be distributed privately.
- **Offline data editing.** Live platform state must not be mutated from a stale local copy.
- **Feature parity with the web app.** A phone client covers alerting, triage and glanceable read — not analytics deep-dives, user administration or knowledge curation.
- **User administration and RBAC changes from mobile.** Excluded on security grounds.
- **In-app purchases, subscriptions or any payment surface.** Kailash has no billing anywhere.
- **A second implementation of business logic.** All computation stays in the backend.
- **Apple Watch, tvOS, visionOS or macOS Catalyst variants.**
- **Third-party analytics or advertising SDKs.**

---

## 6. Business Requirements

### 6.1 Operative requirement (in force today)

| ID | Requirement | Priority | Verification |
|---|---|---|---|
| **BR-iOS-0** | Go4Garage **shall maintain and communicate the position that Kailash has no iOS application and none is planned**, and shall not represent a Kailash mobile app as existing, in progress or forthcoming in any internal document, investor material, roadmap or job specification. The `ios_app_kailash_ai/` directory shall be understood as documentation scaffolding, not as an abandoned or partial project. | Must | Inspect `ios_app_kailash_ai/` — it contains only empty `deployed/` and `not_deployed/` directories. Review internal and external collateral for any contrary claim; there should be none. |

### 6.2 Conditional requirements (dormant until an iOS client is approved)

> The following take effect **only** upon a documented, approved decision to build an iOS client, satisfying the criteria in §11.1.

| ID | Requirement | Priority | Verification |
|---|---|---|---|
| **BR-iOS-1** | The app **shall authenticate against the same Kailash backend** used by the web client, honouring the same JWT session model and the same five-role RBAC, with **no separate user database, no separate credential store and no mobile-only authentication path**. | Must | A user's role change made on the web takes effect in the app on next token refresh; no account exists that is valid in one client and not the other. |
| **BR-iOS-2** | The app **shall support two-factor authentication** where the account has it enabled, accepting a TOTP code or a single-use backup code, matching the web flow exactly. | Must | A 2FA-enabled account cannot complete sign-in in the app without a valid code; a consumed backup code is rejected on reuse. |
| **BR-iOS-3** | The app **shall support biometric session unlock** (Face ID or Touch ID) with a device-passcode fallback, and **shall automatically lock when backgrounded** for longer than a configured interval. | Must | Background the app past the interval; returning requires biometric or passcode. Disabling biometrics at OS level falls back to passcode, never to unauthenticated access. |
| **BR-iOS-4** | The app **shall deliver push notifications via APNs** for at least: anomaly detection above a configured severity, SLA breach, guardian escalation, task assignment to the signed-in user, and system-health incident. Each notification **shall deep-link to the relevant in-app screen**. | Must | Trigger one of each server-side; the device receives it within 60 seconds; tapping opens the correct screen with the correct record loaded. |
| **BR-iOS-5** | Notification permission **shall be requested in context**, after the user has seen why it matters — never on first launch — and the app **shall remain fully usable if permission is denied**. | Must | Decline notifications at first prompt; all non-alerting functionality still works; the app does not re-prompt aggressively. |
| **BR-iOS-6** | The app **shall request the minimum device permissions necessary**, with a clear, specific purpose string for each, and **shall request none at all unless a feature requiring it is used**. | Must | Fresh install requests no permission until the relevant feature is invoked. Each `Info.plist` purpose string names the concrete user benefit. |
| **BR-iOS-7** | The app **shall provide a phone-native executive read experience** — not a reflowed desktop dashboard — covering portfolio health, department status and the current alert set, legible at a glance in under five seconds. | Must | Usability test: an executive extracts the current platform status within five seconds of opening the app. |
| **BR-iOS-8** | The app **shall support focused triage actions**: acknowledge an alert, assign or reassign a task, change task status, and add a comment — each completable in three taps or fewer from the relevant notification. | Must | Time and count the taps for each action from a cold notification tap. |
| **BR-iOS-9** | The app **shall provide GANESHA conversational access** — submit a question, read the composed answer, and see which departments were engaged. | Should | Ask a multi-department question on mobile; the answer and department attribution match what the web client returns for the same prompt. |
| **BR-iOS-10** | The app **shall enforce role-aware presentation** — a `viewer` shall see no action control, and no control visible to any role shall produce an authorisation error when used. | Must | Sign in as each of the five roles; enumerate visible controls; exercise each; zero authorisation errors. |
| **BR-iOS-11** | The app **shall not permit user administration, RBAC changes or settings changes**; those remain web-only on security grounds. | Must | Confirm no such screen exists in the app for any role. |
| **BR-iOS-12** | The app **shall be distributed privately** — via Apple Business Manager custom app distribution or an equivalent managed channel — and **shall not be published to the public App Store**. | Must | Confirm the distribution method; the app is not discoverable in public App Store search. |
| **BR-iOS-13** | The app **shall satisfy App Store Review Guidelines** for whichever distribution channel is chosen, including the guidelines governing business/enterprise apps, account deletion where accounts are created in-app (not applicable if accounts are admin-provisioned only), and accurate privacy disclosures. | Must | A review submission passes without rejection; the guideline compliance checklist is completed and retained. |
| **BR-iOS-14** | The app **shall conform to the iOS Human Interface Guidelines** — native navigation patterns, standard controls, Dynamic Type support, Dark Mode support, safe-area respect, and correct handling of the Home indicator and Dynamic Island where present. | Must | HIG review checklist completed; the app is visually and behaviourally indistinguishable from a well-built native app in these respects. |
| **BR-iOS-15** | The app **shall support the current and previous two major iOS versions** at release, and **shall support both iPhone and iPad** with at minimum a well-behaved scaled iPad experience. | Must | Functional test across the supported version range on at least one small phone, one large phone and one iPad. |
| **BR-iOS-16** | The app **shall meet Apple's accessibility expectations** — full VoiceOver support, Dynamic Type up to the largest accessibility sizes without layout breakage, sufficient contrast, and respect for Reduce Motion. | Must | VoiceOver traversal completes every core journey; the largest Dynamic Type size produces no clipped or overlapping content. |
| **BR-iOS-17** | The app **shall behave predictably without connectivity** — cached content clearly labelled as stale with its retrieval time, no write action silently queued or lost, and an explicit offline state rather than a hang or a blank screen. | Must | Enable Airplane Mode mid-session; cached views show a staleness label; attempted writes are refused with a clear message, not silently dropped. |
| **BR-iOS-18** | The app **shall store credentials only in the iOS Keychain** with appropriate protection class, **shall never write session tokens or platform data to unprotected storage or logs**, and **shall support remote sign-out** invalidating the device session. | Must | Filesystem and log inspection finds no token outside the Keychain; a server-side session revocation signs the device out on next request. |
| **BR-iOS-19** | The app **shall be released through a controlled process** — TestFlight for internal testing with a defined tester group, staged rollout, a documented rollback position, and release notes for every build. | Must | A release passes through TestFlight before production; a rollback path is demonstrated. |
| **BR-iOS-20** | The app **shall not fork business logic** — all computation, orchestration, pricing, GST treatment and AI inference remain in the Kailash backend, with the app strictly a presentation and interaction client. | Must | Code review confirms no domain rule is reimplemented in the app; changing a backend rule changes app behaviour with no app release. |
| **BR-iOS-21** | The app **shall include no third-party analytics, advertising or attribution SDK**, and its App Privacy disclosure shall accurately reflect that. | Must | Dependency audit; the privacy nutrition label matches the actual data collection (which should be minimal and internal). |
| **BR-iOS-22** | Before a build is authorised, **a written business case shall demonstrate that the alerting and triage need cannot be adequately met by email, SMS, chat integration or web push**, with the comparison recorded. | Must | The business case document exists, is dated, and is signed off by the platform owner and leadership. |

---

## 7. Success Metrics / KPIs

### 7.1 Metrics that apply today

| KPI | Definition | Target |
|---|---|---|
| Documentation accuracy | Internal or external materials claiming a Kailash mobile app exists | **0** |
| iOS-mobile web sessions | Kailash web app sessions originating from iOS Safari | Tracked as the primary demand signal for a future decision |
| Unmet mobile requests | Logged staff requests for capability genuinely impossible in mobile web | Tracked; a sustained rise is a decision trigger |
| Alert-channel adequacy | Share of time-critical platform alerts successfully delivered by existing channels (email/SMS/chat) | 95% or better — while this holds, an app is unjustified |

### 7.2 Metrics that would apply to a delivered iOS app

| KPI | Definition | Target |
|---|---|---|
| Adoption | Installs among the intended staff group | 80% or better within 60 days |
| Weekly active users | Distinct users opening the app weekly | 60% or better of installs |
| Notification-to-action time | Median elapsed time from push delivery to an acknowledging action | Under 5 minutes |
| Notification opt-in rate | Users granting notification permission | 80% or better |
| Triage completion rate | Alerts triaged in-app rather than deferred to desktop | 50% or better |
| Crash-free session rate | Sessions without a crash | 99.5% or better |
| Cold-launch time | Time to interactive from a cold start | Under 2 s |
| App Review rejection rate | Submissions rejected on review | Under 10% |
| VoiceOver journey completion | Core journeys completable with VoiceOver | 100% |
| OS-version coverage | Users on a supported iOS version | 95% or better |
| Contract-drift incidents | Production breakages caused by backend changes not reflected in the app | 0 |

---

## 8. Assumptions & Constraints

### 8.1 Assumptions

| # | Assumption | If false |
|---|---|---|
| IA-1 | Kailash remains an internal platform, not a customer-facing product. | The entire mobile question reopens on different terms — a customer app has different economics. |
| IA-2 | Kailash's human work remains desk-based analytical and supervisory work. | Field-based use cases would justify reassessment. |
| IA-3 | Existing alert channels (email, SMS, chat) adequately reach on-call staff. | Alerting alone could justify a lightweight app — or, more cheaply, web push. |
| IA-4 | Go4Garage's mobile engineering capacity is better spent on customer-facing consumer products. | If capacity frees up, the calculus changes. |
| IA-5 | Staff have Go4Garage-managed or personally-owned iOS devices suitable for a managed internal app. | MDM and device-provisioning cost would need to be added to any business case. |
| IA-6 | The responsive web app remains usable on iOS Safari for read journeys. | If the web app regresses on mobile, an app becomes more attractive — but fixing the web app is cheaper. |
| IA-7 | Document capture belongs to consumer products (URGAA, GSTSAAS, Ignition), not to the internal platform. | A platform-level capture need would be the strongest single argument for a client. |

### 8.2 Constraints

| # | Constraint | Nature |
|---|---|---|
| IC-1 | **No iOS codebase, no Xcode project, no bundle identifier, no App Store Connect record exists.** Any build starts from zero. | Absolute |
| IC-2 | iOS development requires macOS hardware and Xcode; the observed development environment for this workspace is Windows 11. | Tooling |
| IC-3 | An Apple Developer Program membership (and, for private distribution, Apple Business Manager enrolment) would be required. | Commercial |
| IC-4 | Apple's review process and guideline changes impose an ongoing external dependency on release timing. | External |
| IC-5 | Annual iOS major releases impose a recurring compatibility maintenance cost regardless of feature work. | Ongoing |
| IC-6 | A second client doubles the surface exposed to backend contract changes. | Technical |
| IC-7 | The parent product roadmap prioritises the Automobile-LLM moat, consumer integration and production hardening — a mobile client competes with all three. | Resource |
| IC-8 | Distributing an internal tool with privileged platform access onto personal devices raises security and MDM obligations. | Security |

---

## 9. Risks & Mitigations

### 9.1 Risks of the current position (no app)

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| IR-1 | **The empty `ios_app_kailash_ai/` directory is misread** as an abandoned or half-finished project by an auditor, investor or new engineer. | High | Low | This document, plus a README in the directory stating the position explicitly. |
| IR-2 | **Time-critical alerts are missed** because on-call staff are away from a desk. | Medium | High | Ensure email/SMS/chat alerting is reliable and monitored; measure the alert-channel adequacy KPI; consider web push before considering an app. |
| IR-3 | **Leadership expectation gap** — an executive assumes a phone app exists. | Medium | Low | Communicate the position; demonstrate the responsive web app on a phone. |
| IR-4 | **Mobile web experience degrades** unnoticed because nobody tests it, creating latent pressure for an app. | Medium | Medium | Include iOS Safari in the web app's tested browser matrix (already specified in the web BRD); test at 414 px and 360 px each release. |
| IR-5 | **A reactive, unplanned mobile build** is commissioned under pressure without a business case. | Low | High | BR-iOS-22 requires a written, signed-off business case before any build is authorised. |

### 9.2 Risks that would attach to building an iOS app

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| IR-6 | **Ongoing maintenance burden** — annual OS releases, deprecations, device-size changes, toolchain upgrades, with no corresponding feature value. | High | Medium | Scope narrowly (alerting and triage only); budget maintenance explicitly; reassess annually against usage. |
| IR-7 | **Feature-parity creep** — pressure to reproduce the whole web app on a phone. | High | High | Hard scope boundary in BR-iOS-11 and §5.3; every addition requires a written justification. |
| IR-8 | **Contract drift between two clients** — a backend change breaks the app but not the web, or vice versa. | High | High | Shared, versioned API contract with schema validation on both clients; contract tests in CI covering both. |
| IR-9 | **App Store review rejection or policy change** delays or blocks release. | Medium | Medium | Private distribution via Apple Business Manager reduces exposure; complete a guideline checklist before submission. |
| IR-10 | **Platform data on personal devices** increases the breach surface. | Medium | High | Keychain-only credential storage, biometric gate, auto-lock on background, remote sign-out, MDM requirement for privileged roles. |
| IR-11 | **Notification fatigue** — over-alerting trains users to ignore pushes. | High | Medium | Severity thresholds, per-user notification preferences, digest batching for non-urgent classes. |
| IR-12 | **Cross-platform framework choice locks in a wrong bet** (React Native vs Flutter vs native Swift). | Medium | Medium | Decide against explicit criteria (team skills, Android intent, native-capability depth) and record an architecture decision. |
| IR-13 | **No macOS build capacity** in a Windows-based development environment. | High | Medium | Provision a Mac build machine or a hosted macOS CI runner as a prerequisite, budgeted in the business case. |
| IR-14 | **Two release cadences diverge** — the app lags backend capability and misrepresents platform state. | Medium | Medium | Version the API; make the app degrade gracefully against a newer backend; enforce a minimum-supported-app-version check. |
| IR-15 | **Security review of an internal tool on mobile** becomes a recurring compliance obligation. | Medium | Medium | Budget for annual mobile security review; define the device-management baseline up front. |

---

## 10. Current Implementation Status

### 10.1 Platform existence statement — iOS

> **No Kailash iOS application exists.**
>
> As of 2026-07-31, at product HEAD commit `40cca17`, the directory `C:\Go4Garage( Eka)\Kailash-Ai\ios_app_kailash_ai\` contains **only two empty subdirectories**: `deployed/` and `not_deployed/`. There are no source files of any kind.
>
> Specifically, there is:
> - **No Xcode project or workspace** (`.xcodeproj`, `.xcworkspace`)
> - **No Swift or Objective-C source**
> - **No React Native, Expo or Flutter project** (no `ios/` platform folder, no `pubspec.yaml`, no `app.json`, no `metro.config.js`)
> - **No `Info.plist`, no bundle identifier, no entitlements file**
> - **No Podfile, no Swift Package manifest, no `GoogleService-Info.plist`**
> - **No App Store Connect record, no TestFlight build, no provisioning profile, no signing certificate**
> - **No iOS-related CI job** — `.github/workflows/ci.yml` defines `lint`, `shared`, `services`, `backend`, `frontend` and `compose-build`; there is no mobile job
> - **No APNs configuration anywhere in the backend** — no push service, no device-token model, no notification dispatch code
>
> Kailash is presently a **backend and web-only internal service**. This is by design, not by omission: it is an internal ML/AI platform consumed by other Go4Garage products over HTTP, with a single human-facing React 19 web dashboard. **No dedicated mobile client is planned**, unless the reader, on reviewing the decision criteria in §11.1, decides otherwise.

### 10.2 What exists instead

| Surface | Status | Location |
|---|---|---|
| **Backend (FastAPI)** | **Built and run locally** — populated `.venv`, roughly 24 API routers, 20 department agents, 3 guardians, 9 platform services | `Kailash-Ai/backend/` |
| **Web app (React 19)** | **Built and compiled** — roughly 70 page modules, populated `node_modules/`, compiled `build/` output, Firebase Hosting configuration | `Kailash-Ai/frontend/` |
| **iOS app** | **Does not exist** — two empty placeholder directories | `Kailash-Ai/ios_app_kailash_ai/` |
| **Android app** | **Does not exist** — two empty placeholder directories | `Kailash-Ai/android_app_kailash_ai/` |

### 10.3 iOS access available today

An iOS user reaches Kailash through **mobile Safari against the web application**. Per the web app's browser matrix, iOS Safari (current and previous major version) is supported for read journeys and core actions, and the responsive requirements specify readable, navigable layouts down to 360 px with no horizontal overflow of primary content.

What that gives an iOS user today: dashboard, departments and department detail, tasks, analytics, reports, GANESHA chat, knowledge base and the policy corpus — all in the browser.

What it does not give: an app icon, APNs push notifications, offline access, Face ID unlock, camera capture, or background execution.

### 10.4 Prerequisites, were a build ever approved

| # | Prerequisite | Status |
|---|---|---|
| 1 | Written, approved business case per BR-iOS-22 | Not started |
| 2 | Apple Developer Program membership | Not held (unverified) |
| 3 | Apple Business Manager enrolment for private distribution | Not held (unverified) |
| 4 | macOS build capacity (physical Mac or hosted macOS CI) | Not available in the observed Windows environment |
| 5 | Framework decision (native Swift/SwiftUI vs React Native vs Flutter) recorded as an ADR | Not made |
| 6 | Backend push infrastructure — device-token model, APNs credentials, dispatch service | **Does not exist** in the backend |
| 7 | Versioned, schema-validated API contract shared across clients | Partially — the `ApiResponse` envelope exists; no client-side schema validation |
| 8 | Mobile engineering capacity | Not allocated |
| 9 | Device-management (MDM) baseline for privileged roles | Not defined |

---

## 11. Roadmap / Milestones

### 11.1 Near term (0 to 3 months) — *hold the position and measure*

| # | Milestone | Success criterion |
|---|---|---|
| IN-1 | **Record the position visibly.** Place a short README in `ios_app_kailash_ai/` stating that no app exists and pointing to this BRD. | No reader mistakes the empty directory for lost work. |
| IN-2 | **Define the decision criteria** (below) and socialise them with leadership. | Written, agreed trigger conditions. |
| IN-3 | **Verify mobile web quality on iOS.** Test the core read journeys in iOS Safari at 414 px and 360 px. | Documented pass/fail per journey; defects raised against the web app, not against a hypothetical native app. |
| IN-4 | **Audit alert-channel reliability.** Confirm time-critical platform alerts reliably reach on-call staff by existing means. | Alert-channel adequacy KPI measured at 95% or better. |
| IN-5 | **Instrument mobile web demand.** Measure iOS-originated web sessions and log unmet mobile requests. | A demand signal exists to inform any future decision. |

**Decision criteria — an iOS client is reconsidered only if all four hold:**

1. iOS-originated mobile web sessions exceed a sustained, material share of total sessions for three consecutive months.
2. A specific, repeatable work task is demonstrably impossible or unacceptably slow in mobile web.
3. The alerting need is proven not satisfiable by email, SMS, chat integration or web push.
4. Mobile engineering capacity exists that does not displace the Automobile-LLM moat, consumer-product integration or production hardening.

### 11.2 Mid term (3 to 9 months) — *cheaper alternatives before an app*

| # | Milestone | Success criterion |
|---|---|---|
| IM-1 | **Improve the mobile web experience** at the phone breakpoints — larger touch targets, collapsed dense tables, a mobile-first executive read view. | Core read journeys complete comfortably at 360 px. |
| IM-2 | **Evaluate web push and PWA installability** as a materially cheaper route to the two genuine native benefits (icon, notifications). | A written comparison of PWA versus native cost and capability. |
| IM-3 | **Build backend notification infrastructure channel-agnostically** — a device/subscription model and a dispatch service that can target email, SMS, web push or, later, APNs. | Alerts deliverable through at least two channels without a client. |
| IM-4 | **Harden the API contract** with schema validation and versioning, so that any future second client inherits safety rather than risk. | Contract tests in CI; a breaking backend change fails the build. |
| IM-5 | **Re-evaluate against the decision criteria.** | A dated written decision: build, defer, or close. |

### 11.3 Long term (9 to 24 months) — *conditional build path*

Applicable **only** if the §11.1 criteria are met and a business case is approved.

| # | Milestone | Success criterion |
|---|---|---|
| IL-1 | **Framework decision recorded as an ADR** (native SwiftUI, React Native, or Flutter), weighing team skills, Android intent and native-capability depth. | Signed ADR. |
| IL-2 | **Provision the build environment** — Apple Developer Program, Apple Business Manager, macOS CI capacity, signing and provisioning. | A signed build produced by CI. |
| IL-3 | **Backend APNs support** — device-token registration, APNs credentials, notification dispatch with deep-link payloads. | A test push reaches a device and deep-links correctly. |
| IL-4 | **MVP: alerting and triage only** — auth with 2FA and biometric unlock, push with deep links, executive read view, alert feed, task acknowledge/assign/status. | All MVP-scoped requirements in §6.2 verified. |
| IL-5 | **TestFlight beta** with a defined internal tester group. | Crash-free session rate 99.5% or better; feedback triaged. |
| IL-6 | **Private production release** via Apple Business Manager. | 80% or better install rate among the intended group within 60 days. |
| IL-7 | **Post-launch review at 6 months** against the §7.2 KPIs. | A written decision to continue, narrow or retire the app. |

---

## 12. Appendix

### 12.1 Parent product documents

This application-level BRD narrows the Kailash platform requirements to the iOS surface — a surface that does not currently exist. The authoritative product-level documents are:

| Document | Location |
|---|---|
| **`BRD_kailash_ai.md`** | `../BRD_kailash_ai.md` — product-level business requirements for the whole Kailash platform |
| **`TRD_kailash_ai.md`** | `../TRD_kailash_ai.md` — product-level technical requirements, including the backend API any client would consume |

Its direct companion is **`TRD_ios_app_kailash_ai.md`** in this same directory, which sets out the conditional technical design.

Sibling surfaces: `../web_app_kailash_ai/` (the one client that does exist) and `../android_app_kailash_ai/` (which records the equivalent no-app position for Android).

### 12.2 Directory contents, verbatim

```
ios_app_kailash_ai/
├── deployed/            (empty)
├── not_deployed/        (empty)
├── BRD_ios_app_kailash_ai.md   ← this document
└── TRD_ios_app_kailash_ai.md
```

No application source of any kind is present.

### 12.3 What the web app already provides on iOS

| Capability | Mobile Safari | Native app would add |
|---|---|---|
| Dashboard, departments, tasks, analytics, reports | Yes | Phone-optimised layout |
| GANESHA chat | Yes | Nothing material |
| Knowledge base | Yes | Nothing material |
| Policy corpus | Yes | Nothing — these are public web URLs by design |
| App icon on home screen | Only via "Add to Home Screen" (no manifest present) | Proper installability |
| Push notifications | No (no service worker present) | **APNs push** |
| Offline access | No | Cached read (of limited value on live data) |
| Biometric unlock | Possible via WebAuthn | **Face ID / Touch ID** natively |
| Camera capture | Via file input | Native camera integration |
| Background execution | No | Background refresh |

Four genuine additions; two of them (push, biometric) have web-based alternatives.

### 12.4 Glossary

| Term | Meaning |
|---|---|
| **APNs** | Apple Push Notification service |
| **TestFlight** | Apple's pre-release distribution and beta testing service |
| **Apple Business Manager** | Apple's private/custom app distribution channel for organisations |
| **HIG** | Apple's Human Interface Guidelines |
| **MDM** | Mobile Device Management |
| **Dynamic Type** | iOS user-controlled text sizing that apps must respect |
| **Keychain** | iOS secure credential storage |
| **ADR** | Architecture Decision Record |
| **PWA** | Progressive Web App — an installable, offline-capable web app; a cheaper alternative to a native client |

### 12.5 Open questions for the document owner

1. Does Go4Garage hold an Apple Developer Program membership, and is Apple Business Manager enrolled?
2. Is there macOS build capacity available, or would it need provisioning?
3. Are time-critical Kailash alerts currently reaching on-call staff reliably, and through which channel?
4. Has any staff member actually requested a Kailash mobile app, and for what specific task?
5. Should the cheaper PWA route (installability plus web push) be evaluated before any native decision?
6. If a mobile client is ever built, is Android the higher priority given the Indian device market?
7. Who would own and maintain a mobile codebase, given the current team's composition?
