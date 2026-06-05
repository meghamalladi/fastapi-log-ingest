I have created a fastapi app that injests logs from clients and stores them in the database
Stage1: I have used the database on my local machine, and both the server and client
    on my local system. 
Stage 2: I have containerized my application.
Stage 3- Deployed the application on AWS cloud EC2 instance
Stage 4- to do: Decouple the architecture by making use of RedPanda/Kafka messaging systems

Current modules needed and versions:
python: 3.9.6
uvicorn web server: 0.30.0
fastapi: 0.128.8
SQLalchemy: 2.0.48 ; 
asyncpg: 0.31.0
pydantic: 2.12.5

command you could use: "pip3 install fastapi uvicorn[standard] sqlalchemy asyncpg pydantic-settings python-dotenv httpx"
