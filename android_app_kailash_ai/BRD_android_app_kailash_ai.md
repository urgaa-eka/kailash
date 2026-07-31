# Business Requirements Document — Kailash-Ai Android Application

## 1. Document Control

| Field | Value |
|---|---|
| **Document title** | Business Requirements Document — Kailash-Ai Android Application |
| **Product** | Kailash — Go4Garage internal ML/AI platform |
| **Surface** | Android (phone / tablet native client) |
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
| **Companion document** | `TRD_android_app_kailash_ai.md` (same directory) |
| **Source of truth** | `C:\Go4Garage( Eka)\Kailash-Ai\android_app_kailash_ai`, product HEAD commit `40cca17` dated 2026-07-31 |

### 1.1 Revision History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0 | 2026-07-31 | Documentation Workstream | Initial draft. Records the current no-native-client position and defines conditional requirements should that position be revisited. |

---

## 2. Executive Summary

### 2.1 The headline finding

**There is no Kailash Android application.** No Kotlin, Java, React Native, Expo or Flutter project exists in this repository for Kailash, and none is currently planned. The directory `android_app_kailash_ai/` contains exactly two empty placeholder subdirectories — `deployed/` and `not_deployed/` — and nothing else. There is no Gradle build, no `AndroidManifest.xml`, no application ID, no Play Console record, no signing keystore and no release track.

This is a **deliberate consequence of what Kailash is**, not an oversight. Kailash is Go4Garage's internal ML/AI platform — the shared AI engine behind URGAA, GSTSAAS, Ignition and ARJUN. Its own README states plainly that it is not a product sold to customers. Its human users are Go4Garage staff doing analytical and supervisory work on dense, multi-panel screens: reading dashboards, comparing forecasts, triaging anomalies, curating knowledge, administering roles. That work belongs on a large screen with a keyboard. Kailash is, by design, a **backend and web-only service**.

### 2.2 The Android-specific consideration

There is one argument that applies more strongly to Android than to iOS: **India runs on Android**. Go4Garage is an Indian EV/automotive business, and its staff, field partners and garage network overwhelmingly carry Android devices. If Kailash ever needed a mobile client, Android would almost certainly be the higher-priority platform, not the second one.

That observation strengthens the *ordering* of a hypothetical mobile programme without changing the *decision*. The question is not "which platform first" but "is any mobile client warranted for an internal analytics and orchestration platform." On the evidence in this repository, it is not — and the Android device-diversity problem (thousands of device/OEM/OS-version combinations, aggressive vendor battery management that suppresses background delivery, and a wide performance floor) makes an Android client materially more expensive to build well than the same client on iOS.

### 2.3 What this document is for

A BRD for an application that does not exist has three legitimate jobs, and this document does all three:

1. **Record the position unambiguously**, so no future reader, auditor, investor or new engineer mistakes an empty directory for lost work or an unmet commitment.
2. **State the decision criteria** — what would have to become true for an Android client to be justified.
3. **Pre-specify the business requirements** that would apply *if* that threshold were crossed.

Every numbered requirement in §6 is therefore **conditional**, except BR-AND-0 in §6.1, which is in force today.

### 2.4 The alternative that already exists

Go4Garage staff who need Kailash on an Android device are not without recourse. The Kailash web application (`../web_app_kailash_ai/`) is a responsive React 19 SPA, and Chrome for Android is in its supported browser matrix for read journeys and core actions, with responsive requirements down to 360 px. What Chrome does not provide is an installed app icon, FCM push notifications, offline access, biometric unlock or camera integration. Those are the entirety of what a native Android client would add — and §3.2 assesses whether any of them justifies the cost.

---

## 3. Business Objectives & Strategic Fit

### 3.1 The strategic question

The parent BRD sets out Kailash's objectives: be the single AI engine for the portfolio, insulate product teams from AI vendor churn, accumulate an automotive data moat, provide an operations cockpit, encode Indian regulatory knowledge, reduce AI time-to-market, be operationally credible, and build toward a licensable Automobile-LLM.

An Android client advances **none of them directly**. It is a delivery channel for objective O-4 (the operations cockpit) only, and that objective is already served by the web app. The question is narrow: *is there a class of Kailash work that must happen away from a desk, frequently and urgently enough to justify a second client codebase, a Play Console relationship, a device-fragmentation test matrix and permanent maintenance?*

On the evidence, the answer today is no.

### 3.2 Assessment of candidate justifications

| Candidate justification | Assessment | Verdict |
|---|---|---|
| **India is an Android market, so staff carry Android phones** | True and relevant — but it argues for *platform ordering*, not for building at all. The web app already runs in Chrome for Android. | Ordering argument, not a build argument |
| **Push notifications for anomalies and SLA breaches** | Genuinely useful — but email, SMS or a chat integration delivers the same alert without an app, and Android vendor battery management (Xiaomi, Oppo, Vivo, Samsung) actively suppresses background delivery, making push *less* reliable here than on iOS. | Addressable more cheaply, and harder here |
| **Offline access for field staff** | Kailash data is live platform state; a stale anomaly list is close to useless and potentially misleading. | Not sufficient |
| **Camera capture for document AI** | The strongest technical argument. But this capture need belongs to the *consumer products* (URGAA certifications, GSTSAAS invoices, Ignition RC documents), which have their own mobile surfaces, not to the internal platform. | Belongs to consumer products |
| **Voice input for GANESHA** | The `speech` service exists and Chrome for Android supports the Web Speech API; the web app's Permissions-Policy already allows microphone to `self`. | Addressable on web |
| **Biometric unlock for a privileged internal tool** | Real ergonomics gain — but Android BiometricPrompt has an equivalent in WebAuthn platform authenticators in Chrome. | Addressable on web |
| **Field garage-network staff need Kailash** | If true, this would be decisive. But the garage network is served by the *consumer products*, not by the internal AI platform. No evidence in this repository suggests platform access is needed in the field. | Not evidenced |
| **Cheaper distribution than iOS (no Apple ecosystem cost)** | Partly true — no annual developer fee equivalent, and sideloading or managed Google Play is simpler. But device fragmentation testing costs more than the distribution saving. | Net neutral at best |

