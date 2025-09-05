def register_all_blueprints(app, user_service, dashboard_service):
    """
    Centraliza el registro de blueprints e inyecta las dependencias.
    """
    from .routes.main_routes import main_bp
    from .routes.dashboard_routes import dashboards_bp
    from .routes.settings_routes import settings_bp

    # Inyectar servicios en los módulos de rutas
    main_bp.user_service = user_service
    dashboards_bp.dashboard_service = dashboard_service
    settings_bp.user_service = user_service

    app.register_blueprint(main_bp)
    app.register_blueprint(dashboards_bp)
    app.register_blueprint(settings_bp)