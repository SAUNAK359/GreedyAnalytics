from passlib.hash import bcrypt

def hash_password(pwd):
    return bcrypt.hash(pwd)

def verify(pwd, hashed):
    return bcrypt.verify(pwd, hashed)
