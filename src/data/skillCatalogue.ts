export interface CanonicalSkill {
  name: string;
  category: string;
  description: string;
  relatedSkills: string[];
}

export const CANONICAL_SKILL_CATALOGUE: CanonicalSkill[] = [
  // Programming
  {
    name: 'Python',
    category: 'Programming Languages',
    description: 'High-level programming language for AI, data science, and web development.',
    relatedSkills: ['FastAPI', 'Django', 'Flask', 'NumPy', 'Pandas', 'Machine Learning', 'Data Science', 'REST API', 'SQL', 'PyTorch'],
  },
  {
    name: 'Java',
    category: 'Programming Languages',
    description: 'Object-oriented, class-based programming language for enterprise and Android development.',
    relatedSkills: ['Spring Boot', 'OOP', 'DSA', 'SQL', 'REST API', 'Microservices'],
  },
  {
    name: 'C',
    category: 'Programming Languages',
    description: 'Procedural systems programming language with low-level memory manipulation.',
    relatedSkills: ['C++', 'DSA', 'Algorithms', 'Linux', 'System Design'],
  },
  {
    name: 'C++',
    category: 'Programming Languages',
    description: 'High-performance object-oriented programming for systems, games, and high-throughput systems.',
    relatedSkills: ['C', 'DSA', 'Algorithms', 'OOP', 'Computer Vision', 'System Design'],
  },
  {
    name: 'C#',
    category: 'Programming Languages',
    description: 'Modern type-safe object-oriented language for .NET, enterprise, and game development.',
    relatedSkills: ['OOP', 'REST API', 'SQL', 'Microservices', 'Azure'],
  },
  {
    name: 'JavaScript',
    category: 'Programming Languages',
    description: 'High-level scripting language powering dynamic behavior on the web.',
    relatedSkills: ['TypeScript', 'React', 'Node.js', 'Express.js', 'HTML', 'CSS', 'Next.js'],
  },
  {
    name: 'TypeScript',
    category: 'Programming Languages',
    description: 'Strict syntactical superset of JavaScript adding static type definitions.',
    relatedSkills: ['JavaScript', 'React', 'Next.js', 'Node.js', 'Angular', 'Vue.js', 'REST API'],
  },
  {
    name: 'Go',
    category: 'Programming Languages',
    description: 'Statically typed, compiled programming language designed for concurrent systems.',
    relatedSkills: ['Microservices', 'Docker', 'Kubernetes', 'REST API', 'gRPC', 'CI/CD'],
  },
  {
    name: 'Rust',
    category: 'Programming Languages',
    description: 'Safe, concurrent, high-performance systems language with memory safety guarantees.',
    relatedSkills: ['C++', 'Systems Programming', 'Linux', 'DSA', 'Algorithms'],
  },
  {
    name: 'Kotlin',
    category: 'Programming Languages',
    description: 'Modern cross-platform statically typed language for JVM and Android.',
    relatedSkills: ['Java', 'Spring Boot', 'Android', 'OOP', 'REST API'],
  },
  {
    name: 'Swift',
    category: 'Programming Languages',
    description: 'Powerful, intuitive language for iOS, macOS, watchOS, and tvOS development.',
    relatedSkills: ['iOS', 'OOP', 'REST API', 'UI Design', 'Xcode'],
  },
  {
    name: 'PHP',
    category: 'Programming Languages',
    description: 'Server-side scripting language designed for web development.',
    relatedSkills: ['MySQL', 'HTML', 'CSS', 'JavaScript', 'Laravel', 'REST API'],
  },

  // Web Development
  {
    name: 'HTML',
    category: 'Frontend Development',
    description: 'Standard markup language for documents designed to be displayed in a web browser.',
    relatedSkills: ['CSS', 'JavaScript', 'React', 'Tailwind CSS', 'Bootstrap'],
  },
  {
    name: 'CSS',
    category: 'Frontend Development',
    description: 'Style sheet language used for describing the presentation of structured documents.',
    relatedSkills: ['HTML', 'Tailwind CSS', 'Bootstrap', 'JavaScript', 'React'],
  },
  {
    name: 'React',
    category: 'Frontend Development',
    description: 'Component-based declarative JavaScript UI library for building reactive interfaces.',
    relatedSkills: ['JavaScript', 'TypeScript', 'HTML', 'CSS', 'Next.js', 'Tailwind CSS', 'Node.js'],
  },
  {
    name: 'Next.js',
    category: 'Frontend Development',
    description: 'Production React framework with hybrid static & server rendering.',
    relatedSkills: ['React', 'TypeScript', 'JavaScript', 'Node.js', 'Tailwind CSS', 'REST API'],
  },
  {
    name: 'Node.js',
    category: 'Web Development',
    description: 'Asynchronous event-driven JavaScript runtime environment for backend services.',
    relatedSkills: ['Express.js', 'JavaScript', 'TypeScript', 'REST API', 'MongoDB', 'PostgreSQL'],
  },
  {
    name: 'Express.js',
    category: 'Web Development',
    description: 'Minimal and flexible Node.js web application framework for robust APIs.',
    relatedSkills: ['Node.js', 'JavaScript', 'TypeScript', 'REST API', 'MongoDB', 'SQL'],
  },
  {
    name: 'Angular',
    category: 'Frontend Development',
    description: 'Component-based framework for building scalable web applications with TypeScript.',
    relatedSkills: ['TypeScript', 'JavaScript', 'HTML', 'CSS', 'REST API', 'RxJS'],
  },
  {
    name: 'Vue.js',
    category: 'Frontend Development',
    description: 'Progressive JavaScript framework for building user interfaces and single-page apps.',
    relatedSkills: ['JavaScript', 'TypeScript', 'HTML', 'CSS', 'Tailwind CSS'],
  },
  {
    name: 'Tailwind CSS',
    category: 'Frontend Development',
    description: 'Utility-first CSS framework for rapid modern UI development.',
    relatedSkills: ['CSS', 'HTML', 'React', 'Next.js', 'Vue.js'],
  },
  {
    name: 'Bootstrap',
    category: 'Frontend Development',
    description: 'Popular responsive CSS framework for mobile-first front-end web design.',
    relatedSkills: ['HTML', 'CSS', 'JavaScript'],
  },

  // Backend / API
  {
    name: 'FastAPI',
    category: 'Backend Development',
    description: 'High-performance Python web framework for building modern REST APIs.',
    relatedSkills: ['Python', 'SQL & PostgreSQL', 'Docker', 'REST API', 'Pydantic', 'Microservices'],
  },
  {
    name: 'Flask',
    category: 'Backend Development',
    description: 'Lightweight WSGI Python web application framework for microservices.',
    relatedSkills: ['Python', 'REST API', 'SQL', 'Docker'],
  },
  {
    name: 'Django',
    category: 'Backend Development',
    description: 'High-level Python web framework with batteries-included ORM and admin tools.',
    relatedSkills: ['Python', 'SQL & PostgreSQL', 'REST API', 'Docker'],
  },
  {
    name: 'Spring Boot',
    category: 'Backend Development',
    description: 'Enterprise Java framework for creating stand-alone, production-grade Spring applications.',
    relatedSkills: ['Java', 'SQL', 'OOP', 'Microservices', 'REST API', 'Docker'],
  },
  {
    name: 'REST API',
    category: 'Backend Development',
    description: 'Architectural style for designing networked scalable web API services.',
    relatedSkills: ['FastAPI', 'Node.js', 'Python', 'Express.js', 'Spring Boot', 'GraphQL'],
  },
  {
    name: 'RESTful API Design',
    category: 'Backend Development',
    description: 'Best practices for designing, documenting, and securing REST APIs.',
    relatedSkills: ['REST API', 'FastAPI', 'Node.js', 'Microservices'],
  },
  {
    name: 'GraphQL',
    category: 'Backend Development',
    description: 'Query language for APIs and runtime for executing queries with existing data.',
    relatedSkills: ['REST API', 'Node.js', 'TypeScript', 'React'],
  },
  {
    name: 'Microservices',
    category: 'Backend Development',
    description: 'Architectural design pattern structuring an application as a collection of loose services.',
    relatedSkills: ['Docker', 'Kubernetes', 'REST API', 'FastAPI', 'Spring Boot', 'Go'],
  },

  // Databases
  {
    name: 'SQL',
    category: 'Databases',
    description: 'Standard declarative query language for relational database management systems.',
    relatedSkills: ['PostgreSQL', 'MySQL', 'SQLite', 'Database Design', 'Python', 'FastAPI'],
  },
  {
    name: 'SQL & PostgreSQL',
    category: 'Databases',
    description: 'Relational database modeling, indexing, query optimization, and transaction management.',
    relatedSkills: ['SQL', 'PostgreSQL', 'FastAPI', 'Python', 'Database Design'],
  },
  {
    name: 'PostgreSQL',
    category: 'Databases',
    description: 'Powerful open-source object-relational database system with advanced indexing.',
    relatedSkills: ['SQL', 'SQL & PostgreSQL', 'Database Design', 'FastAPI', 'Python'],
  },
  {
    name: 'MySQL',
    category: 'Databases',
    description: 'Widely deployed open-source relational database management system.',
    relatedSkills: ['SQL', 'PHP', 'Database Design', 'Node.js'],
  },
  {
    name: 'SQLite',
    category: 'Databases',
    description: 'Self-contained, serverless, zero-configuration embedded SQL database engine.',
    relatedSkills: ['SQL', 'Python', 'Database Design'],
  },
  {
    name: 'MongoDB',
    category: 'Databases',
    description: 'Document-oriented NoSQL database system using JSON-like documents.',
    relatedSkills: ['Node.js', 'Express.js', 'JavaScript', 'TypeScript'],
  },
  {
    name: 'Redis',
    category: 'Databases',
    description: 'In-memory data structure store used as a distributed database and cache.',
    relatedSkills: ['Backend Development', 'FastAPI', 'Node.js', 'System Design'],
  },
  {
    name: 'Database Design',
    category: 'Databases',
    description: 'Entity-relationship modeling, normalization, indexing strategies, and schema migrations.',
    relatedSkills: ['SQL', 'PostgreSQL', 'MySQL', 'MongoDB', 'System Design'],
  },

  // AI / Machine Learning
  {
    name: 'Machine Learning',
    category: 'AI / Data Science',
    description: 'Applied ML, feature engineering, neural networks, and model evaluation.',
    relatedSkills: ['Python', 'NumPy', 'Pandas', 'Scikit-learn', 'Deep Learning', 'NLP', 'Computer Vision', 'TensorFlow', 'PyTorch', 'Data Science'],
  },
  {
    name: 'Artificial Intelligence',
    category: 'AI / Data Science',
    description: 'General AI principles, knowledge representation, heuristics, and intelligent agents.',
    relatedSkills: ['Machine Learning', 'Deep Learning', 'Python', 'Generative AI'],
  },
  {
    name: 'Deep Learning',
    category: 'AI / Data Science',
    description: 'Multi-layer neural network architectures, backpropagation, CNNs, and RNNs.',
    relatedSkills: ['PyTorch', 'TensorFlow', 'Machine Learning', 'Computer Vision', 'NLP', 'Keras'],
  },
  {
    name: 'Natural Language Processing',
    category: 'AI / Data Science',
    description: 'Computational linguistics, text tokenization, embeddings, and sentiment analysis.',
    relatedSkills: ['NLP', 'Large Language Models', 'Generative AI', 'Python', 'PyTorch'],
  },
  {
    name: 'NLP',
    category: 'AI / Data Science',
    description: 'Natural Language Processing algorithms, transformers, and sequence modeling.',
    relatedSkills: ['Natural Language Processing', 'Large Language Models', 'Generative AI', 'Python', 'PyTorch'],
  },
  {
    name: 'Computer Vision',
    category: 'AI / Data Science',
    description: 'Image processing, object detection, segmentation, and convolutional neural networks.',
    relatedSkills: ['Deep Learning', 'PyTorch', 'TensorFlow', 'Python', 'C++'],
  },
  {
    name: 'Generative AI',
    category: 'AI / Data Science',
    description: 'Foundation models, diffusion architectures, LLM prompting, and RAG architectures.',
    relatedSkills: ['Large Language Models', 'NLP', 'Python', 'FastAPI', 'PyTorch'],
  },
  {
    name: 'Large Language Models',
    category: 'AI / Data Science',
    description: 'Transformer-based language models, fine-tuning, context window management, and inference.',
    relatedSkills: ['Generative AI', 'NLP', 'Python', 'PyTorch', 'FastAPI'],
  },
  {
    name: 'Data Science',
    category: 'AI / Data Science',
    description: 'Interdisciplinary field extracting knowledge from structured and unstructured data.',
    relatedSkills: ['Python', 'Pandas', 'NumPy', 'Machine Learning', 'Data Analysis', 'Statistics'],
  },
  {
    name: 'TensorFlow',
    category: 'AI / Data Science',
    description: 'End-to-end open source platform for machine learning and deep neural networks.',
    relatedSkills: ['Keras', 'Python', 'Deep Learning', 'Machine Learning'],
  },
  {
    name: 'PyTorch',
    category: 'AI / Data Science',
    description: 'Optimized tensor library for deep learning with dynamic autograd.',
    relatedSkills: ['Deep Learning', 'Python', 'Machine Learning', 'Computer Vision', 'NLP'],
  },
  {
    name: 'Scikit-learn',
    category: 'AI / Data Science',
    description: 'Simple and efficient tools for predictive data analysis and machine learning in Python.',
    relatedSkills: ['Machine Learning', 'Python', 'Pandas', 'NumPy', 'Data Science'],
  },
  {
    name: 'Keras',
    category: 'AI / Data Science',
    description: 'High-level neural networks API running on top of TensorFlow for fast prototyping.',
    relatedSkills: ['TensorFlow', 'Deep Learning', 'Python', 'Machine Learning'],
  },

  // Data Analysis
  {
    name: 'NumPy',
    category: 'Data Analysis',
    description: 'Core library for scientific computing with Python, offering high-performance arrays.',
    relatedSkills: ['Pandas', 'Python', 'Data Science', 'Machine Learning', 'Statistics'],
  },
  {
    name: 'Pandas',
    category: 'Data Analysis',
    description: 'Fast, flexible data manipulation and analysis tool built on top of Python.',
    relatedSkills: ['NumPy', 'Python', 'Data Analysis', 'SQL', 'Data Science'],
  },
  {
    name: 'Matplotlib',
    category: 'Data Analysis',
    description: 'Comprehensive library for creating static, animated, and interactive visualizations.',
    relatedSkills: ['Seaborn', 'Pandas', 'Python', 'Data Visualization'],
  },
  {
    name: 'Seaborn',
    category: 'Data Analysis',
    description: 'Statistical data visualization library based on matplotlib with attractive default styles.',
    relatedSkills: ['Matplotlib', 'Pandas', 'Python', 'Data Visualization'],
  },
  {
    name: 'Data Visualization',
    category: 'Data Analysis',
    description: 'Graphical representation of information and data to communicate complex trends.',
    relatedSkills: ['Data Analysis', 'Pandas', 'Matplotlib', 'Seaborn', 'Python'],
  },
  {
    name: 'Data Analysis',
    category: 'Data Analysis',
    description: 'Process of inspecting, cleansing, transforming, and modeling data.',
    relatedSkills: ['SQL', 'Python', 'Pandas', 'Statistics', 'Data Visualization'],
  },
  {
    name: 'Statistics',
    category: 'Data Analysis',
    description: 'Probability distributions, hypothesis testing, regression analysis, and statistical inference.',
    relatedSkills: ['Data Analysis', 'Data Science', 'Machine Learning', 'Python'],
  },

  // Cloud & DevOps
  {
    name: 'Git',
    category: 'DevOps / Infrastructure',
    description: 'Distributed version control system for tracking changes in source code.',
    relatedSkills: ['GitHub', 'CI/CD', 'Docker', 'Linux'],
  },
  {
    name: 'GitHub',
    category: 'DevOps / Infrastructure',
    description: 'Cloud hosting platform for Git repositories with CI/CD GitHub Actions integration.',
    relatedSkills: ['Git', 'CI/CD', 'Docker'],
  },
  {
    name: 'Docker',
    category: 'DevOps / Infrastructure',
    description: 'OS-level virtualization delivering software in packages called containers.',
    relatedSkills: ['Kubernetes', 'Cloud & Docker', 'CI/CD', 'AWS', 'Linux'],
  },
  {
    name: 'Cloud & Docker',
    category: 'DevOps / Infrastructure',
    description: 'Containerization, cloud deployments, and CI/CD pipelines.',
    relatedSkills: ['Docker', 'AWS', 'Kubernetes', 'CI/CD'],
  },
  {
    name: 'Kubernetes',
    category: 'DevOps / Infrastructure',
    description: 'Automated deployment, scaling, and management of containerized applications.',
    relatedSkills: ['Docker', 'AWS', 'Cloud & Docker', 'CI/CD'],
  },
  {
    name: 'AWS',
    category: 'DevOps / Infrastructure',
    description: 'Amazon Web Services cloud computing platform and distributed services.',
    relatedSkills: ['Docker', 'Cloud & Docker', 'CI/CD', 'Linux', 'Kubernetes'],
  },
  {
    name: 'Azure',
    category: 'DevOps / Infrastructure',
    description: 'Microsoft Azure cloud services for building, testing, deploying, and managing applications.',
    relatedSkills: ['Docker', 'CI/CD', 'C#', 'Cloud & Docker'],
  },
  {
    name: 'Google Cloud',
    category: 'DevOps / Infrastructure',
    description: 'Suite of cloud computing services that runs on Google infrastructure.',
    relatedSkills: ['Docker', 'Kubernetes', 'Python', 'Cloud & Docker'],
  },
  {
    name: 'CI/CD',
    category: 'DevOps / Infrastructure',
    description: 'Continuous Integration and Continuous Delivery automated release pipelines.',
    relatedSkills: ['Git', 'GitHub', 'Docker', 'AWS', 'Kubernetes'],
  },

  // Computer Science Fundamentals
  {
    name: 'DSA',
    category: 'Computer Science',
    description: 'Data Structures and Algorithms analysis, asymptotic complexity, and memory management.',
    relatedSkills: ['Algorithms', 'Python', 'Java', 'C++', 'OOP'],
  },
  {
    name: 'Algorithms',
    category: 'Computer Science',
    description: 'Design and analysis of efficient algorithms (graphs, dynamic programming).',
    relatedSkills: ['DSA', 'Python', 'C++', 'Java'],
  },
  {
    name: 'Object-Oriented Programming',
    category: 'Computer Science',
    description: 'Programming paradigm based on objects, encapsulation, polymorphism, and inheritance.',
    relatedSkills: ['OOP', 'Java', 'C++', 'Python', 'C#'],
  },
  {
    name: 'OOP',
    category: 'Computer Science',
    description: 'Object-Oriented Programming design principles (SOLID, design patterns).',
    relatedSkills: ['Object-Oriented Programming', 'Java', 'C++', 'Python'],
  },
  {
    name: 'System Design',
    category: 'Computer Science',
    description: 'Architecture of scalable distributed systems, caching, load balancing, and partitioning.',
    relatedSkills: ['Microservices', 'REST API', 'SQL & PostgreSQL', 'Docker', 'Redis'],
  },
  {
    name: 'Linux',
    category: 'Computer Science',
    description: 'Unix-like operating system, shell scripting, process management, and networking.',
    relatedSkills: ['Git', 'Docker', 'CI/CD', 'Systems Programming'],
  },
];

