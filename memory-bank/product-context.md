# Product Context: Conduit API

## Purpose
Conduit is a blogging platform API built with Django and Django REST Framework. It provides the backend services for a Medium-like blogging application, allowing users to create, read, update, and delete articles, follow other users, favorite articles, and comment on content.

## Problem Statement
The application is currently experiencing severe performance issues in production:
- Worker processes are timing out and being killed by the system (SIGKILL)
- Response times are unacceptably high
- Memory usage is excessive, leading to resource exhaustion
- Database queries are inefficient and causing bottlenecks

## User Experience Goals
- Fast and responsive API endpoints
- Reliable service without timeouts or errors
- Consistent performance even under load
- Efficient resource usage to keep hosting costs reasonable

## Technical Architecture
- Django 5.0 backend with Django REST Framework
- PostgreSQL database
- Redis for caching and channels
- Deployed using Docker containers
- Uvicorn as the ASGI server with multiple workers

## Current Deployment
- Digital Ocean droplet with limited resources
- Docker Compose for container orchestration
- Nginx as a reverse proxy (assumed)
- Multiple worker processes that are overwhelming the available memory 