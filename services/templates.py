"""
Email templates for each role, written around Sanket Lodhe's actual
background: 2+ years at CodeRize Technologies, Django/Angular/PostgreSQL
stack, real shipped projects, and AI integration experience.

Each template is honest, specific, and around 130-160 words so it's
easy to read without being a wall of text. Nothing is fabricated.

Structure:
    ROLE_DISPLAY_NAMES  - friendly label shown in the Telegram bot confirmation
    SUBJECT_TEMPLATES   - subject line per role
    TEMPLATES           - the actual email body per role
"""


ROLE_DISPLAY_NAMES = {
    "frontend": "Frontend Developer",
    "backend": "Backend Developer",
    "angular": "Angular Developer",
    "fullstack": "Full Stack Developer",
}


SUBJECT_TEMPLATES = {
    "frontend": "Frontend Developer Application - Sanket Lodhe",
    "backend": "Backend Developer Application - Sanket Lodhe",
    "angular": "Angular Developer Application - Sanket Lodhe",
    "fullstack": "Full Stack Developer Application - Sanket Lodhe",
}


TEMPLATES = {
    # Frontend template focuses on Angular, Angular Material, RxJS,
    # and the UI work done across real projects like GeoSphere and
    # the student enquiry portal.
    "frontend": (
        "Dear Hiring Manager,\n\n"
        "I'm reaching out to apply for the Frontend Developer position at your company.\n\n"
        "I'm a full-stack developer with 2+ years of experience, and a good chunk of that "
        "has been on the frontend side. I work primarily with Angular and TypeScript, and "
        "I'm comfortable with Angular Material, RxJS, Bootstrap, and building responsive "
        "UIs that hold up well under real usage.\n\n"
        "Some of the frontend work I'm most proud of includes building an interactive "
        "map-based interface for a missing person tracking application (Tracemapr.com) "
        "using Leaflet.js, and designing data visualization dashboards that improved "
        "reporting efficiency by 50% in a production environment.\n\n"
        "My resume is attached with more detail on my background and projects. "
        "I'd be glad to connect and talk through how I could contribute to your team.\n\n"
        "Thanks for your time,\n"
        "Sanket Lodhe\n"
        "sanketlodhe9923@gmail.com | +91 9923666493"
    ),

    # Backend template highlights Django REST Framework, FastAPI,
    # PostgreSQL, Redis, and the performance wins at CodeRize.
    "backend": (
        "Dear Hiring Manager,\n\n"
        "I'm writing to apply for the Backend Developer position at your company.\n\n"
        "I have 2+ years of experience building backend systems in Python, mainly with "
        "Django REST Framework and FastAPI. At CodeRize Technologies, I built and optimized "
        "backend services that handle 100K+ daily requests, cut API response times by 40%, "
        "and integrated Redis caching to improve performance across our applications.\n\n"
        "I've also worked on more complex backend challenges, like integrating Databricks "
        "for real-time air quality data processing in a geospatial analytics platform built "
        "for Abu Dhabi, and designing cross-referencing algorithms for a national missing "
        "person database. PostgreSQL is my primary database, and I'm comfortable with "
        "schema design, query optimization, and working with large datasets.\n\n"
        "Resume is attached. Happy to discuss further if my background looks like a fit.\n\n"
        "Thanks,\n"
        "Sanket Lodhe\n"
        "sanketlodhe9923@gmail.com | +91 9923666493"
    ),

    # Angular template is the most specific, pulling in GeoSphere,
    # the student portal, RxJS patterns, and lazy loading work.
    "angular": (
        "Dear Hiring Manager,\n\n"
        "I'm applying for the Angular Developer position at your company.\n\n"
        "Angular has been my primary frontend framework for the past 2+ years. I build "
        "with TypeScript, RxJS, Angular Material, and follow component-driven architecture "
        "with a focus on performance and maintainability.\n\n"
        "A few things I've built with Angular that I can speak to in detail: a real-time "
        "map interface using Leaflet.js for a missing person tracking system, an interactive "
        "financial dashboard with dynamic charts and multi-user support, a GIS-based student "
        "enquiry portal serving 1000+ institute locations with clustering and lazy loading, "
        "and a secure banking application with token-based authentication and multi-tenancy.\n\n"
        "I've also integrated Angular frontends with AI-powered backends using the ChatGPT "
        "API, so I'm comfortable working on more complex feature integrations as well.\n\n"
        "Resume is attached. Looking forward to hearing from you.\n\n"
        "Thanks,\n"
        "Sanket Lodhe\n"
        "sanketlodhe9923@gmail.com | +91 9923666493"
    ),

    # Fullstack template is the broadest, touching both sides of the
    # stack and mentioning AI integration as a differentiator.
    "fullstack": (
        "Dear Hiring Manager,\n\n"
        "I'm reaching out to apply for the Full Stack Developer position at your company.\n\n"
        "I'm a full-stack developer with 2+ years of experience working across Angular "
        "frontends and Python backends (Django REST Framework, FastAPI), with PostgreSQL "
        "and Redis on the data side. I've shipped production applications end to end, from "
        "schema design and API development to building the UI and deploying via CI/CD.\n\n"
        "At CodeRize Technologies, I've worked on a range of projects including a real-time "
        "missing person tracking platform (Tracemapr.com), a financial dashboard with "
        "end-to-end accounting modules, and a geospatial analytics system for environmental "
        "data in Abu Dhabi. I've also built AI-powered features integrating the ChatGPT API "
        "and Claude into production Django applications.\n\n"
        "I like owning features fully, across the stack, and I'm comfortable context-switching "
        "between frontend and backend as the work demands.\n\n"
        "Resume attached. I'd be happy to chat if my background looks relevant.\n\n"
        "Thanks,\n"
        "Sanket Lodhe\n"
        "sanketlodhe9923@gmail.com | +91 9923666493"
    ),
}