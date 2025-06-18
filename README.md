📸 Instagram Clone – A Full-Featured Social Media Platform
Built with Django, Python & Modern Web Technologies
##### Some features are to be finished or implemented as this project is in development mode!

🚀 Deployed with Docker | Scalable ASGI (Daphne) | PostgreSQL Powered

🌟 Key Features

👤 User Management

✔ Secure Authentication

Registration, Login, Logout

JWT & Session-Based Auth

🔐 Email Verification (Account Activation + Password Reset)

🌐 Social Login Integration

Google & Facebook (via django-allauth)

Custom AccountAdapter for OAuth workflows

📝 Profile System

Custom AbstractUser model with extended fields

CRUD for profiles (Bio, Profile Pic, Links)

📷 Post & Content Features

🖼️ Post Management

Image/Video Uploads 

CRUD Operations for Posts

🏷️ Tagging System (Many-to-Many Relations)

🔍 Discovery & Search

Filter by Categories/Tags

Full-Text Search (Post Captions, User Bios) -- in progress

Infinite Scroll/Pagination

💬 Engagement

Comments & Replies 

Likes/Dislikes

Bookmarks -- in progress

User chats using WebSockets

⚙️ Admin & Moderation

👑 Jazzmin-Powered Admin Panel

Modern UI with Dark Mode -- in progress

Analytics Dashboard

🛡️ Moderation Tools

Post Flagging/Deletion

User Banning & Shadow Banning -- in progress

⚡ Advanced Technical Highlights

🔧 Backend
Custom User Model (AbstractUser + UserManager)

Django Signals for Real-Time Actions (e.g., Notifications)

Celery Tasks for Async Email/SMS Alerts


🗃️ Database & Performance

PostgreSQL for Scalability

Redis for Caching & Real-Time Features

Optimized Queries (select_related, prefetch_related) 


🎨 Frontend

Crispy Forms + Bootstrap 5 (Sleek, Responsive UI)

Django Templates for Dynamic Interactions

Light/Dark Mode Toggle -- in progress

🛠️ Tech Stack

Category	Technologies/Libraries

Backend	Django, Python, Celery, Daphne

Database	PostgreSQL, Redis

Auth	AllAuth, Social Auth, JWT

UI/UX	Bootstrap 5, Crispy Forms, JavaScript

DevOps	Docker, Gunicorn

Admin	Jazzmin, Django Admin


🚀 Why This Project Stands Out

✅ Production-Ready Architecture (ASGI, Dockerized)

✅ Modern Social Features (OAuth, Notifications)

✅ Optimized for Scale (Caching, Async Tasks)

✅ Developer-Friendly (Custom Signals, Clean Code)

📥 Get Started
```
git clone [your-repo-url]  
cd instagram-clone  
poetry install  
python manage.py runserver  

```

Live Demo: 