/**
 * Get dynamic smart suggestions for a list of currently selected skills.
 */
export function getSuggestedSkillsForSelected(selectedSkills: string[]): string[] {
  const selectedLower = new Set(selectedSkills.map(s => s.toLowerCase()));
  const suggestionsSet = new Set<string>();

  // Find related skills for each selected skill
  selectedSkills.forEach(selectedName => {
    const item = CANONICAL_SKILL_CATALOGUE.find(
      c => c.name.toLowerCase() === selectedName.toLowerCase()
    );
    if (item && item.relatedSkills) {
      item.relatedSkills.forEach(rel => {
        if (!selectedLower.has(rel.toLowerCase())) {
          suggestionsSet.add(rel);
        }
      });
    }
  });

  // If few or no suggestions found, provide top popular skills
  if (suggestionsSet.size < 6) {
    const popularDefaults = [
      'Python', 'Machine Learning', 'FastAPI', 'React', 'SQL & PostgreSQL',
      'TypeScript', 'Docker', 'Data Science', 'Deep Learning', 'REST API', 'DSA', 'Java'
    ];
    popularDefaults.forEach(defSkill => {
      if (!selectedLower.has(defSkill.toLowerCase())) {
        suggestionsSet.add(defSkill);
      }
    });
  }

  return Array.from(suggestionsSet).slice(0, 12);
}
