// Library build for the Kailash AI design system.
//
// frontend/ is a CRA application, not a packaged design system: it has no
// library entry, no dist/, and its JSX lives in .js files (which esbuild's
// default loader can't parse). This script supplies the missing build so the
// design-sync converter has a normal package to consume:
//
//   1. discovers every component module under src/components
//   2. writes a barrel that re-exports them under stable names
//   3. compiles it to frontend/.ds-lib/entry.js  (ESM, JSX compiled,
//      node_modules left external so the converter bundles them itself)
//   4. compiles Tailwind to frontend/.ds-lib/ds.css and appends the
//      component-authored CSS esbuild extracted, so the bundle ships the
//      utilities the components actually use
//   5. writes .design-sync/.cache/discovered.json — the componentSrcMap the
//      converter needs (there are no .d.ts exports to discover from)
//
// It compiles the repo's own components. It never rewrites them.
//
// Usage: node .design-sync/build-ds.mjs [--quiet]

import { execFileSync } from 'node:child_process';
import { existsSync, mkdirSync, readdirSync, readFileSync, rmSync, statSync, writeFileSync } from 'node:fs';
import { dirname, join, relative, resolve } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const REPO = resolve(HERE, '..');
const PKG_DIR = join(REPO, 'frontend');
const SRC = join(PKG_DIR, 'src');
const COMPONENTS = join(SRC, 'components');
const OUT_DIR = join(PKG_DIR, '.ds-lib');
const CACHE = join(HERE, '.cache');
const QUIET = process.argv.includes('--quiet');

const slash = (p) => p.replace(/\\/g, '/');
const log = (...a) => { if (!QUIET) console.error(...a); };

// esbuild lives in the staged converter deps, not in the app's node_modules.
const esbuild = await import(pathToFileURL(join(REPO, '.ds-sync', 'node_modules', 'esbuild', 'lib', 'main.js')).href);

// ── 1. discover component modules ────────────────────────────────────────────
const SKIP_RX = /\.(test|spec|stories)\.[jt]sx?$/;
// Barrels re-export their siblings; including them duplicates every name.
const BARREL_RX = /(^|\/)index\.jsx?$/;

// Modules kept out of the bundle entirely, with the reason. Anything listed
// here is absent from the design system — not merely unpreviewed — so the list
// stays short and each entry is a hard blocker, never a convenience.
const EXCLUDE = {
  // @react-three/fiber@8.18.0 declares peer react ">=18 <19"; the app is on
  // react@19.2. Its bundled react-reconciler reads
  // __SECRET_INTERNALS…ReactCurrentOwner, which React 19 removed, and throws at
  // module-evaluation time — taking the whole IIFE down before any component
  // registers. This is a pre-existing incompatibility in the app's dependency
  // set, not something the sync introduced.
  'src/components/Globe3D.js': 'imports @react-three/fiber@8, which is incompatible with react@19',
};

function walk(dir) {
  const out = [];
  for (const e of readdirSync(dir, { withFileTypes: true })) {
    const p = join(dir, e.name);
    if (e.isDirectory()) out.push(...walk(p));
    else if (/\.jsx?$/.test(e.name) && !SKIP_RX.test(e.name)) out.push(p);
  }
  return out;
}

const files = walk(COMPONENTS)
  .filter((p) => !BARREL_RX.test(slash(p)))
  .filter((p) => {
    const rel = slash(relative(PKG_DIR, p));
    if (!EXCLUDE[rel]) return true;
    log(`  excluded: ${rel} — ${EXCLUDE[rel]}`);
    return false;
  })
  .sort((a, b) => slash(a).localeCompare(slash(b), 'en'));

// Export extraction. These files follow three shapes consistently:
//   export { A, B }            (shadcn primitives)
//   export const Name = ...    /  export function Name
//   export default Name
const PASCAL = /^[A-Z][A-Za-z0-9]*$/;

