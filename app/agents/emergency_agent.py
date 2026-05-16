import json
import time
from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.tools import tool as langchain_tool
from langchain_core.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
)

from app.core.config import get_settings
from app.agents.tools import AgentTools
from app.agents.prompts import EMERGENCY_AGENT_SYSTEM_PROMPT
from app.utils.logger import get_logger
from app.core.constants import DecisionStatus, MIN_CONFIDENCE_FOR_AUTO_APPROVAL

logger = get_logger("agents.emergency")
settings = get_settings()


class EmergencyAgent:
    """Agente especializado en validación de emergencias"""

    def __init__(self, db: Session):
        self.db = db
        self.tools_instance = AgentTools(db)
        self.llm = self._setup_llm()  
        self.executor = self._setup_executor()

    def _setup_llm(self):
        """Configura el LLM según el proveedor activo en settings"""
        # GROQ 
        if settings.active_agent == "groq":
            try:
                from langchain_groq import ChatGroq
                
                if not settings.groq_api_key:
                    raise ValueError("GROQ_API_KEY no está configurada en .env")
                
                logger.info(f"Usando Groq con modelo: {settings.groq_model}")
                return ChatGroq(
                    model=settings.groq_model,
                    temperature=settings.agent_temperature,
                    max_tokens=settings.agent_max_tokens,
                    groq_api_key=settings.groq_api_key,
                )
            except ImportError:
                logger.error("langchain-groq no instalado. Ejecuta: pip install langchain-groq")
                raise
            except Exception as e:
                logger.error(f"Error configurando Groq: {e}")
                raise
            
        # GOOGLE GEMINI
        elif settings.active_agent == "gemini":
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                
                if not settings.gemini_api_key:
                    raise ValueError("GEMINI_API_KEY no está configurada en .env")
                
                logger.info(f"Usando Gemini con modelo: {settings.gemini_model}")
                return ChatGoogleGenerativeAI(
                    model=settings.gemini_model,
                    temperature=settings.agent_temperature,
                    max_output_tokens=settings.agent_max_tokens,
                    google_api_key=settings.gemini_api_key,
                )
            except ImportError:
                logger.error("langchain-google-genai no instalado")
                raise
            except Exception as e:
                logger.error(f"Error configurando Gemini: {e}")
                raise
        # Error: Proveedor no soportado
        else:
            raise ValueError(
                f"Proveedor '{settings.active_agent}' no soportado. "
                f"Usa: 'groq', 'gemini', o 'ollama'"
            )

    def _setup_executor(self) -> AgentExecutor:
        """Configura executor del agente con las tools"""
        
        @langchain_tool
        def check_policy(cedula: str) -> str:
            """Verifica póliza activa del paciente. Input: cédula (10 dígitos)"""
            result = self.tools_instance.check_policy(cedula)
            return json.dumps(result, ensure_ascii=False, default=str)

        @langchain_tool
        def check_preexisting(cedula: str) -> str:
            """Verifica pre-existencias. Input: cédula del paciente"""
            from app.db.models import Patient
            patient = self.db.query(Patient).filter(Patient.cedula == cedula).first()
            if not patient:
                return json.dumps({"success": False, "error": "PATIENT_NOT_FOUND"})
            
            result = self.tools_instance.check_preexisting(patient.id, cedula)
            return json.dumps(result, ensure_ascii=False, default=str)

        @langchain_tool
        def check_suspension(cedula: str) -> str:
            """Verifica suspensiones de póliza. Input: cédula del paciente"""
            from app.db.models import Patient, Policy
            from app.core.constants import PolicyStatus
            
            patient = self.db.query(Patient).filter(Patient.cedula == cedula).first()
            if not patient:
                return json.dumps({"success": False, "error": "PATIENT_NOT_FOUND"})
            
            policy = self.db.query(Policy).filter(
                Policy.patient_id == patient.id,
                Policy.status == PolicyStatus.ACTIVE
            ).first()
            
            if not policy:
                return json.dumps({"success": False, "error": "NO_ACTIVE_POLICY"})
            
            result = self.tools_instance.check_suspension(policy.id, cedula)
            return json.dumps(result, ensure_ascii=False, default=str)

        tools = [check_policy, check_preexisting, check_suspension]

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", EMERGENCY_AGENT_SYSTEM_PROMPT),
                ("human", "{input}"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )

        agent = create_tool_calling_agent(self.llm, tools, prompt)

        return AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=settings.debug,
            max_iterations=5,
            handle_parsing_errors=True,
        )

    def process_emergency(self, cedula: str) -> Dict[str, Any]:
        """Procesa emergencia y emite decisión."""
        start_time = time.time()

        try:
            logger.info(f"PROCESANDO EMERGENCIA: {cedula}")

            input_prompt = f"""
            Procesar emergencia para cédula: {cedula}
            
            Pasos obligatorios:
            1. Llama a check_policy con la cédula
            2. Llama a check_preexisting con la cédula  
            3. Llama a check_suspension con la cédula
            4. Analiza los resultados y emite decisión en JSON
            
            Recuerda: Debes responder con un JSON válido.
            """

            logger.info(f"Ejecutando agente con {settings.active_agent}...")
            result = self.executor.invoke({"input": input_prompt})

            decision = self._parse_agent_response(result, cedula)

            processing_time = (time.time() - start_time) * 1000
            logger.info(
                f"DECISIÓN EMITIDA: {decision['status']} "
                f"(confianza: {decision['confidence']:.2f}, tiempo: {processing_time:.0f}ms)"
            )

            decision["processing_time_ms"] = int(processing_time)

            return decision

        except Exception as e:
            logger.error(f"Error procesando emergencia: {str(e)}", exc_info=True)
            return self._create_default_decision(cedula, str(e))

    def _parse_agent_response(self, agent_result: Dict[str, Any], cedula: str) -> Dict[str, Any]:
        """Parsea respuesta del agente."""
        try:
            agent_output = agent_result.get("output", "")
            
            if isinstance(agent_output, str):
                start_idx = agent_output.find("{")
                end_idx = agent_output.rfind("}") + 1
                if start_idx != -1 and end_idx > start_idx:
                    json_str = agent_output[start_idx:end_idx]
                    decision = json.loads(json_str)
                else:
                    decision = self._create_default_decision(cedula, "No se encontró JSON válido")
            else:
                decision = agent_output

            return self._validate_decision_structure(decision, cedula)

        except Exception as e:
            logger.error(f"Error parseando respuesta: {e}")
            return self._create_default_decision(cedula, str(e))

    def _validate_decision_structure(self, decision: Dict[str, Any], cedula: str) -> Dict[str, Any]:
        """Valida estructura de decisión."""
        required_fields = {
            "status": DecisionStatus.PENDING_DOCUMENTS,
            "cedula": cedula,
            "decision_reason": "Decisión generada automáticamente",
            "confidence": 0.5,
        }
        
        for field, default in required_fields.items():
            if field not in decision or decision[field] is None:
                decision[field] = default

        valid_statuses = [DecisionStatus.APPROVED, DecisionStatus.DENIED, DecisionStatus.PENDING_DOCUMENTS]
        if decision["status"] not in valid_statuses:
            decision["status"] = DecisionStatus.PENDING_DOCUMENTS

        decision["confidence"] = max(0.0, min(1.0, float(decision.get("confidence", 0.0))))

        if "timestamp" not in decision:
            decision["timestamp"] = datetime.utcnow().isoformat()
        if "policy_number" not in decision:
            decision["policy_number"] = None
        if "pre_existing_conditions" not in decision:
            decision["pre_existing_conditions"] = []
        if "is_suspended" not in decision:
            decision["is_suspended"] = False
        if "requires_manual_review" not in decision:
            decision["requires_manual_review"] = decision["confidence"] < MIN_CONFIDENCE_FOR_AUTO_APPROVAL

        return decision

    def _create_default_decision(self, cedula: str, reason: str = "") -> Dict[str, Any]:
        """Crea decisión por defecto."""
        return {
            "status": DecisionStatus.PENDING_DOCUMENTS,
            "cedula": cedula,
            "policy_number": None,
            "decision_reason": f"Requiere revisión manual. {reason}" if reason else "Error en procesamiento automático",
            "confidence": 0.0,
            "pre_existing_conditions": [],
            "is_suspended": False,
            "requires_manual_review": True,
            "timestamp": datetime.utcnow().isoformat(),
        }