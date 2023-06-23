from concurrent.futures import ThreadPoolExecutor
import socket
from tqdm import tqdm
import ssl
from colorama import Fore
import xml.etree.ElementTree as ET
import csv
import os
import json
import networkx as nx
import PIL
from PIL import Image
from pathlib import Path
import matplotlib.pyplot as plt
import nmap

openPorts = []
openPortsNoInfo = []
sslMessage=[]
counterOpen = 1
versionList = []
versionListClear = []
def get_port_name(port):
        try:
            return socket.getservbyport(port)
        except OSError:
            return "unknown"

def get_service_info(host,port):
       
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            s.connect((host, port))
            banner = s.recv(1024)
            s.close()
            return banner.decode()
        except:
            return "No info returned"

def scan_port_version(target, port):
    target = socket.gethostbyname(target)
    nm = nmap.PortScanner()
    nm.scan(target, str(port), arguments='-sV')

    service = nm[target]['tcp'][port]
    if service['state'] == 'open':
        service = nm[target]['tcp'][port]
        service_name = service['name']
        product = service['product']
        version = service['version']
        extrainfo = service['extrainfo']
        #print(f"{port}/tcp  open  {service['name']}  {service['product']} {service['version']}")
        versionList.append(f"\n\t {Fore.LIGHTGREEN_EX}%{Fore.WHITE} {port}{Fore.LIGHTGREEN_EX}/{Fore.WHITE}tcp  {Fore.LIGHTGREEN_EX}open{Fore.WHITE}  {service_name}  {product} {Fore.LIGHTGREEN_EX}{version}{Fore.WHITE} {Fore.LIGHTGREEN_EX}{extrainfo}{Fore.WHITE}\n")
        versionListClear.append(f'{port}/tcp  open  {service_name}  {product} {version} {extrainfo}')
    else:
        #print(f"{port}/tcp  closed")
        pass

def get_ssl_info(host,port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ssl_sock = ssl.wrap_socket(s)
        ssl_sock.connect((host, port))
        with open(f'output/{host}/{host}_ssl-info.txt', 'a') as f:
            f.write(f"SSL info for port {port}:\n\tCertificate: {ssl_sock.getpeercert()}\n\tCipher: {ssl_sock.cipher()}\n\n\n")
            f.close()
        sslMessage.append(f"\n\t{Fore.LIGHTGREEN_EX} %{Fore.WHITE} SSL info for port {Fore.LIGHTGREEN_EX}{port}{Fore.WHITE}:\n\t\t{Fore.LIGHTGREEN_EX}Certificate{Fore.WHITE}: {ssl_sock.getpeercert()}\n\t\t{Fore.LIGHTGREEN_EX}Cipher{Fore.WHITE}: {ssl_sock.cipher()}\n\n\n")
        ssl_sock.close()
    except:
        return ""
def my_task(host, port, ssl,version,to:None,pbar):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)      
        if(to == None):  
            sock.settimeout(1)      
        else:
            sock.settimeout(int(to[0])) 
        result = sock.connect_ex((host, port))
        
        if result == 0:
            global msg
            global counterOpen
            name = get_port_name(port)
            service = get_service_info(host,port)
            counterOpen+=1
            if(ssl == True):
                msg = get_ssl_info(host,port)
            openPorts.append(f'port {port} ({name}) | {service}')
            openPortsNoInfo.append(f'{port}')
            if(version == True):
                scan_port_version(host,port)
            
        else:
            pass
        
        sock.close()
        pbar.update(1)
    
    except socket.error:
        print(f"Could not connect to {host}:{port}")

def scan_ports(host: str,r: int,t: int,ssl:bool,xml:bool,csv:bool,json:bool,version:bool,to:None):
    # Create a ThreadPoolExecutor with the specified number of threads
    with tqdm(total=len(r), desc="Scanning Ports") as pbar:
        if(len(r) == 1):
            my_task(host,r[0],ssl,version,to,pbar)
        else:
            with ThreadPoolExecutor(max_workers=int(t)) as executor:
                # Submit tasks to the executor
                futures = [executor.submit(my_task, host, port,ssl,version,to,pbar) for port in r]

                # Wait for all tasks to complete
                for future in futures:
                    future.result()
    saveOutPuts(host,xml,csv,json)
    
def graph(open,ho):
    router = Image.open('icons/router_black_144x144.png')
    portimage = Image.open('icons/ethernet_on1600.png')
    
    G = nx.Graph()
    G.add_node("router")
    jk=1
    data = {}
    icons = {
    "router": "icons/router_black_144x144.png",
    "port": "icons/ethernet_on1600.png"
    }
    images = {k: PIL.Image.open(fname) for k, fname in icons.items()}
    for i in range(1, open):
        G.add_node(f"port_{i}", image=images["port"])
    for u in range(1,open):
        G.add_edge("port_"+str(u),"router")
    for j in range(1,open):
        data[f'port_{j}'] = f'{openPortsNoInfo[jk-1]}'
        nx.set_node_attributes(G, {f"port_{j}": {"info": f"{openPortsNoInfo[jk-1]}", "description": ""}})
        jk+=1
