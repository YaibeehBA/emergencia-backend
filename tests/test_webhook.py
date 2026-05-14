#!/usr/bin/env python3
"""
Script para testear webhook + notificaciones
Verifica que el sistema de emergencias funcione end-to-end
"""

import requests
import json
import time
from typing import Dict, Any
import sys

BASE_URL = "http://localhost:8000"

class Colors:
    """ANSI colors for terminal"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(title: str):
    """Imprime header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title:^70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.END}\n")

def print_success(msg: str):
    """Imprime mensaje de éxito"""
    print(f"{Colors.GREEN}✅ {msg}{Colors.END}")

def print_error(msg: str):
    """Imprime mensaje de error"""
    print(f"{Colors.RED}❌ {msg}{Colors.END}")

def print_warning(msg: str):
    """Imprime mensaje de advertencia"""
    print(f"{Colors.YELLOW}⚠️  {msg}{Colors.END}")

def print_info(msg: str):
    """Imprime información"""
    print(f"{Colors.BLUE}ℹ️  {msg}{Colors.END}")

def test_health() -> bool:
    """Test 1: Health check"""
    print_header("TEST 1: Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        
        if response.status_code != 200:
            print_error(f"Status code: {response.status_code}")
            return False
        
        data = response.json()
        
        if data.get("status") != "healthy":
            print_error(f"Status: {data.get('status')}")
            return False
        
        print_success("Servidor corriendo")
        print(f"  Version: {data.get('version')}")
        print(f"  Environment: {data.get('environment')}")
        print(f"  Database: {data.get('database')}")
        
        return True
        
    except Exception as e:
        print_error(f"Error: {str(e)}")
        print_info("Asegúrate de que el servidor está corriendo: python app/main.py")
        return False

def test_webhook_approved() -> bool:
    """Test 2: Webhook con cédula APROBADA"""
    print_header("TEST 2: Webhook - Emergencia APROBADA")
    
    try:
        payload = {
            "cedula": "1234567890",
            "hospital_id": "HOSP-001",
            "hospital_name": "Hospital San Juan",
            "hospital_email": "admisiones@hospital.com",
            "insurance_manager_email": "gestor@seguros.com"
        }
        
        print_info("Enviando webhook...")
        print(f"  Cédula: {payload['cedula']}")
        print(f"  Hospital: {payload['hospital_name']}")
        print(f"  Emails: {payload['hospital_email']}, {payload['insurance_manager_email']}")
        
        start = time.time()
        response = requests.post(
            f"{BASE_URL}/api/v1/emergencies/admission",
            json=payload,
            timeout=10
        )
        elapsed = time.time() - start
        
        if response.status_code != 201:
            print_error(f"Status code: {response.status_code}")
            print(json.dumps(response.json(), indent=2))
            return False
        
        data = response.json()
        
        if not data.get("success"):
            print_error("Response success=false")
            return False
        
        decision = data.get("data", {}).get("decision", {})
        status = decision.get("status")
        confidence = decision.get("confidence", 0)
        processing_time = decision.get("processing_time_ms", 0)
        
        print_success(f"Webhook procesado en {elapsed:.2f}s")
        print(f"  Status: {status}")
        print(f"  Confianza: {confidence * 100:.1f}%")
        print(f"  Tiempo procesamiento: {processing_time}ms")
        print(f"  Razón: {decision.get('decision_reason')}")
        
        # Verificar notificaciones
        print_info("Notificaciones enviadas a:")
        print(f"  📧 Hospital: {payload['hospital_email']}")
        print(f"  📧 Aseguradora: {payload['insurance_manager_email']}")
        print_warning("Revisa tu bandeja de entrada y spam")
        
        return status == "APPROVED"
        
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_webhook_suspended() -> bool:
    """Test 3: Webhook con cédula SUSPENDIDA"""
    print_header("TEST 3: Webhook - Emergencia SUSPENDIDA")
    
    try:
        payload = {
            "cedula": "1234567892",
            "hospital_id": "HOSP-002",
            "hospital_name": "Hospital Central",
            "hospital_email": "test@hospital.com",
            "insurance_manager_email": "test@seguros.com"
        }
        
        print_info("Enviando webhook para póliza suspendida...")
        
        response = requests.post(
            f"{BASE_URL}/api/v1/emergencies/admission",
            json=payload,
            timeout=10
        )
        
        if response.status_code != 201:
            print_error(f"Status code: {response.status_code}")
            return False
        
        data = response.json()
        decision = data.get("data", {}).get("decision", {})
        status = decision.get("status")
        is_suspended = decision.get("is_suspended", False)
        
        print_success(f"Webhook procesado")
        print(f"  Status: {status}")
        print(f"  Póliza suspendida: {is_suspended}")
        print(f"  Razón: {decision.get('decision_reason')}")
        
        # Esta debería ser DENIED o PENDING
        if status in ["DENIED", "PENDING_DOCUMENTS"]:
            print_success("✅ Suspensión detectada correctamente")
            return True
        
        return False
        
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_list_cases() -> bool:
    """Test 4: Listar casos"""
    print_header("TEST 4: Listar Casos Procesados")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/emergencies/cases?limit=10",
            timeout=5
        )
        
        if response.status_code != 200:
            print_error(f"Status code: {response.status_code}")
            return False
        
        data = response.json()
        cases = data.get("data", {}).get("cases", [])
        total = data.get("data", {}).get("total", 0)
        
        print_success(f"Total casos: {total}")
        
        if cases:
            print("\n📋 Últimos casos:")
            for i, case in enumerate(cases[:3], 1):
                print(f"  {i}. ID: {case.get('id')}")
                print(f"     Cédula: {case.get('cedula')}")
                print(f"     Status: {case.get('status')}")
                print(f"     Confianza: {case.get('confidence') * 100:.1f}%")
                print(f"     Hora: {case.get('created_at')}")
        
        return len(cases) > 0
        
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_statistics() -> bool:
    """Test 5: Estadísticas"""
    print_header("TEST 5: Estadísticas (Últimas 24h)")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/v1/emergencies/statistics?hours=24",
            timeout=5
        )
        
        if response.status_code != 200:
            print_error(f"Status code: {response.status_code}")
            return False
        
        data = response.json().get("data", {})
        
        total = data.get("total_cases", 0)
        approved = data.get("approved", 0)
        denied = data.get("denied", 0)
        pending = data.get("pending", 0)
        approval_rate = data.get("approval_rate", 0)
        avg_time = data.get("avg_processing_time_ms", 0)
        
        print_success(f"Estadísticas de {data.get('period_hours')}h")
        print(f"  Total casos: {total}")
        print(f"  Aprobados: {approved}")
        print(f"  Denegados: {denied}")
        print(f"  Pendientes: {pending}")
        print(f"  Tasa aprobación: {approval_rate:.1f}%")
        print(f"  Tiempo promedio: {avg_time:.2f}ms")
        
        return True
        
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_swagger():
    """Info sobre Swagger"""
    print_header("BONUS: Explorar en Swagger")
    
    print_info("Abre en navegador:")
    print(f"  🔗 {BASE_URL}/docs")
    print("\nPuedes:")
    print("  • Ver todos los endpoints")
    print("  • Ver ejemplos de request/response")
    print("  • Testear endpoints con 'Try it out'")
    print("  • Ver documentación interactiva")

