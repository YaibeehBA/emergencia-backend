# Backend - Emergencia-Sync

Backend en **FastAPI** con **ORM SQLAlchemy** para el sistema de alerta temprana de ingresos a emergencias.

## Estructura del Proyecto

```
backend/
├── app/
│   ├── core/              # Configuración y constantes
│   ├── db/                # ORM y modelos
│   ├── schemas/           # Validación Pydantic
│   ├── repositories/      # Patrón Repository
│   ├── services/          # Lógica de negocio
│   ├── agents/            # Agente IA
│   ├── api/               # Endpoints FastAPI
│   ├── utils/             # Utilidades y helpers
│   └── main.py            # Punto de entrada
├── data/
│   ├── seed.py            # Script de data fixtures
├── tests/                 # Tests unitarios
├── requirements.txt       # Dependencias
├── .env.example          # Variables de entorno de ejemplo

```

## Inicio Rápido

### 1. Crear Entorno Virtual

```bash
cd backend
python -m venv venv

# Activar (Linux/Mac)
source venv/bin/activate

# Activar (Windows)
venv\Scripts\activate
```

### 2. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar Variables de Entorno

Configuración del Agente IA

El sistema soporta múltiples proveedores de modelos LLM.

Proveedores disponibles

| Proveedor | Modelo | Variable |
|---|---|---|
| Groq | llama-3.3-70b-versatile | ACTIVE_AGENT=groq |
| Gemini | gemini-2.5-flash | ACTIVE_AGENT=gemini |

---

Variables necesarias

```env
# Proveedor activo
ACTIVE_AGENT=groq

# API Keys
GROQ_API_KEY=tu_api_key
GEMINI_API_KEY=tu_api_key

# Configuración del agente
AGENT_TEMPERATURE=0.7
AGENT_MAX_TOKENS=1000

```bash
cp .env.example .env
# Editar .env con tus valores
```

### 4. Inicializar Base de Datos

```bash
# Crear tablas y carga con datos de prueba
python init_db.py

```

### 5. Ejecutar Servidor

```bash
# Desarrollo (con reload)
python -m app.main

# O con uvicorn directo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Acceder a:
- API: http://localhost:8000
- Swagger Docs: http://localhost:8000/docs

## Arquitectura

### Patrón Repository
- **Abstracción de acceso a datos**: No queremos lógica SQL esparcida
- **Testeable**: Fácil mockar la BD en tests
- **Reutilizable**: Métodos comunes en `BaseRepository`

```python
# Uso
patient_repo = PatientRepository(db)
patient = patient_repo.get_by_cedula("1234567890")
policy = patient_repo.get_active_policy(patient.id)
```

### ORM SQLAlchemy v2
- **Type-safe**: Validación de tipos
- **Relaciones**: `relationship()` automático
- **Índices**: Optimizados para búsquedas
- **Timestamps**: Auto `created_at` y `updated_at`

```python
# Modelos
class Patient(BaseModel):
    cedula: str
    full_name: str
    policies: relationship("Policy")  # Relación automática
```

### Schemas Pydantic v2
- **Validación de entrada**: `EmergencyAdmissionRequest`
- **Serialización de salida**: `CaseResponse`
- **Documentación automática**: En Swagger

```python
class EmergencyAdmissionRequest(BaseModel):
    cedula: str = Field(..., min_length=10, max_length=10)
    hospital_email: str = Field(...)
```


## Base de Datos

### SQLite (Desarrollo)
```bash
# Usa automáticamente emergencia.db
DATABASE_URL=sqlite:///./emergencia.db
```

### PostgreSQL (Producción)
```bash
# Instalar psycopg2
pip install psycopg2-binary

DATABASE_URL=postgresql://user:pass@localhost/emergencia_db
```

### Migrations (Alembic - Opcional)
```bash
# Crear tabla de migrations
alembic init migrations

# Crear migration
alembic revision --autogenerate -m "Add patient model"

# Aplicar
alembic upgrade head
```

## Testing

```bash
# Ejecutar tests
pytest

# Con cobertura
pytest --cov=app

# Específico
pytest tests/test_repositories.py -v
```

## Seguridad

- ✅ Validación Pydantic en entrada
- ✅ SQL Injection protection (ORM)
- ✅ CORS configurado
- ✅ Logging estructurado
- ✅ Exception handling centralizado
- ✅ Variables sensibles en .env (no commiteadas)

## Buenas Prácticas

1. **Type Hints**: Todo el código está typed
2. **Docstrings**: Cada función documentada
3. **Exception Handling**: Custom exceptions específicas
4. **Logging**: Logs JSON estructurados
5. **ORM**: Nunca SQL crudo
6. **Validation**: Schemas Pydantic para todo
7. **DRY**: BaseRepository para evitar repetición

