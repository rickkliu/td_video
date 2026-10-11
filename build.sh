#!/usr/bin/env bash
set -euo pipefail
cd /workspace/ad_video

ffmpeg -y \
  -i clips/shot1.mp4 -i clips/shot2.mp4 -i clips/shot3.mp4 \
  -i clips/shot4.mp4 -i clips/shot5.mp4 -i clips/shot6.mp4 \
  -filter_complex "
[0:v]fps=30,setsar=1,format=yuv420p[v0];
[1:v]fps=30,setsar=1,format=yuv420p[v1];
[2:v]fps=30,setsar=1,format=yuv420p[v2];
[3:v]fps=30,setsar=1,format=yuv420p[v3];
[4:v]fps=30,setsar=1,format=yuv420p[v4];
[5:v]fps=30,setsar=1,format=yuv420p[v5];
[v0][v1]xfade=transition=fade:duration=0.6:offset=7.496[x1];
[x1][v2]xfade=transition=fade:duration=0.6:offset=14.992[x2];
[x2][v3]xfade=transition=fade:duration=0.6:offset=20.472[x3];
[x3][v4]xfade=transition=fade:duration=0.6:offset=27.968[x4];
[x4][v5]xfade=transition=fade:duration=0.6:offset=37.448[x5];
[x5]ass=/workspace/ad_video/assets/subtitles.ass[xt];
[xt]drawbox=x=0:y=0:w=1280:h=720:color=black@0.38:t=fill:enable=gt(t\,41.5)[xb];
[xb]fade=t=in:st=0:d=0.6,fade=t=out:st=44.7:d=0.844,format=yuv420p[vout];
[0:a][1:a]acrossfade=d=0.6:c1=tri:c2=tri[a1];
[a1][2:a]acrossfade=d=0.6:c1=tri:c2=tri[a2];
[a2][3:a]acrossfade=d=0.6:c1=tri:c2=tri[a3];
[a3][4:a]acrossfade=d=0.6:c1=tri:c2=tri[a4];
[a4][5:a]acrossfade=d=0.6:c1=tri:c2=tri[a5];
[a5]afade=t=in:st=0:d=1,afade=t=out:st=44.3:d=1.244[aout]
" \
  -map "[vout]" -map "[aout]" \
  -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p \
  -c:a aac -b:a 192k -ar 32000 -movflags +faststart \
  BEA_TransactionBanking_Ad.mp4

echo "DONE"
ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 BEA_TransactionBanking_Ad.mp4