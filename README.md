# Python Rover

This project is build on the AlphaBot robot chassis 
It should work on just about any chassis with some pin number adjustments

+ Python 3
+ Flask
+ Opencv
+ Raspberry Pi 3B 
+ Pi Camera 
+ Xbox controller (but not an actual xbox controller because they are a mission to get going on a Pi)

Install some apt stuff (Just paste this into your terminal and go take a nap... :)
```
sudo apt-get update -yq; \
sudo apt-get install python-opencv -yq; \
sudo apt-get install python3-opencv -yq; \
sudo apt-get install python3-pip -yq; \
sudo apt-get install rpi.gpio -yq \
sudo apt-get install pigpio -yq; \
sudo apt-get install git -yq;
```

Then a few python libraries
```
sudo pip3 install flask; \
sudo pip3 install inputs; \
sudo pip3 install pigpio; \
sudo pip3 install python-socketio;
```

Setup the piopiod service
```
sudo nano /etc/systemd/system/pigpiod.service
```

Paste this in the new file
```
[Unit]
Description=Pigpio daemon
After=network.target syslog.target
StartLimitIntervalSec=60
StartLimitBurst=5
#StartLimitAction=reboot

[Service]
Type=simple
ExecStartPre=/sbin/sysctl -w net.ipv4.tcp_keepalive_time=300
ExecStartPre=/sbin/sysctl -w net.ipv4.tcp_keepalive_intvl=60
ExecStartPre=/sbin/sysctl -w net.ipv4.tcp_keepalive_probes=5
ExecStart=/usr/bin/pigpiod -g
ExecStop=
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Save and exit then 
```
sudo systemctl enable pigpiod.service
sudo systemctl start pigpiod.service
systemctl status pigpiod.service
```

The Pigpiod service should be running.

I also generally disable services I don't use to free some memory and CPU time
```
sudo systemctl disable bluetooth;
sudo systemctl disable avahi-daemon;
sudo systemctl disable triggerhappy;
sudo reboot
```

Clone this repository
```
git clone "https://github.com/JeBear76/Python-Rover.git"
```

Create the Configuration File
```
cd ./Python-Rover
python3 ./config_writer.py
```

If you are using the AlphaBot, you can just press enter until done.
If not, you will have to populate at least the pin numbers.

Test it with
```
python3 server.py
```

When the server starts, it will show you the IP address of your Raspberry (if you don't already know it).

From a computer on your wifi network, go to 
http://[IP of the Pi]:3001/webcontrol

If all went well, you should see a FPV of the robot, 2 controller buttons and 2 action buttons.

To start the server on boot,
```
sudo pip3 install uwsgi
```

Setup the python-rover service
```
sudo nano /etc/systemd/system/python-rover.service
```

Paste this in the new file
```
[Unit]
Description=uWSGI instance to serve python-rover
After=network.target

[Service]
User=pi
WorkingDirectory=/home/pi/Python-Rover
ExecStart=/usr/local/bin/uwsgi --socket 0.0.0.0:3001 --protocol=http -w python-rover:videoapp

[Install]
WantedBy=multi-user.target
```

Save and exit then 
```
sudo systemctl enable python-rover.service
sudo systemctl start python-rover.service
systemctl status python-rover.service
```

Happy roaming!