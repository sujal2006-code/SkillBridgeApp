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
from app.models.professional_role import StudentProfessionalProfile
from app.core.security import hash_password


DEMO_COMMON_PASSWORD_HASH = hash_password("skillbridge2026")

DEMO_INDIAN_STUDENTS_DATA = [
    {
        "name": "Aarav Sharma",
        "email": "aarav.sharma@skillbridge.edu",
        "university": "IIT Delhi (AI & ML)",
        "graduation_year": 2026,
        "skills": [
            {"name": "Python", "level": "Advanced", "status": "verified"},
            {"name": "PyTorch", "level": "Advanced", "status": "verified"},
            {"name": "Machine Learning", "level": "Advanced", "status": "verified"},
            {"name": "Deep Learning", "level": "Intermediate", "status": "verified"},
            {"name": "Scikit-learn", "level": "Intermediate", "status": "verified"},
            {"name": "Git", "level": "Intermediate", "status": "verified"},
            {"name": "Generative AI", "level": "Intermediate", "status": "verified"},
        ],
        "evidence": [
            {
                "type": "project",
                "title": "Autonomous Healthcare Diagnostic Assistant using Vision-Language Models",
                "description": "Engineered a multimodal diagnostic assistant leveraging vision-language models and PyTorch for clinical CT scans with 94.2% accuracy.",
                "issuer": "IIT Delhi AI Research Lab",
                "status": "verified",
                "url": "https://github.com/aarav-sharma/health-vlm",
                "skills": ["Python", "Deep Learning", "PyTorch", "Machine Learning"],
            },
            {
                "type": "competition",
                "title": "Winner - Smart India Hackathon (SIH) 2025 AI Track",
                "description": "Secured 1st place among 450+ teams developing real-time edge AI pest detection for Indian agrarian supply chains.",
                "issuer": "Ministry of Education & AICTE",
                "status": "verified",
                "url": "https://sih.gov.in/certificates/2025/aarav-sharma",
                "skills": ["Machine Learning", "Python", "Scikit-learn"],
            },
            {
                "type": "certificate",
                "title": "Deep Learning Specialization by Andrew Ng",
                "description": "Completed 5-course sequence covering convolutional networks, sequence models, transformers, and hyperparameter tuning.",
                "issuer": "DeepLearning.AI / Coursera",
                "status": "verified",
                "url": "https://coursera.org/verify/DL-AARAV-2025",
                "skills": ["Deep Learning", "PyTorch", "Python"],
            },
            {
                "type": "project",
                "title": "Multi-Agent Research Assistant using LLM Tool Calling",
                "description": "Autonomous literature review orchestrator performing query decomposition, vector search, and citation synthesis.",
                "issuer": "Personal Open Source Project",
                "status": "pending",
                "url": "https://github.com/aarav-sharma/agentic-researcher",
                "skills": ["Generative AI", "Python"],
            },
        ],
    },
    {
        "name": "Aditya Mishra",
        "email": "aditya.mishra@skillbridge.edu",
        "university": "IIT Bombay (CSE)",
        "graduation_year": 2026,
        "skills": [
            {"name": "React", "level": "Advanced", "status": "verified"},
            {"name": "TypeScript", "level": "Advanced", "status": "verified"},
            {"name": "Node.js", "level": "Advanced", "status": "verified"},
            {"name": "Next.js", "level": "Intermediate", "status": "verified"},
            {"name": "PostgreSQL", "level": "Intermediate", "status": "verified"},
            {"name": "Docker", "level": "Intermediate", "status": "verified"},
            {"name": "Tailwind CSS", "level": "Advanced", "status": "verified"},
        ],
        "evidence": [
            {
                "type": "project",
                "title": "AgroConnect: Direct Farmer-to-Consumer Agricultural Marketplace",
                "description": "Constructed full-stack e-commerce marketplace featuring real-time bidding, multilingual UI, and optimized PostgreSQL indexing.",
                "issuer": "IIT Bombay Techfest",
                "status": "verified",
                "url": "https://github.com/aditya-mishra/agro-connect",
                "skills": ["React", "TypeScript", "Node.js", "Tailwind CSS", "PostgreSQL"],
            },
            {
                "type": "certificate",
                "title": "Meta Certified Full-Stack Developer Professional Certificate",
                "description": "Comprehensive industry certification covering React architectures, Node.js microservices, and modern web application security.",
                "issuer": "Meta / Coursera",
                "status": "verified",
                "url": "https://coursera.org/verify/META-ADITYA-2025",
                "skills": ["React", "Node.js", "TypeScript"],
            },
            {
                "type": "internship",
                "title": "Software Engineering Intern at Udaan",
                "description": "Built resilient buyer checkout microservices handling 20,000+ daily orders with Node.js and TypeScript.",
                "issuer": "Udaan B2B E-Commerce",
                "status": "verified",
                "url": "https://credentials.udaan.com/interns/2025/aditya",
                "skills": ["Node.js", "TypeScript", "Docker"],
            },
            {
                "type": "project",
                "title": "Real-Time Collaborative Code Editor with WebSockets & CRDTs",
                "description": "Zero-latency in-browser collaborative code editor powered by Yjs CRDTs and WebSockets.",
                "issuer": "HackIITB 2026",
                "status": "pending",
                "url": "https://github.com/aditya-mishra/collab-code",
                "skills": ["TypeScript", "React", "Node.js"],
            },
        ],
    },
    {
        "name": "Rohan Das",
        "email": "rohan.das@skillbridge.edu",
        "university": "NIT Rourkela (IT)",
        "graduation_year": 2027,
        "skills": [
            {"name": "Python", "level": "Advanced", "status": "verified"},
            {"name": "FastAPI", "level": "Advanced", "status": "verified"},
            {"name": "SQL & PostgreSQL", "level": "Advanced", "status": "verified"},
            {"name": "Redis", "level": "Intermediate", "status": "verified"},
            {"name": "Docker", "level": "Intermediate", "status": "verified"},
            {"name": "RESTful API Design", "level": "Advanced", "status": "verified"},
            {"name": "Microservices", "level": "Intermediate", "status": "verified"},
        ],
        "evidence": [
            {
                "type": "project",
                "title": "Scalable Microservices Payment Gateway with Idempotency & Rate Limiting",
                "description": "Architected asynchronous REST microservices processing 5,000 req/sec with Redis sliding-window rate limiting and PostgreSQL transactions.",
                "issuer": "NIT Rourkela Hackathon",
                "status": "verified",
                "url": "https://github.com/rohan-das/paybridge-core",
                "skills": ["FastAPI", "Python", "SQL & PostgreSQL", "Redis", "RESTful API Design"],
            },
            {
                "type": "certificate",
                "title": "AWS Certified Developer – Associate",
                "description": "Validated expertise in provisioning serverless ECS containers, API Gateways, and RDS Aurora databases.",
                "issuer": "Amazon Web Services (AWS)",
                "status": "verified",
                "url": "https://aws.amazon.com/verification/AWS-ROH-2025-DEV",
                "skills": ["Docker", "Microservices", "RESTful API Design"],
            },
            {
                "type": "competition",
                "title": "Finalist - Flipkart GRiD 6.0 Software Development Challenge",
                "description": "Designed resilient distributed lock manager and high-throughput warehouse dispatch algorithm.",
                "issuer": "Flipkart Tech",
                "status": "verified",
                "url": "https://unstop.com/certificates/grid6-rohan-das",
                "skills": ["FastAPI", "Python", "Microservices"],
            },
        ],
    },
    {
        "name": "Arjun Patel",
        "email": "arjun.patel@skillbridge.edu",
        "university": "BITS Pilani (ECE)",
        "graduation_year": 2026,
        "skills": [
            {"name": "C++", "level": "Advanced", "status": "verified"},
            {"name": "Python", "level": "Intermediate", "status": "verified"},
            {"name": "Computer Vision", "level": "Advanced", "status": "verified"},
            {"name": "Deep Learning", "level": "Intermediate", "status": "verified"},
            {"name": "Linux", "level": "Advanced", "status": "verified"},
            {"name": "DSA", "level": "Advanced", "status": "verified"},
        ],
        "evidence": [
            {
                "type": "project",
                "title": "Edge Vision: Real-Time Traffic Density & License Plate Detection on Jetson Nano",
                "description": "Implemented CUDA-accelerated OpenCV and TensorRT pipeline performing 60 FPS multi-lane vehicle tracking and OCR.",
                "issuer": "BITS Pilani Center for AI & Robotics",
                "status": "verified",
                "url": "https://github.com/arjun-patel/edge-traffic-ai",
                "skills": ["C++", "Computer Vision", "Python", "Linux"],
            },
            {
                "type": "competition",
                "title": "Top 3 Podium - IEEE Robotics & Automation Challenge",
                "description": "Engineered autonomous robotic ground vehicle SLAM and LiDAR obstacle mapping system.",
                "issuer": "IEEE Robotics & Automation Society",
                "status": "verified",
                "url": "https://ieee.org/awards/bits-arjun-2025",
                "skills": ["C++", "Linux", "Computer Vision", "DSA"],
            },
            {
                "type": "certificate",
                "title": "Computer Vision with OpenCV and PyTorch",
                "description": "Advanced specialization on YOLO architectures, semantic segmentation, and real-time visual odometry.",
                "issuer": "OpenCV.org & PyImageSearch",
                "status": "verified",
                "url": "https://opencv.org/verify/CV-ARJUN-PATEL-88",
                "skills": ["Computer Vision", "Deep Learning"],
            },
        ],
    },
    {
        "name": "Ananya Singh",
        "email": "ananya.singh@skillbridge.edu",
        "university": "IIT Kharagpur (Data Science)",
        "graduation_year": 2027,
        "skills": [
            {"name": "Python", "level": "Advanced", "status": "verified"},
            {"name": "Data Science", "level": "Advanced", "status": "verified"},
            {"name": "Pandas", "level": "Advanced", "status": "verified"},
            {"name": "Natural Language Processing", "level": "Intermediate", "status": "verified"},
            {"name": "NLP", "level": "Intermediate", "status": "verified"},
            {"name": "SQL", "level": "Advanced", "status": "verified"},
            {"name": "Data Visualization", "level": "Intermediate", "status": "verified"},
        ],
        "evidence": [
            {
                "type": "project",
                "title": "IndicSentiment: Multilingual Sentiment Analysis across 10 Indian Regional Languages",
                "description": "Constructed fine-tuned transformer pipeline achieving 91.8% F1-score across Hindi, Bengali, Tamil, Telugu, and Odia corpora.",
                "issuer": "IIT Kharagpur AI Research Group",
                "status": "verified",
                "url": "https://github.com/ananya-singh/indic-sentiment-nlp",
                "skills": ["Python", "NLP", "Natural Language Processing", "Pandas", "Data Science"],
            },
            {
                "type": "competition",
                "title": "Winner - Kaggle Community Hackathon: Indian Financial Insights",
                "description": "Ranked 1st on leaderboard predicting MSME credit delinquency from unstructured banking transaction statements.",
                "issuer": "Kaggle / Google",
                "status": "verified",
                "url": "https://kaggle.com/certificates/ananyasingh-gold",
                "skills": ["Data Science", "Python", "Pandas", "SQL"],
            },
            {
                "type": "certificate",
                "title": "IBM Certified Data Scientist Professional",
                "description": "Comprehensive credential demonstrating mastery in SQL data querying, statistical modeling, and data storytelling.",
                "issuer": "IBM / Coursera",
                "status": "verified",
                "url": "https://coursera.org/verify/IBM-DS-ANANYA-2025",
                "skills": ["Data Science", "SQL", "Data Visualization", "Pandas"],
            },
        ],
    },
    {
        "name": "Priya Nair",
        "email": "priya.nair@skillbridge.edu",
        "university": "NIT Calicut (CSE)",
        "graduation_year": 2026,
        "skills": [
            {"name": "React", "level": "Advanced", "status": "verified"},
            {"name": "Next.js", "level": "Advanced", "status": "verified"},
            {"name": "TypeScript", "level": "Intermediate", "status": "verified"},
            {"name": "Tailwind CSS", "level": "Advanced", "status": "verified"},
            {"name": "HTML", "level": "Advanced", "status": "verified"},
            {"name": "CSS", "level": "Advanced", "status": "verified"},
            {"name": "JavaScript", "level": "Advanced", "status": "verified"},
        ],
        "evidence": [
            {
                "type": "project",
                "title": "Kerala Heritage Tourism Portal: Dynamic Interactive Web Experience",
                "description": "Architected accessible, high-performance web experience with Next.js App Router, SSR, and custom Tailwind design system.",
                "issuer": "Kerala Tourism Dept & NITC Hackathon",
                "status": "verified",
                "url": "https://github.com/priya-nair/kerala-heritage-web",
                "skills": ["Next.js", "React", "Tailwind CSS", "TypeScript", "HTML", "CSS"],
            },
            {
                "type": "certificate",
                "title": "Frontend Masters - Advanced Web Performance & React Architecture",
                "description": "Mastery in Lighthouse 100/100 optimization, bundle splitting, React Server Components, and Web Vitals.",
                "issuer": "Frontend Masters",
                "status": "verified",
                "url": "https://frontendmasters.com/certificates/priya-nair-adv-react",
                "skills": ["React", "Next.js", "JavaScript"],
            },
            {
                "type": "competition",
                "title": "1st Place - Devfolio Modern Web Sprint",
                "description": "Designed award-winning responsive accessibility-first medical triage UI.",
                "issuer": "Devfolio Community",
                "status": "verified",
                "url": "https://devfolio.co/submissions/priya-nair-portfolio-92",
                "skills": ["React", "TypeScript", "CSS"],
            },
        ],
    },
    {
        "name": "Sneha Das",
        "email": "sneha.das@skillbridge.edu",
        "university": "Jadavpur University (IT)",
        "graduation_year": 2026,
        "skills": [
            {"name": "Docker", "level": "Advanced", "status": "verified"},
            {"name": "Kubernetes", "level": "Intermediate", "status": "verified"},
            {"name": "AWS", "level": "Advanced", "status": "verified"},
            {"name": "CI/CD", "level": "Advanced", "status": "verified"},
            {"name": "Git", "level": "Advanced", "status": "verified"},
            {"name": "Linux", "level": "Advanced", "status": "verified"},
            {"name": "GitHub", "level": "Advanced", "status": "verified"},
        ],
        "evidence": [
            {
                "type": "project",
                "title": "Zero-Downtime Multi-Region Canary Deployment Pipeline with GitHub Actions & ArgoCD",
                "description": "Created automated GitOps pipeline deploying microservices across multi-cluster Kubernetes with Prometheus canary analysis.",
                "issuer": "Jadavpur University Open Source Society",
                "status": "verified",
                "url": "https://github.com/sneha-das/canary-k8s-pipeline",
                "skills": ["CI/CD", "Docker", "Kubernetes", "AWS", "Git", "GitHub"],
            },
            {
                "type": "certificate",
                "title": "AWS Certified Solutions Architect – Associate",
                "description": "Validated architectural proficiency in high-availability VPCs, S3 data lifecycle, and multi-AZ failovers.",
                "issuer": "Amazon Web Services",
                "status": "verified",
                "url": "https://aws.amazon.com/verification/AWS-SNEHA-SAA-2025",
                "skills": ["AWS", "Docker", "Linux"],
            },
            {
                "type": "certificate",
                "title": "Certified Kubernetes Application Developer (CKAD)",
                "description": "CNCF certified competency in container networking, Helm charts, ingress controllers, and config secrets.",
                "issuer": "Cloud Native Computing Foundation (CNCF)",
                "status": "verified",
                "url": "https://cncf.io/verify/CKAD-SNEHA-DAS-449",
                "skills": ["Kubernetes", "Docker", "Linux"],
            },
        ],
    },
    {
        "name": "Kavya Sharma",
        "email": "kavya.sharma@skillbridge.edu",
        "university": "Delhi Technological University (DTU)",
        "graduation_year": 2027,
        "skills": [
            {"name": "Python", "level": "Intermediate", "status": "verified"},
            {"name": "Java", "level": "Intermediate", "status": "verified"},
            {"name": "SQL", "level": "Intermediate", "status": "verified"},
            {"name": "Linux", "level": "Advanced", "status": "verified"},
            {"name": "REST API", "level": "Intermediate", "status": "verified"},
            {"name": "DSA", "level": "Intermediate", "status": "verified"},
            {"name": "Git", "level": "Intermediate", "status": "verified"},
        ],
        "evidence": [
            {
                "type": "project",
                "title": "Automated API Vulnerability Scanner & OWASP Top 10 Security Auditing Harness",
                "description": "Built automated AST static analyzer and fuzz tester in Python identifying SQLi and SSRF in RESTful endpoints.",
                "issuer": "DTU Cyber Security Cell",
                "status": "verified",
                "url": "https://github.com/kavya-sharma/owasp-api-scanner",
                "skills": ["Python", "Linux", "REST API", "SQL"],
            },
            {
                "type": "certificate",
                "title": "CompTIA Security+ Certified",
                "description": "Validated expertise in network security fundamentals, threat modeling, and cryptographic protocols.",
                "issuer": "CompTIA",
                "status": "verified",
                "url": "https://comptia.org/verify/COMPTIA-KAVYA-SEC-2025",
                "skills": ["Linux", "SQL"],
            },
            {
                "type": "competition",
                "title": "Top 5 Finalist - Cyber Defense National CTF 2025",
                "description": "Solved complex reverse engineering and binary exploitation challenges under time constraints.",
                "issuer": "National Cyber Security Council",
                "status": "verified",
                "url": "https://nciipc.gov.in/ctf/kavya-sharma",
                "skills": ["Linux", "Python", "DSA"],
            },
        ],
    },
    {
        "name": "Rahul Kumar",
        "email": "rahul.kumar@skillbridge.edu",
        "university": "IIT Roorkee (Robotics & AI)",
        "graduation_year": 2026,
        "skills": [
            {"name": "Python", "level": "Advanced", "status": "verified"},
            {"name": "C++", "level": "Intermediate", "status": "verified"},
            {"name": "Computer Vision", "level": "Intermediate", "status": "verified"},
            {"name": "Machine Learning", "level": "Intermediate", "status": "verified"},
            {"name": "Linux", "level": "Intermediate", "status": "verified"},
            {"name": "Algorithms", "level": "Intermediate", "status": "verified"},
        ],
        "evidence": [
            {
                "type": "project",
                "title": "Autonomous Quadcopter Obstacle Avoidance using Monocular Vision & SLAM",
                "description": "Implemented real-time optical flow visual odometry and trajectory re-planning on drone hardware.",
                "issuer": "IIT Roorkee Robotics Club",
                "status": "verified",
                "url": "https://github.com/rahul-kumar/uav-obstacle-slam",
                "skills": ["Python", "Computer Vision", "C++", "Algorithms"],
            },
            {
                "type": "competition",
                "title": "Gold Medal - Inter-IIT Tech Meet 13.0 Autonomous Driving Challenge",
                "description": "Ranked 1st among all Indian Institutes of Technology in autonomous lane centering and dynamic obstacle overtaking.",
                "issuer": "Inter-IIT Council",
                "status": "verified",
                "url": "https://interiittech.org/certificates/2025/rahul-kumar-gold",
                "skills": ["Python", "Machine Learning", "Computer Vision"],
            },
            {
                "type": "certificate",
                "title": "Self-Driving Cars Specialization",
                "description": "Comprehensive 4-course sequence in state estimation, Kalman filters, visual perception, and motion planning.",
                "issuer": "University of Toronto / Coursera",
                "status": "verified",
                "url": "https://coursera.org/verify/TORONTO-SDC-RAHUL-2025",
                "skills": ["Python", "Algorithms", "Linux"],
            },
        ],
    },
    {
        "name": "Neha Sharma",
        "email": "neha.sharma@skillbridge.edu",
        "university": "Delhi Technological University (DTU)",
        "graduation_year": 2026,
        "skills": [
            {"name": "Linux", "level": "Advanced", "status": "verified"},
            {"name": "Git", "level": "Advanced", "status": "verified"},
            {"name": "Docker", "level": "Advanced", "status": "verified"},
            {"name": "CI/CD", "level": "Advanced", "status": "verified"},
            {"name": "AWS", "level": "Advanced", "status": "verified"},
            {"name": "Kubernetes", "level": "Intermediate", "status": "verified"},
            {"name": "Cloud", "level": "Advanced", "status": "verified"},
        ],
        "evidence": [
            {
                "type": "project",
                "title": "Automated Multi-Cluster CI/CD Pipeline & Zero-Downtime Deployment Engine",
                "description": "Constructed automated containerized deployment pipelines using Docker, GitHub Actions, Linux, and AWS ECS with automated health rollbacks.",
                "issuer": "DTU DevOps Center of Excellence",
                "status": "verified",
                "url": "https://github.com/neha-sharma/cloud-cicd-pipeline",
                "skills": ["Linux", "Git", "Docker", "CI/CD", "AWS"],
            },
            {
                "type": "certificate",
                "title": "AWS Certified Solutions Architect & SysOps Administrator",
                "description": "Industry certification validating secure cloud architecture, automated VPC networking, and resilient container clustering.",
                "issuer": "Amazon Web Services (AWS)",
                "status": "verified",
                "url": "https://aws.amazon.com/verification/AWS-NEHA-SHARMA-2025",
                "skills": ["AWS", "Cloud", "Docker", "Linux"],
            },
            {
                "type": "competition",
                "title": "Winner - National Cloud & DevOps Infrastructure Hackathon 2025",
                "description": "Designed resilient multi-region infrastructure as code with sub-minute deployment pipelines.",
                "issuer": "Cloud Native Computing Foundation (CNCF Chapter)",
                "status": "verified",
                "url": "https://cncf.io/community/hackathons/neha-sharma-2025",
                "skills": ["Docker", "CI/CD", "Linux", "Git"],
            },
        ],
    },
    {
        "name": "Abhishek Mohanty",
        "email": "abhishek.mohanty@skillbridge.edu",
        "university": "IIIT Bhubaneswar (CSE)",
        "graduation_year": 2026,
        "skills": [
            {"name": "Java", "level": "Advanced", "status": "verified"},
            {"name": "Spring Boot", "level": "Advanced", "status": "verified"},
            {"name": "SQL", "level": "Advanced", "status": "verified"},
            {"name": "Microservices", "level": "Intermediate", "status": "verified"},
            {"name": "Docker", "level": "Intermediate", "status": "verified"},
            {"name": "OOP", "level": "Advanced", "status": "verified"},
            {"name": "DSA", "level": "Advanced", "status": "verified"},
        ],
        "evidence": [
            {
                "type": "project",
                "title": "Odisha Transit: Real-Time High-Throughput Bus Fleet Tracking & Ticketing Engine",
                "description": "Constructed Spring Boot enterprise architecture with Kafka event streams and sub-10ms ticket validation.",
                "issuer": "IIIT Bhubaneswar Tech Innovation Hub",
                "status": "verified",
                "url": "https://github.com/abhishek-mohanty/odisha-transit-backend",
                "skills": ["Java", "Spring Boot", "SQL", "Microservices", "OOP"],
            },
            {
                "type": "certificate",
                "title": "Oracle Certified Professional: Java SE 17 Developer",
                "description": "Official Oracle credential validating advanced concurrency, modular architecture, and lambda streams.",
                "issuer": "Oracle University",
                "status": "verified",
                "url": "https://catalog-education.oracle.com/pls/certview/share/OCP-ABHISHEK-MOHANTY",
                "skills": ["Java", "OOP", "DSA"],
            },
            {
                "type": "internship",
                "title": "Java Backend Developer Intern at Infosys FinTech Lab",
                "description": "Maintained core banking ledger endpoints and refactored monolithic services into Spring Boot microservices.",
                "issuer": "Infosys Labs",
                "status": "verified",
                "url": "https://credentials.infosys.com/interns/abhishek-mohanty-2025",
                "skills": ["Java", "Spring Boot", "SQL", "Docker"],
            },
        ],
    },
    {
        "name": "Pooja Mishra",
        "email": "pooja.mishra@skillbridge.edu",
        "university": "VJTI Mumbai (AI & Data Science)",
        "graduation_year": 2027,
        "skills": [
            {"name": "Python", "level": "Advanced", "status": "verified"},
            {"name": "Generative AI", "level": "Advanced", "status": "verified"},
            {"name": "Large Language Models", "level": "Advanced", "status": "verified"},
            {"name": "FastAPI", "level": "Intermediate", "status": "verified"},
            {"name": "NLP", "level": "Intermediate", "status": "verified"},
            {"name": "PostgreSQL", "level": "Intermediate", "status": "verified"},
        ],
        "evidence": [
            {
                "type": "project",
                "title": "LegalEase India: Retrieval-Augmented Generation (RAG) over Indian Case Law & Statutes",
                "description": "Constructed hybrid vector-lexical search pipeline using pgvector and LangChain to answer complex Indian constitutional queries with citation grounding.",
                "issuer": "VJTI Mumbai Technovanza",
                "status": "verified",
                "url": "https://github.com/pooja-mishra/legalease-rag",
                "skills": ["Generative AI", "Large Language Models", "Python", "FastAPI", "PostgreSQL"],
            },
            {
                "type": "competition",
                "title": "Winner - GenAI Genesis Hackathon Mumbai 2025",
                "description": "Won 1st prize building low-latency localized voice AI assistant for regional Indian banking customers.",
                "issuer": "AWS & NVIDIA India",
                "status": "verified",
                "url": "https://aws.amazon.com/events/genai-hackathon/pooja-mishra",
                "skills": ["Generative AI", "Large Language Models", "Python", "NLP"],
            },
            {
                "type": "certificate",
                "title": "Generative AI with Large Language Models",
                "description": "Specialized training on PEFT, LoRA fine-tuning, RLHF alignment, and quantized inference architectures.",
                "issuer": "DeepLearning.AI / AWS",
                "status": "verified",
                "url": "https://coursera.org/verify/GENAI-POOJA-2025",
                "skills": ["Large Language Models", "NLP", "Generative AI"],
            },
        ],
    },
    {
        "name": "Saurav Behera",
        "email": "saurav.behera@skillbridge.edu",
        "university": "VSSUT Burla (ETC)",
        "graduation_year": 2026,
        "skills": [
            {"name": "Python", "level": "Intermediate", "status": "verified"},
            {"name": "SQL", "level": "Advanced", "status": "verified"},
            {"name": "Database Design", "level": "Advanced", "status": "verified"},
            {"name": "Data Analysis", "level": "Advanced", "status": "verified"},
            {"name": "PostgreSQL", "level": "Advanced", "status": "verified"},
            {"name": "Git", "level": "Intermediate", "status": "verified"},
            {"name": "Pandas", "level": "Intermediate", "status": "verified"},
        ],
        "evidence": [
            {
                "type": "project",
                "title": "Mahanadi Basin Water Resource Telemetry Data Warehouse & Analytics Engine",
                "description": "Designed partitioned PostgreSQL data lakehouse ingesting sensor feeds across 45 hydrological stations with automated ETL.",
                "issuer": "VSSUT Innovation & Incubation Cell",
                "status": "verified",
                "url": "https://github.com/saurav-behera/mahanadi-telemetry-dw",
                "skills": ["SQL", "Database Design", "PostgreSQL", "Python", "Data Analysis"],
            },
            {
                "type": "certificate",
                "title": "Google Data Analytics Professional Certificate",
                "description": "Demonstrated expertise in complex SQL joins, window functions, statistical data cleansing, and Tableau KPI dashboards.",
                "issuer": "Google / Coursera",
                "status": "verified",
                "url": "https://coursera.org/verify/GOOGLE-DA-SAURAV-2025",
                "skills": ["SQL", "Data Analysis", "Database Design", "Pandas"],
            },
            {
                "type": "competition",
                "title": "3rd Place - All Odisha Open Data Analytics Championship",
                "description": "Constructed automated predictive demand forecasting pipeline for municipal electricity distribution grids.",
                "issuer": "Odisha Big Data Forum",
                "status": "verified",
                "url": "https://odishadata.org/awards/saurav-behera-2025",
                "skills": ["Data Analysis", "Pandas", "SQL"],
            },
        ],
    },
    {
        "name": "Ishita Gupta",
        "email": "ishita.gupta@skillbridge.edu",
        "university": "IIIT Hyderabad (CSE)",
        "graduation_year": 2026,
        "skills": [
            {"name": "C++", "level": "Advanced", "status": "verified"},
            {"name": "DSA", "level": "Advanced", "status": "verified"},
            {"name": "Algorithms", "level": "Advanced", "status": "verified"},
            {"name": "Python", "level": "Intermediate", "status": "verified"},
            {"name": "System Design", "level": "Intermediate", "status": "verified"},
            {"name": "Linux", "level": "Intermediate", "status": "verified"},
            {"name": "Git", "level": "Intermediate", "status": "verified"},
        ],
        "evidence": [
            {
                "type": "competition",
                "title": "ICPC Asia-Amritapuri Regionalist (Rank 24)",
                "description": "Qualified for the ACM ICPC Regional contest solving algorithmic problems in dynamic programming, graph theory, and computational geometry.",
                "issuer": "ICPC Foundation",
                "status": "verified",
                "url": "https://icpc.global/regionals/amritapuri/ishita-gupta",
                "skills": ["C++", "DSA", "Algorithms"],
            },
            {
                "type": "project",
                "title": "High-Performance Lock-Free Concurrent Key-Value Store in C++20",
                "description": "Built lock-free cache with atomic CAS primitives, skip-list indexing, and benchmarked 1.8M operations/second under multi-core load.",
                "issuer": "IIIT Hyderabad Systems Research Center",
                "status": "verified",
                "url": "https://github.com/ishita-gupta/lockfree-kv-cpp",
                "skills": ["C++", "System Design", "Algorithms", "Linux"],
            },
            {
                "type": "certificate",
                "title": "Advanced Data Structures & Graph Algorithms",
                "description": "Scored Top 1% Gold Medal in national NPTEL examination on advanced combinatorial optimization.",
                "issuer": "IIIT Hyderabad / NPTEL",
                "status": "verified",
                "url": "https://nptel.ac.in/noc/Ecertificate/?q=NPTEL-ISHITA-DSA-2025",
                "skills": ["DSA", "Algorithms"],
            },
        ],
    },
    {
        "name": "Vivek Reddy",
        "email": "vivek.reddy@skillbridge.edu",
        "university": "NIT Warangal (CSE)",
        "graduation_year": 2027,
        "skills": [
            {"name": "Go", "level": "Advanced", "status": "verified"},
            {"name": "Docker", "level": "Advanced", "status": "verified"},
            {"name": "Kubernetes", "level": "Intermediate", "status": "verified"},
            {"name": "Microservices", "level": "Advanced", "status": "verified"},
            {"name": "RESTful API Design", "level": "Advanced", "status": "verified"},
            {"name": "Linux", "level": "Intermediate", "status": "verified"},
            {"name": "Git", "level": "Intermediate", "status": "verified"},
        ],
        "evidence": [
            {
                "type": "project",
                "title": "GopherMesh: Lightweight Service Discovery & Reverse Proxy in Golang",
                "description": "Implemented high-performance reverse proxy with Raft consensus, health checking, and dynamic round-robin routing.",
                "issuer": "NIT Warangal Technozion",
                "status": "verified",
                "url": "https://github.com/vivek-reddy/gopher-mesh",
                "skills": ["Go", "Microservices", "RESTful API Design", "Docker", "Linux"],
            },
            {
                "type": "certificate",
                "title": "Certified Kubernetes Administrator (CKA)",
                "description": "Demonstrated competence in Kubernetes cluster architecture, network policies, storage classes, and cluster troubleshooting.",
                "issuer": "Linux Foundation & CNCF",
                "status": "verified",
                "url": "https://linuxfoundation.org/verify/CKA-VIVEK-REDDY-992",
                "skills": ["Kubernetes", "Docker", "Linux"],
            },
            {
                "type": "competition",
                "title": "Winner - Telangana State Open Source Hackathon 2025",
                "description": "Engineered low-resource containerized telemedicine data bridge for district clinics.",
                "issuer": "Telangana Information Technology Association",
                "status": "verified",
                "url": "https://tita.org.in/awards/vivek-reddy-2025",
                "skills": ["Go", "Microservices", "Docker"],
            },
        ],
    },
]


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

    # 1b. Safe schema migrations for existing databases
    try:
        inspector = inspect(engine)
        team_cols = [c["name"] for c in inspector.get_columns("teams")]
        if "project_name" not in team_cols:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE teams ADD COLUMN project_name VARCHAR;"))

        req_cols = [c["name"] for c in inspector.get_columns("team_skill_requirements")]
        if "domain" not in req_cols:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE team_skill_requirements ADD COLUMN domain VARCHAR;"))
    except Exception as e:
        print(f"[INFO] Schema migration check: {e}")

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

    # 4. Additive Seeding of 15 Indian Demo Student Profiles & Portfolios
    existing_students = {s.email.lower(): s for s in db.query(Student).all()}
    existing_students_by_name = {s.name.lower(): s for s in existing_students.values()}

    created_students = {}
    for s_data in DEMO_INDIAN_STUDENTS_DATA:
        name = s_data["name"]
        email = s_data["email"]

        st = existing_students.get(email.lower()) or existing_students_by_name.get(name.lower())
        if not st:
            st = Student(
                name=name,
                email=email,
                university=s_data["university"],
                graduation_year=s_data["graduation_year"],
                password_hash=DEMO_COMMON_PASSWORD_HASH,
                last_screen="dashboard",
            )
            db.add(st)
            db.flush()
            existing_students[email.lower()] = st
            existing_students_by_name[name.lower()] = st

        created_students[name] = st

        # Ensure verified skills
        existing_student_skills = {ss.skill_id for ss in db.query(StudentSkill).filter(StudentSkill.student_id == st.id).all()}
        for sk_item in s_data.get("skills", []):
            sk_obj = existing_skills.get(sk_item["name"].lower())
            if sk_obj and sk_obj.id not in existing_student_skills:
                st_skill = StudentSkill(
                    student_id=st.id,
                    skill_id=sk_obj.id,
                    proficiency_level=sk_item["level"],
                    verification_status=sk_item["status"],
                    verified_at=datetime.now(timezone.utc) if sk_item["status"] == "verified" else None,
                )
                db.add(st_skill)
                existing_student_skills.add(sk_obj.id)

        # Ensure evidence portfolio
        existing_ev_titles = {ev.title.lower() for ev in db.query(Evidence).filter(Evidence.student_id == st.id).all()}
        for ev_item in s_data.get("evidence", []):
            if ev_item["title"].lower() not in existing_ev_titles:
                primary_skill_name = ev_item["skills"][0] if ev_item.get("skills") else "Python"
                primary_skill = existing_skills.get(primary_skill_name.lower())

                ev = Evidence(
                    student_id=st.id,
                    skill_id=primary_skill.id if primary_skill else None,
                    evidence_type=ev_item["type"],
                    title=ev_item["title"],
                    description=ev_item["description"],
                    issuer=ev_item["issuer"],
                    verification_status=ev_item["status"],
                    evidence_url=ev_item.get("url"),
                )
                db.add(ev)
                db.flush()

                for sk_name in ev_item.get("skills", []):
                    sk_obj = existing_skills.get(sk_name.lower())
                    if sk_obj and sk_obj not in ev.skills:
                        ev.skills.append(sk_obj)

                existing_ev_titles.add(ev_item["title"].lower())

    # 5. Teams start completely clean (0 teams) so users experience clean initial state
    # No hardcoded demo teams seeded. Real persistent teams created by users via UI.

    # 6. Ensure legacy evidence rows have evidence_skills associations
    all_evidence = db.query(Evidence).options(joinedload(Evidence.skills)).all()
    for ev in all_evidence:
        if ev.skill_id and not ev.skills:
            sk = existing_skills.get(db.query(Skill.name).filter(Skill.id == ev.skill_id).scalar(), None)
            if not sk:
                sk = db.query(Skill).filter(Skill.id == ev.skill_id).first()
            if sk and sk not in ev.skills:
                ev.skills.append(sk)

    # 7. Seed or initialize professional profiles for students
    demo_roles_map = {
        "aarav.sharma@skillbridge.edu": ("AI/ML Developer", "AI & Machine Learning, Data Systems"),
        "aditya.mishra@skillbridge.edu": ("Full Stack Developer", "Frontend & UI, Backend Development"),
        "rohan.das@skillbridge.edu": ("Backend Developer", "Backend Development, Data Systems & Databases"),
        "arjun.patel@skillbridge.edu": ("AI/ML Developer", "AI & Machine Learning, Computer Vision"),
        "ananya.singh@skillbridge.edu": ("Data Scientist", "Data Systems & Databases, AI & Machine Learning"),
        "priya.nair@skillbridge.edu": ("Frontend Developer", "Frontend & UI, Web Performance"),
        "sneha.das@skillbridge.edu": ("DevOps & Cloud Engineer", "DevOps & Cloud, Backend Development"),
        "kavya.sharma@skillbridge.edu": ("Cybersecurity Developer", "Backend Development, Security"),
        "rahul.kumar@skillbridge.edu": ("AI/ML Developer", "AI & Machine Learning, Robotics"),
        "neha.sharma@skillbridge.edu": ("DevOps Engineer", "DevOps & Cloud, Cloud Infrastructure"),
        "abhishek.mohanty@skillbridge.edu": ("Backend Developer", "Backend Development, Enterprise Java"),
        "pooja.mishra@skillbridge.edu": ("AI/ML Developer", "Generative AI, Large Language Models"),
        "saurav.behera@skillbridge.edu": ("Data/Database Specialist", "Data Systems & Databases, Data Analysis"),
        "ishita.gupta@skillbridge.edu": ("Backend Developer", "Algorithms, Systems Engineering"),
        "vivek.reddy@skillbridge.edu": ("DevOps & Cloud Engineer", "DevOps & Cloud, Microservices"),
    }

    for st in db.query(Student).all():
        existing_prof = db.query(StudentProfessionalProfile).filter(StudentProfessionalProfile.student_id == st.id).first()
        if not existing_prof:
            default_role, default_specs = demo_roles_map.get(st.email.lower(), ("Full Stack Developer", "Frontend & UI, Backend Development"))
            db.add(StudentProfessionalProfile(
                student_id=st.id,
                primary_role=default_role,
                secondary_specializations=default_specs,
                bio=f"Verified student at {st.university}.",
            ))

    # Update existing demo teams with project names if missing
    for t in db.query(Team).all():
        if not t.project_name:
            if "AI" in t.name or "NLP" in t.name or "Vision" in t.name:
                t.project_name = "AI Student Platform"
            elif "Transit" in t.name or "Bharat" in t.name or "FinBridge" in t.name:
                t.project_name = "Rural FinTech & Transport Engine"
            else:
                t.project_name = f"{t.name} Collaborative Initiative"

    db.commit()


_db_initialized = False


def ensure_db_initialized(db: Session = None) -> None:
    """
    Thread-safe and serverless-safe database initializer.
    Guarantees that tables exist and canonical demo data is seeded
    even in environments (e.g. Vercel serverless) where ASGI lifespan is skipped.
    """
    global _db_initialized
    if _db_initialized:
        return

    from app.database.session import SessionLocal
    own_session = False
    if db is None:
        db = SessionLocal()
        own_session = True

    try:
        init_db(db)
        _db_initialized = True
    except Exception as e:
        print(f"[WARN] ensure_db_initialized error: {e}")
    finally:
        if own_session:
            db.close()
