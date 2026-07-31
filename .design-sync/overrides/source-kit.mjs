// forked from design-sync lib/source-kit.mjs — group comes from docs frontmatter, not the source dir
// Non-storybook `package` adapter. Bundles dist/ when present (the authoritative
// component list comes from shipped .d.ts; with no dist it synthesizes an
// entry from src/ as a last resort) and opportunistically enriches each
// component from src/ — JSDoc and dir-derived group. Every enrichment miss
// degrades to the plain-dist behaviour.
//
// Discovery is heuristic-based; each heuristic has a `.design-sync/config.json`
// override (ASSUMPTION comments below name them) so repos that don't match the
// defaults write config, not code. `componentSrcMap` is the single override
// knob for component inclusion: non-null value = add/pin src path, null =
// exclude a .d.ts-exported internal.

import { existsSync, writeFileSync } from 'node:fs';
import { dirname, join, relative, resolve } from 'node:path';
import { leadingJsdoc, readText, slash, walk } from '../../.ds-sync/lib/common.mjs';
import { resolveDistEntry } from '../../.ds-sync/lib/bundle.mjs';
import { exportedNames, isComponentName } from '../../.ds-sync/lib/dts.mjs';

const NON_IMPL_RX = /\.(stories|test|spec)\./;
const SRC_IMPL_RX = /\.(tsx|jsx)$/;
// Dir names that don't usefully group components — skip so the emitted path
// is `components/<group>/<Name>` not `components/components/<Name>`.
const GENERIC_DIR = new Set(['components', 'component', 'src', 'lib', 'ui', 'packages', 'react']);
const slug = (s) => s.trim().toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '') || 'general';

// FORK: upstream's synth-entry fallback (deriveComponentsFromSrc) is dropped.
// It is unreachable here — .design-sync/build-ds.mjs always produces
// frontend/.ds-lib/entry.js, so `entry` is never synthesized — and dropping it
// removes this fork's only bare import (ts-morph), which would otherwise not
// resolve from .design-sync/overrides/ without a node_modules symlink.

export async function resolvePackage(ctx) {
  const { PKG_DIR, pkgJson, ENTRY_OVERRIDE, PKG, OUT, cfg } = ctx;
  const srcMap = cfg.componentSrcMap ?? {};

  // ── 1. src/ discovery (best-effort; feeds enrichment + synth-entry fallback).
  // ASSUMPTION: source root is first of src/ | lib/ | components/. Override: cfg.srcDir.
  const srcRoot = [cfg.srcDir, 'src', 'lib', 'components']
    .map((d) => d && resolve(PKG_DIR, d))
    .find((d) => d && existsSync(d));
  const srcFiles = srcRoot ? walk(srcRoot, (n) => /\.(tsx|jsx|mdx?)$/.test(n)) : [];

  // ── 2. entry: dist if it exists, else synthesize from src/ (last resort).
  let entry = resolveDistEntry({ pkgDir: PKG_DIR, pkgJson, override: ENTRY_OVERRIDE, pkgName: PKG, soft: true });
  let synthEntry = false;
  if (!entry) {
    if (!srcRoot) {
      console.error(`[NO_DIST] ${PKG} has no built entry and no src/ to synthesize from — run its build.`);
      process.exit(1);
    }
    const comps = srcFiles.filter((p) => SRC_IMPL_RX.test(p) && !NON_IMPL_RX.test(p));
    entry = join(OUT, '.pkg-entry.mjs');
    writeFileSync(entry, comps.map((p) => `export * from ${JSON.stringify(p)};`).join('\n') + '\n');
    synthEntry = true;
    console.error(
      `[NO_DIST] no built entry — synthesizing from ${comps.length} src files (run the package's build for best results)`,
    );
  }

  // ── 3. component list: from shipped .d.ts (authoritative when dist exists).
  // ASSUMPTION: components = PascalCase value exports in the .d.ts tree.
  // Override: cfg.componentSrcMap (non-null adds/pins, null excludes).
  const exported = exportedNames(PKG_DIR, pkgJson);
  const names = new Set([...exported].filter(isComponentName));
  for (const [k, v] of Object.entries(srcMap)) {
    if (v === null) { names.delete(k); continue; }
    // Names reach `<script>` blocks in the emitted HTML — reject anything
    // that isn't a plain PascalCase identifier.
    if (!/^[A-Z][A-Za-z0-9]*$/.test(k)) {
      console.error(`[CONFIG] componentSrcMap: "${k}" is not a valid component name (PascalCase identifiers only)`);
      continue;
    }
    names.add(k);
  }
  let components = [...names].sort().map((name) => ({ name, group: 'general' }));
  if (!components.length) {
    if (cfg.cssEntry || existsSync(join(PKG_DIR, 'styles.css'))) {
      console.error('[ZERO_MATCH] no component exports — treating as tokens-only DS');
      return { shape: 'package', entry, components: [], tokensOnly: true };
    }
    console.error(`[ZERO_MATCH] no PascalCase exports in ${PKG} and no styles — nothing to sync`);
    process.exit(1);
  }

  // ── 4. src/ enrichment per component. Every miss degrades to plain-dist.
  if (srcRoot) {
    for (const c of components) {
      // Pinned via config → skip fuzzy-find entirely.
      let hit = typeof srcMap[c.name] === 'string' ? slash(resolve(PKG_DIR, srcMap[c.name])) : null;
      if (!hit) {
        // ASSUMPTION: <Name>.tsx | <name>/<name>.tsx | <Name>/index.tsx |
        // <kebab-name>.tsx, case-insensitive; dir-match ranks above
        // bare-file match, then prefer one that actually exports `c.name`.
        // Override: cfg.componentSrcMap.
        const kebab = c.name.replace(/([a-z0-9])([A-Z])/g, '$1-$2');
        const nameRx = new RegExp(
          `(?:^|/)(?:${c.name}/(?:index|${c.name})\\.(tsx|jsx)|(?:${c.name}|${kebab})\\.(tsx|jsx))$`,
          'i',
        );
        const hits = srcFiles
          .filter((p) => nameRx.test(p) && !NON_IMPL_RX.test(p))
          .sort(
            (a, b) =>
              (b.toLowerCase().includes(`/${c.name.toLowerCase()}/`) ? 1 : 0) -
              (a.toLowerCase().includes(`/${c.name.toLowerCase()}/`) ? 1 : 0),
          );
        const exportRx = new RegExp(`export\\s+(?:default\\s+)?(?:const|let|var|function|class)\\s+${c.name}\\b`);
        hit = hits.find((p) => exportRx.test(readText(p))) ?? hits[0];
      }
      if (!hit || !existsSync(hit)) continue;
      c.srcPath = hit;
      c.doc = leadingJsdoc(readText(hit), c.name) || undefined;
      // FORK: grouping is owned by .design-sync/docs/<Name>.md frontmatter,
      // which package-build applies only when the dir-derived group is
      // 'general'. Upstream's dir-derived group would win for the two source
      // subdirectories that have one (src/components/InvestorDashboard/ and
      // src/components/Layout/), splitting those components out of the
      // taxonomy build-ds.mjs assigns. Leaving it 'general' lets the docs
      // frontmatter decide for every component uniformly.
      c.group = 'general';
    }
  }

  console.error(
    `  package: ${components.length} components` +
      (srcRoot ? ` (${components.filter((c) => c.srcPath).length} src-matched)` : ' (no src/ — dist-only)'),
  );
  return { shape: 'package', entry, components, synthEntry, exported };
}
