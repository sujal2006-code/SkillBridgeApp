import os
import sys
from datetime import datetime, timezone

# Add backend directory to sys.path
backend_dir = os.path.abspath(os.path.dirname(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.database.session import SessionLocal, engine
from app.models.student import Student
from app.models.skill import Skill, StudentSkill
from app.models.evidence import Evidence, evidence_skills
from app.models.internship import Internship, InternshipSkill
from app.models.team import Team, TeamMember, TeamSkillRequirement, TeamInvitation
from app.models.activity import Activity
from app.models.match import Match
from app.core.security import hash_password
from app.database.init_db import init_db

COMMON_DEMO_PASSWORD = "skillbridge2026"
COMMON_PASSWORD_HASH = hash_password(COMMON_DEMO_PASSWORD)

DEMO_STUDENTS_DATA = [
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
        "name": "Neha Patel",
        "email": "neha.patel@skillbridge.edu",
        "university": "SVNIT Surat (Computer Engg)",
        "graduation_year": 2027,
        "skills": [
            {"name": "JavaScript", "level": "Advanced", "status": "verified"},
            {"name": "TypeScript", "level": "Intermediate", "status": "verified"},
            {"name": "React", "level": "Advanced", "status": "verified"},
            {"name": "HTML", "level": "Advanced", "status": "verified"},
            {"name": "CSS", "level": "Advanced", "status": "verified"},
            {"name": "REST API", "level": "Intermediate", "status": "verified"},
            {"name": "Git", "level": "Intermediate", "status": "verified"},
        ],
        "evidence": [
            {
                "type": "project",
                "title": "HealthTrack India: Offline-First Rural Telemedicine & Vaccination Tracker",
                "description": "Created progressive web app with IndexedDB offline sync and responsive UI for primary healthcare workers.",
                "issuer": "SVNIT Surat Innotech",
                "status": "verified",
                "url": "https://github.com/neha-patel/healthtrack-india",
                "skills": ["React", "JavaScript", "CSS", "HTML", "REST API"],
            },
            {
                "type": "competition",
                "title": "Runner Up - Google Solution Challenge (India Regional)",
                "description": "Developed maternal healthcare tracking web app addressing UN Sustainable Development Goals.",
                "issuer": "Google Developer Student Clubs",
                "status": "verified",
                "url": "https://developers.google.com/community/gdsc-solution-challenge/neha-patel",
                "skills": ["React", "TypeScript", "Git"],
            },
            {
                "type": "certificate",
                "title": "Modern React & TypeScript Full Guide",
                "description": "Advanced frontend engineering certification on state management, hooks, and clean component patterns.",
                "issuer": "Udemy / Academind",
                "status": "verified",
                "url": "https://udemy.com/certificate/UC-NEHA-REACT-2025",
                "skills": ["React", "JavaScript", "TypeScript"],
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

# Old placeholder demo accounts to cleanly remove from the active candidate pool
OLD_PLACEHOLDER_NAMES = [
    "alex rivera",
    "sarah chen",
    "marcus vance",
    "marcus young",
    "elena rostova",
    "priyansh sharma",
    "abc",
    "abe",
]


def seed_demo_accounts():
    db = SessionLocal()
    try:
        print("[1/5] Initializing tables and canonical skills catalog...")
        init_db(db)

        # 1. Clean up old placeholder demo students (preserving real user accounts like SujalSahu, Somadutta Sahu, Anshuman Khuntia)
        print("\n[2/5] Cleaning up old placeholder demo candidate accounts...")
        existing_students = db.query(Student).all()
        for st in existing_students:
            st_name_lower = st.name.strip().lower()
            st_email_lower = st.email.strip().lower()
            if (
                any(old_name in st_name_lower for old_name in OLD_PLACEHOLDER_NAMES)
                or "@stanford.edu" in st_email_lower
                or "@berkeley.edu" in st_email_lower
                or "@cmu.edu" in st_email_lower
                or "@gatech.edu" in st_email_lower
                or "@illinois.edu" in st_email_lower
            ):
                print(f" -> Removing old placeholder student: ID {st.id}, '{st.name}' ({st.email})")
                # Remove associated team memberships, activities, matches, evidence, skills
                db.query(Activity).filter(Activity.student_id == st.id).delete()
                db.query(Match).filter(Match.student_id == st.id).delete()
                db.query(TeamInvitation).filter((TeamInvitation.sender_id == st.id) | (TeamInvitation.recipient_id == st.id)).delete()
                db.query(TeamMember).filter(TeamMember.student_id == st.id).delete()
                db.query(Team).filter(Team.creator_id == st.id).delete()
                # Delete evidence & skills handled via cascade or explicit delete
                db.delete(st)

        db.commit()

        # 2. Build map of all canonical skills
        skills_map = {s.name.lower(): s for s in db.query(Skill).all()}

        # 3. Additive Seeding of the 15 Indian Demo Profiles
        print("\n[3/5] Seeding 15 Indian Demo Profiles...")
        created_or_found_students = {}

        for s_data in DEMO_STUDENTS_DATA:
            name = s_data["name"]
            email = s_data["email"]

            st = db.query(Student).filter((Student.email == email) | (Student.name == name)).first()
            if not st:
                st = Student(
                    name=name,
                    email=email,
                    university=s_data["university"],
                    graduation_year=s_data["graduation_year"],
                    password_hash=COMMON_PASSWORD_HASH,
                    last_screen="dashboard",
                )
                db.add(st)
                db.flush()
                print(f" + Created Student: ID {st.id} - '{st.name}' ({st.email}) at {st.university}")
            else:
                st.university = s_data["university"]
                st.graduation_year = s_data["graduation_year"]
                st.password_hash = COMMON_PASSWORD_HASH
                print(f" = Updated Student: ID {st.id} - '{st.name}' ({st.email})")

            created_or_found_students[name] = st

            # Seed Skills
            existing_skill_ids = {ss.skill_id for ss in db.query(StudentSkill).filter(StudentSkill.student_id == st.id).all()}
            for sk_item in s_data.get("skills", []):
                sk_obj = skills_map.get(sk_item["name"].lower())
                if sk_obj and sk_obj.id not in existing_skill_ids:
                    st_skill = StudentSkill(
                        student_id=st.id,
                        skill_id=sk_obj.id,
                        proficiency_level=sk_item["level"],
                        verification_status=sk_item["status"],
                        verified_at=datetime.now(timezone.utc) if sk_item["status"] == "verified" else None,
                    )
                    db.add(st_skill)
                    existing_skill_ids.add(sk_obj.id)

            # Seed Evidence
            existing_ev_titles = {ev.title.lower() for ev in db.query(Evidence).filter(Evidence.student_id == st.id).all()}
            for ev_item in s_data.get("evidence", []):
                if ev_item["title"].lower() not in existing_ev_titles:
                    primary_skill_name = ev_item["skills"][0] if ev_item.get("skills") else "Python"
                    primary_skill = skills_map.get(primary_skill_name.lower())

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

                    # Attach multi-skill association
                    for sk_name in ev_item.get("skills", []):
                        sk_obj = skills_map.get(sk_name.lower())
                        if sk_obj and sk_obj not in ev.skills:
                            ev.skills.append(sk_obj)

                    existing_ev_titles.add(ev_item["title"].lower())

            # Seed Live Activity Feed Item
            has_activity = db.query(Activity).filter(Activity.student_id == st.id).first()
            if not has_activity:
                db.add(Activity(
                    student_id=st.id,
                    activity_type="verification",
                    title="Skill Passport Verified",
                    description=f"{s_data['skills'][0]['name']} & technical evidence verified by SkillBridge Protocol.",
                    icon="verified",
                    related_entity_type="student",
                    related_entity_id=st.id,
                    is_read=False,
                ))

        db.commit()

        # 4. Additive Seeding of Demo Hackathon Teams with Indian Student Leads & Gaps
        print("\n[4/5] Seeding Hackathon Teams & Requirements...")
        aarav = created_or_found_students.get("Aarav Sharma")
        aditya = created_or_found_students.get("Aditya Mishra")
        abhishek = created_or_found_students.get("Abhishek Mohanty")
        pooja = created_or_found_students.get("Pooja Mishra")
        rohan = created_or_found_students.get("Rohan Das")
        ananya = created_or_found_students.get("Ananya Singh")

        teams_to_seed = [
            {
                "name": "Bharat AI HealthTech",
                "description": "Building edge-AI and multimodal diagnostics for community healthcare centers across India.",
                "creator": aarav,
                "members": [
                    {"student": aarav, "role": "ML & AI Lead", "status": "joined"},
                    {"student": pooja, "role": "GenAI & RAG Specialist", "status": "joined"},
                ],
                "required_skills": [
                    {"skill_name": "Python", "level": "Advanced"},
                    {"skill_name": "Deep Learning", "level": "Intermediate"},
                    {"skill_name": "React", "level": "Intermediate"},
                    {"skill_name": "Cloud & Docker", "level": "Intermediate"},
                ],
            },
            {
                "name": "KisanSetu AgriPlatform",
                "description": "Decentralized fair-price agricultural marketplace with multilingual voice bidding for Indian farmers.",
                "creator": aditya,
                "members": [
                    {"student": aditya, "role": "Frontend & FullStack Lead", "status": "joined"},
                    {"student": ananya, "role": "NLP & Data Lead", "status": "joined"},
                    {"student": rohan, "role": "Backend Architect", "status": "joined"},
                ],
                "required_skills": [
                    {"skill_name": "React", "level": "Advanced"},
                    {"skill_name": "Node.js", "level": "Intermediate"},
                    {"skill_name": "Python", "level": "Intermediate"},
                    {"skill_name": "AWS", "level": "Intermediate"},
                ],
            },
            {
                "name": "FinBridge MicroBharat",
                "description": "High-throughput micro-credit and automated subsidy dispatch engine for MSMEs.",
                "creator": abhishek,
                "members": [
                    {"student": abhishek, "role": "Java Enterprise Lead", "status": "joined"},
                ],
                "required_skills": [
                    {"skill_name": "Java", "level": "Advanced"},
                    {"skill_name": "Spring Boot", "level": "Intermediate"},
                    {"skill_name": "SQL", "level": "Intermediate"},
                    {"skill_name": "Docker", "level": "Intermediate"},
                ],
            },
        ]

        for t_info in teams_to_seed:
            creator = t_info["creator"]
            if not creator:
                continue
            existing_team = db.query(Team).filter(Team.name == t_info["name"]).first()
            if not existing_team:
                new_team = Team(
                    name=t_info["name"],
                    description=t_info["description"],
                    creator_id=creator.id,
                )
                db.add(new_team)
                db.flush()
                print(f" + Created Team: ID {new_team.id} - '{new_team.name}' (Lead: {creator.name})")

                for m in t_info["members"]:
                    st_mem = m["student"]
                    if st_mem:
                        db.add(TeamMember(
                            team_id=new_team.id,
                            student_id=st_mem.id,
                            role=m["role"],
                            status=m["status"],
                            joined_at=datetime.now(timezone.utc),
                        ))

                for req in t_info["required_skills"]:
                    sk_obj = skills_map.get(req["skill_name"].lower())
                    if sk_obj:
                        db.add(TeamSkillRequirement(
                            team_id=new_team.id,
                            skill_id=sk_obj.id,
                            minimum_proficiency=req["level"],
                            required=True,
                        ))
            else:
                print(f" = Team exists: ID {existing_team.id} - '{existing_team.name}'")

        db.commit()

        # 5. Verification & Summary
        print("\n[5/5] Final Verification of Database Pool:")
        all_st = db.query(Student).all()
        print(f"Total Active Students in Database: {len(all_st)}")
        for st in all_st:
            ev_count = db.query(Evidence).filter(Evidence.student_id == st.id).count()
            sk_count = db.query(StudentSkill).filter(StudentSkill.student_id == st.id).count()
            print(f" - [{st.id}] {st.name} <{st.email}> | University: {st.university} | Skills: {sk_count}, Evidence: {ev_count}")

        teams_count = db.query(Team).count()
        print(f"\nTotal Teams in Database: {teams_count}")
        pending_ev = db.query(Evidence).filter(Evidence.verification_status == "pending").count()
        print(f"Total Pending Evidence in Admin Queue: {pending_ev}")
        print("\nSUCCESS: All 15 Indian Demo Profiles and Hackathon Teams are live and ready for demo!")

    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_accounts()
