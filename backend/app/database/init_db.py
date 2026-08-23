from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import inspect, text
from app.database.session import Base, engine
from app.models.student import Student
from app.models.skill import Skill, StudentSkill
from app.models.evidence import Evidence, evidence_skills
from app.models.internship import Internship, InternshipSkill
from app.models.match import Match
from app.models.team import Team, TeamMember, TeamSkillRequirement, TeamInvitation
from app.models.activity import Activity
from app.models.otp import OTP


CANONICAL_SKILLS_CATALOGUE = [
    # Programming
    {"name": "Python", "category": "Programming Languages", "description": "High-level programming language for AI, data science, and web development."},
    {"name": "Java", "category": "Programming Languages", "description": "Object-oriented, class-based programming language for enterprise and Android development."},
    {"name": "C", "category": "Programming Languages", "description": "Procedural systems programming language with low-level memory manipulation."},
    {"name": "C++", "category": "Programming Languages", "description": "High-performance object-oriented programming for systems, games, and high-throughput systems."},
    {"name": "C#", "category": "Programming Languages", "description": "Modern type-safe object-oriented language for .NET, enterprise, and game development."},
    {"name": "JavaScript", "category": "Programming Languages", "description": "High-level scripting language powering dynamic behavior on the web."},
    {"name": "TypeScript", "category": "Programming Languages", "description": "Strict syntactical superset of JavaScript adding static type definitions."},
    {"name": "Go", "category": "Programming Languages", "description": "Statically typed, compiled programming language designed at Google for concurrent systems."},
    {"name": "Rust", "category": "Programming Languages", "description": "Safe, concurrent, high-performance systems language with memory safety guarantees."},
    {"name": "Kotlin", "category": "Programming Languages", "description": "Modern cross-platform statically typed language for JVM and Android."},
    {"name": "Swift", "category": "Programming Languages", "description": "Powerful, intuitive language for iOS, macOS, watchOS, and tvOS development."},
    {"name": "PHP", "category": "Programming Languages", "description": "Server-side scripting language designed for web development."},
    
    # Web Development
    {"name": "HTML", "category": "Frontend Development", "description": "Standard markup language for documents designed to be displayed in a web browser."},
    {"name": "CSS", "category": "Frontend Development", "description": "Style sheet language used for describing the presentation of structured documents."},
    {"name": "React", "category": "Frontend Development", "description": "Component-based declarative JavaScript UI library for building reactive interfaces."},
    {"name": "Next.js", "category": "Frontend Development", "description": "Production React framework with hybrid static & server rendering and route optimization."},
    {"name": "Node.js", "category": "Web Development", "description": "Asynchronous event-driven JavaScript runtime environment for backend services."},
    {"name": "Express.js", "category": "Web Development", "description": "Minimal and flexible Node.js web application framework for robust APIs."},
    {"name": "Angular", "category": "Frontend Development", "description": "Component-based framework for building scalable web applications with TypeScript."},
    {"name": "Vue.js", "category": "Frontend Development", "description": "Progressive JavaScript framework for building user interfaces and single-page apps."},
    {"name": "Tailwind CSS", "category": "Frontend Development", "description": "Utility-first CSS framework for rapid modern UI development."},
    {"name": "Bootstrap", "category": "Frontend Development", "description": "Popular responsive CSS framework for mobile-first front-end web design."},

    # Backend / API
    {"name": "FastAPI", "category": "Backend Development", "description": "High-performance Python web framework for building modern REST APIs."},
    {"name": "Flask", "category": "Backend Development", "description": "Lightweight WSGI Python web application framework for microservices."},
    {"name": "Django", "category": "Backend Development", "description": "High-level Python web framework with batteries-included ORM and admin tools."},
    {"name": "Spring Boot", "category": "Backend Development", "description": "Enterprise Java framework for creating stand-alone, production-grade Spring applications."},
    {"name": "REST API", "category": "Backend Development", "description": "Architectural style for designing networked scalable web API services."},
    {"name": "RESTful API Design", "category": "Backend Development", "description": "Best practices for designing, documenting, and securing REST APIs."},
    {"name": "GraphQL", "category": "Backend Development", "description": "Query language for APIs and runtime for executing queries with existing data."},
    {"name": "Microservices", "category": "Backend Development", "description": "Architectural design pattern structuring an application as a collection of loose services."},

    # Databases
    {"name": "SQL", "category": "Databases", "description": "Standard declarative query language for relational database management systems."},
    {"name": "SQL & PostgreSQL", "category": "Databases", "description": "Relational database modeling, indexing, query optimization, and transaction management."},
    {"name": "PostgreSQL", "category": "Databases", "description": "Powerful open-source object-relational database system with advanced indexing."},
    {"name": "MySQL", "category": "Databases", "description": "Widely deployed open-source relational database management system."},
    {"name": "SQLite", "category": "Databases", "description": "Self-contained, serverless, zero-configuration embedded SQL database engine."},
    {"name": "MongoDB", "category": "Databases", "description": "Document-oriented NoSQL database system using JSON-like documents with dynamic schemas."},
    {"name": "Redis", "category": "Databases", "description": "In-memory data structure store used as a distributed database, cache, and message broker."},
    {"name": "Database Design", "category": "Databases", "description": "Entity-relationship modeling, normalization, indexing strategies, and schema migrations."},

    # AI / Machine Learning
    {"name": "Machine Learning", "category": "AI / Data Science", "description": "Applied ML, feature engineering, neural networks, and model evaluation."},
    {"name": "Artificial Intelligence", "category": "AI / Data Science", "description": "General AI principles, knowledge representation, heuristics, and intelligent agents."},
    {"name": "Deep Learning", "category": "AI / Data Science", "description": "Multi-layer neural network architectures, backpropagation, CNNs, and RNNs."},
    {"name": "Natural Language Processing", "category": "AI / Data Science", "description": "Computational linguistics, text tokenization, embeddings, and sentiment analysis."},
    {"name": "NLP", "category": "AI / Data Science", "description": "Natural Language Processing algorithms, transformers, and sequence modeling."},
    {"name": "Computer Vision", "category": "AI / Data Science", "description": "Image processing, object detection, segmentation, and convolutional neural networks."},
    {"name": "Generative AI", "category": "AI / Data Science", "description": "Foundation models, diffusion architectures, LLM prompting, and RAG architectures."},
    {"name": "Large Language Models", "category": "AI / Data Science", "description": "Transformer-based language models, fine-tuning, context window management, and inference."},
    {"name": "Data Science", "category": "AI / Data Science", "description": "Interdisciplinary field extracting knowledge from structured and unstructured data."},
    {"name": "TensorFlow", "category": "AI / Data Science", "description": "End-to-end open source platform for machine learning and deep neural networks."},
    {"name": "PyTorch", "category": "AI / Data Science", "description": "Optimized tensor library for deep learning using GPUs and CPUs with dynamic autograd."},
    {"name": "Scikit-learn", "category": "AI / Data Science", "description": "Simple and efficient tools for predictive data analysis and machine learning in Python."},
    {"name": "Keras", "category": "AI / Data Science", "description": "High-level neural networks API running on top of TensorFlow for fast prototyping."},

    # Data Analysis & Mathematics
    {"name": "NumPy", "category": "Data Analysis", "description": "Core library for scientific computing with Python, offering high-performance arrays."},
    {"name": "Pandas", "category": "Data Analysis", "description": "Fast, flexible data manipulation and analysis tool built on top of Python."},
    {"name": "Matplotlib", "category": "Data Analysis", "description": "Comprehensive library for creating static, animated, and interactive visualizations."},
    {"name": "Seaborn", "category": "Data Analysis", "description": "Statistical data visualization library based on matplotlib with attractive default styles."},
    {"name": "Data Visualization", "category": "Data Analysis", "description": "Graphical representation of information and data to communicate complex trends."},
    {"name": "Data Analysis", "category": "Data Analysis", "description": "Process of inspecting, cleansing, transforming, and modeling data to discover useful insights."},
    {"name": "Statistics", "category": "Data Analysis", "description": "Probability distributions, hypothesis testing, regression analysis, and statistical inference."},

    # Cloud & DevOps
    {"name": "Git", "category": "DevOps / Infrastructure", "description": "Distributed version control system for tracking changes in source code."},
    {"name": "GitHub", "category": "DevOps / Infrastructure", "description": "Cloud hosting platform for Git repositories with CI/CD GitHub Actions integration."},
    {"name": "Docker", "category": "DevOps / Infrastructure", "description": "OS-level virtualization delivering software in packages called containers."},
    {"name": "Cloud & Docker", "category": "DevOps / Infrastructure", "description": "Containerization, cloud deployments, and CI/CD pipelines."},
    {"name": "Kubernetes", "category": "DevOps / Infrastructure", "description": "Automated deployment, scaling, and management of containerized applications."},
    {"name": "AWS", "category": "DevOps / Infrastructure", "description": "Amazon Web Services cloud computing platform and distributed services."},
    {"name": "Azure", "category": "DevOps / Infrastructure", "description": "Microsoft Azure cloud services for building, testing, deploying, and managing applications."},
    {"name": "Google Cloud", "category": "DevOps / Infrastructure", "description": "Suite of cloud computing services that runs on Google infrastructure."},
    {"name": "CI/CD", "category": "DevOps / Infrastructure", "description": "Continuous Integration and Continuous Delivery automated build, test, and release pipelines."},

    # Computer Science Fundamentals
    {"name": "DSA", "category": "Computer Science", "description": "Data Structures and Algorithms analysis, asymptotic complexity, and memory management."},
    {"name": "Algorithms", "category": "Computer Science", "description": "Design and analysis of efficient algorithms (graph search, dynamic programming, divide & conquer)."},
    {"name": "Object-Oriented Programming", "category": "Computer Science", "description": "Programming paradigm based on concepts of objects, encapsulation, polymorphism, and inheritance."},
    {"name": "OOP", "category": "Computer Science", "description": "Object-Oriented Programming design principles (SOLID, design patterns, reusability)."},
    {"name": "System Design", "category": "Computer Science", "description": "Architecture of scalable distributed systems, caching, load balancing, and partitioning."},
    {"name": "Linux", "category": "Computer Science", "description": "Unix-like open source operating system, shell scripting, process management, and networking."},
]