### 3.3 Objectives, conditional on a future decision

Were an Android client ever approved, its objectives would be:

| # | Objective |
|---|---|
| **AO-1** | Deliver time-critical platform alerts (anomalies, SLA breaches, guardian escalations) to on-call staff wherever they are — reliably, in spite of Android vendor battery restrictions — with one-tap navigation to context. |
| **AO-2** | Give leadership a genuinely mobile-native read experience of the executive dashboard, designed for a phone rather than reflowed from desktop. |
| **AO-3** | Enable fast triage away from a desk — acknowledge, assign, comment, escalate — on the devices Indian staff actually carry. |
| **AO-4** | Perform acceptably on the mid-range and budget devices common in the Indian market, not merely on flagships. |
| **AO-5** | Do all of the above without forking business logic — the app is a client of the same backend contract, never a second implementation. |

### 3.4 Strategic fit conclusion

An Android client is a **channel investment, not a capability investment**. Kailash's strategic priorities per the parent BRD are the Automobile-LLM moat, consumer-product integration, durable retrieval and production hardening. A mobile client competes for the same scarce engineering attention while advancing none of those. The recommended position is: **do not build; revisit only against the explicit criteria in §11.1 — and if any mobile client is ever built, build Android first.**

---

## 4. Target Users / Personas / Stakeholders

### 4.1 Current position

**There are no Android app users, because there is no Android app.** All Kailash users are web users. Users who access the web app from an Android phone or tablet are served by the responsive web surface documented in `../web_app_kailash_ai/BRD_web_app_kailash_ai.md`.

### 4.2 Prospective personas, conditional on a future decision

| Persona | Mobile need | Would an app help? | Likely device class |
|---|---|---|---|
| **On-call platform engineer** | Receive an alert that Kailash is degraded or a guardian escalated; assess and acknowledge | **Yes** — the one unambiguous native case | Mid to high-end Android |
| **Operations manager (in the field)** | Check department status; reassign an urgent task; see today's anomalies | **Partly** — web covers reading; native improves action speed | Mid-range Android |
| **Executive** | Glance at portfolio health between meetings | **Marginal** — Chrome for Android already renders it | High-end Android or iPhone |
| **Business analyst** | Multi-panel analysis, filtering, export | **No** — desktop work by nature | Desktop |
| **Domain SME** | Curate knowledge, review digests | **No** — long-form reading and editing | Desktop |
| **Administrator** | User and role administration | **No** — and arguably should be blocked on mobile for security | Desktop |
| **Compliance officer / external reviewer** | Read a policy page and cite it | **No** — policy pages are public web URLs by design | Any |

One of seven personas has an unambiguous native need, and that need (alerting) is satisfiable by channels that require no app.

### 4.3 Device profile, conditional

If an Android client were built for an Indian internal user base, the realistic target profile would be:

| Attribute | Expected distribution |
|---|---|
| OEM | Samsung, Xiaomi/Redmi/Poco, Vivo, Oppo/OnePlus, Realme, Motorola, Google Pixel |
| Android version | Predominantly current minus 1 through current minus 4 |
| RAM | 4 GB to 8 GB typical; 3 GB devices present |
| Screen | 5.5-inch to 6.8-inch phones; some 10-inch tablets |
| Connectivity | 4G predominant, 5G growing, intermittent coverage common |
| Vendor customisation | **Aggressive battery management on Xiaomi, Oppo, Vivo and Realme** — the single largest technical risk to notification reliability |

### 4.4 Stakeholders in the decision

| Stakeholder | Interest |
|---|---|
| Go4Garage leadership | Whether the investment is justified against the moat roadmap |
| Platform engineering | Second codebase, second release cadence, contract-drift risk across clients |
| Security / Compliance | Device-level data exposure, MDM posture, sideloading versus managed Play distribution |
| Finance | Mobile engineering capacity, device test matrix, ongoing OS-version maintenance |
| Consumer-product teams | Whether platform mobile effort would be better spent on *their* customer-facing Android apps — which serve the Indian market directly |

---

## 5. Scope

### 5.1 Current scope

**Empty.** There is no Android application in scope. This document's scope is limited to recording the position and pre-specifying conditional requirements.

### 5.2 Conditional in-scope (if an Android client is ever approved)

