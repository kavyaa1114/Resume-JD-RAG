# Resume-JD-RAG

### AI Recruiting Intelligence

[🚀 Live Demo](https://resume-jd-rag.streamlit.app) | [💻 GitHub](https://github.com/kavyaa1114/Resume-JD-RAG)

A RAG-powered recruiter assistant that analyzes a candidate's resume against a specific job description and generates concise, evidence-grounded insights.

## Overview

Recruiters often need to quickly determine how a candidate's experience aligns with the requirements of a particular role.

Resume-JD-RAG uses Retrieval-Augmented Generation (RAG) to retrieve relevant evidence from a candidate's resume based on the requirements of a job description and presents the findings as recruiter-focused decision support.

The system does not assign an ATS score or make a hiring decision.

## Key Features

- Upload a candidate resume in PDF format
- Upload a job description in PDF format
- Extract and chunk resume content
- Generate semantic embeddings using OpenAI
- Store resume embeddings in a FAISS vector database
- Retrieve resume evidence relevant to the job description
- Generate concise recruiter analysis using GPT-4.1
- Highlight strong matches and areas that require verification
- Generate targeted interview questions
- Provide evidence behind the generated analysis

## How It Works

```text
Candidate Resume
       │
       ▼
   PDF Loader
       │
       ▼
  Text Chunking
       │
       ▼
OpenAI Embeddings
       │
       ▼
   FAISS Vector Store
       │
       │
Job Description ──────────┐
                           ▼
                     Retriever
                           │
                           ▼
                Relevant Resume Evidence
                           │
                           ▼
                       GPT-4.1
                           │
                           ▼
               Recruiter Analysis