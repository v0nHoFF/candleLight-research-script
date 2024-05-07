This script is designed to run on linux, using the candleLight/candleLight-FD controller, connected and configured using the following command:
      For candlelight: ip link set can0 up type can bitrate 500000
      For candleLight-FD: ip link set can0 up type can bitrate 500000 dbitrate 5000000 fd on
For debug purposes, use the following command in a separate terminal window, to actually see what the script is doing:
      candump -ta -x can0
