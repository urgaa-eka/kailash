# design-sync notes — Kailash AI Design System

Repo-specific gotchas for future syncs. Read this before re-running.

Project: https://claude.ai/design/p/cacafaa4-4139-4b7d-8d58-c5294c73c60c

## Shape

- `frontend/` is a **CRA application**, not a packaged design system: no library
  entry, no `dist/`, no `.d.ts`, and JSX lives in `.js` files (esbuild's default
  `.js` loader can't parse that). `.design-sync/build-ds.mjs` supplies the
  missing library build; `cfg.buildCmd` runs it. Everything else in this file
  follows from that.
- The converter is pointed at the generated entry:
  `--entry ./frontend/.ds-lib/entry.js --node-modules ./frontend/node_modules`.
- `build-ds.mjs` regenerates `componentSrcMap` and `dtsPropsFor` into
  `config.json` on every run, preserving every hand-maintained key. Don't hand-edit
  those two fields — edit the extractor.

## Build gotchas (each cost a debugging cycle)

- **`.js` files hold JSX.** `loader: {'.js': 'jsx'}` in build-ds.mjs. Without it
  the build dies on the first `<`.
- **Everything except React is bundled at the build-ds stage**, not left for the
  converter. `@react-three/fiber` pulls in `react-reconciler`, which reaches
  `scheduler`; the converter's shim throws `[SCHEDULER_MISSING]` on any bare
  `scheduler` import.
- **`process` shim** (banner in build-ds.mjs). CRA's webpack injects one; several
  bundled deps read more of `process` than a `NODE_ENV` define covers, and the
  whole IIFE dies before assigning `window.KailashDS`.
- **`require` shim** (banner in build-ds.mjs). `react-reconciler` and
  `use-sync-external-store` are CommonJS and call `require("react")`. In ESM output
  esbuild compiles that to a `__require()` stub that throws unless a `require` is in
  scope. The shim answers from `window.React`, which the converter vendors.
- **Output must be ESM.** Emitting CJS from build-ds.mjs collapses the converter's
  bundle export list to one entry, and every component is then filtered out
  (`[ZERO_MATCH]`, `components: 0`).
- **Tailwind is compiled separately.** `src/index.css` is Tailwind source, not a
  stylesheet. `build-ds.mjs` runs the Tailwind CLI over
  `.design-sync/tailwind.ds.config.js` (which `require`s the app's own config so
  brand colours can't drift) and concatenates the extracted component CSS +
  `src/styles/theme.css` into `frontend/.ds-lib/ds.css` → `cfg.cssEntry`.
  **Authored preview sources are in that config's `content` globs** — utilities used
  only in a preview card would otherwise be purged.
- Tailwind's CLI must be invoked as `node node_modules/tailwindcss/lib/cli.js`.
  Node refuses to spawn the `.cmd` shim on Windows (`EINVAL`), and going through a
  shell would need quoting for the space in this repo's path.

## Findings worth acting on (repo bugs, not sync problems)

- **`Globe3D` is excluded from the design system.** `@react-three/fiber@8.18.0`
  declares peer `react ">=18 <19"`; the app is on `react@19.2`. Its bundled
  `react-reconciler` reads `__SECRET_INTERNALS….ReactCurrentOwner`, removed in
  React 19, and throws at module-evaluation time — taking the entire bundle down.
  This is very likely broken in the running app too. Fix = upgrade to
  `@react-three/fiber@9`. Then drop the entry from `EXCLUDE` in build-ds.mjs.
- **`src/components/UI/toaster.jsx` imports `@/components/ui/toast`** (lowercase
  `ui`); the directory is `UI`. This resolves on Windows/macOS and breaks on a
  case-sensitive filesystem — i.e. in Docker/Linux CI. (Eight files carried this;
  fixed in the working tree on 2026-08-01, along with `components.json`'s
  `aliases.ui`, which was regenerating the defect on every `shadcn add`.)
- **`src/components/UI/Toast.js` and `UI/toast.jsx` collide under case-insensitive
  module resolution.** CRA resolves `.js` before `.jsx`, so
  `@/components/UI/toast` reaches the Radix primitives on Linux and the bespoke
  `Toast.js` on Windows. Renaming `Toast.js` is the clean fix; it is in the live
  import graph via `context/ToastContext.js`, so it was left alone here.
- **`LoadingState` fetches its mascot from `customer-assets.emergentagent.com`.**
  A third-party host is in the critical path of the app's first paint; if it goes
  away the loading screen renders without its brand mark. The preview shows that
  degraded state, since capture runs offline.
- **`DepartmentDetailsPanel` fetches from `REACT_APP_BACKEND_URL` on mount**, so
  only its pre-response state is capturable. Its card is honest about that.
- **8 of the 11 brand tokens do not match their own documented hex.** In
  `frontend/src/index.css` each `--g4g-*` token carries a comment naming the brand
  hex, and for eight of them the declared HSL triple renders something else:

  | Token | Declared | Renders | Comment says |
  |---|---|---|---|
  | `--g4g-purple` | `282 95% 27%` | `#5F0386` | `#570683` |
  | `--g4g-purple-light` | `271 36% 57%` | `#936AB9` | `#8172AD` |
  | `--g4g-green` | `126 34% 37%` | `#3E7E45` | `#417E46` |
  | `--g4g-bright-green` | `147 90% 44%` | `#0BD566` | `#0DA34E` |
  | `--g4g-orange` | `24 64% 59%` | `#D98954` | `#DF8C4D` |
  | `--g4g-green-light` | `102 34% 60%` | `#8BBC76` | `#83B56F` |
  | `--g4g-gray` | `250 20% 82%` | `#CBC8DA` | `#D0CFD8` |
  | `--g4g-text-gray` | `0 0% 35%` | `#595959` | `#5A5A5A` |

  Most deltas are small enough to read as HSL↔hex rounding. **`--g4g-bright-green`
  is not** — `#0DA34E` is `hsl(146 85% 34.5%)`, so the declared lightness is ~9.5
  points too high and the rendered green is markedly brighter. That token also
  feeds `--accent` (line 46), so it reaches every shadcn accent surface (menu hover
  and selected rows, the Menubar active trigger, `Command`'s selected row,
  `Calendar`'s in-range days) and the focus outlines at lines 298/338/340. With
  white `--accent-foreground` the contrast is **1.96:1**, against **3.30:1** for the
  intended colour — both under WCAG AA, but the shipped token is about half.

  **Deliberately not "fixed" here.** The design system must ship the same tokens the
  app ships, and changing a brand colour changes the running product — the owner's
  call. `conventions.md` documents the values that actually render and tells the
  design agent to use token names rather than pasted hexes.

- **`DepartmentCard` asks for a Tailwind colour that does not exist.**
  `frontend/src/components/DepartmentCard.js:12` uses `ring-2 ring-sacred-gold`, but
  `sacred-gold` is defined only as a CSS custom property in
  `src/styles/spiritual-theme.css` and is **not registered in
  `tailwind.config.js`** (zero occurrences of "sacred" there). The utility never
  compiles, so `ring-2` falls back to Tailwind's default `blue-500/50` — the
  selected-department ring, which is the entire visual signal of the active state,
  renders periwinkle blue instead of gold. Register the `sacred-*` palette in the
  Tailwind theme to fix.

- **`DepartmentDetailsPanel` hardcodes raw Tailwind blues** (`bg-blue-600` /
  `hover:bg-blue-700` on the Retry CTA at line 143, `bg-blue-500` at 54, `bg-blue-50`
  at 305) instead of DS tokens, so the panel's only interactive control is off-palette.

- **`SpiritualQuote` ignores its `deityId` prop.** `SpiritualQuote.js` destructures
  `deityId` and then calls `getDailyQuote()` with no argument, so every instance
  renders the same daily quote regardless. Either plumb the prop through or drop it
  from the signature. (Related, but deliberate: `src/data/deityImages.js` maps every
  deity key to one shared `SPIRITUAL_LOGO`, so `DeityAvatar`'s `deityId` is also
  visually a no-op — that one is the data layer's stated intent.)

- **`Slider` supports neither ranges nor a disabled affordance.**
  `src/components/UI/slider.jsx` renders exactly one hardcoded
  `<SliderPrimitive.Thumb />`, so a two-value `defaultValue` paints a filled segment
  with no upper handle. Its only disabled styling is `disabled:opacity-50` on that
  thumb, and Radix sets `data-disabled` rather than the `:disabled` pseudo-class, so
  it never fires — a disabled slider is pixel-identical to an enabled one. To support
  ranges, map over `props.value`/`defaultValue` to render one Thumb per value; for
  the disabled state, switch the variant to `data-[disabled]:opacity-50`.

## Naming

Three names are exported by two modules each. `RENAMES` in build-ds.mjs decides
which module owns the plain name:

| Plain name | Owner | Other module becomes |
|---|---|---|
| `Toast` | `UI/toast.jsx` (Radix) | `UI/Toast.js` → `SimpleToast` |
| `Toaster` | `UI/toaster.jsx` (Radix + `useToast`) | `UI/sonner.jsx` → `SonnerToaster` |
| `Header` | `components/Header.js` (marketing) | `Layout/Header.js` → `LayoutHeader` |

## Grouping

Groups come from `.design-sync/docs/<Name>.md` frontmatter, generated by
build-ds.mjs from its `GROUPS` table, bound via `cfg.docsDir`. This needs the
`.design-sync/overrides/source-kit.mjs` fork: package-build only applies a doc
category when the dir-derived group is `general`, and
`src/components/{InvestorDashboard,Layout}/` would otherwise pin their own names.
To reclassify a component, edit `GROUPS` — never the generated docs.

## Provider

`DesignSystemProvider` (`.design-sync/ds-provider.jsx`) is exported from the
bundle and set as `cfg.provider`. It supplies react-router (`Link`, `useNavigate`,
`useLocation`, `Navigate` — used by 6 components) and the Radix tooltip context.
It is scaffolding, not a component the app itself ships.

## Authoring previews for this DS

- **Import from `'frontend'`.** The story-import policy maps the package name to
  `window.KailashDS`, so `import { Button } from 'frontend'` renders the shipped
  bundle rather than a second source copy.
- **Overlays are rendered open**, because their content is a fixed-position
  portal and a closed one leaves an empty card. Each one has a different lever:
  `defaultOpen` for Dialog / AlertDialog / Sheet / Drawer / Popover / DropdownMenu,
  `open` for Tooltip and HoverCard (hover-only), and the **root's `defaultValue`**
  for Menubar and NavigationMenu.
- **ContextMenu is the exception.** Radix's context-menu root has no `open` prop,
  and `ContextMenuContent` hardcodes a Portal that is gated on the open state, so
  `forceMount` does nothing (tried; the card showed only the trigger). The
  previews dispatch a real `contextmenu` MouseEvent at the trigger in a
  `useEffect` — the same event the component listens for.
- Every fixed-position component carries `cfg.overrides.<Name> = {cardMode:
  "single", viewport: "WxH"}`. Dialog and AlertDialog use a **≥640px** viewport on
  purpose so their footers' `sm:flex-row` applies and the card reads as desktop.
- Radix autofocuses the first field on open, which paints a text-selection
  highlight across the captured card. `onOpenAutoFocus={(e) => e.preventDefault()}`
  on the content is the fix; it does not affect keyboard reachability.
- **`Toaster` is deliberately left on the floor card.** It renders from the
  module-level `useToast` store, which lives inside the bundle, and neither
  `toast` nor `useToast` is on the barrel (both are non-PascalCase, so the
  discovery filter drops them). A preview therefore has no way to push a toast
  into it. `Toast` itself is authored, driven straight through `ToastProvider`.
  To author `Toaster` later, add a module exporting the hook via `cfg.extraEntries`.
- `Form` works even though `Form` is react-hook-form's `FormProvider` from the
  bundle's copy while the preview calls `useForm()` from its own — the provider
  being rendered is the bundle's, so the bundle's `useFormContext` reads it.
- `Calendar` previews pin a fixed month. A today-relative default would change
  the render hash every calendar day and force a needless re-verify.
- **Watch for responsive classes: Tailwind breakpoints key off the browser
  viewport, not the card.** A component styled `hidden lg:block` or
  `lg:grid-cols-4` renders in its narrow form — or not at all — unless that
  component's `cfg.overrides.<Name>.viewport` is wider than the breakpoint
  (`lg` = 1024px). This bit twice: `GlobeVisualization` captured completely blank
  (`hidden lg:block`, now on the floor card because no capture width helps a
  `display:none`), and `KPIGrid`'s `columns={4}` captured as a 2×2 grid until its
  viewport was raised to 1180px. A wrapper `className` cannot fix either — only
  the viewport can.

## Build-process gotchas

- **Never run two `package-build.mjs` processes against the same `--out`.** Both
  `rm -rf` the directory at start; the second one corrupts the first. If it
  happens, `rm -rf ds-bundle` and rebuild once.
- `preview-rebuild.mjs` refuses with `[CONFIG_STALE]` after any `cfg.overrides`
  edit — the full build re-stamps the grade keys. Batch override changes so one
  full build covers several components.
- The fast inner loop, when only preview `.tsx` files changed:
  `build-ds.mjs --quiet` → `cp frontend/.ds-lib/ds.css ds-bundle/_ds_bundle.css`
  → `preview-rebuild.mjs --components …` → `package-capture.mjs --components …`.
  The `cp` is what carries newly used Tailwind utilities into the rendered cards.
- Use `--skip-dts` for intermediate builds only. It stubs the `.d.ts` bodies and
  `package-validate.mjs` hard-fails `[DTS_STUBBED]`; the final pre-upload build
  must run without it.

## Known render warns

The final gate is `validate exit 0`, `bad: 0`, with these eight `[RENDER_THIN]`
warns and one `[FONT_REMOTE]` — all triaged as legitimate. A warn NOT on this list
is new and should be looked at.

- `[FONT_REMOTE] "Inter", "source-code-pro", "JetBrains Mono"` — expected. The app
  loads Inter and JetBrains Mono from Google Fonts in `public/index.html`;
  `ds.css` mirrors that with the same `@import`, so the families load at runtime.
- `[RENDER_THIN]` on the five hero visuals — `DualRingWheel`, `MascotWheel`,
  `NeuralNetworkMap`, `SimpleGlobeAnimation`, `VideoBackground`. These are
  page-level decorations with almost no text; they render their real branded
  content but are cropped at the top by construction (see the authoring section).
- `[RENDER_THIN] LoginCard`, `LoginCardOverlay`, `TwoFactorModal` — large branded
  surfaces whose text-to-area ratio is low. All three were visually confirmed
  complete during grading; `TwoFactorModal` is additionally top-cropped because it
  anchors against a full-page container.
- `AspectRatio` no longer trips the warn — its cells now give the wrapper a visible
  child.

## Re-sync risks

- `build-ds.mjs` extracts prop contracts by **parsing the source's destructured
  parameter list and `cva()` variants** — there are no types in this repo. It is a
  heuristic: props that are only read off a `props` object, or forwarded through a
  wrapper, won't appear, and inferred types are best-effort. 246 of 270 components
  got a contract; the rest fall back to an open index signature. Spot-check a few
  `.d.ts` files after any refactor of component signatures.
- The Tailwind purge depends on `content` globs. **A new preview directory or a
  class built by string concatenation will silently render unstyled.**
- `frontend/node_modules` is assumed installed and matching the lockfile; nothing
  in this pipeline reinstalls it.
- The `EXCLUDE` list in build-ds.mjs is the only place a component can silently
  disappear from the design system. Check it when a count looks wrong.
- Playwright 1.62.1 is installed in `.ds-sync/` and matches the cached
  `chromium-1234` build. A newer playwright would try to download a browser.