function exportsOf(file) {
  const text = readFileSync(file, 'utf8');
  const named = new Set();
  let hasDefault = false;
  let defaultName = null;

  for (const m of text.matchAll(/export\s+(?:const|let|var|function|class)\s+([A-Za-z0-9_$]+)/g)) {
    named.add(m[1]);
  }
  for (const m of text.matchAll(/export\s*\{([^}]*)\}/g)) {
    for (const part of m[1].split(',')) {
      const seg = part.trim();
      if (!seg) continue;
      const as = /^(\S+)\s+as\s+(\S+)$/.exec(seg);
      const name = as ? as[2] : seg;
      if (name === 'default') continue;
      named.add(name);
    }
  }
  const def = /export\s+default\s+([A-Za-z0-9_$]+)\s*;?\s*$/m.exec(text)
    || /export\s+default\s+(?:function|class)\s+([A-Za-z0-9_$]+)/.exec(text);
  if (/export\s+default\b/.test(text)) {
    hasDefault = true;
    defaultName = def ? def[1] : null;
  }
  return {
    named: [...named].filter((n) => PASCAL.test(n)),
    // Non-component named exports (buttonVariants, useToast…) are dropped from
    // the public surface but stay reachable through the module they live in.
    helpers: [...named].filter((n) => !PASCAL.test(n)),
    hasDefault,
    defaultName,
  };
}

// Three names are exported by two modules each. Rather than let the generic
// collision fallback invent "ToastToast", say explicitly which module owns the
// plain name and what the other one is called. Keyed "<src path>::<name>".
const RENAMES = {
  'src/components/UI/Toast.js::Toast': 'SimpleToast',           // bespoke inline-styled toast; the Radix one owns `Toast`
  'src/components/UI/sonner.jsx::Toaster': 'SonnerToaster',     // sonner-backed renderer; toaster.jsx owns `Toaster`
  'src/components/Layout/Header.js::Header': 'LayoutHeader',    // sidebar-layout header; the marketing one owns `Header`
};

// name → {file, via:'named'|'default', localName}
const picks = new Map();
const collisions = [];

for (const file of files) {
  const info = exportsOf(file);
  const base = file.split(/[\\/]/).pop().replace(/\.jsx?$/, '');
  const dirTag = slash(relative(COMPONENTS, dirname(file))).split('/').filter(Boolean).pop() || '';

  const candidates = info.named.map((n) => ({ name: n, via: 'named', localName: n }));
  if (info.hasDefault) {
    // Prefer the declared identifier; fall back to the file's PascalCase name.
    const dn = info.defaultName && PASCAL.test(info.defaultName)
      ? info.defaultName
      : base.replace(/(^|[-_.])([a-z])/g, (_, __, c) => c.toUpperCase());
    if (PASCAL.test(dn) && !candidates.some((c) => c.name === dn)) {
      candidates.push({ name: dn, via: 'default', localName: 'default' });
    }
  }

  const relPath = slash(relative(PKG_DIR, file));
  for (const c of candidates) {
    let name = RENAMES[`${relPath}::${c.name}`] ?? c.name;
    if (name !== c.name) {
      collisions.push({ name: c.name, renamedTo: name, file: relPath, reason: 'explicit' });
    }
    if (picks.has(name)) {
      const prefix = dirTag && dirTag.toLowerCase() !== 'ui'
        ? dirTag.replace(/(^|[-_])([a-z])/g, (_, __, ch) => ch.toUpperCase())
        : base.replace(/(^|[-_.])([a-z])/g, (_, __, ch) => ch.toUpperCase());
      const alias = PASCAL.test(prefix + name) ? prefix + name : `${name}Alt`;
      collisions.push({ name, keptFrom: slash(relative(PKG_DIR, picks.get(name).file)), renamedTo: alias, file: relPath, reason: 'fallback' });
      if (picks.has(alias)) continue;
      name = alias;
    }
    picks.set(name, { file, via: c.via, localName: c.localName });
  }
}

// ── 2. write the barrel ──────────────────────────────────────────────────────
mkdirSync(OUT_DIR, { recursive: true });
mkdirSync(CACHE, { recursive: true });

const byFile = new Map();
for (const [name, p] of picks) {
  if (!byFile.has(p.file)) byFile.set(p.file, []);
  byFile.get(p.file).push({ name, ...p });
}

