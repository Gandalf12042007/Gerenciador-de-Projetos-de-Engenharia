# -*- coding: utf-8 -*-
"""
Script simples para iniciar o servidor
"""

if __name__ == "__main__":
    import uvicorn
    
    print("\n" + "="*60)
    print("INICIANDO SERVIDOR...")
    print("="*60)
    print("\nAguarde, o servidor esta carregando...\n")
    
    try:
        uvicorn.run(
            "app:app",
            host="127.0.0.1",
            port=8000,
            reload=False,
            log_level="info"
        )
    except Exception as e:
        print(f"\nERRO ao iniciar servidor: {e}")
        import traceback
        traceback.print_exc()
        input("\nPressione Enter para sair...")
