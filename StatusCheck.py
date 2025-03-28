from rich.console import Console
from rich.traceback import install
from rich.table import Table
from rich.text import Text
import pyperclip
import requests
import detectKeys as keys
import argparse
import json
import time
import os
install()
c = Console()

class Scanner:
    def __init__(self) -> None:
        self.database = []
        self.memoryFilename = "mem_statusCheck.json"
        self.timeout = 1
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("-t", "--title", help="Optional Title for the displayed table")
        self.parser.add_argument("-s", "--single", help="Single Ip Mode")
        self.parser.add_argument("-r", "--recheck", action="store_true", help="Recheck the last list that was checked")
        self.parser.add_argument("-m", "--manual", action="store_true", help="Manually Enter IPs")
        self.parser.add_argument("-w", "--watch", action="store_true", help="Watch IP(s) unitl they come online")
        self.parser.add_argument("-p", "--ports", action="store_true", help="Outside Port Mode")
        self.parser.add_argument("-f", "--filter", help="Filter and display results (Offline, Online)")
        self.args = self.parser.parse_args()
        self.tableTitle = self.args.title
        self.singleIP = self.args.single
        self.portMode = self.args.ports
        self.recheckMode = self.args.recheck
        self.watchMode = self.args.watch
        self.manualEntry = self.args.manual
        self.filter = self.args.filter
        self.watchCycle = 10
        self.baseIP = ''

        try:
            with open(self.memoryFilename, 'r+') as file:
                self.memory = json.load(file)
        except FileNotFoundError:
            self.memory = []
            with open(self.memoryFilename, 'w') as file:
                pass
        except json.JSONDecodeError:
            self.memory = []
    
    def clear(self) -> None:
        os.system('cls')
    
    
    def ping(self, host) -> bool:
        try:
            response = requests.get(f"http://{host}", timeout=self.timeout)
            return response.status_code == 200
        except requests.exceptions.ConnectTimeout:
            return False
        except requests.exceptions.Timeout:
            return False
        except requests.exceptions.ReadTimeout:
            return False
        except requests.exceptions.ConnectionError:
            return False
    
    def getTableFromClipboard(self, ports=False) -> None:
        c.print("[+] Copy the Table")
        keys.waitForCopy()
        pasteDump = pyperclip.paste()
        RowSplit = pasteDump.split('\n')
        self.database = []
        for i in RowSplit:
            tempList = i.split('\t')
            DeviceName = tempList[0]
            if ports:
                IP = self.baseIP + ":" + tempList[1].replace('\r', '')
            else:
                IP = tempList[1].replace('\r', '')
            self.database.append({"device": DeviceName, "IP": IP, "status": "UnKown"})

    def getTableFromUser(self) -> None:
        self.database = []
        c.print("[+] Enter the IPs to check")
        while True:
            usrInput = input(">>")
            if usrInput != "":
                self.database.append({"device": "", "IP": usrInput, "status": "UnKnown"})
            else:
                break

    
    def showTable(self, filter="None") -> None:
        self.clear()
        if self.tableTitle != None:
            if self.filter != None:
                table = Table(title=f"{self.tableTitle} - Filtered for {self.filter}")
            else:
                table = Table(title=self.tableTitle)
        else:
            if self.filter != None:
                table  = Table(title=f"Devices - Filtered for {self.filter}")
            else:
                table = Table(title="Devices")
        if self.singleIP == None or self.manualEntry:
            table.add_column("Device", justify="left")
        table.add_column("IP Addres", justify="center")
        table.add_column("Status", justify="center")

        if self.portMode:
            table.add_row("Base IP", self.baseIP, "")

        for i in self.database:
            if i["status"] == "Online":
                statusStyle = "green"
            elif i["status"] == "Checking":
                statusStyle = "yellow"
            elif i["status"] == "Offline":
                statusStyle = "red"
            else:
                statusStyle = "white"
                
            if filter == "None" or i["status"] == filter:
                if self.singleIP == None or self.manualEntry:
                    if self.portMode:
                        table.add_row(i["device"], i["IP"].replace(self.baseIP, ""), Text(i["status"], style=statusStyle, justify="center"))
                    else:
                        table.add_row(i["device"], i["IP"], Text(i["status"], style=statusStyle, justify="center"))
                else:
                    table.add_row(i["IP"], Text(i["status"], style=statusStyle, justify="center"))
        
        c.print(table)

    def generateStatistics(self, alsoPrint=True) -> dict:
        stats = {}
        stats['totalDevices'] = len(self.database)
        stats['onlineDevices'] = 0
        for i in self.database:
            if i["status"] == "Online":
                stats['onlineDevices'] += 1
        stats['offlineDevices'] = len(self.database) - stats["onlineDevices"]
        onlinePercent = stats['onlineDevices'] / stats['totalDevices']
        stats['percentOnline'] = str(round((onlinePercent * 100), 1)) + "%"
        stats['percentOffline'] = str(round((100 - float(stats['percentOnline'].replace("%", ""))), 1)) + "%"

        if alsoPrint:
            c.print(f"Checked a total of {stats['totalDevices']} Devices")
            c.print(f"{stats['onlineDevices']} or {stats['percentOnline']} Online")
            c.print(f"{stats['offlineDevices']} or {stats['percentOffline']} Offline")

        return stats
    
    def saveDB(self) -> None:
        with open(self.memoryFilename, 'w') as file:
            json.dump(self.database, file)


    def buildDB(self) -> None:
        if self.singleIP != None:
            self.database = [{"device": "Device", "IP": self.singleIP, "status": "UnKnown"}]
        elif self.recheckMode:
            self.database = self.memory
        elif self.manualEntry:
            self.database = self.getTableFromUser()
        else:
            if self.portMode:
                c.print('Enter the Base IP address')
                self.baseIP = input('>')
            
            try:
                self.getTableFromClipboard(self.portMode)
            except KeyboardInterrupt:
                c.print("[+] Exiting...", style="red")
                exit()

        self.saveDB()


    def checkDB(self) -> None:
        for i in self.database:
            try:
                self.clear()
                i["status"] = "Checking"
                self.showTable()
                if self.ping(i["IP"]):
                    i["status"] = "Online"
                else:
                    i["status"] = "Offline"
            except KeyboardInterrupt:
                c.print("[+] Exiting...", style="red")
                exit()
            
        self.saveDB()
        

    def watchDB(self) -> None:
        allFound = False
        attemptCount = 0
        while not allFound:
            allFound = True
            attemptCount += 1
            for i in self.database:
                self.clear()
                i["status"] = "Checking"
                self.showTable()
                if self.ping(i["IP"]):
                    i["status"] = "Online"
                else:
                    i["status"] = "Offline"
                    allFound = False
            self.clear()
            self.showTable()
            c.print(f"Tried {attemptCount} times...")
            if not allFound:
                c.print("Waiting...", style="blue")
                try:
                    time.sleep(self.watchCycle)
                except KeyboardInterrupt:
                    c.print("Exiting...", style="red")
                    c.clear()
                    exit()

        c.print("All IPs Online", style="green")

    def run(self) -> None:
        self.buildDB()
        if self.watchMode:
            self.watchDB()
        elif self.filter != None:
            self.checkDB()
            self.clear()
            self.showTable(self.filter)
            self.generateStatistics()
        else:
            self.checkDB()
            self.showTable()
            self.generateStatistics()

if __name__ == "__main__":
    scanner = Scanner()
    scanner.run()