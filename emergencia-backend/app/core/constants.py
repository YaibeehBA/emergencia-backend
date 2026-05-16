from enum import Enum

class PolicyStatus(str, Enum):
    """Estados posibles de una póliza"""
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class DecisionStatus(str, Enum):
    """Estados de decisión del agente"""
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    PENDING_DOCUMENTS = "PENDING_DOCUMENTS"
    PENDING_MANUAL_REVIEW = "PENDING_MANUAL_REVIEW"


class EmergencyType(str, Enum):
    """Tipos de emergencia"""
    CARDIAC = "CARDIAC"
    RESPIRATORY = "RESPIRATORY"
    TRAUMATIC = "TRAUMATIC"
    NEUROLOGICAL = "NEUROLOGICAL"
    OTHER = "OTHER"


# ============================================================================
# REGLAS DE NEGOCIO
# ============================================================================

# Cobertura en emergencias
EMERGENCY_COVERAGE_PERCENTAGE = 100  # Las emergencias cubren 100%
PREEXISTING_COVERAGE_IN_EMERGENCY = True  # Las pre-existencias siempre cubren en emergencias

# Copago
STANDARD_COPAY_PERCENTAGE = 10
MAX_COPAY_MONTHLY = 100.00  # USD

# Tiempos
AGENT_TIMEOUT_SECONDS = 5
WEBHOOK_TIMEOUT_SECONDS = 30
NOTIFICATION_RETRY_COUNT = 3

# Confianza mínima
MIN_CONFIDENCE_FOR_AUTO_APPROVAL = 0.85

# Palabras clave de decisión
KEYWORDS_APPROVED = ["aprobado", "approved", "autorizado", "authorized", "cubre", "covers"]
KEYWORDS_DENIED = ["denegado", "denied", "rechazado", "rejected", "no cubre", "not covered"]
KEYWORDS_PENDING = ["pendiente", "pending", "documentos", "documents", "revisión", "review"]
