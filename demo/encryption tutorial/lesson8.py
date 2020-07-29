from cryptography.fernet import Fernet

# Generate a Key and Instantiate a Fernet Instance
key = Fernet.generate_key()
f = Fernet(key)
print(key)

# Define our message
plaintext = b"encryption is very useful"


# Encrypt
ciphertext = f.encrypt(plaintext)
print(ciphertext)


# Decrypt
decryptedtext = f.decrypt(ciphertext)
print(decryptedtext)


key2 = b'8cozhW9kSi5poZ6TWFuMCV123zg-9NORTs3gJq_J5Do='
f2 = Fernet(key2)
ciphertext2 = b'gAAAAABc8Wf3rxaime-363wbhCaIe1FoZUdnFeIXX_Nh9qKSDkpBFPqK8L2HbkM8NCQAxY8yOWbjxzMC4b5uCaeEpqDYCRNIhnqTK8jfzFYfPdozf7NPvGzNBwuuvIxK5NZYJbxQwfK72BNrZCKpfp6frL8m8pdgYbLNFcy6jCJBXATR3gHBb0Y=
decrypted=f2.decrypt(ciphertext2)
print(decrypted)


message = b'encrypting is just as useful'
ciphertext3 = f2.encrypt(message)
print(ciphertext3)
decrypted3 = f2.decrypt(ciphertext3)
print(decrypted3)