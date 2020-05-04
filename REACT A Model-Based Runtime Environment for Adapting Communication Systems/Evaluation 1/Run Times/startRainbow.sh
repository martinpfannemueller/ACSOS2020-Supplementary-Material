
atime () {
local precision="${1:-5}"
perl -MTime::HiRes=time -sne '
    BEGIN {$start = time} 
    printf "%.${prec}f %s", (time - $start), $_
' -- -prec="$precision"
}

cd /rainbow && export SOCAT_PORT=4242 && ./run-oracle.sh -a -p rainbow-gui.properties -nogui rainbow-example | atime > /rainbow/logs/rainbow-console.out