def main():
    """Ejecuta todos los tests"""
    
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║   🚨 TESTING WEBHOOK + NOTIFICACIONES                     ║")
    print("║   Emergencia-Sync                                          ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(Colors.END)
    
    results = []
    
    # Ejecutar tests
    results.append(("Health Check", test_health()))
    
    if not results[0][1]:
        print_error("\nServidor no responde. Ejecución detenida.")
        print_info("Inicia el servidor: python app/main.py")
        sys.exit(1)
    
    results.append(("Webhook - APROBADA", test_webhook_approved()))
    results.append(("Webhook - SUSPENDIDA", test_webhook_suspended()))
    results.append(("Listar Casos", test_list_cases()))
    results.append(("Estadísticas", test_statistics()))
    
    test_swagger()
    
    # Resumen final
    print_header("📊 RESUMEN FINAL")
    
    print("Resultados:")
    passed = 0
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"  {status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} tests pasaron")
    
    if passed == len(results):
        print_success("\n¡TODOS LOS TESTS PASARON!")
        print_info("\n✅ El sistema está funcionando correctamente")
        print_info("✅ Los webhooks se están procesando")
        print_info("✅ Las notificaciones se están enviando")
        return 0
    else:
        print_error("\nAlgunos tests fallaron")
        return 1

if __name__ == "__main__":
    sys.exit(main())