EXPANDED_INTERNSHIPS_DATA = [
    # AI / ML
    {
        "title": "Machine Learning Intern",
        "company": "NeuroTech Innovations",
        "location": "Remote / San Francisco, CA",
        "description": "Join our core ML engineering team to build, train, and deploy predictive models, feature transformation pipelines, and evaluation harnesses.",
        "required_skills": ["Python", "Machine Learning", "PyTorch"],
        "preferred_skills": ["Scikit-learn", "NumPy", "Pandas", "Docker"],
    },
    {
        "title": "AI Engineer Intern",
        "company": "Synthetix AI Labs",
        "location": "San Francisco, CA (Hybrid)",
        "description": "Develop generative AI workflows, agentic reasoning pipelines, and LLM-assisted code generation tools using state-of-the-art architectures.",
        "required_skills": ["Python", "Generative AI", "Large Language Models"],
        "preferred_skills": ["FastAPI", "Docker", "PyTorch"],
    },
    {
        "title": "Data Science Intern",
        "company": "Apex Data Labs",
        "location": "Boston, MA (Hybrid)",
        "description": "Extract actionable predictive insights from high-velocity telemetry data using statistical modeling, Pandas, and machine learning pipelines.",
        "required_skills": ["Python", "Data Science", "Pandas", "SQL"],
        "preferred_skills": ["NumPy", "Matplotlib", "Scikit-learn"],
    },
    {
        "title": "NLP Intern",
        "company": "Linguistix Cognitive AI",
        "location": "Remote / New York, NY",
        "description": "Research and construct multi-lingual text extraction, fine-tuned transformer tokenizers, and sentiment classification systems.",
        "required_skills": ["Python", "NLP", "Machine Learning"],
        "preferred_skills": ["PyTorch", "Large Language Models", "FastAPI"],
    },
    {
        "title": "Computer Vision Intern",
        "company": "Visionary Robotics",
        "location": "Pittsburgh, PA",
        "description": "Implement real-time visual perception, semantic segmentation, and object detection for autonomous robotic systems.",
        "required_skills": ["Python", "Computer Vision", "Deep Learning"],
        "preferred_skills": ["PyTorch", "C++", "Docker"],
    },
    {
        "title": "Generative AI Intern",
        "company": "Creative Intelligence Labs",
        "location": "Seattle, WA (Remote)",
        "description": "Build high-throughput diffusion and LLM retrieval-augmented generation (RAG) microservices for creative applications.",
        "required_skills": ["Python", "Generative AI", "FastAPI"],
        "preferred_skills": ["Large Language Models", "PostgreSQL", "Docker"],
    },

    # Software Engineering
    {
        "title": "Backend Engineering Intern",
        "company": "CloudSphere Dynamics",
        "location": "Austin, TX (Remote)",
        "description": "Engineer high-concurrency microservices, robust REST APIs, and database persistence layers using modern asynchronous frameworks.",
        "required_skills": ["Python", "FastAPI", "SQL & PostgreSQL"],
        "preferred_skills": ["Docker", "Redis", "RESTful API Design"],
    },
    {
        "title": "Full-Stack Developer Intern",
        "company": "HyperScale Digital",
        "location": "New York, NY (Hybrid)",
        "description": "Help develop user-facing web applications, responsive component libraries, and end-to-end connected API services.",
        "required_skills": ["React", "TypeScript", "Node.js"],
        "preferred_skills": ["FastAPI", "SQL", "Tailwind CSS"],
    },
    {
        "title": "Frontend Developer Intern",
        "company": "PixelCraft Studio",
        "location": "Remote / Los Angeles, CA",
        "description": "Craft responsive, accessible, pixel-perfect user interfaces with React, Tailwind CSS, and modern interactive web technologies.",
        "required_skills": ["React", "JavaScript", "HTML", "CSS"],
        "preferred_skills": ["TypeScript", "Next.js", "Tailwind CSS"],
    },
    {
        "title": "Software Engineering Intern",
        "company": "Vanguard Systems",
        "location": "Chicago, IL",
        "description": "Work across core systems engineering, algorithm optimization, and automated testing pipelines for mission-critical services.",
        "required_skills": ["Python", "DSA", "Git"],
        "preferred_skills": ["C++", "Linux", "OOP"],
    },
    {
        "title": "Java Developer Intern",
        "company": "Enterprise Global FinTech",
        "location": "New York, NY",
        "description": "Develop and maintain robust enterprise banking microservices, transaction pipelines, and Spring Boot REST controllers.",
        "required_skills": ["Java", "Spring Boot", "SQL"],
        "preferred_skills": ["OOP", "DSA", "Docker"],
    },
    {
        "title": "Python Developer Intern",
        "company": "AutomateIQ",
        "location": "Remote / Denver, CO",
        "description": "Create automated scraping, data orchestration, and backend microservice pipelines using asynchronous Python.",
        "required_skills": ["Python", "FastAPI", "Git"],
        "preferred_skills": ["SQL", "Docker", "REST API"],
    },

    # Data Engineering & Analytics
    {
        "title": "Data Analyst Intern",
        "company": "Matrix Global Insights",
        "location": "Remote / Chicago, IL",
        "description": "Analyze complex business metrics, design executive KPI dashboards, and perform exploratory data analysis with SQL and Python.",
        "required_skills": ["SQL", "Python", "Data Analysis"],
        "preferred_skills": ["Pandas", "Data Visualization", "Statistics"],
    },
    {
        "title": "Data Engineering Intern",
        "company": "Pipeline Dynamics",
        "location": "San Jose, CA",
        "description": "Build high-volume streaming ETL pipelines, data lakehouse storage architectures, and automated schema validation tests.",
        "required_skills": ["Python", "SQL", "Database Design"],
        "preferred_skills": ["PostgreSQL", "Docker", "Git"],
    },
    {
        "title": "Business Intelligence Intern",
        "company": "Insightful Markets",
        "location": "Atlanta, GA (Hybrid)",
        "description": "Translate multidimensional operational data into actionable visual dashboards and statistical performance reports.",
        "required_skills": ["SQL", "Data Analysis", "Data Visualization"],
        "preferred_skills": ["Python", "Statistics", "Pandas"],
    },

    # Cloud & DevOps
    {
        "title": "Cloud Engineering Intern",
        "company": "SkyHigh Infrastructure",
        "location": "Seattle, WA",
        "description": "Provision, monitor, and optimize scalable cloud architecture, serverless execution layers, and multi-region storage systems.",
        "required_skills": ["AWS", "Docker", "Git"],
        "preferred_skills": ["CI/CD", "Linux", "Kubernetes"],
    },
    {
        "title": "DevOps Intern",
        "company": "Continuous Delivery Works",
        "location": "Remote / Austin, TX",
        "description": "Implement automated CI/CD deployment pipelines, container orchestration, and real-time infrastructure observability.",
        "required_skills": ["Docker", "Git", "GitHub"],
        "preferred_skills": ["Kubernetes", "CI/CD", "Linux", "AWS"],
    },
]