- **Authentication** — email and password against the Kailash backend, TOTP two-factor challenge, and biometric unlock via BiometricPrompt for session resumption.
- **Push notifications via FCM** for anomaly alerts, SLA breaches, guardian escalations, task assignments and system-health incidents, with deep links into the relevant screen — **including explicit handling of OEM battery-optimisation suppression**.
- **Read surfaces** — executive dashboard, department list and detail, task list and detail, alert feed, system health, designed for a phone rather than reflowed.
- **Focused write actions** — acknowledge an alert, assign or reassign a task, change task status, add a comment.
- **GANESHA conversational access** — ask a question, read the composed answer, see which departments were engaged.
- **Role-aware presentation** consistent with the backend's five-role model.
- **Session security** — EncryptedSharedPreferences or Android Keystore-backed storage, biometric gate, auto-lock on background, remote sign-out.
- **Material 3 (Material You) design conformance**, including dynamic colour on Android 12 and above.
- **Distribution** — managed Google Play (private app) for Go4Garage, or internal-track distribution; **not** a public Play Store listing.
- **Tablet support** — at minimum a correct scaled experience; ideally an adaptive layout.
- **Performance on mid-range and budget devices**, not only flagships.

### 5.3 Conditional out-of-scope

- **Public Google Play listing.** Kailash is internal; distribution would be private.
- **Offline data editing.** Live platform state must not be mutated from a stale local copy.
- **Feature parity with the web app.** A phone client covers alerting, triage and glanceable read — not analytics deep-dives, user administration or knowledge curation.
- **User administration and RBAC changes from mobile.** Excluded on security grounds.
- **In-app purchases, subscriptions or Google Play Billing.** Kailash has no billing surface anywhere.
- **A second implementation of business logic.** All computation stays in the backend.
- **Wear OS, Android TV, Android Auto or ChromeOS-specific builds.**
- **Third-party analytics or advertising SDKs.**
- **Support for Android versions below the defined minimum** (see BR-AND-15).

---

## 6. Business Requirements

### 6.1 Operative requirement (in force today)

| ID | Requirement | Priority | Verification |
|---|---|---|---|
| **BR-AND-0** | Go4Garage **shall maintain and communicate the position that Kailash has no Android application and none is planned**, and shall not represent a Kailash mobile app as existing, in progress or forthcoming in any internal document, investor material, roadmap or job specification. The `android_app_kailash_ai/` directory shall be understood as documentation scaffolding, not as an abandoned or partial project. | Must | Inspect `android_app_kailash_ai/` — it contains only empty `deployed/` and `not_deployed/` directories. Review internal and external collateral for any contrary claim; there should be none. |

### 6.2 Conditional requirements (dormant until an Android client is approved)

> The following take effect **only** upon a documented, approved decision to build an Android client, satisfying the criteria in §11.1.

