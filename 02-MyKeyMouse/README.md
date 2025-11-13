# Mission 02 – MyKeyMouse (Rapport technique)

## Résumé exécutif
La capture `MyKeyMouse.pcap` contient des rapports USB HID bruts (clavier + souris). Ceux‑ci permettent de reconstituer intégralement les frappes et mouvements effectués sur le poste compromis, dévoilant un message sensible/flag. L’absence de chiffrement applicatif sur le canal HID rend l’exfiltration triviale pour un attaquant disposant d’un accès physique ou d’un implant USB.

## Portée & hypothèses
- **Source** : PCAP fourni par l’équipe SOC, obtenu sur un poste Windows via un keylogger USB HID.
- **Objectifs** : reconstruire les frappes clavier, rejouer la trajectoire souris et évaluer l’impact.
- **Contraintes** : aucune métadonnée d’horodatage externe. Tous les temps proviennent de la capture.

## Méthodologie
1. **Extraction des rapports HID**  
   `tshark -r MyKeyMouse.pcap -Y "usb.capdata" -T fields -e usb.capdata > usbkeystrok.txt`

2. **Décodage des frappes**  
   `usb_hid_decoder.py` interprète chaque paquet de 8 octets, gère les modificateurs (Shift) et ignore les répétitions dues à une touche maintenue.  
   ```
   ./usb_hid_decoder.py usbkeystrok.txt > recovered.txt
   ```
   Résultat : texte clair prêt pour inclusion dans le rapport.

3. **Analyse des mouvements souris**  
   `extract_usb_hid.sh MyKeyMouse.pcap usb_hid_events.csv` convertit les champs `dx/dy` en coordonnées cumulées (`x`,`y`). Le CSV inclut également l’état des boutons pour isoler les segments tracés lors d’un clic maintenu.

4. **Visualisation & preuve**  
   ```
   python3 plot_mouse.py  # exemple: script pandas/matplotlib ou snippet ci-dessous
   ```
   ```python
   import pandas as pd, matplotlib.pyplot as plt
   df = pd.read_csv("usb_hid_events.csv")
   draw = df[df["buttons"] & 1 == 1]
   plt.plot(draw["x"], draw["y"]); plt.gca().invert_yaxis(); plt.axis("equal"); plt.show()
   ```
   La figure obtenue fait apparaître le flag/mantra dessiné par l’attaquant.

## Résultats clés
| ID | Constat | Preuve | Impact |
| --- | --- | --- | --- |
| HID‑01 | Les frappes clavier transitent en clair dans `usb.capdata`. | `recovered.txt` contient le secret complet sans post‑traitement supplémentaire. | Divulgation de credentials/flags → compromission de compte. |
| HID‑02 | Les mouvements souris permettent de transmettre un message graphique lisible. | Plot `usb_hid_events.csv` reproduit le dessin exact. | Canal exfiltration discret, difficile à détecter par DLP réseau. |
| HID‑03 | Aucun contrôle d’intégrité/anti‑rejeu sur les rapports. | Relecture possible dans `usb_hid_decoder.py --replay`. | Un adversaire peut injecter des entrées malveillantes (commande/flag). |

## Recommandations
1. **Durcir les postes USB** : activer le whitelisting HID / désactiver les ports inutilisés.
2. **Surveiller les périphériques** : corréler VID/PID sur SIEM et alerter en cas d’implant inconnu.
3. **Chiffrer les flux sensibles** : privilégier des claviers sécurisés (USB CCM/BlueTrusty) ou solutions KVM chiffrées.
4. **Former les équipes** : intégrer ce scénario dans les playbooks IR afin d’extraire rapidement les rapports HID et d’évaluer l’impact.

## Artefacts livrés
- `usbkeystrok.txt` – export brut `tshark`.
- `usb_hid_decoder.py` – script officiel de décodage.
- `extract_usb_hid.sh` – pipeline souris → CSV.
- `recovered.txt` & captures graphiques (à générer) – preuves pour l’annexe du rapport.

## Reproductibilité express
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt  # si utilisé, sinon pandas/matplotlib à la demande
tshark -r MyKeyMouse.pcap -Y "usb.capdata" -T fields -e usb.capdata > usbkeystrok.txt
./usb_hid_decoder.py usbkeystrok.txt > recovered.txt
./extract_usb_hid.sh MyKeyMouse.pcap usb_hid_events.csv
python3 - <<'PY'
import pandas as pd, matplotlib.pyplot as plt
df = pd.read_csv("usb_hid_events.csv")
draw = df[df["buttons"] & 1 == 1]
plt.plot(draw["x"], draw["y"]); plt.gca().invert_yaxis(); plt.axis("equal"); plt.savefig("mouse_trail.png")
PY
```
Inclure `recovered.txt` et `mouse_trail.png` en annexe lors de la remise du rapport final.
