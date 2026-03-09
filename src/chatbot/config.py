"""Chatbot configuration — OpenRouter API and MCP client settings."""
import os
import sys
from pathlib import Path

# OpenRouter
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "z-ai/glm-4.5-air:free")
# Produção: google/gemini-2.5-flash-lite
OPENROUTER_MAX_TOKENS = int(os.getenv("OPENROUTER_MAX_TOKENS", "4096"))
OPENROUTER_TEMPERATURE = float(os.getenv("OPENROUTER_TEMPERATURE", "0.3"))

# MCP Server
MCP_SERVER_COMMAND = sys.executable          # mesmo Python do venv
MCP_SERVER_ARGS = ["-m", "olist_mcp.server"] # module entry point
MCP_SERVER_CWD = str(Path(__file__).resolve().parent.parent.parent)  # raiz do projeto

# Feature toggle
CHATBOT_ENABLED = os.getenv("CHATBOT_ENABLED", "true").lower() == "true"

# Session
MAX_HISTORY_MESSAGES = int(os.getenv("CHATBOT_MAX_HISTORY", "50"))
MAX_TOOL_ITERATIONS = int(os.getenv("CHATBOT_MAX_TOOL_ITERATIONS", "10"))
