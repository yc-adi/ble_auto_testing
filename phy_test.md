# PHY switching time test

## LE 1M PHY, 2M PHY, and Coded PHY
The physical layer is the bottom layer of the Bluetooth protocol stack. The physical parameters of the radio transmission and reception determine how a bit (0 or 1) is represented over the air.  

The supported PHYs include 1M, 2M, and Coded PHY (S=2 or S=8).  

LE 1M PHY transfers the data over the mandatory symbol rate of 1 mega symbol per second, where each symbol represents 1 bit. Hence, the bit rate is 1 Mb/s.  
LE 2M PHY is similar but the mandatory symbol rate is 2 mega symbol per second and corresponding bit rate is 2 Mb/s.  

In many applications, longer ranges are required. With the TX power unchanged, this can be achieved by sacrificing the data throughput in the LE Coded PHY.    
The LE Coded PHY can be operated with two data rates:  
*S2 (S=2)*: in this mode, each bit is represented by two symbols. Thus, the data rate is 1M/2=500kbps. In this mode the range is roughly doubled compared to the LE 1M PHY.  
*S8 (S=8)*: In LE Coded S8 (S=8) mode, each bit is represented by eight symbols. The data rated is reduced to 1M/8=125kbps. But the range is roughly quadrupled compared to the LE 1M PHY.  

## Changing PHY
BLE_hci.py provides the command "phy" to change the PHY by HCI command.
```commandline
>>> phy -h
usage:  phy [-h] phy

positional arguments:
  phy         
                  Desired PHY
                  1: 1M
                  2: 2M
                  3: S8 
                  4: S2
                  default: 1M
```
The internal HCI implementation looks like the following.
```commandline
2022-11-28 14:47:18.347459 - DUT 1: phy 2
2022-11-28 14:47:18.348065 > 0132200700000002020000
2022-11-28 14:47:18.436944 < 040F0400013220
2022-11-28 14:47:18.469101 < 043E060C0000000202

2022-11-28 14:48:04.556294 - DUT 1: phy 3
2022-11-28 14:48:04.556503 > 0132200700000004040200
2022-11-28 14:48:04.661120 < 040F0400013220
2022-11-28 14:48:04.729899 < 043E060C0000000303
2022-11-28 14:48:04.767343 < 043E0B0700001B00900A1B00900A

2022-11-28 14:48:50.786839 - DUT 1: phy 4
2022-11-28 14:48:50.787062 > 0132200700000004040100
2022-11-28 14:48:50.824143 < 040F0400013220
2022-11-28 14:48:50.913090 < 043E060C0000000303
2022-11-28 14:48:50.929239 < 043E0B0700001B00900A1B00900A
```

## Captured packet example
The following picture shows the captured packets when changing the LE PHY 1M to 2M.  
![Changing from 1M to 2M](https://user-images.githubusercontent.com/110848915/204564910-47868b31-cff3-44e1-b0d3-e4caf234c724.png)


