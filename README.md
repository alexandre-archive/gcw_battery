# GCW Battery

GCW Graphic battery application using PyGame

### Requirements

- Python 2.7
- PyGame
- GCW Zero Toolchain

### Build

`make` will generate an *opk* file.

### Testing

On your PC:

```export PYTHONPATH=$PYTHONPATH:~/yourpath/gcw_battery
cd test
python test.py```

If you want to use your battery status just change `battery.GCW_BATTERY_FILE = 'uevent'` to `GCW_BATTERY_FILE = '/sys/class/power_supply/BAT0/uevent'`, where `0` is your battery number.

### Screenshot

![full][1]

![half][2]

![empty][3]

  [1]: http://i.imgur.com/ZS8tE4a.png
  [2]: http://i.imgur.com/zpxafTy.png
  [3]: http://i.imgur.com/eDTTt4G.png

### Note

Status is aways Unknown. For some no reason it's never updated.
