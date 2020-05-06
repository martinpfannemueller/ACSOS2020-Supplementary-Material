# Evaluation 2

The SDN evaluation has been conducted on four cloud machines:

* Host1 (SDN Controller, 10.0.1.3): 3 VCPUs, 4GB RAM
* Host2 (SMAE, 10.0.1.4): 1 VCPU, 2GB RAM
* Host3 (PK, 10.0.1.2): 2 VCPUs, 8GB RAM
* Host4 (Mininet Wifi, 10.0.1.5): 8 VCPUs, 16GB RAM

A private network in the network 10.0.1.0/24 was used. The network topology looked like this:

```
Host1 (10.0.1.3)+                  +Host3 (10.0.1.2)
                |                  |
                +-+Virtual Switch+-+
                |                  |
Host2 (10.0.1.4)+                  +Host4 (10.0.1.5)

```
