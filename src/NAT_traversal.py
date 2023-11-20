from minimal import Minimal, int_or_str
import stun
import argparse
import sounddevice as sd

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument("-n", "--get-endpoint-nat", action="store_true", help="Print public endpoint and NAT type")
parser.add_argument("-d", "--list-devices", action="store_true", help="Print the available audio devices and quit")

class NAT_traversal(Minimal):
    def __init__(self):
        super().__init__()
        self.nat_type, self.external_ip, self.external_port = stun.get_ip_info(stun_host='stun.l.google.com')
        self.our_nat_type = self.get_nat_type()

    def get_nat_type(self):
        nat_type1, external_ip1, external_port1 = stun.get_ip_info(stun_host='stun.l.google.com')
        nat_type2, external_ip2, external_port2 = stun.get_ip_info(stun_host='stun.l.google.com')

        if external_port1 == external_port2:
            return "Cone"
        
        else:
            return "Symmetric"

if __name__ == '__main__':
    args = parser.parse_known_args()[0]

    if args.list_devices:
        print("Available devices:")
        print(sd.query_devices())
        quit()
        
    n = NAT_traversal()

    if args.get_endpoint_nat:
        print("NAT type (self-determined): " + n.our_nat_type)
        print("NAT type (STUN servers): " + n.nat_type)
        print("Public IP: " + n.external_ip)
        print("Port: " + str(n.external_port))

    else:
        try:
            n.run()
        except KeyboardInterrupt:
            parser.exit("\nSIGINT received")
        finally:
            n.print_final_averages()

