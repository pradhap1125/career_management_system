# AI-Driven Career Management System

# Overview

The AI-Driven Career Management System is a web-based platform that modernizes recruitment by integrating Large Language Models (LLMs) for natural language SQL query generation and FAISS vector database for semantic resume search.

# It allows:

Applicants to register, upload resumes, and manage profiles.

Administrators to perform dynamic queries in plain English and retrieve the most relevant candidates through semantic search.

This project was developed as part of ACS 575: Database Systems (Spring 2025, Purdue University Fort Wayne).

# Features

Applicant Portal: Registration, resume upload, and profile management.

# Admin Dashboard:

CRUD operations on applicant data

Natural language → SQL query generation (via LLM)

Resume search using semantic embeddings + FAISS

# AI-Powered Search:

Natural language queries like “Show me candidates with 5+ years of experience”

Semantic resume retrieval beyond keyword matching

Analytics (OLAP): Skill trends, location-based distributions, experience level analysis, roll-up/drill-down queries.

# Architecture

Backend: Flask (Python)

# Databases:

PostgreSQL → Relational/transactional data

FAISS → Vector-based semantic search

# AI Models:

gemini-2.0-flash-thinking-exp-01-21 → Natural language → SQL generation

multi-qa-mpnet-base-dot-v1 (SentenceTransformer) → Resume embeddings

# Flow:

Applicants interact via React frontend.

Flask backend stores data in PostgreSQL & resume embeddings in FAISS.

Admin issues queries in natural language.

LLM translates queries into SQL.

Resume searches are served from FAISS for semantic matching.

