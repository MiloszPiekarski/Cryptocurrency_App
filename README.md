# CASH MAELSTROM (Turboplan X)
 AI-Native Institutional Trading Platform

Cloud Native Architecture (v1.0.0)

## Overview
This platform integrates real-time market data ingestion with advanced AI agents for trading analysis. It utilizes a microservices architecture with a Next.js frontend, FastAPI backend, and a TimescaleDB/Redis data layer.

## Installation & Setup

1. Clone Codebase
Clone the repository and navigate to the project root.

2. Configuration
This project relies on environment variables for configuration. Create a .env file in the root directory based on the provided example. You will need to configure:
- Database credentials (PostgreSQL)
- Cloud provider keys (Google Cloud Vertex AI)
- API keys for market data providers

3. Start the System
The system includes a comprehensive startup script that handles service orchestration and dependency checking.

Run the following command:
./RESTART_EVERYTHING.sh

This script will:
- Initialize Docker containers (TimescaleDB, Redis)
- Start the Real-time Data Streamer
- Launch the Backend API (Port 8000)
- Launch the AI Engine (Port 8001)
- Start the Frontend Application (Port 3000)

## Access Points
Once the system is running, you can access the interface at http://localhost:3000

## Security Note
Do not commit sensitive keys, passwords, or service account JSON files to the repository. Ensure your .gitignore is properly configured to exclude these files.
