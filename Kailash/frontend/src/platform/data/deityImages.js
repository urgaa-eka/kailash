// Deity Images for KAILASH System
// Using unified spiritual logo for all departments

// The uploaded spiritual meditation logo - SQUARE TRANSPARENT HD
const SPIRITUAL_LOGO = 'https://customer-assets.emergentagent.com/job_mystic-ui-2/artifacts/ue6hdyaa_icon.png';

export const DEITY_IMAGES = {
  ganesha: {
    primary: SPIRITUAL_LOGO,
    alt: 'Lord Ganesha - Executive Assistant & Obstacle Remover',
    description: 'Divine coordinator and remover of obstacles'
  },
  vishwakarma: {
    primary: SPIRITUAL_LOGO,
    alt: 'Lord Vishwakarma - Chief Technology Officer',
    description: 'Divine architect and master of technology'
  },
  lakshmi: {
    primary: SPIRITUAL_LOGO,
    alt: 'Goddess Lakshmi - Finance & Prosperity',
    description: 'Divine embodiment of wealth and prosperity'
  },
  surya: {
    primary: SPIRITUAL_LOGO,
    alt: 'Lord Surya - URJAA Head (Energy Solutions)',
    description: 'Divine source of light and energy'
  },
  shiv: {
    primary: SPIRITUAL_LOGO,
    alt: 'Lord Shiv - Security Guardian',
    description: 'Divine protector and transformer'
  },
  tvashta: {
    primary: SPIRITUAL_LOGO,
    alt: 'Lord Tvashta - Go4Garage Operations',
    description: 'Divine craftsman'
  },
  kartikeya: {
    primary: SPIRITUAL_LOGO,
    alt: 'Lord Kartikeya - IGNITION Mobile App',
    description: 'Divine warrior and leader'
  },
  kamadeva: {
    primary: SPIRITUAL_LOGO,
    alt: 'Lord Kamadeva - Chief Marketing Officer',
    description: 'Divine beauty and attraction'
  },
  kubera: {
    primary: SPIRITUAL_LOGO,
    alt: 'Lord Kubera - Chief Sales Officer',
    description: 'Divine treasurer'
  },
  brihaspati: {
    primary: SPIRITUAL_LOGO,
    alt: 'Lord Brihaspati - Investor Relations',
    description: 'Divine teacher and guide'
  },
  mitra: {
    primary: SPIRITUAL_LOGO,
    alt: 'Lord Mitra - Partnerships & Alliances',
    description: 'Divine friend and ally'
  },
  dharma: {
    primary: SPIRITUAL_LOGO,
    alt: 'Lord Dharma - Government Relations',
    description: 'Divine righteousness'
  },
  shukra: {
    primary: SPIRITUAL_LOGO,
    alt: 'Lord Shukra - Chief Strategy Officer',
    description: 'Divine wisdom'
  },
  chandra: {
    primary: SPIRITUAL_LOGO,
    alt: 'Lord Chandra - Data & Analytics',
    description: 'Divine illumination'
  },
  brahma: {
    primary: SPIRITUAL_LOGO,
    alt: 'Lord Brahma - Research & Development',
    description: 'Divine creator'
  },
  indra: {
    primary: SPIRITUAL_LOGO,
    alt: 'Lord Indra - Chief Operating Officer',
    description: 'Divine leader'
  },
  chitragupta: {
    primary: SPIRITUAL_LOGO,
    alt: 'Lord Chitragupta - Quality Assurance',
    description: 'Divine record keeper'
  },
  prajapati: {
    primary: SPIRITUAL_LOGO,
    alt: 'Lord Prajapati - Product Management',
    description: 'Divine lord of creatures'
  },
  yama: {
    primary: SPIRITUAL_LOGO,
    alt: 'Lord Yama - Legal & Compliance',
    description: 'Divine justice'
  },
  vani: {
    primary: SPIRITUAL_LOGO,
    alt: 'Goddess Vani - Content & Communications',
    description: 'Divine speech'
  },
  vayu: {
    primary: SPIRITUAL_LOGO,
    alt: 'Lord Vayu - Sustainability & ESG',
    description: 'Divine wind'
  },
  default: {
    primary: SPIRITUAL_LOGO,
    alt: 'Divine Deity',
    description: 'Sacred representation'
  }
};

// Function to get deity image with fallback
export function getDeityImage(deityId) {
  return DEITY_IMAGES[deityId?.toLowerCase()] || DEITY_IMAGES.default;
}

// Sacred symbols and patterns - Using text representations for brand compliance
export const SACRED_SYMBOLS = {
  om: 'OM',
  lotus: 'LOTUS',
  dharmachakra: 'WHEEL',
  trishul: 'TRISHUL'
};
