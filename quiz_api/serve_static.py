#!/usr/bin/env python3
"""
Servidor HTTP simple para servir archivos estáticos en el puerto 3000
"""
import http.server
import socketserver
from pathlib import Path
import os
from typing import Any

PORT = 3000
DIRECTORY = Path(__file__).parent / "static"

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)
    
    def end_headers(self) -> None:
        # Agregar headers CORS para que el frontend pueda hacer peticiones a la API
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

if __name__ == "__main__":
    os.chdir(DIRECTORY)
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"")
        print(f"║  🌐 URL: http://localhost:3000")
        print(f"║  📁 Sirviendo desde: {str(DIRECTORY)} ")
        print(f"║  🔌 API en puerto 8000")
        print(f"║  Presiona CTRL+C para detener")
        print(f"")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n✓ Servidor detenido correctamente")
