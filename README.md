# Udacity Full-stack Nanodegree Projects

Projects completed as part of the Udacity-FSND.

### Project 1: Booking Site Fyyur 

`projects/01_fyyur/`

Aim of the project was to build a full-stack Web App with Flask and Boostrap which enables
Venues & Artists to list themselves and arrange Shows together.

Used tech stack:
- `SQLAlchemy` as ORM library of choice
- `PostgreSQL` as database
- `Python3` and `Flask` for server language and framework
- `Flask-Migrate` for creating and running schema migrations
- Frontend: HTML, CSS, and Javascript with Bootstrap 3 (mainly provided by Udacity Team)

Applied concepts:
- How to use Git Bash & Github as version control tool
- Configure local database and connect it to a web application
- Create Model Schemas with columns and relationships (1:1, 1:n and N:N)
- Use SQLAlchemy ORM with PostgreSQL to query, insert, edit & delete Data
- Use WTForms to encapsulate input forms in seperate file & to allow for custom validations
- Use Boostrap as a simple to use Front End Libary and Ajax to fetch flask routes
- Create SQL-like Queries, but without any SQL syntax, only using SQLAlchemy ORM
- How to clearly structurize a larger web application in different files & folders

### Project 2: Trivia API

`projects/02_trivia_api/`

Using 'Flask' and 'React', created a Full-Stack App to manage questions
for different categories & develop an API to power the Quiz Gameplay. Frontend was mostly boilerplate/provided by Udacity.

Used tech stack:
- React Components as frontend (provided by Udacity Team)
- Python3 and Flask for server language and API development
- `cors` to handle access to the API
- `unittest` for automated testing of APIs
- `README.md` to document project setup & API endpoints

Applied concepts:
- `test-driven-development (TDD)` to rapidly create highly tested & maintainable endpoints.
- directly test and make response to any endpoint out there with `curl` (or `http` in most cases...).
- implement `errorhandler` to format & design appropiate error messages to client

### Project 3: Coffee Shop (Security & Authorization)

`projects/03_coffee_shop_full_stack/`

Using 'Flask' and 'Auth0', created a Full-Stack App to let Users
login to Site & make actions according to their Role & Permission Sets.

Used tech stack:
- `Python3` & `Flask` for server language and API development 
- `SQLAlchemy` as ORM / `Sqlite` as database
- `Ionic` to serve and build the frontend (provided by Udacity Team)
- `Auth0` as external Authorization Service & permission creation
- `jose` JavaScript Object Signing and Encryption for JWTs. Useful for encoding, decoding, and verifying JWTs.
- `postman` to automatize endpoint testing & verification of correct Authorization behaviour.

### Project 4: Server Deployment, Containerization and Testing

`projects/04_docker_k8s_deploy`

Deployed a Flask API to a Kubernetes cluster using Docker, AWS EKS, CodePipeline, and CodeBuild. Immediately shut it down because it cost $50 to get up and running for < 1 day (bunch of failed deploys due to bad CloudFormation template).

Used tech stack:
- `Docker` for app containerization & image creation to ensure environment consistency across development and production server
- `AWS EKS` & `Kubernetes` as container orchestration service to allow for horizontal scaling
- `aswscli` to interact with AWS Cloud Services
- `ekscli` for EKS cluster creation
- `kubectl` to interact with kubernetes cluster & pods
- `CodePipeline` for Continuous Delivery (CD) & to watch Github Repo for changes
- `CodeBuild` for Continuous Integration (CI), together with `pytest` for automated testing before deployment
- `CloudFormation` for reource provision and management

### Project 5: Capstone

TBD... probably going to do this in a separate repo that I will link to here as it's part of a project I want to work on separately from this course...


