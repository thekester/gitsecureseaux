# MyKeyMouse – Guide rapide

## Aperçu
- `MyKeyMouse.pcap` : capture USB HID fournie par l’énoncé Polytech.
- `extract_usb_hid.sh` : convertit les rapports `usb.capdata` en CSV (mouvements souris).
- `usb_hid_decoder.py` : reconstitue les frappes clavier exportées dans `usbkeystrok.txt`.

## Pré-requis
| Outil | Usage |
| --- | --- |
| `tshark` | Extraction des rapports HID à partir du PCAP. |
| `python3` (≥3.10) | Décodage clavier / scripts d’analyse. |
| `awk` | Post-traitement dans `extract_usb_hid.sh` (implémentation POSIX). |

## Extraction des mouvements souris
```bash
./extract_usb_hid.sh MyKeyMouse.pcap usb_hid_events.csv
# colonnes : frame,time_epoch,buttons,dx,dy,dwheel,x,y
```
Astuce : tracer `x` vs `y` (par ex. avec pandas/matplotlib) pour visualiser la signature ou le flag dessiné.

## Décodage clavier (usbkeystrok.txt)
```bash
# Générer usbkeystrok.txt depuis le PCAP si besoin :
tshark -r MyKeyMouse.pcap -Y "usb.capdata" -T fields -e usb.capdata > usbkeystrok.txt

# Décoder les rapports 8 octets :
./usb_hid_decoder.py usbkeystrok.txt > recovered.txt
```
Le script gère les touches Shift, Tab et Backspace et ignore les répétitions dues à une touche maintenue.

## Exemple de pipeline souris → visualisation
```bash
python3 - <<'PY'
import pandas as pd, matplotlib.pyplot as plt
df = pd.read_csv("usb_hid_events.csv")
cursor = df[df["buttons"] & 1 == 1]
plt.plot(cursor["x"], cursor["y"])
plt.gca().invert_yaxis(); plt.axis("equal"); plt.show()
PY
```

## Virtualenv (`.venv`)
```bash
python3 -m venv .venv          # création
source .venv/bin/activate      # activation (Linux/macOS)
# sous Windows (PowerShell) : .\.venv\Scripts\Activate.ps1
pip install --upgrade pip      # mise à jour
# installer vos dépendances éventuelles :
pip install pandas matplotlib  # (exemple pour la visualisation)
```
Pour quitter le venv : `deactivate`.

## Résolution attendue
1. Isoler les rapports HID pertinents (souris ou clavier).
2. Rejouer / visualiser la trajectoire afin d’identifier le message caché.
3. Documenter la méthodologie, les outils et les recommandations de sécurité dans le write-up final.
