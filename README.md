# ARP Spoofing

Questo script Python esegue **attacchi ARP spoofing** all'interno di una rete locale, con l’obiettivo di simulare condizioni di **Denial of Service (DoS)**.  
È pensato **esclusivamente per fini educativi**, per test di sicurezza in **ambienti controllati** e in contesti accademici.

> Università degli Studi di Bari    
> Corso di Laurea Magistrale in Sicurezza Informatica    
> Corso di Sicurezza nelle Reti e nei Sistemi Distribuiti

⚠️ **ATTENZIONE:** Qualsiasi utilizzo non autorizzato è potenzialmente illegale.  
Usa questo script **solo su reti di tua proprietà** o dove hai ottenuto **esplicito permesso**.

---

## Funzionalità

- Scansione della rete locale con `nmap`
- Esecuzione di attacchi ARP spoofing:
  - Singoli target
  - Multipli in parallelo (multithreading)
- Attivazione e disattivazione automatica dell’IP forwarding.


---

## Requisiti

- Python 3
- Sistema operativo Linux
- `nmap` (per la scansione)
- `arpspoof` (incluso in `dsniff`)
- Esecuzione con permessi di root

