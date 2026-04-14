
# Assignment week 1
Create a web application to display comic book library. 
Dataset can be found on Moodle.
Think about the architecture and decisions must be made!
Use:
* Docker containers (all local for now)
* GitHub repo (shared with wiley.finch@inholland.nl and micha.vandermeer@inholland.nl )
* TDD (Test Driven Development)
* Store secrets save?
* RBAC (Role Based Access Control) behind login. 
* “super admin” -> can create only “admin”s
* “admin” -> can create other users except “super admin”s and can add, change and delete comics
* “friends” -> can see the comics
* visitors without login can not see anything



# starting application
docker compose up --build

# closing application
docker compose down

# Stack:
Frontend: Vue.js (version 3)
Backend: Python (flask)
Database: MySQL with phpMyAdmin for local management
All services run in Docker containers via Docker Compose (local only, no cloud for now)


# Security practices used

Secrets (DB passwords, JWT secret, etc.) must be stored safely — use a .env file, never hardcoded, never committed to Git
Passwords must be hashed (bcrypt)
Authentication via JWT tokens stored in httpOnly cookies (not localStorage)
Input validation and sanitization on all forms (prevent SQL injection and XSS)
RBAC enforced server-side, not just in the frontend
.env listed in .gitignore from day one


## ToDo
- instead of user id -> UUID 
- password ratelimiting
- not every feature of the assignment is working yet / implemented feel free to check out what is not working / implemented yet
- keep security in mind when implementing sth
- secure the endppoints so a user who is not logged in cannot do /comics 







 

  