const lines = [
  '// GENERATED by .design-sync/build-ds.mjs — do not edit.',
  '// Barrel entry for the design-sync converter. Re-exports the repo\'s own',
  '// components; adds nothing.',
];
for (const [file, entries] of byFile) {
  const spec = './' + slash(relative(OUT_DIR, file));
  const named = entries.filter((e) => e.via === 'named').map((e) => (e.localName === e.name ? e.name : `${e.localName} as ${e.name}`));
  const def = entries.find((e) => e.via === 'default');
  if (named.length) lines.push(`export { ${named.join(', ')} } from ${JSON.stringify(spec)};`);
  if (def) lines.push(`export { default as ${def.name} } from ${JSON.stringify(spec)};`);
}
lines.push(`export { DesignSystemProvider } from ${JSON.stringify('./' + slash(relative(OUT_DIR, join(HERE, 'ds-provider.jsx'))))};`);
lines.push('');

const barrel = join(OUT_DIR, '.barrel.jsx');
writeFileSync(barrel, lines.join('\n'));
log(`  barrel: ${picks.size + 1} exports from ${byFile.size} modules`);
if (collisions.length) {
  log(`  name collisions (${collisions.length}) — later module renamed:`);
  for (const c of collisions) log(`    ${c.name}: kept ${c.keptFrom}, ${c.file} -> ${c.renamedTo}`);
}

// ── 3. compile ───────────────────────────────────────────────────────────────
const result = await esbuild.build({
  entryPoints: [barrel],
  outfile: join(OUT_DIR, 'entry.js'),
  bundle: true,
  // ESM: the converter enumerates the bundle's exports to build its component
  // list, and a CJS entry collapses that list to one entry.
  format: 'esm',
  platform: 'browser',
  target: 'es2020',
  // Only React itself stays external — the converter's shim rewrites those
  // imports to window.React/window.ReactDOM. Everything else is bundled here
  // rather than left for the converter, because @react-three/fiber reaches
  // `scheduler` transitively and the converter's shim throws on a bare
  // `scheduler` import ([SCHEDULER_MISSING]). Bundling it at this stage means
  // no bare `scheduler` import ever reaches the converter.
  external: ['react', 'react/*', 'react-dom', 'react-dom/*'],
  jsx: 'automatic',
  // CRA convention: JSX in .js files.
  loader: { '.js': 'jsx', '.svg': 'dataurl', '.png': 'dataurl' },
  alias: { '@': SRC },
  // ds-provider.jsx sits in .design-sync/, outside the package — point node
  // resolution at the app's node_modules so its imports resolve like any
  // other component's.
  nodePaths: [join(PKG_DIR, 'node_modules')],
  metafile: true,
  logLevel: QUIET ? 'error' : 'warning',
  define: { 'process.env.NODE_ENV': '"development"' },
  // CRA's webpack build injects a `process` shim; several bundled deps read
  // more of it than the NODE_ENV define covers, and without this the whole
  // IIFE dies on "process is not defined" before it can assign window.KailashDS.
  banner: {
    js: [
      'var process = (typeof globalThis !== "undefined" && globalThis.process) || '
        + '{ env: { NODE_ENV: "development" }, browser: true, version: "", versions: {}, '
        + 'platform: "browser", argv: [], cwd: function () { return "/"; }, '
        + 'nextTick: function (f) { var a = [].slice.call(arguments, 1); setTimeout(function () { f.apply(null, a); }, 0); } };',
      // react-reconciler (via @react-three/fiber) and use-sync-external-store are
      // CommonJS and call require("react"). esbuild compiles that to a __require()
      // stub which throws unless a `require` is in scope; the stub checks for one
      // at module init. React itself is the converter's job — it vendors it onto
      // window.React before the bundle runs — so answer from there.
      'var require = function (m) {',
      '  if (m === "react") return window.React;',
      '  if (m === "react-dom" || m === "react-dom/client") return window.ReactDOM;',
      '  throw new Error("Dynamic require of \\"" + m + "\\" is not supported");',
      '};',
    ].join('\n'),
  },
});

const outKey = Object.keys(result.metafile.outputs).find((k) => k.endsWith('entry.js'));
const realExports = result.metafile.outputs[outKey].exports.slice().sort();
log(`  entry.js: ${realExports.length} exports`);

