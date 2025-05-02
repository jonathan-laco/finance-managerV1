from app import app
from seed import run_seed

if __name__ == '__main__':
    with app.app_context():
        try:
            run_seed()
        except Exception as e:
            print(f"Erro ao executar seed: {e}")
            print("Continuando a execução da aplicação...")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

