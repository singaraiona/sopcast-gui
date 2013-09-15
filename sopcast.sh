#!/bin/bash

SOURCE=$1
export LD_LIBRARY_PATH=./
SOPBIN=sp-sc-auth
SOPPORT=3908
LOCALPORT=8908
SOPDIR=/home/volonter/sp-auth

PLAYERBIN=mplayer 
PLAYERSOURCE=http://localhost

pids=(`pgrep sopcast.sh`)
kill -9 pids[1]
pkill -9 ${SOPBIN}
pkill -9 ${PLAYERBIN}

if [ -z ${SOURCE} ]; then
    SOURCE=`zenity  --title "Source:" --entry --text "Sopcast source:"`
    if [ -z ${SOURCE}]; then
	exit 1
    fi
fi

cd ${SOPDIR}

exec ./${SOPBIN} ${SOURCE} ${SOPPORT} ${LOCALPORT} > /dev/null &2>1 &

sleep 5

while true; do

    if [ -z `pgrep ${SOPBIN}`]; then
	pkill -9 ${PLAYERBIN}
	zenity --error --text "Stream not found."
	exit 1
    fi

    ${PLAYERBIN} ${PLAYERSOURCE}:${LOCALPORT} > /dev/null
done

exit 0