| ID | Requirement | Priority | Verification |
|---|---|---|---|
| **BR-AND-1** | The app **shall authenticate against the same Kailash backend** used by the web client, honouring the same JWT session model and the same five-role RBAC, with **no separate user database, no separate credential store and no mobile-only authentication path**. | Must | A role change made on the web takes effect in the app on next token refresh; no account is valid in one client but not the other. |
| **BR-AND-2** | The app **shall support two-factor authentication** where enabled on the account, accepting a TOTP code or a single-use backup code, matching the web flow exactly, with SMS autofill support where the code is delivered that way. | Must | A 2FA-enabled account cannot sign in without a valid code; a consumed backup code is rejected on reuse. |
| **BR-AND-3** | The app **shall support biometric session unlock** via BiometricPrompt (fingerprint, face or device credential), with a device-credential fallback, and **shall automatically lock when backgrounded** beyond a configured interval. | Must | Background past the interval; resumption requires biometric or device credential. Cancelling returns to a locked state, never to content. |
| **BR-AND-4** | The app **shall deliver push notifications via Firebase Cloud Messaging** for at least: anomaly above a configured severity, SLA breach, guardian escalation, task assignment to the signed-in user, and system-health incident. Each notification **shall deep-link to the relevant in-app screen**. | Must | Trigger each server-side; the device receives it within 60 seconds on an unrestricted device; tapping opens the correct screen with the correct record. |
| **BR-AND-5** | The app **shall detect and mitigate OEM battery-optimisation suppression of notifications** — detecting when the app is battery-restricted, guiding the user through the OEM-specific exemption flow (Xiaomi, Oppo, Vivo, Realme, Samsung and others), and **shall degrade to a secondary channel (email or SMS) when push delivery cannot be assured**. | Must | On a Xiaomi or Oppo device with default battery settings, verify delivery; verify the in-app guidance appears when restricted; verify the fallback channel fires when push is undeliverable. |
| **BR-AND-6** | Notification permission (Android 13 and above) **shall be requested in context**, after the user has seen why it matters — never on first launch — and the app **shall remain fully usable if permission is denied**. | Must | Decline at first prompt; all non-alerting functionality still works; the app does not re-prompt aggressively. |
| **BR-AND-7** | The app **shall request the minimum runtime permissions necessary**, with clear rationale shown before each request, and **shall request none at all unless a feature requiring it is used**. At MVP scope only `POST_NOTIFICATIONS` (Android 13+) and biometric access are expected. | Must | Fresh install requests no permission until the relevant feature is invoked; the manifest declares no unused permission. |
| **BR-AND-8** | The app **shall provide a phone-native executive read experience** — not a reflowed desktop dashboard — covering portfolio health, department status, open alerts by severity and task load, legible at a glance in under five seconds. | Must | Usability test: an executive extracts current platform status within five seconds on a mid-range device. |
| **BR-AND-9** | The app **shall support focused triage actions**: acknowledge an alert, assign or reassign a task, change task status, and add a comment — each completable in three taps or fewer from the relevant notification. | Must | Tap-count measurement for each action from a cold notification tap. |
| **BR-AND-10** | The app **shall provide GANESHA conversational access** — submit a question, read the composed answer, and see which departments were engaged. | Should | The same prompt returns equivalent content on Android and web; long responses show progress rather than appearing frozen. |
| **BR-AND-11** | The app **shall enforce role-aware presentation** — a `viewer` shall see no action control, and no control visible to any role shall produce an authorisation error when used. | Must | Sign in as each of the five roles; enumerate visible controls; exercise each; zero authorisation errors. |
| **BR-AND-12** | The app **shall not permit user administration, RBAC changes or platform settings changes**; those remain web-only on security grounds. | Must | Confirm no such screen exists for any role. |
| **BR-AND-13** | The app **shall be distributed privately** — via managed Google Play (private app targeted at the Go4Garage organisation) or an equivalent controlled channel — and **shall not be published as a public Play Store listing**. | Must | Confirm the distribution method; the app is not discoverable in public Play Store search. |
| **BR-AND-14** | The app **shall satisfy Google Play policy requirements** for the chosen track, including the Data Safety declaration, target-API-level requirements, permissions declarations, and any policy provisions specific to private/enterprise apps. | Must | A Play Console submission passes review; a completed policy checklist is retained. |
| **BR-AND-15** | The app **shall conform to Material Design 3 (Material You)** — standard navigation components, dynamic colour on Android 12+, correct elevation and motion, edge-to-edge layout with proper insets, predictive back gesture support, and system theme (light/dark) adherence. | Must | Material Design review checklist completed; the app is visually and behaviourally native on a Pixel and on a heavily-skinned OEM device. |
| **BR-AND-16** | The app **shall support a minimum API level covering at least 90% of the target user base** (expected: API 26 / Android 8.0 or later at time of build) and **shall target the current API level required by Google Play policy**, with functional support on both phones and tablets. | Must | Functional pass on the minimum supported version, the target version, one budget device, one mid-range device, one flagship and one tablet. |
| **BR-AND-17** | The app **shall perform acceptably on mid-range and budget Indian-market devices** — not merely flagships — with defined cold-launch, scroll and memory budgets met on a 4 GB device. | Must | Performance test on a representative budget device (4 GB RAM, mid-tier SoC); budgets in the companion TRD met. |
| **BR-AND-18** | The app **shall meet Android accessibility expectations** — full TalkBack support, respect for system font scaling up to the largest setting without layout breakage, sufficient contrast, minimum 48 dp touch targets, and respect for reduced-motion settings. | Must | TalkBack traversal completes every core journey; largest font scale produces no clipped or overlapping content. |
| **BR-AND-19** | The app **shall behave predictably without connectivity** — cached content clearly labelled as stale with its retrieval time, no write action silently queued or lost, and an explicit offline state rather than a hang or a blank screen. This matters more on Android given intermittent Indian network coverage. | Must | Enable Airplane Mode mid-session; cached views show staleness labels; attempted writes are refused with a clear message. |
| **BR-AND-20** | The app **shall store credentials only in Android Keystore-backed encrypted storage**, **shall never write session tokens or platform data to unprotected storage, logs or backups**, and **shall support remote sign-out** invalidating the device session. Auto-backup shall exclude all sensitive data. | Must | Filesystem, logcat and backup-content inspection finds no token in the clear; a server-side revocation signs the device out on next request. |
| **BR-AND-21** | The app **shall be released through a controlled process** — internal testing track, then closed testing, then the private production track — with staged rollout, a documented rollback position, and release notes for every build. | Must | A release passes through the internal track before production; a staged rollout halt and rollback are demonstrated. |
| **BR-AND-22** | The app **shall not fork business logic** — all computation, orchestration, pricing, GST treatment and AI inference remain in the Kailash backend, with the app strictly a presentation and interaction client. | Must | Code review confirms no domain rule is reimplemented; changing a backend rule changes app behaviour with no app release. |
| **BR-AND-23** | The app **shall include no third-party analytics, advertising or attribution SDK**, and its Play Data Safety declaration shall accurately reflect that. | Must | Dependency audit; the Data Safety form matches actual data collection (minimal and internal). |
| **BR-AND-24** | Before a build is authorised, **a written business case shall demonstrate that the alerting and triage need cannot be adequately met by email, SMS, chat integration or web push**, and shall account for the Android device-fragmentation test matrix cost. | Must | The business case exists, is dated, and is signed off by the platform owner and leadership. |

---

## 7. Success Metrics / KPIs

### 7.1 Metrics that apply today

| KPI | Definition | Target |
|---|---|---|
| Documentation accuracy | Internal or external materials claiming a Kailash mobile app exists | **0** |
| Android-mobile web sessions | Kailash web app sessions originating from Chrome for Android | Tracked as the primary demand signal for a future decision |
| Unmet mobile requests | Logged staff requests for capability genuinely impossible in mobile web | Tracked; a sustained rise is a decision trigger |
| Alert-channel adequacy | Share of time-critical platform alerts successfully delivered by existing channels | 95% or better — while this holds, an app is unjustified |

### 7.2 Metrics that would apply to a delivered Android app

