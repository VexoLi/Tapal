import os
from dotenv import load_dotenv

# Cargar variables de entorno desde un archivo .env
load_dotenv()

# Configuración global (si aplica)
os.environ.setdefault("ENV", "development")
