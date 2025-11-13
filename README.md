# gitsecureseaux – Dossier de missions sécurité

## Objectif
Centraliser des engagements de réponse à incident / pentest menés dans le cadre du module « Sécurité réseaux ». Chaque sous-dossier contient les artefacts bruts (captures, binaires), les scripts d’analyse et un rapport opérationnel prêt à être livré au client.

## Périmètre actuel
- **`02-MyKeyMouse/`** – Analyse d’une compromission USB HID. Rapport focalisé sur l’exfiltration de frappes clavier et de mouvements souris à partir d’un PCAP fourni.
- **`challenge/`** – Jeux de données TLS (certificat, clé privée, capture réseau) et scripts d’aide (`analyze_cipher.py`, `test.sh`) pour auditer une configuration de chiffrement.

Chaque mission suit le même fil conducteur :
1. **Collecte** – Inventorier les preuves (pcap, archives, scripts) et valider leur intégrité.
2. **Analyse technique** – Reproduire les outils fournis, enrichir si besoin, tracer les actions menées.
3. **Reporting** – Documenter constats, impact métier, preuve exploit et recommandations durcies.

## Outils & prérequis
| Outil | Usage |
| --- | --- |
| `python3` (≥3.10) | Scripts d’analyse personnalisés (HID, TLS, parsing). |
| `tshark` | Extraction des flux bas niveau (HID, TLS records). |
| `openssl` / `nmap` | Vérifications cryptographiques (challenge TLS). |
| `gnuplot`/`matplotlib` | Visualisation d’événements pour preuves (ex. trajectoire souris). |

> Astuce : isolez vos dépendances par mission via `python3 -m venv .venv && source .venv/bin/activate`. Ajoutez toujours `.venv` dans le `.gitignore` pour éviter de contaminer l’historique.

## Structure type d’un rapport
1. **Résumé exécutif** – deux à trois phrases sur le risque observé.
2. **Portée & hypothèses** – périmètre testé, actifs concernés, limitations.
3. **Méthodologie** – outils, commandes clés, horodatages.
4. **Constats détaillés** – preuves, reproduction, impact.
5. **Recommandations** – actions correctives priorisées (P1 → P3).

Les READMEs de chaque dossier reprennent ce canevas afin de produire rapidement des livrables cohérents avec les attentes d’un pentester.
