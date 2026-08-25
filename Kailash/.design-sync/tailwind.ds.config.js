// Tailwind config for the design-system build.
//
// Identical to frontend/tailwind.config.js (required, not copied — so brand
// colours, tokens and plugins can never drift) with three additions:
//   · content globs are absolute, since this config is invoked from a
//     different directory than the app's own build
//   · authored preview sources are scanned too, so utilities used only in a
//     preview card still make it into the compiled stylesheet
//   · a safelist (below) — the reason this file is not just a re-export
const path = require('path');
const base = require('../frontend/tailwind.config.js');

const repo = path.resolve(__dirname, '..');

// WHY A SAFELIST.
// The app's own build purges every utility it does not use, which is correct
// for an app and wrong for a design system: the stylesheet we ship is consumed
// by an agent writing *new* markup, and any utility it reaches for that no
// existing file happens to use would resolve to nothing and render silently
// unstyled. The families below are the vocabulary the README teaches, plus the
// spacing/type/layout scales any new layout needs, so a design built with this
// system styles correctly whether or not the app already used that exact class.
const TOKEN_COLORS =
  'background|foreground|card|card-foreground|popover|popover-foreground|' +
  'primary|primary-foreground|secondary|secondary-foreground|muted|muted-foreground|' +
  'accent|accent-foreground|destructive|destructive-foreground|border|input|ring|' +
  'g4g-blue|g4g-steel-grey|g4g-electric-yellow|g4g-graphite|cool-grey|dark-slate|' +
  'highlight-teal|error-red|transparent|current|white|black';

const SPACE = '0|px|0\\.5|1|1\\.5|2|2\\.5|3|3\\.5|4|5|6|7|8|9|10|11|12|14|16|20|24|32';

module.exports = {
  ...base,
  content: [
    path.join(repo, 'frontend/src/**/*.{js,jsx}'),
    path.join(repo, '.design-sync/previews/**/*.{tsx,jsx}'),
    path.join(repo, '.design-sync/ds-provider.jsx'),
  ],
  safelist: [
    {
      pattern: new RegExp(
        `^(bg|text|border|ring|fill|stroke|divide|placeholder|outline|decoration)-(${TOKEN_COLORS})$`,
      ),
      variants: ['hover', 'focus', 'focus-visible', 'active', 'disabled', 'group-hover'],
    },
    { pattern: new RegExp(`^(p|px|py|pt|pr|pb|pl|m|mx|my|mt|mr|mb|ml)-(${SPACE})$`) },
    { pattern: new RegExp(`^(gap|gap-x|gap-y|space-x|space-y)-(${SPACE})$`) },
    { pattern: new RegExp(`^(w|h|min-w|min-h)-(${SPACE}|full|screen|fit|auto|min|max)$`) },
    { pattern: /^max-w-(xs|sm|md|lg|xl|2xl|3xl|4xl|5xl|6xl|7xl|full|prose|none)$/ },
    { pattern: /^grid-cols-(1|2|3|4|5|6|7|8|9|10|11|12)$/, variants: ['sm', 'md', 'lg'] },
    { pattern: /^(col|row)-span-(1|2|3|4|5|6|7|8|9|10|11|12|full)$/ },
    { pattern: /^text-(xs|sm|base|lg|xl|2xl|3xl|4xl|5xl|6xl|7xl|left|center|right)$/ },
    { pattern: /^font-(thin|light|normal|medium|semibold|bold|extrabold|sans|mono)$/ },
    { pattern: /^(leading|tracking)-(none|tight|snug|normal|relaxed|loose|wide|wider|widest|tighter)$/ },
    { pattern: /^rounded(-(none|sm|md|lg|xl|2xl|3xl|full))?$/ },
    { pattern: /^rounded-(t|r|b|l|tl|tr|br|bl)(-(none|sm|md|lg|xl|2xl|3xl|full))?$/ },
    { pattern: /^border(-(0|2|4|8|t|r|b|l))?$/ },
    { pattern: /^shadow(-(sm|md|lg|xl|2xl|none|inner|card|card-hover))?$/ },
    { pattern: /^(opacity|z)-(0|5|10|20|25|30|40|50|60|70|75|80|90|95|100)$/ },
    { pattern: /^(flex|grid|block|inline-flex|inline-block|hidden|inline-grid)$/ },
    { pattern: /^(flex-(row|col|wrap|nowrap|1|auto|initial|none))$/ },
    { pattern: /^(items|justify|self|content)-(start|end|center|between|around|evenly|stretch|baseline|auto)$/ },
    { pattern: /^(absolute|relative|fixed|sticky|static)$/ },
    { pattern: /^(inset|top|right|bottom|left)-(0|auto|full)$/ },
    { pattern: /^(overflow|overflow-x|overflow-y)-(auto|hidden|visible|scroll)$/ },
    { pattern: /^(truncate|whitespace-nowrap|break-words|line-clamp-(1|2|3|4))$/ },
  ],
};
