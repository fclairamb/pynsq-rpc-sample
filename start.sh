#!/bin/sh

killall -9 nsqlookupd nsqd nsqadmin

[ -d logs ] || mkdir logs
[ -d data ] || mkdir data

nsqd -lookupd-tcp-address localhost:4160 -data-path data >logs/nsqd.log 2>&1 & # listening on 4150 + 4151
nsqlookupd >logs/nsqlookupd.log 2>&1 & # HTTP listening on 4160 + 4161
nsqadmin --lookupd-http-address localhost:4161 >logs/nsqadmin.log 2>&1 & # HTTP listening on 4171

python rpc-server.py &
python rpc-client.py &
