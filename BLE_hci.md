# Manual of BLE_hci.py commands

## help
```
usage:  [-h]
        {addr,adv,scan,init,dataLen,sendAcl,sinkAcl,connStats,phy,reset,listen,txTest,tx,txTestVS,rxTest,rx,endTest,end,txPower,txp,discon,dc,setChMap,cmd,readReg,writeReg,exit,quit,help,h}
        ...

positional arguments:
  {addr,adv,scan,init,dataLen,sendAcl,sinkAcl,connStats,phy,reset,listen,txTest,tx,txTestVS,rxTest,rx,endTest,end,txPower,txp,discon,dc,setChMap,cmd,readReg,writeReg,exit,quit,help,h}
    addr                Set the device address
    adv                 Send the advertising commands
    scan                Send the scanning commands and print scan reports. ctrl-c to exit
    init                Send the initiating commands to open a connection
    dataLen             Set the max data length
    sendAcl             Send ACL packets
    sinkAcl             Sink ACL packets, do not send events to host
    connStats           Get the connection stats
    phy                 Update the PHY in the active connection
    reset               Sends a HCI reset command
    listen              Listen for HCI events, print to screen
    txTest (tx)         Execute the transmitter test
    txTestVS (tx)       Execute the transmitter test
    rxTest (rx)         Execute the receiver test
    endTest (end)       End the TX/RX test, print the number of correctly received packets
    txPower (txp)       Set the TX power
    discon (dc)         Send the command to disconnect
    setChMap            Set the connection channel map to a given channel.
    cmd                 Send raw HCI commands
    readReg             Read register, device performs a memcpy from address and returns the value
    writeReg            Write register, device performs a memcpy to memory address
    exit (quit)         Exit the program
    help (h)            Show help message

optional arguments:
  -h, --help            show this help message and exit
```


## addr
```
usage:  addr [-h] addr

positional arguments:
  addr        Set the device address, ex: 00:11:22:33:44:55

optional arguments:
  -h, --help  show this help message and exit
```

## adv
```
usage:  adv [-h] [-i INTERVAL] [-c CONNECT] [-l LISTEN] [-s] [-m]

optional arguments:
  -h, --help            show this help message and exit
  -i INTERVAL, --interval INTERVAL
                        Advertising interval in units of 0.625 ms, 16-bit hex number 0x0020 - 0x4000, default: 0x60
  -c CONNECT, --connect CONNECT
                        Advertise as a connectable device, default: True
  -l LISTEN, --listen LISTEN
                        Listen for events 
                                "True" for indefinitely, ctrl-c to exit 
                                "False" to return 
                                number of seconds
  -s, --stats           Periodically print the connection stats if listening
  -m, --maintain        Setup an event listener to restart advertising if we disconnect
  ```

## cmd
```
usage:  cmd [-h] [-l] cmd

positional arguments:
  cmd           String of hex bytes LSB first
                ex: "01030C00" to send HCI Reset command

optional arguments:
  -h, --help    show this help message and exit
  -l, --listen  Listen for events indefinitely, ctrl-c to exit
```

## connStats
```
usage:  connStats [-h]

optional arguments:
  -h, --help  show this help message and exit
```

## dataLen
```
usage:  dataLen [-h]

optional arguments:
  -h, --help  show this help message and exit
```

## init
```
usage:  init [-h] [-i INTERVAL] [-t TIMEOUT] [-l LISTEN] [-s] [-m] addr

positional arguments:
  addr                  Address of peer to connect with, ex: 00:11:22:33:44:55 

optional arguments:
  -h, --help            show this help message and exit
  -i INTERVAL, --interval INTERVAL
                        Connection interval in units of 1.25 ms, 16-bit hex number 0x0006 - 0x0C80, default: 0x6
  -t TIMEOUT, --timeout TIMEOUT
                        Supervision timeout in units of 10 ms, 16-bit hex number 0x000A - 0x0C80, default: 0x64
  -l LISTEN, --listen LISTEN
                        Listen for events 
                                "True" for indefinitely, ctrl-c to exit 
                                "False" to return 
                                number of seconds
  -s, --stats           Periodically print the connection stats if listening
  -m, --maintain        Setup an event listener to restart the connection if we disconnect
  ```

## listen
```
usage:  listen [-h] [-t TIME] [-s]

optional arguments:
  -h, --help            show this help message and exit
  -t TIME, --time TIME  Time to listen in seconds, default: 0(indef)
  -s, --stats           Periodically print the connection stats if listening
```

## phy
```
usage:  phy [-h] phy

positional arguments:
  phy         
                  Desired PHY
                  1: 1M
                  2: 2M
                  3: S8 
                  4: S2
                  default: 1M
                  

optional arguments:
  -h, --help  show this help message and exit
```

## sendAcl
```
usage:  sendAcl [-h] packetLen numPackets

positional arguments:
  packetLen   Number of bytes per ACL packet, 16-bit decimal ex: 128, 0 to disable
  numPackets  Number of packets to send, 8-bit decimal ex: 255, 0 to enable auto-generate 

optional arguments:
  -h, --help  show this help message and exit
```

## sinkAcl
```
usage:  sinkAcl [-h]

optional arguments:
  -h, --help  show this help message and exit
```

## txPower
```
usage:  txPower [-h] [--handle HANDLE] power

positional arguments:
  power            Integer power setting in units of dBm

optional arguments:
  -h, --help       show this help message and exit
  --handle HANDLE  Connection handle, integer
```


