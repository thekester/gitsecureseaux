tshark -r challenge.pcapng \
  -o tls.keys_list:"192.168.56.107,443,http,/home/test/Documents/challenge/target.com.key" \
  -Y 'http.request.method == "POST"' \
  -T fields -e frame.number -e http.file_data \
| while read frame hex; do
    decoded=$(echo "$hex" | xxd -r -p | python3 -c 'import sys,urllib.parse;print(urllib.parse.unquote(sys.stdin.read().strip()))')
    printf "%s -> %s\n" "$frame" "$decoded"
  done
