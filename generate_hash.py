from werkzeug.security import generate_password_hash

# Генерация хэша для пароля "admin"
password_hash = generate_password_hash("admin")

print("Хэш пароля 'admin':")
print(password_hash)