#    for k in range(1,open):
#        nx.set_node_attributes(G, {f"port_{k}": {"image": portimage}})
    nx.set_node_attributes(G, {f"router": {"image": router}})
    nx.set_node_attributes(G, {"router": {"info": "Node 1", "description": "This is node 1"}})
    node_info = nx.get_node_attributes(G, 'info')
    node_description = nx.get_node_attributes(G, 'description')
    node_image = nx.get_node_attributes(G, 'image')
    labels = {node: f"{node_info[node]}\n{node_description[node]}" for node in G.nodes()}
    
    nx.set_node_attributes(G, data, "data")
    fig, ax = plt.subplots()

    # Draw the graph with labels
    #nx.draw(G, labels=labels, ax=ax)

    # Iterate over the nodes and add the images
    """for node, image in node_image.items():
        ax.imshow(image, extent=(-0.5, 0.5, -0.5, 0.5), zorder=1, alpha=0.5)
    """
    
    pos = nx.spring_layout(G, seed=1734289230)
    #fig, ax = plt.subplots()
    
    nx.draw_networkx_edges(
    G,
    pos,
    ax=ax,
    arrows=True,
    arrowstyle="-",
    min_source_margin=15,
    min_target_margin=15,
    )
    nx.draw_networkx_labels(G, pos, labels=data)
    
    
    # Transform from data coordinates (scaled between xlim and ylim) to display coordinates
    tr_figure = ax.transData.transform
    # Transform from display to figure coordinates
    tr_axes = fig.transFigure.inverted().transform

    # Select the size of the image (relative to the X axis)
    icon_size = (ax.get_xlim()[1] - ax.get_xlim()[0]) * 0.025
    icon_center = icon_size / 2.0

    # Add the respective image to each node
    for n in G.nodes:
        xf, yf = tr_figure(pos[n])
        xa, ya = tr_axes((xf, yf))
        # get overlapped axes and plot icon
        a = plt.axes([xa - icon_center, ya - icon_center, icon_size, icon_size])
        a.imshow(G.nodes[n]["image"])
        a.axis("off")
    nx.draw(G, labels=labels)
    plt.savefig(f"output/{ho}/open_ports-map.png")
    #plt.show()

def plot_port_counts(hosts, open_ports):
    fig, ax = plt.subplots()
    #ax.bar(hosts, open_ports, label='Closed')
    ax.bar(hosts,open_ports, label='Open')
    ax.set_xlabel('Host')
    ax.set_ylabel('Port Count')
    ax.set_title('Port Scan Results')
    ax.legend()
    plt.savefig(f"output/{hosts}/open_ports-graph.png")
    

def saveOutPuts(host,xml:bool,csvv:bool,jsonn:bool):
    if not os.path.exists(f'output/{host}'):
        os.makedirs(f'output/{host}')
    output_file = f"output/{host}/{host}_raw-output.txt"
    if os.path.exists(output_file):
        os.remove(output_file)
    with open(output_file, "w") as file:
        for _ in openPortsNoInfo:
            file.write(f"{_}\n")
    if(len(versionListClear) > 0):
        if not os.path.exists(f'output/{host}'):
            os.makedirs(f'output/{host}')
        output_file = f"output/{host}/{host}_versions-output.txt"
        if os.path.exists(output_file):
            os.remove(output_file)
        with open(output_file, "w") as file:
            for _ in versionListClear:
                file.write(f"{_}\n")
    if(xml): 
        root = ET.Element('ports')
        for port in openPorts:
            port_element = ET.SubElement(root, 'port')
            port_element.text = str(port)
            
        tree = ET.ElementTree(root)

        # Write the XML tree to a file
        if not os.path.exists(f'output/{host}'):
            os.makedirs(f'output/{host}')

        output_file = f"output/{host}/{host}_output.xml"

        if not os.path.exists(output_file):
            open(output_file, "w").close()
        tree.write(f"output/{host}/{host}_output.xml")

    if(csvv):
        with open(f"output/{host}/{host}_output.csv", 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerow(['port', 'status'])
            for result in openPorts:
                writer.writerow([result, "open"])

    if(jsonn):
        with open(f"output/{host}/{host}_output.json", 'w') as json_file:
            json.dump(openPorts, json_file, indent=4)

def retPorts():
    return openPorts

def retSsl():
    return sslMessage
