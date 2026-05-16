
import asyncio
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional

from app.core.config import get_settings
from app.utils.logger import get_logger
from app.utils.exceptions import NotificationError

logger = get_logger("services.notification")
settings = get_settings()


class NotificationService:
    """Servicio para enviar notificaciones"""

    def __init__(self):
        """Inicializa servicio"""
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_user = settings.smtp_user
        self.smtp_password = settings.smtp_password
        self.sender_email = settings.sender_email
        self.sender_name = settings.sender_name
        self.mock_email = settings.mock_email

    async def send_hospital_notification(
        self,
        hospital_email: str,
        hospital_name: Optional[str],
        cedula: str,
        decision: Dict[str, Any],
    ) -> bool:
        """
        Envía notificación al hospital.

        Args:
            hospital_email: Email del hospital
            hospital_name: Nombre del hospital
            cedula: Cédula del paciente
            decision: Decisión del agente

        Returns:
            True si se envió exitosamente
        """
        try:
            logger.info(f"📧 Enviando notificación a hospital: {hospital_email}")

            subject = f"🚨 ALERTA: Paciente ingresó a emergencia - Cédula {cedula}"

            status = decision.get("status")
            status_emoji = "✅" if status == "APPROVED" else "⚠️"

            body = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6;">
    <div style="max-width: 600px; margin: 0 auto; border: 1px solid #ddd; padding: 20px;">
        
        <h1 style="color: #d32f2f;">🚨 ALERTA DE EMERGENCIA</h1>
        
        <hr>
        
        <h2>Información del Paciente</h2>
        <p><strong>Cédula:</strong> {cedula}</p>
        {f'<p><strong>Hospital:</strong> {hospital_name}</p>' if hospital_name else ''}
        
        <h2>Decisión del Sistema</h2>
        <p style="font-size: 18px; font-weight: bold; color: {'#4caf50' if status == 'APPROVED' else '#ff9800'};">
            {status_emoji} Estado: {status}
        </p>
        
        <p><strong>Razón:</strong> {decision.get('decision_reason', 'N/A')}</p>
        <p><strong>Confianza:</strong> {decision.get('confidence', 0) * 100:.1f}%</p>
        <p><strong>Tiempo de procesamiento:</strong> {decision.get('processing_time_ms', 'N/A')} ms</p>
        
        <h2>Detalles de la Cobertura</h2>
        <p><strong>Número de Póliza:</strong> {decision.get('policy_number', 'N/A')}</p>
        <p><strong>Suspensión activa:</strong> {'Sí ⚠️' if decision.get('is_suspended') else 'No ✅'}</p>
        
        <h2>Pre-existencias</h2>
        <p>
            {f"<br>".join(decision.get('pre_existing_conditions', ['Ninguna'])) if decision.get('pre_existing_conditions') else 'Ninguna'}
        </p>
        
        <hr>
        
        <p style="color: #666; font-size: 12px;">
            Este mensaje fue generado automáticamente por Emergencia-Sync.
            <br>
            Timestamp: {decision.get('timestamp', 'N/A')}
        </p>
        
    </div>
