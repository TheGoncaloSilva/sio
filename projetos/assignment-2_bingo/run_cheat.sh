#!/bin/bash

sh -c "python3.10 -m venv venv"

num_players=$1
N=$2

gnome-terminal --tab --title="Playing Area" --command="bash -c 'cd playing_area/ && python3.10 playing_area.py --N $2 --max_players $1; $SHELL'" \
               --tab --title="Caller"         --command="bash -c 'sleep .4 && source venv/bin/activate && cd caller && python3.10 caller.py;$SHELL'" \


for i in $(seq 1 $num_players); do
  gnome-terminal --tab --title="Player $i" --command="bash -c 'sleep .9 && source venv/bin/activate && cd player && python3.10 player.py;$SHELL'"
done
