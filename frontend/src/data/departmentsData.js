// Complete department data structure with sub-agents
// NO emojis - all text only

export const DEPARTMENTS = [
  {
    id: 'ganesha',
    name: 'GANESHA',
    chief: 'Lord Ganesha',
    role: 'Executive Assistant & Obstacle Remover',
    tier: 'Executive',
    color: '#FFD700',
    status: 'active',
    workload: 78,
    activeTasks: 15,
    completedToday: 7,
    description: 'Coordinates all departments, removes obstacles, processes CEO commands',
    responsibilities: [
      'Natural language command processing',
      'Task routing and assignment',
      'Department coordination',
      'Obstacle identification and removal'
    ],
    aiTools: ['Claude API', 'Command Parser', 'Task Router'],
    k1Location: '/oversight/ganesha/',
    subAgents: [
      { name: 'Command Parser', role: 'Natural language understanding', status: 'active', workload: 82, tasks: 5 },
      { name: 'Task Router', role: 'Intelligent task distribution', status: 'active', workload: 75, tasks: 6 },
      { name: 'Priority Manager', role: 'Task prioritization', status: 'active', workload: 68, tasks: 4 },
      { name: 'Obstacle Detector', role: 'Identifies and removes blockers', status: 'active', workload: 71, tasks: 3 }
    ]
  },
  {
    id: 'vishwakarma',
    name: 'VISHWAKARMA',
    chief: 'Lord Vishwakarma',
    role: 'Chief Technology Officer',
    tier: 'Executive',
    color: '#4F46E5',
    status: 'active',
    workload: 85,
    activeTasks: 18,
    completedToday: 9,
    description: 'Divine architect managing all technical infrastructure',
    responsibilities: [
      'System architecture design',
      'Infrastructure management',
      'DevOps and automation',
      'Security implementation'
    ],
    aiTools: ['GitHub Copilot', 'Infrastructure Monitor', 'Deploy Manager'],
    k1Location: '/oversight/vishwakarma/',
    subAgents: [
      { name: 'Infrastructure Manager', role: 'Server and cloud management', status: 'active', workload: 88, tasks: 7 },
      { name: 'DevOps Specialist', role: 'CI/CD and automation', status: 'active', workload: 82, tasks: 6 },
      { name: 'Security Engineer', role: 'Security protocols', status: 'active', workload: 79, tasks: 5 }
    ]
  },
  {
    id: 'surya',
    name: 'SURYA',
    chief: 'Lord Surya',
    role: 'URJAA Head (Energy Solutions)',
    tier: 'Product',
    color: '#F59E0B',
    status: 'active',
    workload: 72,
    activeTasks: 14,
    completedToday: 8,
    description: 'Powers URJAA energy solutions and solar operations',
    responsibilities: [
      'Solar energy analytics',
      'Energy trading platform',
      'Customer success',
      'Product development'
    ],
    aiTools: ['Energy Predictor', 'Trading Algorithm', 'Customer Insights'],
    k1Location: '/oversight/surya/',
    subAgents: [
      { name: 'Solar Analytics', role: 'Energy data analysis', status: 'active', workload: 76, tasks: 5 },
      { name: 'Trading Engine', role: 'Energy market optimization', status: 'active', workload: 70, tasks: 6 },
      { name: 'Customer Success', role: 'Client relationship management', status: 'active', workload: 68, tasks: 3 }
    ]
  },
  {
    id: 'tvashta',
    name: 'TVASHTA',
    chief: 'Lord Tvashta',
    role: 'Go4Garage Operations',
    tier: 'Product',
    color: '#8B5CF6',
    status: 'active',
    workload: 80,
    activeTasks: 16,
    completedToday: 10,
    description: 'Manages Go4Garage service platform and operations',
    responsibilities: [
      'Service booking management',
      'Garage partner operations',
      'Quality assurance',
      'Customer experience'
    ],
    aiTools: ['Booking Optimizer', 'Partner Matcher', 'Quality Checker'],
    k1Location: '/oversight/tvashta/',
    subAgents: [
      { name: 'Booking Manager', role: 'Service appointment scheduling', status: 'active', workload: 83, tasks: 6 },
      { name: 'Partner Coordinator', role: 'Garage network management', status: 'active', workload: 78, tasks: 5 },
      { name: 'Quality Inspector', role: 'Service quality monitoring', status: 'active', workload: 81, tasks: 5 }
    ]
  },
  {
    id: 'kartikeya',
    name: 'KARTIKEYA',
    chief: 'Lord Kartikeya',
    role: 'IGNITION Mobile App',
    tier: 'Product',
    color: '#EC4899',
    status: 'active',
    workload: 74,
    activeTasks: 12,
    completedToday: 6,
    description: 'Leads IGNITION mobile platform development and user experience',
    responsibilities: [
      'Mobile app development',
      'User experience design',
      'Feature rollout',
      'App performance'
    ],
    aiTools: ['UX Analyzer', 'Performance Monitor', 'Feature Recommender'],
    k1Location: '/oversight/kartikeya/',
    subAgents: [
      { name: 'App Developer', role: 'Mobile development', status: 'active', workload: 77, tasks: 5 },
      { name: 'UX Designer', role: 'User interface design', status: 'active', workload: 72, tasks: 4 },
      { name: 'Performance Engineer', role: 'App optimization', status: 'active', workload: 73, tasks: 3 }
    ]
  },
  {
    id: 'kamadeva',
    name: 'KAMADEVA',
    chief: 'Lord Kamadeva',
    role: 'Chief Marketing Officer',
    tier: 'Executive',
    color: '#EF4444',
    status: 'active',
    workload: 76,
    activeTasks: 13,
    completedToday: 8,
    description: 'Drives marketing strategy and brand presence',
    responsibilities: [
      'Brand strategy',
      'Digital marketing',
      'Content creation',
      'Campaign management'
    ],
    aiTools: ['Content Generator', 'Campaign Analyzer', 'Trend Predictor'],
    k1Location: '/oversight/kamadeva/',
    subAgents: [
      { name: 'Brand Manager', role: 'Brand identity and positioning', status: 'active', workload: 79, tasks: 5 },
      { name: 'Digital Marketer', role: 'Online campaign execution', status: 'active', workload: 75, tasks: 4 },
      { name: 'Content Creator', role: 'Marketing content production', status: 'active', workload: 74, tasks: 4 }
    ]
  },
  {
    id: 'kubera',
    name: 'KUBERA',
    chief: 'Lord Kubera',
    role: 'Chief Sales Officer',
    tier: 'Executive',
    color: '#10B981',
    status: 'active',
    workload: 82,
    activeTasks: 17,
    completedToday: 11,
    description: 'Leads sales operations and revenue generation',
    responsibilities: [
      'Sales strategy',
      'Revenue targets',
      'Client acquisition',
      'Sales team management'
    ],
    aiTools: ['Lead Scorer', 'Pipeline Manager', 'Revenue Forecaster'],
    k1Location: '/oversight/kubera/',
    subAgents: [
      { name: 'Lead Generator', role: 'Prospect identification', status: 'active', workload: 85, tasks: 6 },
      { name: 'Account Manager', role: 'Client relationship', status: 'active', workload: 80, tasks: 6 },
      { name: 'Revenue Analyst', role: 'Sales performance tracking', status: 'active', workload: 81, tasks: 5 }
    ]
  },
  {
    id: 'lakshmi',
    name: 'LAKSHMI',
    chief: 'Goddess Lakshmi',
    role: 'Chief Financial Officer',
    tier: 'Executive',
    color: '#F59E0B',
    status: 'active',
    workload: 79,
    activeTasks: 14,
    completedToday: 9,
    description: 'Manages financial operations and planning',
    responsibilities: [
      'Financial planning',
      'Budget management',
      'Financial reporting',
      'Cash flow management'
    ],
    aiTools: ['Financial Modeler', 'Budget Optimizer', 'Risk Analyzer'],
    k1Location: '/oversight/lakshmi/',
    subAgents: [
      { name: 'Budget Controller', role: 'Budget oversight', status: 'active', workload: 82, tasks: 5 },
      { name: 'Financial Analyst', role: 'Financial reporting', status: 'active', workload: 78, tasks: 5 },
      { name: 'Cash Manager', role: 'Cash flow optimization', status: 'active', workload: 77, tasks: 4 }
    ]
  },
  {
    id: 'brihaspati',
    name: 'BRIHASPATI',
    chief: 'Lord Brihaspati',
    role: 'Investor Relations',
    tier: 'Executive',
    color: '#3B82F6',
    status: 'active',
    workload: 68,
    activeTasks: 9,
    completedToday: 5,
    description: 'Manages investor communications and relations',
    responsibilities: [
      'Investor communications',
      'Fundraising',
      'Board relations',
      'Financial presentations'
    ],
    aiTools: ['Pitch Generator', 'Investor Tracker', 'Valuation Modeler'],
    k1Location: '/oversight/brihaspati/',
    subAgents: [
      { name: 'Investor Manager', role: 'Investor engagement', status: 'active', workload: 71, tasks: 4 },
      { name: 'Presentation Designer', role: 'Deck creation', status: 'active', workload: 66, tasks: 3 },
      { name: 'Fundraising Lead', role: 'Capital raising', status: 'active', workload: 67, tasks: 2 }
    ]
  },
  {
    id: 'mitra',
    name: 'MITRA',
    chief: 'Lord Mitra',
    role: 'Partnerships & Alliances',
    tier: 'Operations',
    color: '#8B5CF6',
    status: 'active',
    workload: 70,
    activeTasks: 11,
    completedToday: 6,
    description: 'Develops strategic partnerships and collaborations',
    responsibilities: [
      'Partnership development',
      'Alliance management',
      'Collaboration frameworks',
      'Partnership ROI'
    ],
    aiTools: ['Partner Matcher', 'Deal Analyzer', 'ROI Calculator'],
    k1Location: '/oversight/mitra/',
    subAgents: [
      { name: 'Partnership Manager', role: 'Partner relationship', status: 'active', workload: 73, tasks: 4 },
      { name: 'Deal Negotiator', role: 'Contract negotiation', status: 'active', workload: 69, tasks: 4 },
      { name: 'Integration Lead', role: 'Partnership integration', status: 'active', workload: 68, tasks: 3 }
    ]
  },
  {
    id: 'dharma',
    name: 'DHARMA',
    chief: 'Lord Dharma',
    role: 'Government Relations',
    tier: 'Operations',
    color: '#059669',
    status: 'active',
    workload: 65,
    activeTasks: 8,
    completedToday: 4,
    description: 'Manages government affairs and regulatory compliance',
    responsibilities: [
      'Government liaisons',
      'Policy advocacy',
      'Regulatory compliance',
      'Public affairs'
    ],
    aiTools: ['Policy Tracker', 'Compliance Monitor', 'Regulation Analyzer'],
    k1Location: '/oversight/dharma/',
    subAgents: [
      { name: 'Policy Analyst', role: 'Policy research', status: 'active', workload: 68, tasks: 3 },
      { name: 'Compliance Officer', role: 'Regulatory adherence', status: 'active', workload: 64, tasks: 3 },
      { name: 'Liaison Coordinator', role: 'Government relations', status: 'active', workload: 63, tasks: 2 }
    ]
  },
  {
    id: 'shukra',
    name: 'SHUKRA',
    chief: 'Lord Shukra',
    role: 'Chief Strategy Officer',
    tier: 'Executive',
    color: '#6366F1',
    status: 'active',
    workload: 73,
    activeTasks: 12,
    completedToday: 7,
    description: 'Defines corporate strategy and long-term planning',
    responsibilities: [
      'Strategic planning',
      'Market analysis',
      'Competitive intelligence',
      'Business modeling'
    ],
    aiTools: ['Strategy Simulator', 'Market Analyzer', 'Scenario Planner'],
    k1Location: '/oversight/shukra/',
    subAgents: [
      { name: 'Strategy Analyst', role: 'Strategic research', status: 'active', workload: 76, tasks: 4 },
      { name: 'Market Researcher', role: 'Market intelligence', status: 'active', workload: 72, tasks: 4 },
      { name: 'Business Modeler', role: 'Business case development', status: 'active', workload: 71, tasks: 4 }
    ]
  },
  {
    id: 'chandra',
    name: 'CHANDRA',
    chief: 'Lord Chandra',
    role: 'Data & Analytics',
    tier: 'Operations',
    color: '#06B6D4',
    status: 'active',
    workload: 84,
    activeTasks: 16,
    completedToday: 10,
    description: 'Manages data infrastructure and analytics',
    responsibilities: [
      'Data warehousing',
      'Analytics platform',
      'Business intelligence',
      'Data governance'
    ],
    aiTools: ['Data Pipeline', 'BI Dashboard', 'Predictive Models'],
    k1Location: '/oversight/chandra/',
    subAgents: [
      { name: 'Data Engineer', role: 'Data infrastructure', status: 'active', workload: 87, tasks: 6 },
      { name: 'Analytics Lead', role: 'Data analysis', status: 'active', workload: 83, tasks: 5 },
      { name: 'BI Developer', role: 'Dashboard development', status: 'active', workload: 82, tasks: 5 }
    ]
  },
  {
    id: 'brahma',
    name: 'BRAHMA',
    chief: 'Lord Brahma',
    role: 'Research & Development',
    tier: 'Operations',
    color: '#F59E0B',
    status: 'active',
    workload: 77,
    activeTasks: 13,
    completedToday: 8,
    description: 'Leads innovation and product research',
    responsibilities: [
      'Technology research',
      'Product innovation',
      'Prototype development',
      'IP management'
    ],
    aiTools: ['Research Assistant', 'Patent Analyzer', 'Innovation Tracker'],
    k1Location: '/oversight/brahma/',
    subAgents: [
      { name: 'Research Scientist', role: 'Technology research', status: 'active', workload: 80, tasks: 5 },
      { name: 'Innovation Lead', role: 'New product concepts', status: 'active', workload: 76, tasks: 4 },
      { name: 'Prototype Engineer', role: 'Prototype building', status: 'active', workload: 75, tasks: 4 }
    ]
  },
  {
    id: 'indra',
    name: 'INDRA',
    chief: 'Lord Indra',
    role: 'Chief Operating Officer',
    tier: 'Executive',
    color: '#EF4444',
    status: 'active',
    workload: 86,
    activeTasks: 19,
    completedToday: 12,
    description: 'Oversees daily operations and execution',
    responsibilities: [
      'Operations management',
      'Process optimization',
      'Resource allocation',
      'Performance monitoring'
    ],
    aiTools: ['Operations Dashboard', 'Process Optimizer', 'Resource Planner'],
    k1Location: '/oversight/indra/',
    subAgents: [
      { name: 'Operations Manager', role: 'Daily operations', status: 'active', workload: 89, tasks: 7 },
      { name: 'Process Engineer', role: 'Process improvement', status: 'active', workload: 85, tasks: 6 },
      { name: 'Resource Coordinator', role: 'Resource management', status: 'active', workload: 84, tasks: 6 }
    ]
  },
  {
    id: 'chitragupta',
    name: 'CHITRAGUPTA',
    chief: 'Lord Chitragupta',
    role: 'Quality Assurance',
    tier: 'Operations',
    color: '#10B981',
    status: 'active',
    workload: 71,
    activeTasks: 10,
    completedToday: 6,
    description: 'Ensures quality standards and testing',
    responsibilities: [
      'Quality control',
      'Testing protocols',
      'Standards compliance',
      'Defect tracking'
    ],
    aiTools: ['Test Automator', 'Defect Tracker', 'Quality Scorer'],
    k1Location: '/oversight/chitragupta/',
    subAgents: [
      { name: 'Test Engineer', role: 'Automated testing', status: 'active', workload: 74, tasks: 4 },
      { name: 'Quality Analyst', role: 'Quality audits', status: 'active', workload: 70, tasks: 3 },
      { name: 'Compliance Checker', role: 'Standards verification', status: 'active', workload: 69, tasks: 3 }
    ]
  },
  {
    id: 'prajapati',
    name: 'PRAJAPATI',
    chief: 'Lord Prajapati',
    role: 'Product Management',
    tier: 'Operations',
    color: '#8B5CF6',
    status: 'active',
    workload: 78,
    activeTasks: 14,
    completedToday: 9,
    description: 'Manages product strategy and roadmap',
    responsibilities: [
      'Product strategy',
      'Roadmap planning',
      'Feature prioritization',
      'User feedback'
    ],
    aiTools: ['Roadmap Planner', 'Feature Scorer', 'User Insight'],
    k1Location: '/oversight/prajapati/',
    subAgents: [
      { name: 'Product Manager', role: 'Product strategy', status: 'active', workload: 81, tasks: 5 },
      { name: 'Roadmap Lead', role: 'Roadmap planning', status: 'active', workload: 77, tasks: 5 },
      { name: 'User Researcher', role: 'User feedback analysis', status: 'active', workload: 76, tasks: 4 }
    ]
  },
  {
    id: 'yama',
    name: 'YAMA',
    chief: 'Lord Yama',
    role: 'Legal & Compliance',
    tier: 'Operations',
    color: '#6B7280',
    status: 'active',
    workload: 66,
    activeTasks: 9,
    completedToday: 5,
    description: 'Manages legal affairs and compliance',
    responsibilities: [
      'Legal counsel',
      'Contract management',
      'Compliance oversight',
      'Risk mitigation'
    ],
    aiTools: ['Contract Analyzer', 'Compliance Checker', 'Legal Research'],
    k1Location: '/oversight/yama/',
    subAgents: [
      { name: 'Legal Counsel', role: 'Legal advice', status: 'active', workload: 69, tasks: 3 },
      { name: 'Contract Manager', role: 'Contract review', status: 'active', workload: 65, tasks: 3 },
      { name: 'Compliance Lead', role: 'Regulatory compliance', status: 'active', workload: 64, tasks: 3 }
    ]
  },
  {
    id: 'vani',
    name: 'VANI',
    chief: 'Goddess Vani',
    role: 'Content & Communications',
    tier: 'Operations',
    color: '#EC4899',
    status: 'active',
    workload: 75,
    activeTasks: 12,
    completedToday: 7,
    description: 'Creates content and manages communications',
    responsibilities: [
      'Content strategy',
      'Internal communications',
      'External PR',
      'Editorial oversight'
    ],
    aiTools: ['Content Generator', 'PR Manager', 'Communication Planner'],
    k1Location: '/oversight/vani/',
    subAgents: [
      { name: 'Content Writer', role: 'Content creation', status: 'active', workload: 78, tasks: 4 },
      { name: 'Communications Lead', role: 'Internal comms', status: 'active', workload: 74, tasks: 4 },
      { name: 'PR Manager', role: 'Public relations', status: 'active', workload: 73, tasks: 4 }
    ]
  },
  {
    id: 'vayu',
    name: 'VAYU',
    chief: 'Lord Vayu',
    role: 'Sustainability & ESG',
    tier: 'Operations',
    color: '#10B981',
    status: 'active',
    workload: 64,
    activeTasks: 7,
    completedToday: 4,
    description: 'Manages sustainability initiatives and ESG',
    responsibilities: [
      'Sustainability strategy',
      'Environmental impact',
      'Social responsibility',
      'ESG reporting'
    ],
    aiTools: ['Carbon Tracker', 'ESG Scorer', 'Impact Analyzer'],
    k1Location: '/oversight/vayu/',
    subAgents: [
      { name: 'Sustainability Lead', role: 'Green initiatives', status: 'active', workload: 67, tasks: 3 },
      { name: 'ESG Analyst', role: 'ESG metrics', status: 'active', workload: 63, tasks: 2 },
      { name: 'Impact Coordinator', role: 'Social impact', status: 'active', workload: 62, tasks: 2 }
    ]
  }
];
