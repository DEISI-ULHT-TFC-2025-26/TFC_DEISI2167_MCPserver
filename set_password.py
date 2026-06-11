import secrets
import string
import hashlib

def gerar_nova_password():
    # Gera uma password aleatória de 16 caracteres (letras e números)
    alfabeto = string.ascii_letters + string.digits
    nova_pwd = ''.join(secrets.choice(alfabeto) for i in range(16))
    
    # Transforma a password num Hash SHA-256 por segurança
    pwd_hash = hashlib.sha256(nova_pwd.encode()).hexdigest()
    
    # Guarda apenas o Hash num ficheiro oculto
    with open('.admin_secret', 'w') as f:
        f.write(pwd_hash)
        
    print("\n" + "="*40)
    print("NOVA PASSWORD DE ADMIN GERADA")
    print("="*40)
    print(f"Utilizador: admin")
    print(f"Password:   {nova_pwd}")
    print("="*40)
    print("Guarde esta password! Ela não voltará a ser mostrada.")
    print("Se a perder, terá de correr este script novamente.\n")

if __name__ == "__main__":
    gerar_nova_password()