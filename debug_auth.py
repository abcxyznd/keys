@app.route("/debug/auth-config", methods=["GET"])
def debug_auth_config():
    """Debug endpoint: Check current auth config"""
    config = load_auth_config()
    
    # Don't expose passwords in debug
    safe_config = {
        "owner_email": config.get("owner_email"),
        "authorized_emails": config.get("authorized_emails", []),
        "has_password_access": bool(config.get("password_access")),
        "password_emails": list(config.get("password_access", {}).keys()) if config.get("password_access") else [],
        "file_exists": os.path.exists(AUTH_FILE),
        "file_path": AUTH_FILE
    }
    
    return jsonify({
        "status": "ok",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "auth_config": safe_config
    })