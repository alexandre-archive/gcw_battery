all: opk

clean:
	rm -rf temp battery.opk

opk:
	chmod 777 battery.py
	mkdir temp
	cp battery.py pyinotify.py battery.png default.gcw0.desktop temp
	mksquashfs temp battery.opk -all-root -noappend -no-exports -no-xattrs
	rm -rf temp
