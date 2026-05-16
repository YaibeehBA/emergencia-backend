
from app.db import init_db
from data.seed import seed_database 

if __name__ == "__main__":
    print("Inicializando base de datos...")
    
    try:
        init_db()
        print("Tablas creadas")
        
        # Poblar con datos
        print("Poblando con datos de prueba...")
        seed_database ()
        print("Datos insertados")
        
        print("\n" + "="*50)
        print("BASE DE DATOS INICIALIZADA EXITOSAMENTE")
        print("="*50)
        print("\nAhora ejecuta: python -m app.main para iniciar el servidor")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()