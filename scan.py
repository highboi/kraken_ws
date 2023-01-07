from scapy.all import *

def scan_network():
	ip = "192.168.88.0/24"

	ans, unans = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst=ip), timeout=2)

	for snd, rcv in ans:
		print("")
		print(rcv.sprintf(r"%Ether.src% - %ARP.psrc%"))

scan_network()
