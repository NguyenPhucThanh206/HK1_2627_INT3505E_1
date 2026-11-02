from factory import create_app

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        from api.extensions import db
        db.create_all()
        
    app.run(debug=True)