| KPI | Definition | Target |
|---|---|---|
| Adoption | Installs among the intended staff group | 80% or better within 60 days |
| Weekly active users | Distinct users opening the app weekly | 60% or better of installs |
| **Notification delivery rate** | Pushes delivered ÷ pushes dispatched, **segmented by OEM** | 95% or better overall; **no OEM below 90%** |
| Notification-to-action time | Median from push delivery to acknowledging action | Under 5 minutes |
| Notification opt-in rate | Users granting `POST_NOTIFICATIONS` | 80% or better |
| Battery-exemption grant rate | Users completing the OEM battery-exemption flow when prompted | 70% or better |
| Triage completion rate | Alerts triaged in-app rather than deferred to desktop | 50% or better |
| Crash-free session rate | Sessions without a crash | 99.5% or better |
| ANR rate | Application Not Responding events per session | Under 0.47% (Play Console bad-behaviour threshold) |
| Cold-launch time | Time to interactive from cold start **on a 4 GB mid-range device** | Under 3 s |
| Device-model coverage | Distinct device models with a passing functional test | Top 20 models covering 80% or more of the user base |
| OS-version coverage | Users on a supported Android version | 95% or better |
| Contract-drift incidents | Production breakages caused by backend changes not reflected in the app | 0 |

Note the Android-specific KPIs — notification delivery **segmented by OEM**, battery-exemption grant rate, ANR rate and device-model coverage — which have no iOS equivalent and represent the additional cost of the platform.

---

## 8. Assumptions & Constraints

### 8.1 Assumptions

| # | Assumption | If false |
|---|---|---|
| AA-1 | Kailash remains an internal platform, not a customer-facing product. | The entire mobile question reopens on different economics. |
| AA-2 | Kailash's human work remains desk-based analytical and supervisory work. | Field-based use cases would justify reassessment — and Android would lead. |
| AA-3 | Existing alert channels (email, SMS, chat) adequately reach on-call staff. | Alerting alone could justify a lightweight app — or, more cheaply, web push. |
| AA-4 | Go4Garage's mobile engineering capacity is better spent on customer-facing consumer products, which serve the Indian Android market directly. | If capacity frees up, the calculus changes. |
| AA-5 | Staff have Android devices capable of running a modern app (API 26+, 4 GB RAM or better). | The minimum-spec floor would need lowering, raising cost. |
| AA-6 | The responsive web app remains usable in Chrome for Android for read journeys. | If mobile web regresses, an app becomes more attractive — but fixing the web app is cheaper. |
| AA-7 | Document capture belongs to consumer products, not the internal platform. | A platform-level capture need would be the strongest single argument for a client. |
| AA-8 | Managed Google Play or an equivalent private channel is available for internal distribution. | Sideloading or an MDM-pushed APK would be needed, with weaker update control. |

### 8.2 Constraints

| # | Constraint | Nature |
|---|---|---|
| AC-1 | **No Android codebase, no Gradle project, no application ID, no Play Console record exists.** Any build starts from zero. | Absolute |
| AC-2 | **Android device fragmentation** — thousands of device/OEM/OS combinations — makes a credible test matrix materially more expensive than iOS. | Technical / cost |
| AC-3 | **OEM battery management** (Xiaomi, Oppo, Vivo, Realme, Samsung) actively suppresses background work and notification delivery, undermining the single strongest use case. | Technical |
| AC-4 | Google Play target-API-level policy forces annual compatibility work regardless of feature development. | External / ongoing |
| AC-5 | A second client doubles the surface exposed to backend contract changes. | Technical |
| AC-6 | The parent product roadmap prioritises the Automobile-LLM moat, consumer integration and production hardening — a mobile client competes with all three. | Resource |
| AC-7 | Distributing an internal tool with privileged platform access onto personal devices raises security and MDM obligations. | Security |
| AC-8 | No push infrastructure of any kind exists in the Kailash backend today. | Prerequisite |

---

## 9. Risks & Mitigations

### 9.1 Risks of the current position (no app)

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| AR-1 | **The empty `android_app_kailash_ai/` directory is misread** as an abandoned or half-finished project. | High | Low | This document, plus a README in the directory stating the position explicitly. |
| AR-2 | **Time-critical alerts are missed** because on-call staff are away from a desk. | Medium | High | Ensure email/SMS/chat alerting is reliable and monitored; measure alert-channel adequacy; consider web push before an app. |
| AR-3 | **Leadership expectation gap** — an executive assumes a phone app exists, particularly given the Indian Android context. | Medium | Low | Communicate the position; demonstrate the responsive web app on an Android phone. |
| AR-4 | **Mobile web experience degrades** unnoticed in Chrome for Android, creating latent pressure for an app. | Medium | Medium | Keep Chrome for Android in the web app's tested browser matrix; test at 414 px and 360 px each release. |
| AR-5 | **A reactive, unplanned mobile build** is commissioned under pressure without a business case or the prerequisites. | Low | High | BR-AND-24 requires a written, signed-off business case before any build is authorised. |

### 9.2 Risks that would attach to building an Android app

