from app.auth import hash_password, verify_password


h = hash_password("senha123")
print(h)
print(verify_password("senha123", h))
print(verify_password("senha_errada", h))