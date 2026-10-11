#!/usr/bin/env bash
# Chunked render for TRUST ad — fresh node process per chunk avoids OOM.
cd /workspace/ad_video/motion
TOTAL=1236
CHUNK=80

render_lang() {
  local L=$1 W=$2
  local ci=0
  for ((i=0; i<TOTAL; i+=CHUNK)); do
    if (( (ci % 2) == W )); then
      local end=$((i+CHUNK)); (( end > TOTAL )) && end=TOTAL
      local last
      last=$(printf "f_%05d.png" $((end-1)))
      local att=0
      while [[ ! -f "frames_trust_$L/$last" && $att -lt 4 ]]; do
        node render_trust.js "lang=$L" "from=$i" "to=$end" >/dev/null 2>&1 || true
        ((att++))
      done
    fi
    ((ci++))
  done
}

for L in zh en; do
  render_lang "$L" 0 &
  render_lang "$L" 1 &
  wait
  echo "$L: $(ls frames_trust_$L | wc -l)/$TOTAL"
done
echo ALLDONE