def init_db(db: Session) -> None:
    """Safely and additively create database tables and seed canonical skills and internships."""
    # 1. Additive table creation
    Base.metadata.create_all(bind=engine)

    # 2. Non-destructive Additive Seeding of Centralized Canonical Skills Catalogue
    existing_skills_list = db.query(Skill).all()
    existing_skills = {s.name.lower(): s for s in existing_skills_list}

    new_skills_to_add = []
    for s_data in CANONICAL_SKILLS_CATALOGUE:
        name_key = s_data["name"].lower()
        if name_key not in existing_skills:
            new_skill = Skill(
                name=s_data["name"],
                category=s_data["category"],
                description=s_data["description"]
            )
            new_skills_to_add.append(new_skill)

    if new_skills_to_add:
        db.add_all(new_skills_to_add)
        db.flush()
        for ns in new_skills_to_add:
            existing_skills[ns.name.lower()] = ns

    # 3. Additive Seeding of Expanded Internships
    existing_internships = {f"{it.title.lower()}::{it.company.lower()}": it for it in db.query(Internship).all()}

    new_internships_to_add = []
    for it_data in EXPANDED_INTERNSHIPS_DATA:
        it_key = f"{it_data['title'].lower()}::{it_data['company'].lower()}"
        if it_key not in existing_internships:
            new_it = Internship(
                title=it_data["title"],
                company=it_data["company"],
                location=it_data["location"],
                description=it_data["description"],
                required_skills=it_data["required_skills"],
                preferred_skills=it_data["preferred_skills"],
            )
            new_internships_to_add.append((new_it, it_data))
            db.add(new_it)

    if new_internships_to_add:
        db.flush()
        for new_it, it_data in new_internships_to_add:
            existing_internships[f"{it_data['title'].lower()}::{it_data['company'].lower()}"] = new_it
            for req_name in it_data["required_skills"]:
                if req_name.lower() in existing_skills:
                    sk = existing_skills[req_name.lower()]
                    db.add(InternshipSkill(
                        internship_id=new_it.id,
                        skill_id=sk.id,
                        required=True,
                        minimum_proficiency="Intermediate"
                    ))

            for pref_name in it_data["preferred_skills"]:
                if pref_name.lower() in existing_skills:
                    sk = existing_skills[pref_name.lower()]
                    db.add(InternshipSkill(
                        internship_id=new_it.id,
                        skill_id=sk.id,
                        required=False,
                        minimum_proficiency="Beginner"
                    ))

    # 4. Ensure legacy evidence rows have evidence_skills associations
    all_evidence = db.query(Evidence).options(joinedload(Evidence.skills)).all()
    for ev in all_evidence:
        if ev.skill_id and not ev.skills:
            sk = existing_skills.get(db.query(Skill.name).filter(Skill.id == ev.skill_id).scalar(), None)
            if not sk:
                sk = db.query(Skill).filter(Skill.id == ev.skill_id).first()
            if sk and sk not in ev.skills:
                ev.skills.append(sk)

    db.commit()
