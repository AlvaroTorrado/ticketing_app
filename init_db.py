from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

app = create_app()

with app.app_context():
    print("📦 Creando tablas si no existen...")
    db.create_all()

    admin_user = User.query.filter_by(username='admin').first()
    if admin_user:
        print("🔁 Usuario 'admin' ya existe. Eliminando para regenerar...")
        db.session.delete(admin_user)
        db.session.commit()

    print("👤 Creando nuevo usuario administrador...")
    new_admin = User(username='admin', role='admin')
    new_admin.password_hash = generate_password_hash('admin123', method='pbkdf2:sha256')
    db.session.add(new_admin)
    db.session.commit()
    print("✅ Usuario 'admin' creado con contraseña: admin123 (pbkdf2:sha256)")
    
    