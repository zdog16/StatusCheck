from rich.console import Console
from rich.traceback import install
from rich.table import Table
from rich.text import Text
import pyperclip
import requests
import keyboard
import argparse
import json
import time
import os
import sys
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
        self.args = self.parser.parse_args()
        self.tableTitle = self.args.title
        self.singleIP = self.args.single
        self.recheckMode = self.args.recheck
        self.watchMode = self.args.watch
        self.manualEntry = self.args.manual
        self.watchCycle = 10

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
    
    def waitForCopy(self):
        while True:
            if keyboard.is_pressed('ctrl'):
                if keyboard.is_pressed('c'):
                    time.sleep(0.1)
                    return True
            elif keyboard.is_pressed('esc'):
                c.print("[-] Exiting... ", style="red")
                sys.exit()
    
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
    
    def getTableFromClipboard(self) -> None:
        c.print("[+] Copy the Table")
        self.waitForCopy()
        pasteDump = pyperclip.paste()
        RowSplit = pasteDump.split('\n')
        self.database = []
        for i in RowSplit:
            tempList = i.split('\t')
            DeviceName = tempList[0]
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

    
    def showTable(self) -> None:
        if self.tableTitle != None:
            table = Table(title=self.tableTitle)
        else:
            table = Table(title="Device")
        if self.singleIP == None or self.manualEntry:
            table.add_column("Device", justify="left")
        table.add_column("IP Addres", justify="center")
        table.add_column("Status", justify="center")

        for i in self.database:
            if i["status"] == "Online":
                statusStyle = "green"
            elif i["status"] == "Checking":
                statusStyle = "yellow"
            elif i["status"] == "Offline":
                statusStyle = "red"
            else:
                statusStyle = "white"
                
            if self.singleIP == None or self.manualEntry:
                table.add_row(i["device"], i["IP"], Text(i["status"], style=statusStyle, justify="center"))
            else:
                table.add_row(i["IP"], Text(i["status"], style=statusStyle, justify="center"))
        c.print(table)

    def generateStatistics(self) -> dict:
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
        return stats
        
    def buildDB(self) -> None:
        if self.singleIP != None:
            self.database = [{"device": "Device", "IP": self.singleIP, "status": "UnKnown"}]
        elif self.recheckMode:
            self.database = self.memory
        elif self.manualEntry:
            self.database = self.getTableFromUser()
        else:
            try:
                self.getTableFromClipboard()
            except KeyboardInterrupt:
                c.print("[+] Exiting...", style="red")
                exit()
        
        with open(self.memoryFilename, 'w') as file:
            json.dump(self.database, file)


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
            
        self.clear()
        self.showTable()
        stats = self.generateStatistics()
        c.print(f"Total of {stats['totalDevices']} Devices")
        c.print(f"{stats['onlineDevices']} or {stats['percentOnline']} Online")
        c.print(f"{stats['offlineDevices']} or {stats['percentOffline']} Offline")

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
        else:
            self.checkDB()

if __name__ == "__main__":
    scanner = Scanner()
    scanner.run()