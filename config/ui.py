from colorama import Fore, Style


def printBanner():
    banner = '''
\t\t███████╗ ██████╗ █████╗ ███╗   ██╗██████╗ ██╗███████╗ ∬ 
\t\t██╔════╝██╔════╝██╔══██╗████╗  ██║██╔══██╗██║██╔════╝ ∬ 
\t\t███████╗██║     ███████║██╔██╗ ██║██████╔╝██║█████╗   ∬ scanPIE dx where x ＝ PIE {
\t\t╚════██║██║     ██╔══██║██║╚██╗██║██╔═══╝ ██║██╔══╝   ∬ [scanPortInformationEnumeration]
\t\t███████║╚██████╗██║  ██║██║ ╚████║██║     ██║███████╗ ∬ }
\t\t╚══════╝ ╚═════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝     ╚═╝╚══════╝ ∬ 
\n\t\t\t∫ Author: Salman Alwan ∫
    '''
    banner = banner.replace("█", Fore.LIGHTGREEN_EX + "█" + Fore.WHITE)
    banner = banner.replace("dx", Fore.LIGHTGREEN_EX + "dx" + Fore.WHITE)
    banner = banner.replace("x", Fore.LIGHTGREEN_EX + "x" + Fore.WHITE)
    banner = banner.replace("∫", Fore.LIGHTGREEN_EX + "∫" + Fore.WHITE)
    print(banner)