// ── 4. CSS: compiled Tailwind + the component CSS esbuild extracted ──────────
// Invoke the CLI's JS entry directly — node refuses to spawn .cmd shims on
// Windows without a shell, and going through a shell would need quoting for
// the space in this repo's path.
const tailwindCli = join(PKG_DIR, 'node_modules', 'tailwindcss', 'lib', 'cli.js');
const twOut = join(OUT_DIR, '.tailwind.css');
execFileSync(process.execPath, [tailwindCli, '-c', join(HERE, 'tailwind.ds.config.js'), '-i', join(SRC, 'index.css'), '-o', twOut], {
  cwd: PKG_DIR,
  stdio: QUIET ? 'ignore' : 'inherit',
});

const extractedCss = join(OUT_DIR, 'entry.css');
const parts = [
  '/* Kailash AI design system — generated by .design-sync/build-ds.mjs */',
  // The app loads these from Google Fonts in public/index.html; mirror that so
  // rendered designs get the real brand faces.
  '@import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap");',
  readFileSync(twOut, 'utf8'),
  existsSync(extractedCss) ? readFileSync(extractedCss, 'utf8') : '',
  readFileSync(join(SRC, 'styles', 'theme.css'), 'utf8'),
];
const dsCss = join(OUT_DIR, 'ds.css');
writeFileSync(dsCss, parts.join('\n\n'));
log(`  ds.css: ${(statSync(dsCss).size / 1024).toFixed(0)} KB`);

