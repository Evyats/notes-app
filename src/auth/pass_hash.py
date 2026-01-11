from passlib.context import CryptContext


hash_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    deprecated="auto",
    pbkdf2_sha256__default_rounds=260000,
)

def hash(password: str) -> str:
    return hash_context.hash(password)

def verify(plain: str, hashed: str) -> bool:
    return hash_context.verify(plain, hashed)




if __name__ == "__main__":
    pass
    a = hash("hello")
    print(verify("hello", a))
    # expect to seing True printed