#!/usr/bin/env bash

# Parse USB HID mouse traffic from a PCAP with tshark and export it as CSV.
# Usage: ./extract_usb_hid.sh [pcap_file] [output_csv]
# Defaults: pcap_file=MyKeyMouse.pcap, output_csv=usb_hid_events.csv
# The resulting CSV can be graphed to visualize the cursor path and reveal the flag.

set -euo pipefail

# Ensure tshark is available before doing anything else.
if ! command -v tshark >/dev/null 2>&1; then
  echo "Error: tshark is required but not found in PATH." >&2
  exit 1
fi

PCAP_PATH="${1:-MyKeyMouse.pcap}"
OUT_PATH="${2:-usb_hid_events.csv}"

# Catch obvious typos in the PCAP path early.
if [[ ! -f "$PCAP_PATH" ]]; then
  echo "Error: PCAP '$PCAP_PATH' not found." >&2
  exit 1
fi

# Extract raw HID reports, convert them to signed deltas, and accumulate absolute coordinates.
tshark -r "$PCAP_PATH" \
  -Y "usb.capdata" \
  -T fields \
  -e frame.number \
  -e frame.time_epoch \
  -e usb.capdata |
awk -F '\t' -v OFS=',' '
BEGIN {
  # CSV header consumed later by pandas / spreadsheets.
  print "frame,time_epoch,buttons,dx,dy,dwheel,x,y";
}
{
  frame=$1;
  time=$2;
  data=$3;
  gsub(/:/, "", data);   # Wireshark prints octets with ":", csv prefers plain hex.
  if (length(data) < 8) {
    next;
  }

  # Byte layout: [buttons][dx][dy][wheel]
  buttons=hex2u(substr(data, 1, 2));
  dx=hex2s(substr(data, 3, 2));
  dy=hex2s(substr(data, 5, 2));
  dw=hex2s(substr(data, 7, 2));

  # Accumulate coordinates so we can redraw the path later.
  x+=dx;
  y+=dy;

  print frame, time, buttons, dx, dy, dw, x, y;
}

function hex2s(h,   v) {
  # Convert unsigned byte to signed 2-complement value.
  v=hex2u(h);
  if (v >= 128) {
    v-=256;
  }
  return v;
}

function hex2u(h,   i, digit, val, c, table) {
  table="abcdef";
  val=0;
  # Manual hex parsing keeps the script POSIX-awk compatible.
  for (i=1; i<=length(h); i++) {
    c=substr(h, i, 1);
    if (c >= "0" && c <= "9") {
      digit=c+0;
    } else {
      c=tolower(c);
      digit=index(table, c);
      if (digit == 0) {
        digit=0;
      } else {
        digit+=9;
      }
    }
    val = val * 16 + digit;
  }
  return val;
}
' > "$OUT_PATH"

rows=$(($(wc -l < "$OUT_PATH") - 1))
printf "Wrote %s (%d HID samples).\n" "$OUT_PATH" "$rows"