// ── 5. groups ────────────────────────────────────────────────────────────────
// The converter derives a group from the source directory, which puts all 47
// shadcn primitives plus every root-level component into one bucket. Map by
// source file to a real taxonomy instead; emitted as docs stubs below.
const GROUPS = [
  [/UI\/(button|toggle|toggle-group)\.jsx$/, 'Actions'],
  [/UI\/(input|input-otp|textarea|checkbox|radio-group|select|switch|slider|label|form|calendar)\.jsx$/, 'Forms'],
  [/UI\/(dialog|alert-dialog|sheet|drawer|popover|hover-card|tooltip|context-menu|dropdown-menu|menubar|command)\.jsx$/, 'Overlays'],
  [/UI\/(tabs|breadcrumb|pagination|navigation-menu)\.jsx$/, 'Navigation'],
  [/UI\/(alert|toast|toaster|sonner|progress|skeleton)\.jsx$/, 'Feedback'],
  [/UI\/Toast\.js$/, 'Feedback'],
  [/UI\//, 'Data display'],

  [/components\/(Login|TwoFactor|ProtectedRoute|SessionTimeout)/, 'Auth'],
  [/components\/Layout\//, 'App shell'],
  [/components\/(AppLayout|Header|MinimalHeader|MinimalFooter|LegalFooter|LeftPanel|RightPanel)\.js$/, 'App shell'],
  [/components\/InvestorDashboard\//, 'Dashboard'],
  [/components\/(KPICards|Department|Product|ProgramTile|ServiceRow|EnhancedUserProfile)/, 'Dashboard'],
  [/components\/(Globe3D|GlobeVisualization|SimpleGlobeAnimation|NeuralNetworkMap|MascotWheel|CenterWheel|DualRingWheel|FloatingOrbs|VideoBackground)/, 'Visualisation'],
  [/components\/(DeityAvatar|MadeInBharat|Meditation|Spiritual)/, 'Brand'],
  [/components\/(CookieConsent|LoadingState|ErrorBoundary|OnboardingOverlay)/, 'Feedback'],
];
const groupFor = (relPath) => GROUPS.find(([rx]) => rx.test(relPath))?.[1] ?? 'General';

// ── 6. prop contracts ────────────────────────────────────────────────────────
// There are no .d.ts files in this repo, so the converter emits an empty
// `[key: string]: unknown` props interface for every component — the design
// agent would have no API to code against. Recover the real surface from the
// source: the destructured parameter list, defaults, and cva() variant keys.
const DEFAULT_TYPE = (expr) => {
  const v = expr.trim();
  if (v === 'true' || v === 'false') return 'boolean';
  if (/^-?\d+(\.\d+)?$/.test(v)) return 'number';
  if (/^['"`]/.test(v)) return 'string';
  if (/^\[/.test(v)) return 'unknown[]';
  if (/^\{/.test(v)) return 'Record<string, unknown>';
  if (/^\(.*\)\s*=>/.test(v)) return '(...args: unknown[]) => void';
  return null;
};

const NAME_TYPE = (prop) => {
  if (prop === 'children') return 'React.ReactNode';
  if (prop === 'className') return 'string';
  if (prop === 'style') return 'React.CSSProperties';
  if (/^on[A-Z]/.test(prop)) return '(...args: unknown[]) => void';
  if (/^(is|has|show|hide|open|disabled|required|checked|selected|active|loading|inset|asChild)/.test(prop)) return 'boolean';
  if (/(Count|Index|Size|Width|Height|Duration|Delay|Value)$/.test(prop) || prop === 'size') return 'number | string';
  if (/^(icon|Icon)$/.test(prop) || /Icon$/.test(prop)) return 'React.ElementType';
  if (/(label|title|name|text|message|description|href|src|alt|placeholder|id|type|variant|status|color)$/i.test(prop)) return 'string';
  return 'unknown';
};

// Balanced-brace read of the destructuring pattern that opens a parameter list.
function readDestructure(text, from) {
  const open = text.indexOf('{', from);
  if (open === -1) return null;
  let depth = 0;
  for (let i = open; i < text.length; i++) {
    const ch = text[i];
    if (ch === '{') depth++;
    else if (ch === '}') {
      depth--;
      if (depth === 0) return text.slice(open + 1, i);
    }
  }
  return null;
}

// Split on top-level commas only — defaults can contain objects and calls.
function splitTop(s) {
  const out = [];
  let depth = 0, quote = null, cur = '';
  for (let i = 0; i < s.length; i++) {
    const ch = s[i];
    if (quote) { cur += ch; if (ch === quote && s[i - 1] !== '\\') quote = null; continue; }
    if (ch === '"' || ch === "'" || ch === '`') { quote = ch; cur += ch; continue; }
    if ('{[('.includes(ch)) depth++;
    if ('}])'.includes(ch)) depth--;
    if (ch === ',' && depth === 0) { out.push(cur); cur = ''; continue; }
    cur += ch;
  }
  if (cur.trim()) out.push(cur);
  return out;
}

// cva("base", { variants: { variant: { default: …, ghost: … }, size: {…} } })
function cvaVariants(text, varName) {
  const decl = new RegExp(`(?:const|let|var)\\s+${varName}\\s*=\\s*cva\\(`).exec(text);
  if (!decl) return {};
  const body = readDestructure(text, decl.index + decl[0].length);
  if (!body) return {};
  const vBlock = /variants\s*:\s*\{/.exec(body);
  if (!vBlock) return {};
  const inner = readDestructure(body, vBlock.index + vBlock[0].length - 1);
  if (!inner) return {};
  const out = {};
  for (const m of inner.matchAll(/(\w+)\s*:\s*\{/g)) {
    const block = readDestructure(inner, m.index + m[0].length - 1);
    if (!block) continue;
    const keys = [...block.matchAll(/(?:^|,)\s*["']?([A-Za-z0-9_-]+)["']?\s*:/g)].map((k) => k[1]);
    if (keys.length) out[m[1]] = keys;
  }
  return out;
}

const dtsPropsFor = {};
const propReport = {};

for (const [name, p] of picks) {
  const text = readFileSync(p.file, 'utf8');
  const local = p.via === 'default' ? (/(?:const|function|class)\s+([A-Za-z0-9_$]+)[\s\S]*?export\s+default\s+\1/.exec(text)?.[1] ?? name) : p.localName;
  const declRx = new RegExp(`(?:const|let|var|function)\\s+${local}\\b`);
  const decl = declRx.exec(text);
  if (!decl) continue;

  // The parameter list is the first destructuring after the declaration, but
  // only if it comes before the body opens a JSX/return — cap the search.
  const window = text.slice(decl.index, decl.index + 600);
  const paramStart = /\(\s*\{|=>\s*\(?\s*\{|forwardRef\s*\(\s*\(\s*\{/.exec(window);
  if (!paramStart) continue;
  const raw = readDestructure(window, paramStart.index);
  if (raw === null) continue;

  // A cva variants object referenced in the body — `buttonVariants({variant,size})`
  const variantsVar = new RegExp(`(\\w*[Vv]ariants)\\s*\\(`).exec(window.slice(raw.length))?.[1];
  const variants = variantsVar ? cvaVariants(text, variantsVar) : {};

  const lines = [];
  let rest = false;
  for (const part of splitTop(raw)) {
    const seg = part.trim();
    if (!seg) continue;
    if (seg.startsWith('...')) { rest = true; continue; }
    const eq = seg.indexOf('=');
    const lhs = (eq === -1 ? seg : seg.slice(0, eq)).trim();
    const def = eq === -1 ? null : seg.slice(eq + 1).trim();
    // `icon: Icon` — the prop name is the key, not the local binding.
    const prop = lhs.split(':')[0].trim();
    if (!/^[A-Za-z_$][\w$]*$/.test(prop)) continue;

    // An icon prop renamed to a capitalised local (`icon: Icon`) is rendered as
    // <Icon /> and takes a component type; one kept lowercase is interpolated as
    // {icon} and takes an already-rendered element. Getting this backwards makes
    // React throw "Objects are not valid as a React child", so read the binding
    // rather than the name.
    const aliasedToComponent = /^[A-Z]/.test((lhs.split(':')[1] ?? '').trim());
    let type = variants[prop]
      ? variants[prop].map((v) => `'${v}'`).join(' | ')
      : (def !== null ? DEFAULT_TYPE(def) : null)
        ?? (/^(icon|Icon)$|Icon$/.test(prop) && !aliasedToComponent ? 'React.ReactNode' : NAME_TYPE(prop));
    const optional = def !== null || prop === 'className' || prop === 'children' ? '?' : '?';
    lines.push(`  ${prop}${optional}: ${type};${def !== null ? `  // default: ${def.replace(/\s+/g, ' ').slice(0, 40)}` : ''}`);
  }
  // Variant props consumed only via the cva call, never destructured by name.
  for (const [v, keys] of Object.entries(variants)) {
    if (lines.some((l) => l.trim().startsWith(`${v}?`))) continue;
    lines.push(`  ${v}?: ${keys.map((k) => `'${k}'`).join(' | ')};`);
  }
  if (!lines.length && !rest) continue;
  if (rest) lines.push('  /** Remaining props spread onto the underlying element. */\n  [key: string]: unknown;');

  dtsPropsFor[name] = '\n' + lines.join('\n') + '\n';
  propReport[name] = lines.length;
}

// ── 7. docs stubs (grouping) + componentSrcMap ───────────────────────────────
const DOCS = join(HERE, 'docs');
rmSync(DOCS, { recursive: true, force: true });
mkdirSync(DOCS, { recursive: true });

const srcMap = {};
const docsMap = {};
const groupCounts = {};
for (const name of realExports) {
  const p = picks.get(name);
  if (!p) continue; // DesignSystemProvider lives outside src/components
  const rel = slash(relative(PKG_DIR, p.file));
  srcMap[name] = rel;
  const group = groupFor(rel);
  groupCounts[group] = (groupCounts[group] ?? 0) + 1;
  const docPath = join(DOCS, `${name}.md`);
  writeFileSync(docPath, `---\ncategory: ${group}\n---\n`);
  docsMap[name] = slash(relative(PKG_DIR, docPath));
}
writeFileSync(
  join(CACHE, 'discovered.json'),
  JSON.stringify({ componentSrcMap: srcMap, docsMap, dtsPropsFor, collisions, exports: realExports }, null, 2) + '\n',
);
log(`  discovered.json: ${Object.keys(srcMap).length} components, ${Object.keys(dtsPropsFor).length} with extracted props`);
log(`  groups: ${Object.entries(groupCounts).sort((a, b) => b[1] - a[1]).map(([g, n]) => `${g}=${n}`).join(', ')}`);

// Fold the generated fields into the converter config, preserving every
// hand-maintained key (projectId, provider, readmeHeader, overrides, …).
const cfgPath = join(HERE, 'config.json');
const cfg = existsSync(cfgPath) ? JSON.parse(readFileSync(cfgPath, 'utf8')) : {};
writeFileSync(cfgPath, JSON.stringify({ ...cfg, componentSrcMap: srcMap, dtsPropsFor }, null, 2) + '\n');
log('  config.json: componentSrcMap + dtsPropsFor refreshed');

rmSync(barrel, { force: true });