| ID | Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| AR-6 | **OEM battery optimisation silently suppresses notifications**, defeating the app's primary justification on the very devices most common in India. | **High** | **High** | High-priority FCM messages; in-app detection and OEM-specific exemption guidance (BR-AND-5); mandatory secondary channel fallback; per-OEM delivery-rate monitoring. |
| AR-7 | **Device fragmentation** produces defects that only appear on specific OEM skins or Android versions. | **High** | Medium | Cloud device-farm testing across the top 20 models; per-model crash and ANR monitoring; staged rollout with halt criteria. |
| AR-8 | **Performance floor on budget devices** — an app tuned on a flagship is unusable on a 4 GB mid-range phone. | High | Medium | Set budgets against a mid-range reference device (BR-AND-17); profile on that device, not on a flagship. |
| AR-9 | **Ongoing maintenance burden** — annual target-API-level bumps, OEM skin changes, new device form factors (foldables). | High | Medium | Scope narrowly; budget maintenance explicitly; reassess annually against usage KPIs. |
| AR-10 | **Feature-parity creep** — pressure to reproduce the whole web app on a phone. | High | High | Hard scope boundary (BR-AND-12, §5.3); written justification for every addition. |
| AR-11 | **Contract drift between clients** — a backend change breaks Android but not web. | High | High | Shared, versioned API contract with schema validation on all clients; contract tests in CI. |
| AR-12 | **Play policy change** delays or blocks release. | Medium | Medium | Private/managed distribution reduces exposure; complete a policy checklist before each submission. |
| AR-13 | **Platform data on personal devices** widens the breach surface, with Android's more open filesystem and sideloading culture increasing exposure. | Medium | High | Keystore-backed encrypted storage, biometric gate, auto-lock, remote sign-out, backup exclusion, root detection, MDM for privileged roles. |
| AR-14 | **Notification fatigue** trains users to dismiss pushes. | High | Medium | Severity thresholds, per-category preferences, quiet hours, digest batching. |
| AR-15 | **Framework choice locks in a wrong bet** (Kotlin/Compose vs React Native vs Flutter). | Medium | Medium | Decide by ADR against explicit criteria; weight existing React competency and iOS intent heavily. |
| AR-16 | **ANR and crash rates breach Play Console bad-behaviour thresholds**, harming distribution even on a private track. | Medium | Medium | Enforce main-thread discipline; monitor ANR rate against the 0.47% threshold; profile on budget hardware. |
| AR-17 | **Two release cadences diverge**, with the app lagging backend capability. | Medium | Medium | Version the API; enforce a minimum-supported-app-version check; tolerate additive backend changes. |
| AR-18 | **Intermittent Indian network coverage** produces a poor experience without careful offline and retry design. | High | Medium | Explicit offline states (BR-AND-19), bounded retry with backoff, small payloads, pagination everywhere. |

---

## 10. Current Implementation Status

### 10.1 Platform existence statement — Android

