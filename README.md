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
paste this in the new file
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

Finally
```
cd ./Python-Rover
python3 server.py
```

