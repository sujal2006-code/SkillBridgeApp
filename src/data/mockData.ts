import { Skill, Internship, TeamCandidate, VerificationRequest, ActivityItem, EvidenceItem } from '../types';

export const INITIAL_SKILLS: Skill[] = [
  {
    id: 'skill-python',
    name: 'Python',
    category: 'Programming',
    level: 'Advanced',
    percentage: 90,
    evidenceCount: 4,
    verifiedByAi: true,
    evidenceIds: ['ev-1', 'ev-4'],
  },
  {
    id: 'skill-js',
    name: 'JavaScript',
    category: 'Programming',
    level: 'Intermediate',
    percentage: 75,
    evidenceCount: 2,
    verifiedByAi: true,
    evidenceIds: ['ev-2'],
  },
  {
    id: 'skill-ml',
    name: 'Machine Learning',
    category: 'Data Science',
    level: 'Advanced',
    percentage: 85,
    evidenceCount: 6,
    verifiedByAi: true,
    evidenceIds: ['ev-1', 'ev-5'],
  },
  {
    id: 'skill-uiux',
    name: 'UI/UX Design',
    category: 'Design',
    level: 'Expert',
    percentage: 95,
    evidenceCount: 8,
    verifiedByAi: true,
    evidenceIds: ['ev-3'],
  },
  {
    id: 'skill-react',
    name: 'React',
    category: 'Programming',
    level: 'Advanced',
    percentage: 88,
    evidenceCount: 5,
    verifiedByAi: true,
    evidenceIds: ['ev-2'],
  },
  {
    id: 'skill-sql',
    name: 'SQL',
    category: 'Data Science',
    level: 'Beginner',
    percentage: 45,
    evidenceCount: 1,
    verifiedByAi: true,
    evidenceIds: ['ev-4'],
  },
];

export const INITIAL_EVIDENCE: EvidenceItem[] = [
  {
    id: 'ev-1',
    title: 'Customer Churn Predictive Pipeline',
    type: 'Project',
    institution: 'Stanford Online / Machine Learning Specialization',
    skills: ['Python', 'Machine Learning', 'Data Preprocessing'],
    date: '2026-07-28',
    verificationStatus: 'verified',
    score: 94,
    fileName: 'churn_pipeline_final_report.pdf',
    aiFeedback: 'Demonstrates strong end-to-end model construction, validation splitting, and feature engineering in Scikit-Learn.',
    url: 'https://github.com/alex-mercer/churn-prediction'
  },
  {
    id: 'ev-2',
    title: 'Weather App with Interactive Radar',
    type: 'Project',
    institution: 'Frontend Architecture Coursework',
    skills: ['React', 'JavaScript', 'TypeScript', 'Tailwind CSS'],
    date: '2026-08-12',
    verificationStatus: 'verified',
    score: 91,
    fileName: 'weather_radar_spa.zip',
    aiFeedback: 'Clean modular state architecture with custom hooks, memoized canvas rendering, and accessible ARIA attributes.',
    url: 'https://github.com/alex-mercer/weather-radar'
  },
  {
    id: 'ev-3',
    title: 'Design System & Component Library',
    type: 'Coursework',
    institution: 'Design Academy',
    skills: ['UI/UX Design', 'Figma', 'Prototyping', 'User Testing'],
    date: '2026-06-15',
    verificationStatus: 'verified',
    score: 98,
    fileName: 'fintech_design_system_v2.fig',
    aiFeedback: 'Exemplary 8pt spatial grid fidelity, WCAG AA color ratios, and component auto-layout scalability.',
    url: 'https://figma.com/@alex_m/fintech-system'
  },
  {
    id: 'ev-4',
    title: 'E-Commerce Analytics Query Suite',
    type: 'Coursework',
    institution: 'DataCamp SQL Professional',
    skills: ['SQL', 'Python', 'Data Analysis'],
    date: '2026-05-10',
    verificationStatus: 'verified',
    score: 86,
    fileName: 'analytics_queries.sql',
    aiFeedback: 'Demonstrates window functions, CTEs, and index optimization on high-cardinality transaction tables.',
  },
  {
    id: 'ev-5',
    title: 'NeurIPS Reproducibility Challenge Entry',
    type: 'Competition',
    institution: 'Global AI Research Consortium',
    skills: ['Machine Learning', 'PyTorch', 'Python'],
    date: '2026-04-20',
    verificationStatus: 'verified',
    score: 96,
    fileName: 'paper_reproduction_torch.pdf',
    aiFeedback: 'High fidelity reproduction of attention weight distributions with reproducible Docker configurations.',
  }
];