> **No Kailash Android application exists.**
>
> As of 2026-07-31, at product HEAD commit `40cca17`, the directory `C:\Go4Garage( Eka)\Kailash-Ai\android_app_kailash_ai\` contains **only two empty subdirectories**: `deployed/` and `not_deployed/`. There are no source files of any kind.
>
> Specifically, there is:
> - **No Gradle project** (`build.gradle`, `build.gradle.kts`, `settings.gradle`, `gradle.properties`, `gradlew`)
> - **No Kotlin or Java source**
> - **No `AndroidManifest.xml`**, no application ID, no `res/` directory
> - **No React Native, Expo or Flutter project** (no `android/` platform folder, no `pubspec.yaml`, no `app.json`, no `metro.config.js`)
> - **No `google-services.json`**
> - **No signing keystore, no Play Console record, no release track, no App Bundle**
> - **No Android CI job** — `.github/workflows/ci.yml` defines `lint`, `shared`, `services`, `backend`, `frontend` and `compose-build`; there is no mobile job
> - **No FCM configuration anywhere in the backend** — no push service, no device-token model, no notification dispatch code
>
> Kailash is presently a **backend and web-only internal service**. It is Go4Garage's internal ML/AI platform, consumed by other Go4Garage products over HTTP and operated by staff through a single React 19 web dashboard. **No dedicated mobile client is planned**, unless the reader decides otherwise on the basis of the decision criteria in §11.1.

### 10.2 What exists instead

| Surface | Status | Location |
|---|---|---|
| **Backend (FastAPI)** | **Built and run locally** — populated `.venv`, roughly 24 API routers, 20 department agents, 3 guardians, 9 platform services | `Kailash-Ai/backend/` |
| **Web app (React 19)** | **Built and compiled** — roughly 70 page modules, populated `node_modules/`, compiled `build/` output, Firebase Hosting configuration | `Kailash-Ai/frontend/` |
| **Android app** | **Does not exist** — two empty placeholder directories | `Kailash-Ai/android_app_kailash_ai/` |
| **iOS app** | **Does not exist** — two empty placeholder directories | `Kailash-Ai/ios_app_kailash_ai/` |

### 10.3 Android access available today

An Android user reaches Kailash through **Chrome for Android against the web application**. Per the web app's browser matrix, Chrome for Android (current) is supported for read journeys and core actions, with responsive requirements specifying readable, navigable layouts down to 360 px and no horizontal overflow of primary content.

What that gives an Android user today: dashboard, departments and department detail, tasks, analytics, reports, GANESHA chat, knowledge base and the policy corpus — all in the browser.

What it does not give: an installed app icon, FCM push notifications, offline access, biometric unlock, camera capture or background execution.

### 10.4 Prerequisites, were a build ever approved

| # | Prerequisite | Status |
|---|---|---|
| 1 | Written, approved business case per BR-AND-24 | Not started |
| 2 | Google Play Console developer account | Not held (unverified) |
| 3 | Managed Google Play / private app distribution channel | Not established |
| 4 | Framework decision (Kotlin + Jetpack Compose vs React Native vs Flutter) recorded as an ADR | Not made |
| 5 | Backend push infrastructure — device-token model, FCM credentials, dispatch service | **Does not exist** in the backend |
| 6 | FCM project configuration (Firebase project `kailash-38268` exists for hosting; FCM is not configured) | Not configured |
| 7 | Versioned, schema-validated API contract shared across clients | Partially — the `ApiResponse` envelope exists; no client-side schema validation |
| 8 | Device test matrix and cloud device-farm access | Not established |
| 9 | Signing keystore and secure key management | Not created |
| 10 | Mobile engineering capacity | Not allocated |
| 11 | MDM baseline for privileged roles | Not defined |

Note that Go4Garage **already uses Firebase** (project `kailash-38268` for web hosting, and the Firebase Admin SDK in the backend). This lowers the barrier to FCM specifically: the account relationship exists, only the messaging configuration would be new.

---

## 11. Roadmap / Milestones

### 11.1 Near term (0 to 3 months) — *hold the position and measure*

| # | Milestone | Success criterion |
|---|---|---|
| AN-1 | **Record the position visibly.** Place a short README in `android_app_kailash_ai/` stating that no app exists and pointing to this BRD. | No reader mistakes the empty directory for lost work. |
| AN-2 | **Define the decision criteria** (below) and socialise them with leadership. | Written, agreed trigger conditions. |
| AN-3 | **Verify mobile web quality on Android.** Test core read journeys in Chrome for Android at 414 px and 360 px, on at least one mid-range device. | Documented pass/fail per journey; defects raised against the web app. |
| AN-4 | **Audit alert-channel reliability.** Confirm time-critical alerts reliably reach on-call staff by existing means. | Alert-channel adequacy KPI measured at 95% or better. |
| AN-5 | **Instrument mobile web demand.** Measure Android-originated web sessions and log unmet mobile requests. | A demand signal exists to inform any future decision. |

**Decision criteria — an Android client is reconsidered only if all four hold:**

1. Android-originated mobile web sessions exceed a sustained, material share of total sessions for three consecutive months.
2. A specific, repeatable work task is demonstrably impossible or unacceptably slow in Chrome for Android.
3. The alerting need is proven not satisfiable by email, SMS, chat integration or web push — **and** OEM battery-optimisation testing shows that a native app would actually deliver more reliably, not less.
4. Mobile engineering capacity exists that does not displace the Automobile-LLM moat, consumer-product integration or production hardening.

Criterion 3 is deliberately harder than its iOS equivalent, because on Android the native path is not automatically the more reliable one.

### 11.2 Mid term (3 to 9 months) — *cheaper alternatives before an app*

| # | Milestone | Success criterion |
|---|---|---|
| AM-1 | **Improve the mobile web experience** at phone breakpoints — larger touch targets, collapsed dense tables, a mobile-first executive read view. | Core read journeys complete comfortably at 360 px on a mid-range Android device. |
| AM-2 | **Evaluate PWA installability and web push on Chrome for Android** — which supports both, and which would deliver the two genuine native benefits (icon, notifications) at a fraction of the cost. **Android supports web push natively, unlike iOS's more limited position.** | A written comparison of PWA versus native cost and capability, including OEM battery-restriction testing of web push. |
| AM-3 | **Build backend notification infrastructure channel-agnostically** — a device/subscription model and a dispatch service targeting email, SMS, web push or, later, FCM. | Alerts deliverable through at least two channels without any app. |
| AM-4 | **Harden the API contract** with schema validation and versioning, so any future client inherits safety rather than risk. | Contract tests in CI; a breaking backend change fails the build. |
| AM-5 | **Re-evaluate against the decision criteria.** | A dated written decision: build, defer, or close. |

The PWA route deserves particular emphasis on Android: Chrome for Android supports both installability and web push, which means a service worker added to the existing React app could deliver the app icon and the notifications — the two genuine native benefits — without a second codebase. This should be exhausted before any native build is contemplated.

### 11.3 Long term (9 to 24 months) — *conditional build path*

Applicable **only** if the §11.1 criteria are met and a business case is approved.

| # | Milestone | Success criterion |
|---|---|---|
| AL-1 | **Framework decision recorded as an ADR** (Kotlin + Jetpack Compose, React Native, or Flutter), weighing team skills, iOS intent and native-capability depth. | Signed ADR. |
| AL-2 | **Provision the build and distribution environment** — Play Console account, managed Google Play channel, signing keystore with secure key management, CI build capacity. | A signed App Bundle produced by CI. |
| AL-3 | **Backend FCM support** — device-token registration, FCM credentials, notification dispatch with deep-link payloads and high-priority delivery. | A test push reaches a device and deep-links correctly. |
| AL-4 | **OEM battery-restriction mitigation** — detection, guidance flows for the major Indian OEMs, and fallback-channel wiring. | Delivery rate 90% or better on Xiaomi, Oppo, Vivo and Samsung with default settings. |
| AL-5 | **MVP: alerting and triage only** — auth with 2FA and biometric unlock, push with deep links, executive read view, alert feed, task acknowledge/assign/status. | All MVP-scoped requirements in §6.2 verified. |
| AL-6 | **Internal and closed testing tracks** with a defined tester group across at least five OEM skins. | Crash-free session rate 99.5% or better; ANR rate under threshold; feedback triaged. |
| AL-7 | **Private production release** via managed Google Play with staged rollout. | 80% or better install rate among the intended group within 60 days. |
| AL-8 | **Post-launch review at 6 months** against the §7.2 KPIs, with particular attention to per-OEM notification delivery. | A written decision to continue, narrow or retire the app. |

---

## 12. Appendix

### 12.1 Parent product documents

This application-level BRD narrows the Kailash platform requirements to the Android surface — a surface that does not currently exist. The authoritative product-level documents are:

| Document | Location |
|---|---|
| **`BRD_kailash_ai.md`** | `../BRD_kailash_ai.md` — product-level business requirements for the whole Kailash platform |
| **`TRD_kailash_ai.md`** | `../TRD_kailash_ai.md` — product-level technical requirements, including the backend API any client would consume |

Its direct companion is **`TRD_android_app_kailash_ai.md`** in this same directory, which sets out the conditional technical design.

Sibling surfaces: `../web_app_kailash_ai/` (the one client that does exist) and `../ios_app_kailash_ai/` (which records the equivalent no-app position for iOS).

### 12.2 Directory contents, verbatim

```
android_app_kailash_ai/
├── deployed/            (empty)
├── not_deployed/        (empty)
├── BRD_android_app_kailash_ai.md   ← this document
└── TRD_android_app_kailash_ai.md
```

No application source of any kind is present.

### 12.3 What the web app already provides on Android

| Capability | Chrome for Android | Native app would add |
|---|---|---|
| Dashboard, departments, tasks, analytics, reports | Yes | Phone-optimised layout |
| GANESHA chat | Yes | Nothing material |
| Knowledge base | Yes | Nothing material |
| Policy corpus | Yes | Nothing — these are public web URLs by design |
| App icon on home screen | Possible via PWA install — **but no manifest or service worker exists today** | Proper installability |
| Push notifications | **Possible via web push** — but no service worker exists today | FCM push (and not necessarily more reliable, given OEM restrictions) |
| Offline access | No (no service worker) | Cached read (of limited value on live data) |
| Biometric unlock | Possible via WebAuthn platform authenticator | BiometricPrompt natively |
| Camera capture | Via file input | Native camera integration |
| Background execution | No | Constrained by OEM battery management anyway |

The critical Android-specific observation: **two of the four genuine native benefits (icon, notifications) are achievable by adding a service worker and manifest to the existing React app.** Chrome for Android supports both. That is a fraction of the cost of a native client and should be evaluated first.

### 12.4 Comparison with the iOS position

| Dimension | iOS | Android |
|---|---|---|
| App exists | No | No |
| Web fallback | Mobile Safari | Chrome for Android |
| Web push available today | Limited on iOS | **Fully supported on Chrome for Android** |
| PWA installability | Limited ("Add to Home Screen") | **Full install support** |
| Notification reliability if built | High | **Compromised by OEM battery management** |
| Device fragmentation | Low | **High** |
| Market relevance to Go4Garage | Lower | **Higher — India is Android-first** |
| Development environment barrier | macOS required | None (Windows/Linux fine) |
| Recommended priority if any mobile client is built | Second | **First** |

The net position: Android is the higher-priority platform *if* a mobile client is ever built, but it also has the strongest cheaper alternative (PWA), and the weakest guarantee that a native app would actually improve notification reliability.

### 12.5 Glossary

| Term | Meaning |
|---|---|
| **FCM** | Firebase Cloud Messaging — Google's push notification service |
| **Managed Google Play** | Google's private app distribution channel for organisations |
| **Material 3 / Material You** | Google's current design system, including dynamic colour |
| **BiometricPrompt** | Android's unified biometric authentication API |
| **ANR** | Application Not Responding — a Play Console bad-behaviour metric |
| **API level** | Android's SDK version identifier (for example API 26 = Android 8.0) |
| **App Bundle (AAB)** | Google Play's required publishing format |
| **OEM battery management** | Vendor-specific background restrictions (Xiaomi, Oppo, Vivo, Realme, Samsung) that suppress notifications |
| **MDM** | Mobile Device Management |
| **ADR** | Architecture Decision Record |
| **PWA** | Progressive Web App — installable, offline-capable web app; the cheaper Android alternative |

### 12.6 Open questions for the document owner

1. Does Go4Garage hold a Google Play Console developer account, and is managed Google Play available?
2. Should the PWA route (service worker plus manifest on the existing React app) be evaluated and costed before any native Android decision? (Strongly recommended — Chrome for Android supports both installability and web push.)
3. Are time-critical Kailash alerts currently reaching on-call staff reliably, and through which channel?
4. Has any staff member actually requested a Kailash mobile app, and for what specific task?
5. Given the Indian market, should Android lead any mobile programme — and does that change the framework choice toward React Native (shared with a later iOS client) rather than Kotlin?
6. What is the realistic OEM distribution across Go4Garage staff devices, and what would per-OEM notification testing cost?
7. Who would own and maintain a mobile codebase, given the current team's composition?
8. Should the backend's channel-agnostic notification dispatcher be built now regardless of the mobile decision? (Recommended: yes — it improves alerting today.)
