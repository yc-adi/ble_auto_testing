# BLE Connection Test

## Connection procedure
![image](https://user-images.githubusercontent.com/110848915/200624837-a5285af5-bdd0-42da-a0a7-31a3a306965f.png)
<div align=""center">Figure x1 Central’s view of LL connection setup with CONNECT_IND</div>  

## Connection interval

![Connection interval](https://user-images.githubusercontent.com/110848915/200607648-efdca827-a7ed-41db-9521-03e41cc234be.png)
<div align=""center">Figure 1 CONNECT_REQ packet</div>    

The connection interval determines how fast the master will communicate with the slave. It is defined as the start of the last connection event and the start of the next connection event. In this test, the connection interval is 7.5 ms as shown in the Figure 1 CONNECT_REQ packet.  

![Master packet example](https://user-images.githubusercontent.com/110848915/200615053-bfc523a8-49cb-4acc-9d64-18fca31205d4.png)
<div align=""center">Figure 2 Master packet example</div>    

In the Figure 2, the master sent an empty packet to the slave. The total length of the packet is: preamble (1) + access address (4) + header (2) + payload (0) + CRC (3) = 10 Bytes.
In this test, it used 1 M PHY. 10 Bytes (80 bits) is 80 us.
Connection interval (7500) - master packet (80) - T_IFS (150) - slave ack (80) = 7190 us.  

![Delta time](https://user-images.githubusercontent.com/110848915/200620005-af62e756-ddcd-4e46-8cd1-827d1dc476c3.png)
<div align=""center">Figure 3 Delta time</div>    

Figure 3 shows that the delta times are between 7189 us and 7190 us which are matched with the calculation above.  


