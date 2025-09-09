from app.main import create_app

# Crea la aplicación llamando a la fábrica
app = create_app()

if __name__ == "__main__":
    # La configuración de host, port y debug ahora viene del archivo de settings
    app.run(
        host=app.config.get("HOST", "0.0.0.0"),
        port=app.config.get("PORT", 5000),
        debug=app.config.get("FLASK_DEBUG", True)
    )