# Import the Python Library
import sys
import bcrypt

password = b"studyhard"

# Hash a password for the first time, with a certain number of rounds
salt = bcrypt.gensalt(14)
hashed = bcrypt.hashpw(password, salt)
print(salt)
print(hashed)

# Check a plain text string against the salted, hashed digest
bcrypt.checkpw(password, hashed)

password=b'learningisfun'
salt = b"$2b$14$EFOxm3q8UWH8ZzK1h.WTZe"
hashed = bcrypt.hashpw(password, salt)
print(salt)
print(hashed)

password=b'udacity'
salt = b"$2b$14$EFOxm3q8UWH8ZzK1h.WTZe"
hashed = bcrypt.hashpw(password, salt)
print(salt)
print(hashed)

password=b'securepassword'
salt = b"$2b$14$EFOxm3q8UWH8ZzK1h.WTZe"
hashed = bcrypt.hashpw(password, salt)
print(salt)
print(hashed)