export const INITIAL_INTERNSHIPS: Internship[] = [
  {
    id: 'int-1',
    title: 'Junior AI Researcher',
    company: 'Global Minds',
    logo: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=120&auto=format&fit=crop&q=80',
    location: 'Remote',
    type: 'Remote',
    employmentType: 'Full-time',
    matchPercentage: 92,
    isTopMatch: true,
    postedDate: '2 days ago',
    verifiedSkills: ['Python', 'Machine Learning', 'PyTorch'],
    missingSkills: ['CUDA Optimization'],
    description: 'Work alongside lead research scientists analyzing multimodal embeddings and preparing reproducible benchmark pipelines.',
    applied: false
  },
  {
    id: 'int-2',
    title: 'Product Designer',
    company: 'CreativeFlow',
    logo: 'https://images.unsplash.com/photo-1557804506-669a67965ba0?w=120&auto=format&fit=crop&q=80',
    location: 'Remote',
    type: 'Remote',
    employmentType: 'Full-time',
    matchPercentage: 75,
    postedDate: '3 days ago',
    verifiedSkills: ['Figma', 'UI Design', 'Prototyping'],
    missingSkills: ['Design Tokens in Swift'],
    description: 'Help shape next-generation creative tooling interfaces, conduct live usability sessions, and maintain our cross-platform design library.',
    applied: false
  },
  {
    id: 'int-3',
    title: 'Frontend Developer',
    company: 'TechCorp',
    logo: 'https://images.unsplash.com/photo-1572021335469-31706a17aaef?w=120&auto=format&fit=crop&q=80',
    location: 'Remote',
    type: 'Remote',
    employmentType: 'Full-time',
    matchPercentage: 94,
    isTopMatch: true,
    postedDate: 'Just now',
    verifiedSkills: ['React', 'TypeScript', 'JavaScript'],
    missingSkills: ['GraphQL Federation'],
    description: 'Build responsive, accessible SaaS micro-frontends with cutting-edge state synchronization and ultra-fast page transitions.',
    applied: false
  },
  {
    id: 'int-4',
    title: 'Data Analyst Intern',
    company: 'InsightCo',
    logo: 'https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=120&auto=format&fit=crop&q=80',
    location: 'New York, NY',
    type: 'Hybrid',
    employmentType: 'Internship',
    matchPercentage: 89,
    postedDate: '1 day ago',
    verifiedSkills: ['Python', 'SQL', 'Tableau'],
    missingSkills: ['Snowflake Warehouse'],
    description: 'Deliver actionable KPI dashboards, automate recurring stakeholder data extracts, and run anomaly detection routines on ingestion feeds.',
    applied: false
  },
  {
    id: 'int-5',
    title: 'ML Engineering Intern',
    company: 'NeuroTech Inc.',
    logo: 'https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?w=120&auto=format&fit=crop&q=80',
    location: 'San Francisco, CA',
    type: 'On-site',
    employmentType: 'Full-time',
    matchPercentage: 91,
    postedDate: '4 days ago',
    verifiedSkills: ['Python', 'Machine Learning', 'Data Preprocessing'],
    missingSkills: ['Kubeflow Pipelines'],
    description: 'Collaborate with neuroscience researchers to fine-tune neural decoding models and optimize latency on edge hardware.',
    applied: false
  }
];

