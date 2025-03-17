# Project Brief: Conduit API Performance Optimization

## Project Overview
Conduit is a Django-based API backend for a blogging platform. The application is experiencing severe performance issues on the production droplet, with worker timeouts and SIGKILL errors indicating memory problems.

## Core Requirements
1. Identify and fix performance bottlenecks in the codebase
2. Optimize database queries to reduce load
3. Implement proper caching strategies
4. Configure worker processes appropriately for the available resources
5. Reduce memory usage to prevent worker timeouts and SIGKILL errors

## Project Scope
- Focus on the most critical performance issues first
- Prioritize changes that can be implemented quickly with significant impact
- Document all changes and their expected impact
- Provide recommendations for long-term improvements

## Success Criteria
- No more worker timeouts or SIGKILL errors
- Reduced response times for API endpoints
- Lower memory usage on the production server
- Improved database query efficiency 