</body>
</html>
"""

            return await self._send_email(
                to_email=hospital_email,
                subject=subject,
                body=body,
            )

        except Exception as e:
            logger.error(f"❌ Error enviando notificación a hospital: {str(e)}", exc_info=e)
            raise NotificationError(hospital_email, str(e))

    async def send_insurance_notification(
        self,
        insurance_email: str,
        cedula: str,
        decision: Dict[str, Any],
    ) -> bool:
        """
        Envía notificación al gestor de casos del seguro.

        Args:
            insurance_email: Email del gestor
            cedula: Cédula del paciente
            decision: Decisión del agente

        Returns:
            True si se envió exitosamente
        """
        try:
            logger.info(f"Enviando notificación a aseguradora: {insurance_email}")

            subject = f"PROCESAMIENTO DE EMERGENCIA - Cédula {cedula}"

            status = decision.get("status")
            status_emoji = "✅" if status == "APPROVED" else "⚠️"

            body = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6;">
    <div style="max-width: 600px; margin: 0 auto; border: 1px solid #ddd; padding: 20px;">
        
        <h1 style="color: #1976d2;"> NOTIFICACIÓN DE PROCESAMIENTO</h1>
        
        <hr>
        
        <h2>Resumen del Caso</h2>
        <p><strong>Cédula del Afiliado:</strong> {cedula}</p>
        <p><strong>Timestamp:</strong> {decision.get('timestamp', 'N/A')}</p>
        
        <h2>Decisión del Agente IA</h2>
        <p style="font-size: 18px; font-weight: bold; color: {'#4caf50' if status == 'APPROVED' else '#ff9800'};">
            {status_emoji} {status}
        </p>
        
        <h2>Detalles Técnicos</h2>
        <p><strong>Número de Póliza:</strong> {decision.get('policy_number', 'N/A')}</p>
        <p><strong>Razonamiento:</strong> {decision.get('decision_reason', 'N/A')}</p>
        <p><strong>Nivel de Confianza:</strong> {decision.get('confidence', 0) * 100:.1f}%</p>
        <p><strong>Tiempo de Procesamiento:</strong> {decision.get('processing_time_ms', 'N/A')} ms</p>
        
        <h2>Estado de la Póliza</h2>
        <p><strong>Suspensión activa:</strong> {'Sí ⚠️' if decision.get('is_suspended') else 'No ✅'}</p>
        <p><strong>Requiere revisión manual:</strong> {'Sí ⚠️' if decision.get('requires_manual_review') else 'No ✅'}</p>
        
        <h2>Condiciones Pre-existentes</h2>
        {f"<p>" + "<br>".join(decision.get('pre_existing_conditions', ['Ninguna'])) + "</p>" if decision.get('pre_existing_conditions') else '<p>Ninguna</p>'}
        
        <hr>
        
        <p style="color: #666; font-size: 12px;">
            Este es un mensaje automático del sistema Emergencia-Sync.
            <br>
            No responder a este email.
        </p>
        
    </div>
</body>
</html>
"""

            return await self._send_email(
                to_email=insurance_email,
                subject=subject,
                body=body,
            )

        except Exception as e:
            logger.error(f"❌ Error enviando notificación a aseguradora: {str(e)}", exc_info=e)
            raise NotificationError(insurance_email, str(e))

    async def _send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
    ) -> bool:
        """
        Envía email real o mock.

        Args:
            to_email: Destinatario
            subject: Asunto
            body: Cuerpo (HTML)

        Returns:
            True si se envió exitosamente
        """
        try:
            if self.mock_email:
                # MOCK: Solo simular
                logger.info(f"[MOCK] Email enviado a: {to_email}")
                logger.info(f"[MOCK] Asunto: {subject}")
                logger.info(f"[MOCK] Cuerpo: {body[:100]}...")
                return True

            # REAL: Enviar por SMTP
            logger.info(f"Conectando a SMTP: {self.smtp_host}:{self.smtp_port}")

            # Crear mensaje
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{self.sender_name} <{self.sender_email}>"
            msg["To"] = to_email

            # Parte HTML
            part = MIMEText(body, "html")
            msg.attach(part)

            # Enviar
            with smtplib.SMTP(self.smtp_host, self.smtp_port, timeout=10) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(self.sender_email, to_email, msg.as_string())

            logger.info(f"Email enviado exitosamente a: {to_email}")
            return True

        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"Error de autenticación SMTP: {str(e)}")
            raise NotificationError(to_email, "Credenciales SMTP inválidas")

        except smtplib.SMTPException as e:
            logger.error(f"Error SMTP: {str(e)}")
            raise NotificationError(to_email, f"Error SMTP: {str(e)}")

        except Exception as e:
            logger.error(f"Error enviando email: {str(e)}", exc_info=e)
            raise NotificationError(to_email, str(e))

    async def send_notification_async(
        self,
        hospital_email: str,
        insurance_email: str,
        hospital_name: Optional[str],
        cedula: str,
        decision: Dict[str, Any],
    ) -> Dict[str, bool]:
        """
        Envía ambas notificaciones de forma concurrente.

        Args:
            hospital_email: Email del hospital
            insurance_email: Email del gestor
            hospital_name: Nombre del hospital
            cedula: Cédula del paciente
            decision: Decisión del agente

        Returns:
            Dict con estado de ambos envíos
        """
        logger.info("Iniciando envío de notificaciones concurrentes")

        try:
            # Ejecutar ambos envíos en paralelo
            hospital_result, insurance_result = await asyncio.gather(
                self.send_hospital_notification(
                    hospital_email, hospital_name, cedula, decision
                ),
                self.send_insurance_notification(insurance_email, cedula, decision),
                return_exceptions=True,
            )

            # Verificar resultados
            hospital_ok = isinstance(hospital_result, bool) and hospital_result
            insurance_ok = isinstance(insurance_result, bool) and insurance_result

            if isinstance(hospital_result, Exception):
                logger.error(f"Error enviando a hospital: {hospital_result}")
                hospital_ok = False

            if isinstance(insurance_result, Exception):
                logger.error(f"Error enviando a aseguradora: {insurance_result}")
                insurance_ok = False

            logger.info(
                f"✅ Notificaciones enviadas: "
                f"Hospital={hospital_ok}, Aseguradora={insurance_ok}"
            )

            return {
                "hospital_notified": hospital_ok,
                "insurance_notified": insurance_ok,
                "all_sent": hospital_ok and insurance_ok,
            }

        except Exception as e:
            logger.error(f"Error en envío concurrente: {str(e)}", exc_info=e)
            return {
                "hospital_notified": False,
                "insurance_notified": False,
                "all_sent": False,
            }