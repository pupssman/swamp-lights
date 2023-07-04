Swamp Hub
---------

A central controlling point for:
    -- blinkers and other devices to connect to get commands and report events
    -- mobile apps / etc to connect to view state & issue mode changes
    -- play background sound based on modes

Howto
-----

0. ensure pulseaudio server is running in home os:
  1. see https://stackoverflow.com/a/29893375 / https://ubuntuforums.org/showthread.php?t=2442411
  2. test with `PULSE_SERVER=172.17.0.1 mplayer assets/room_00_0.mp3`
1. run dev: `docker compose up --build`
2. to enable sound loopback:
  1. install deps via `sudo apt install pavucontrol`
  2. enable via `pactl load-module module-loopback latency_msec=1`
3. to enable combine sink:
  1. enable via `pactl load-module module-combine-sink`
  2. disable via `pactl unload-module module-combile-sink`
