from colorama import Fore,Style
import os
import platform
from config.ui import printBanner
def handle_interrupt(signal, frame):
    clearConsole()
    printBanner()
    
    print("\nGoodbye! Thanks for using the program.")
    exit(0)

def clearConsole():
    operating_system = platform.system()
    if operating_system == "Windows":
        import subprocess
        subprocess.call('cls', shell=True)
    else:
        import os
        os.system('clear')
