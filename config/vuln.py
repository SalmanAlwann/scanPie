import subprocess

def scan_vulnerabilities(target, port):
    command = f'nmap -p {port} --script vulners.nse {target}'
    output = subprocess.check_output(command, shell=True, encoding='utf-8')
    vulnerabilities = []

    for line in output.splitlines():
        if 'VULNERABLE:' in line:
            vulnerability = line.split(':')[1].strip()
            vulnerabilities.append(vulnerability)

    return vulnerabilities

target = '127.0.0.1'  # Replace with the IP address or hostname of the host
port = 80  # Replace with the specific port you want to scan for vulnerabilities

vulnerabilities = scan_vulnerabilities(target, port)

if vulnerabilities:
    for vulnerability in vulnerabilities:
        print(f"Vulnerability: {vulnerability}")
else:
    print("No vulnerabilities found.")