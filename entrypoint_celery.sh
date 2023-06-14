#!/bin/bash
Xvfb :0 -screen 0 1280x1024x24 &
x11vnc -display :0 -N -forever -shared &

exec "$@"