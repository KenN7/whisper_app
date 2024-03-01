import bcrypt


def verify_password(hashed_password, plain_password):
    password_byte_enc = plain_password.encode("utf-8")
    hashed_password = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password=password_byte_enc, hashed_password=hashed_password)


def hash_password(plain_password):
    pwd_bytes = plain_password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password.decode("utf-8")
