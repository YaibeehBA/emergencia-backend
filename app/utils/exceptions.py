class EmergenciaSyncException(Exception):
    """Excepción base de la aplicación"""
    pass


class PatientNotFoundError(EmergenciaSyncException):
    """Paciente no encontrado"""
    def __init__(self, cedula: str):
        self.cedula = cedula
        super().__init__(f"Paciente con cédula {cedula} no encontrado")


class PolicyNotFoundError(EmergenciaSyncException):
    """Póliza no encontrada"""
    def __init__(self, policy_number: str):
        self.policy_number = policy_number
        super().__init__(f"Póliza {policy_number} no encontrada")


class PolicyNotActiveError(EmergenciaSyncException):
    """Póliza no está activa"""
    def __init__(self, policy_number: str, status: str):
        self.policy_number = policy_number
        self.status = status
        super().__init__(f"Póliza {policy_number} no está activa (estado: {status})")


class PolicySuspendedError(EmergenciaSyncException):
    """Póliza está suspendida"""
    def __init__(self, policy_number: str, reason: str):
        self.policy_number = policy_number
        self.reason = reason
        super().__init__(f"Póliza {policy_number} está suspendida: {reason}")


class AgentExecutionError(EmergenciaSyncException):
    """Error al ejecutar el agente"""
    def __init__(self, message: str):
        super().__init__(f"Error en ejecución del agente: {message}")


class DatabaseError(EmergenciaSyncException):
    """Error de base de datos"""
    pass


class NotificationError(EmergenciaSyncException):
    """Error al enviar notificación"""
    def __init__(self, email: str, reason: str):
        self.email = email
        self.reason = reason
        super().__init__(f"Error enviando email a {email}: {reason}")


class InvalidWebhookError(EmergenciaSyncException):
    """Webhook inválido o no autorizado"""
    pass


class InvalidInputError(EmergenciaSyncException):
    """Entrada de usuario inválida"""
    pass