export const INITIAL_CANDIDATES: TeamCandidate[] = [
  {
    id: 'cand-1',
    name: 'Sarah K.',
    role: 'UX Expert',
    level: 'Graduate Level',
    avatar: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=160&auto=format&fit=crop&q=80',
    matchPercentage: 95,
    aiInsight: 'Perfectly complements your Python backend skills. Strong portfolio in interactive data visualizations.',
    verifiedSkills: ['Wireframing', 'Prototyping', 'User Testing'],
    education: 'Stanford University, Human-Computer Interaction',
    location: 'San Francisco, CA',
    invited: false
  },
  {
    id: 'cand-2',
    name: 'James L.',
    role: 'ML Student',
    level: 'Junior',
    avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=160&auto=format&fit=crop&q=80',
    matchPercentage: 88,
    aiInsight: 'Shared background in PyTorch projects. High collaboration score on past group assignments.',
    verifiedSkills: ['PyTorch', 'Data Preprocessing', 'Python'],
    education: 'UC Berkeley, Computer Science & EECS',
    location: 'Berkeley, CA',
    invited: false
  },
  {
    id: 'cand-3',
    name: 'Elena Rostova',
    role: 'Fullstack Engineer',
    level: 'Senior',
    avatar: 'https://images.unsplash.com/photo-1580489944761-15a19d654956?w=160&auto=format&fit=crop&q=80',
    matchPercentage: 91,
    aiInsight: 'Expertise in high-throughput API design and real-time streaming architectures. Fast delivery cycle.',
    verifiedSkills: ['React', 'TypeScript', 'Node.js', 'PostgreSQL'],
    education: 'Carnegie Mellon, Software Engineering',
    location: 'Pittsburgh, PA',
    invited: false
  }
];

export const INITIAL_ACTIVITIES: ActivityItem[] = [
  {
    id: 'act-1',
    title: 'Project "Weather App" verified',
    subtitle: 'Frontend Architecture • 2 hours ago',
    time: '2 hours ago',
    icon: 'check_circle',
    type: 'verification'
  },
  {
    id: 'act-2',
    title: 'Matched with AI Intern role',
    subtitle: 'NeuroTech Inc. • 1 day ago',
    time: '1 day ago',
    icon: 'stars',
    type: 'match'
  },
  {
    id: 'act-3',
    title: 'Skill "Machine Learning" updated to 85%',
    subtitle: 'After NeurIPS challenge submission • 3 days ago',
    time: '3 days ago',
    icon: 'trending_up',
    type: 'verification'
  }
];

export const INITIAL_VERIFICATION_QUEUE: VerificationRequest[] = [
  {
    id: 'vq-1',
    studentName: 'Alex Chen',
    studentInitials: 'AC',
    title: 'Web Development Project',
    type: 'Project',
    submittedTime: '2 hours ago',
    skills: ['React', 'TypeScript', 'Tailwind CSS'],
    status: 'pending',
    evidenceSnippet: 'Full stack dashboard with live WebSocket notifications and accessible navigation.'
  },
  {
    id: 'vq-2',
    studentName: 'Maria G.',
    studentInitials: 'MG',
    title: 'AWS Cloud Cert',
    type: 'Certificate',
    submittedTime: '4 hours ago',
    skills: ['AWS', 'Cloud Architecture', 'DevOps'],
    status: 'pending',
    evidenceSnippet: 'Certified Solutions Architect Associate credential ID: AWS-7829103'
  },
  {
    id: 'vq-3',
    studentName: 'Jamal D.',
    studentInitials: 'JD',
    title: 'Data Analysis Portfolio',
    type: 'Coursework',
    submittedTime: '1 day ago',
    skills: ['Python', 'SQL', 'Pandas'],
    status: 'pending',
    evidenceSnippet: 'Comprehensive exploratory data analysis on 1.2M municipal housing records.'
  },
  {
    id: 'vq-4',
    studentName: 'Sofia Rodriguez',
    studentInitials: 'SR',
    title: 'NLP Sentiment Model',
    type: 'Competition',
    submittedTime: '2 days ago',
    skills: ['Machine Learning', 'PyTorch', 'Transformers'],
    status: 'pending',
    evidenceSnippet: 'BERT fine-tuning achieving 94.2% F1 score on Kaggle finance sentiment competition.'
  }
];
