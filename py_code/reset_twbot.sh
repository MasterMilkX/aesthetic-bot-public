#!/bin/bash

# remove previous processes
echo "> KILLING PREVIOUS PROCESSES"
pkill -f -9 'error_monitor'
pkill -f -9 twit

#remove previous files
echo "> REMOVING PREVIOUS OUT FILES"
rm twit_p*.out

#reset p0 (level gen) and p1 (twitter poll)
echo "> RUNNING TWITTER BOT P0 & P1 SCRIPTS"
nohup python3 -u bot_twitter_sql_P0.py > twit_p0.out 2>&1 &
nohup python3 -u bot_twitter_sql_P1.py > twit_p1.out 2>&1 &

# run the error monitor
echo "> RUNNING THE ERROR MONITOR"
nohup python3 error_monitor.py > err_mon.out &
