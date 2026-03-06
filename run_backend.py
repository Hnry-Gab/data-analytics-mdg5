#!/usr/bin/env python3
"""
Script de inicialização do backend FastAPI
Uso: python run_backend.py
"""
import uvicorn
from src.config import HOST, PORT, DEBUG

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Iniciando Olist Logistics Backend")
    print("=" * 60)
    print(f"Host: {HOST}")
    print(f"Port: {PORT}")
    print(f"Debug: {DEBUG}")
    print(f"\nAcesse:")
    print(f"  - Frontend: http://{HOST}:{PORT}")
    print(f"  - API Docs: http://{HOST}:{PORT}/docs")
    print(f"  - Health: http://{HOST}:{PORT}/api/health")
    print("=" * 60)
    print()

    uvicorn.run(
        "src.main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
        log_level="info"
    )
