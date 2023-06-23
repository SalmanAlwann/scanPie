import argparse
import re
from config.utils import clearConsole
from config.scanner import scan_ports
from config.scanner import retPorts
from config.scanner import retSsl
from config.scanner import graph
from config.scanner import plot_port_counts
from config.scanner import counterOpen
from config.scanner import openPortsNoInfo
from config.scanner import versionList
from config.ui import printBanner
from colorama import Fore,Style
import os
import signal
from config.utils import handle_interrupt

signal.signal(signal.SIGINT, handle_interrupt)

class PortAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        port_list = []
        
        # Check if the input value is in the format "80" or "80,443,8080"
        if re.match(r'^\d+(,\d+)*$', values):
            ports = values.split(',')
            
            for port in ports:
                port_list.append(int(port))
        
        elif re.match(r'^\d+-\d+$', values):
            start_port, end_port = values.split('-')
            
            port_list = list(range(int(start_port), int(end_port)+1))
        else:
            raise argparse.ArgumentError(self, f"Invalid port value: {values}")
        
        setattr(namespace, self.dest, port_list)


class HostAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        host = ""
        value = values[0] 
        
        if re.match(r'^(\d{1,3}\.){3}\d{1,3}$', value):
            host = value
        elif re.match(r'^(https?://)?([a-zA-Z0-9-]+\.)*[a-zA-Z0-9-]+\.[a-zA-Z]{2,}(/[a-zA-Z0-9-._~:/?#[\]@!$&\'()*+,;=]*)?$', value):
            host = value
        else:
            raise argparse.ArgumentError(self, f"Invalid host value: {values}")
        
        setattr(namespace, self.dest, host)
        
class ThreadAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        threads = 1
        value = values[0]
        if int(value) >= 1:
            threads = int(value)
        else:
            raise argparse.ArgumentError(self, f"Invalid threads value: {values}")

        setattr(namespace, self.dest, threads)
    
if __name__ == "__main__":
    clearConsole()
    printBanner()
    parser = argparse.ArgumentParser()
    parser.add_argument('-port', '-p', metavar='PORT', action=PortAction, help=f'{Fore.LIGHTGREEN_EX}Ports to scan (e.g., -port 80,443 or -port80,443){Fore.WHITE}')
    parser.add_argument('-host', metavar="HOST", nargs=1,action=HostAction,help=f'{Fore.LIGHTGREEN_EX}{Fore.LIGHTGREEN_EX}host to scan (e.g., -hos 127.0.0.1 or -host http://example.com {Fore.WHITE}')
    parser.add_argument('-threads', metavar="THREADS", nargs=1,action=ThreadAction,help=f'{Fore.LIGHTGREEN_EX}integer number of threads to use{Fore.WHITE}')
    parser.add_argument('-ssl', action='store_true',help=f'{Fore.LIGHTGREEN_EX}enable ssl scan{Fore.WHITE}')
    parser.add_argument('-xml','-x', action='store_true',help=f'{Fore.LIGHTGREEN_EX}enable xml output{Fore.WHITE}')
    parser.add_argument('-csv', action='store_true',help=f'{Fore.LIGHTGREEN_EX}enable csv output{Fore.WHITE}')
    parser.add_argument('-json','-js', action='store_true',help=f'{Fore.LIGHTGREEN_EX}enable json output{Fore.WHITE}')
    parser.add_argument('-graph','-gp', action='store_true',help=f'{Fore.LIGHTGREEN_EX}enable graph output{Fore.WHITE}')
    parser.add_argument('-all', action='store_true',help=f'{Fore.LIGHTGREEN_EX}enable all output{Fore.WHITE}')
    parser.add_argument('-version', action='store_true',help=f'{Fore.LIGHTGREEN_EX}enable scanning for versions{Fore.WHITE}')
    parser.add_argument('-timeout', '-to', nargs=1, help=f'{Fore.LIGHTGREEN_EX}custom timeout{Fore.WHITE}')
    
    try:
        args, unknown_args = parser.parse_known_args()
        if unknown_args:
            raise argparse.ArgumentError(None, f"Unrecognized arguments: {', '.join(unknown_args)}")
        args = parser.parse_args()
        if not args.port or not args.host or not args.threads:
            parser.print_help()
            quit()
        if os.path.exists(f'output/{args.host}/{args.host}_ssl-info.txt'):
            # Delete the file
            os.remove(f'output/{args.host}/{args.host}_ssl-info.txt')
        if args.all:
            args.xml = True
            args.csv = True
            args.json = True
            args.graph = True
        scan_ports(args.host,args.port,args.threads,args.ssl,args.xml,args.csv,args.json,args.version,args.timeout)
        toPrint = retPorts()
        print('\n')
        if not os.path.exists(f'output/{args.host}'):
            os.makedirs(f'output/{args.host}')
        
        if os.path.exists(f'output/{args.host}/{args.host}_output.txt'):
            # Delete the file
            os.remove(f'output/{args.host}/{args.host}_output.txt')
        
        if len(toPrint) > 0:
            with open(f'output/{args.host}/{args.host}_output.txt', "w") as file:
                for port in toPrint:
                    print(f"\t {Fore.LIGHTGREEN_EX}%{Fore.WHITE} Found a port open at: {Fore.LIGHTGREEN_EX}{port}{Fore.WHITE}!")
                    file.write(f"{port}\n")
                file.close()
            for _ in retSsl():
                print(_)
            
            if(args.graph):
                graph(len(openPortsNoInfo)+1,args.host)
                plot_port_counts(args.host,len(openPortsNoInfo))
            for _ in versionList:
                print(_)
            print("\nData written to the file successfully.")
                    
        else:
            print(f"\t {Fore.LIGHTGREEN_EX}%{Fore.WHITE} Didn't find any {Fore.LIGHTGREEN_EX}open{Fore.WHITE} ports!")
               
        print('\n')
        
    except argparse.ArgumentError as e:
        print(f"Error: {e.message}")
        parser.print_help()