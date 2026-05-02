// Spiritual Quotes & Mantras for KAILASH System
// Wisdom from sacred texts and Hindu philosophy

export const SPIRITUAL_QUOTES = [
  {
    id: 1,
    text: 'Yoga is the journey of the self, through the self, to the self.',
    source: 'Bhagavad Gita',
    deity: 'all',
    category: 'wisdom'
  },
  {
    id: 2,
    text: 'When the mind is calm, how quickly, how smoothly, how beautifully you will perceive everything.',
    source: 'Paramahansa Yogananda',
    deity: 'all',
    category: 'mindfulness'
  },
  {
    id: 3,
    text: 'Excellence is not a destination; it is a continuous journey that never ends.',
    source: 'Upanishads',
    deity: 'vishwakarma',
    category: 'excellence'
  },
  {
    id: 4,
    text: 'Prosperity flows to those who serve with dedication and wisdom.',
    source: 'Lakshmi Suktam',
    deity: 'lakshmi',
    category: 'prosperity'
  },
  {
    id: 5,
    text: 'The light of consciousness illuminates all paths.',
    source: 'Surya Gayatri',
    deity: 'surya',
    category: 'enlightenment'
  },
  {
    id: 6,
    text: 'Remove obstacles with wisdom, not with force.',
    source: 'Ganesha Purana',
    deity: 'ganesha',
    category: 'wisdom'
  },
  {
    id: 7,
    text: 'Balance in all things brings harmony to existence.',
    source: 'Vedic Wisdom',
    deity: 'parvati',
    category: 'harmony'
  },
  {
    id: 8,
    text: 'Protection comes from vigilance and righteousness.',
    source: 'Shiva Mahimna',
    deity: 'shiv',
    category: 'protection'
  },
  {
    id: 9,
    text: 'True wealth is not in what we have, but in what we give.',
    source: 'Mahabharata',
    deity: 'kubera',
    category: 'wealth'
  },
  {
    id: 10,
    text: 'Knowledge is the supreme treasure that multiplies when shared.',
    source: 'Saraswati Vandana',
    deity: 'saraswati',
    category: 'knowledge'
  },
  {
    id: 11,
    text: 'In stillness lies infinite power.',
    source: 'Patanjali Yoga Sutras',
    deity: 'all',
    category: 'meditation'
  },
  {
    id: 12,
    text: 'Dharma protects those who protect dharma.',
    source: 'Manusmriti',
    deity: 'dharma',
    category: 'righteousness'
  },
  {
    id: 13,
    text: 'The mind is everything. What you think, you become.',
    source: 'Buddha (Hindu Influence)',
    deity: 'all',
    category: 'mindfulness'
  },
  {
    id: 14,
    text: 'Through service to others, we serve the divine.',
    source: 'Karma Yoga Philosophy',
    deity: 'hanuman',
    category: 'service'
  },
  {
    id: 15,
    text: 'Quality is not an act, it is a habit of excellence.',
    source: 'Ancient Wisdom',
    deity: 'vishnu',
    category: 'quality'
  }
];

export const MANTRAS = {
  om: 'ॐ',
  ganesha: 'ॐ गं गणपतये नमः',
  lakshmi: 'ॐ श्रीं महालक्ष्म्यै नमः',
  surya: 'ॐ सूर्याय नमः',
  shiv: 'ॐ नमः शिवाय',
  saraswati: 'ॐ ऐं सरस्वत्यै नमः'
};

export const MEDITATION_GUIDANCE = [
  'Take a deep breath... Focus on the present moment',
  'Let go of distractions... Embrace clarity',
  'Center your mind... Find your inner peace',
  'Breathe in wisdom... Breathe out stress',
  'Connect with your higher purpose'
];

export function getQuoteByDeity(deityId) {
  const quotes = SPIRITUAL_QUOTES.filter(q => q.deity === deityId || q.deity === 'all');
  return quotes[Math.floor(Math.random() * quotes.length)];
}

export function getRandomQuote() {
  return SPIRITUAL_QUOTES[Math.floor(Math.random() * SPIRITUAL_QUOTES.length)];
}

export function getDailyQuote() {
  // Returns a consistent quote for the day based on date
  const day = new Date().getDate();
  return SPIRITUAL_QUOTES[day % SPIRITUAL_QUOTES.length];
}
