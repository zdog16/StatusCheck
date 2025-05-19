from rich.console import Console
from rich.traceback import install
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text
import pyperclip
import requests
import keyboard
import argparse
import subprocess
import json
import time
import sys
import os
install()
c = Console()

class toolkit:
    def __init__(self) -> None:
        pass

    def waitForCopy(self) -> bool:
        while True:
            if keyboard.is_pressed('ctrl'):
                if keyboard.is_pressed('c'):
                    while keyboard.is_pressed('c'):
                        pass
                    return True
            elif keyboard.is_pressed('esc'):
                c.print("[+] Escape Key Detected, Program terminated", style="red")
                sys.exit()
    
    def buildMenu(options) -> str:
        curOption = 1
        if type(options) == list:
            for item in options:
                c.print(f"{curOption}) {item}")
                curOption += 1
        elif type(options) == dict:
            keys = []
            for item in options:
                c.print(f"{curOption}) {item} - {options[item]}")
                curOption += 1
                keys.append(item)
        
        while True:
            try:
                usrSelection = int(input(">"))
            except ValueError:
                c.print("Please enter a number", style="red")
            
            if usrSelection < 1 or usrSelection > len(options):
                c.print("Please Enter a Valid selection", style="red")
            else:
                break
        
        if type(options) == list:
            return options[usrSelection - 1]
        elif type(options) == dict:
            return keys[usrSelection - 1]
        
    def getStyle(status):
        if status == "Offline":
            return "red"
        elif status == "Online":
            return "green"
        else:
            return "white"

class ProjectBuilder:
    def __init__(self) -> None:
        self.database = []
        self.projectName = []
        self.sections = []
        self.sectionNames = []
        self.tools = toolkit()

    def saveDB(self) -> None:
        with open(self.projectName + ".json", "w") as file:
            json.dump(self.database, file)

        c.print(f"[+] Database File Written to {self.projectName + '.json'}", style="green")

        
    def buildSectionsTable(self, showNumbers=False) -> None:
        curOption = 1
        table = Table(title=self.projectName)
        if showNumbers:
            table.add_column("#")
        table.add_column("Section")
        for section in self.sections:
            if showNumbers:
                table.add_row(str(curOption), section["name"])
            else:
                table.add_row(section["name"])        
            curOption += 1
        c.print(table)


    def buildProjectDB(self) -> None:
        self.projectName = Prompt.ask("What is the Project Name?")

        while True:
            c.clear()
            self.buildSectionsTable()
            usrSelection = toolkit.buildMenu(["Add Section", "Replace Section", "Delete Section", "Save Project DB"])
            
            if usrSelection == "Add Section":
                name = Prompt.ask("What is the section name?")
                self.sectionNames.append(name)
                c.print("Copy the Section Data")
                self.tools.waitForCopy()

                rowSplit = pyperclip.paste().split("\n")
                tempDatabase = []
                for i in rowSplit:
                    tempList = i.split('\t')
                    tempDatabase.append({"device": tempList[0], "IP": tempList[1].replace("\r", ""), "responseStatus": "UnKnown", "pingStatus": "UnKnown"})

                self.sections.append({"name": name, "data": tempDatabase})    

            elif usrSelection == "Replace Section":
                c.clear()
                c.print("[?] Which Section do you want to delete?")
                
                pass

            elif usrSelection == "Delete Section":
                ## Delete Section
                pass
                
            elif usrSelection == "Save Project DB":
                self.saveDB()
                break

class Scanner:
    def __init__(self, project=None) -> None:
        try:
            with open("StatusCheck_Settings.json", "r") as settingsFile:
                self.settings = json.load(settingsFile)
        except FileNotFoundError:
            with open("StatusCheck_Settings.json", "w") as settingsFile:
                self.settings = {"checkPing": True, "checkResponse": True, "defaultFilter": "", "projectName": ""}
                json.dump(self.settings, settingsFile)

        self.database = []
        self.memoryFilename = "mem_statusCheck.json"
        self.projectDatabase = []
        self.projectName = project
        self.timeout = 1
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument("-t", "--title", help="Optional Title for the displayed table")
        self.parser.add_argument("-s", "--single", help="Single Ip Mode")
        self.parser.add_argument("-r", "--recheck", action="store_true", help="Recheck the last list that was checked")
        self.parser.add_argument("-m", "--manual", action="store_true", help="Manually Enter IPs")
        self.parser.add_argument("-w", "--watch", action="store_true", help="Watch IP(s) unitl they come online")
        self.parser.add_argument("-p", "--ports", action="store_true", help="Outside Port Mode")
        self.parser.add_argument("-f", "--filter", help="Filter and display results (Offline, Online)")
        self.parser.add_argument("-b", "--build", action="store_true", help="Build Project Database")  
        self.parser.add_argument("-x", "--settings", action="store_true", help="Modify Program Settings")
        self.args = self.parser.parse_args()
        self.tableTitle = self.args.title
        self.singleIP = self.args.single
        self.portMode = self.args.ports
        self.recheckMode = self.args.recheck
        self.watchMode = self.args.watch
        self.manualEntry = self.args.manual
        if self.args.filter == None:
            self.filter = self.settings["defaultFilter"]
        else:
            self.filter = self.args.filter
        self.filter = self.args.filter
        self.checkPing = self.settings["checkPing"]
        self.checkResponse = self.settings["checkResponse"]
        self.buildProjectMode = self.args.build
        self.changeSettings = self.args.settings
        self.watchCycle = 10
        self.baseIP = ''
        self.tools = toolkit()

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
    
    def modifySettings(self) -> None:
        while True:
            table = Table(title="Script Settings", show_lines=True)
            table.add_column("#", justify="center")
            table.add_column("Setting", justify="center")
            table.add_column("Value", justify="center")
            curOption = 1
            keys = []
            for setting in self.settings:
                table.add_row(str(curOption), setting, str(self.settings[setting]))
                keys.append(setting)
                curOption += 1
            table.add_row(str(curOption), "Save and Exit")
            keys.append("exit")
        
            self.clear()
            c.print(table)
            usrSelection = keys[int(input(">")) - 1]
            if usrSelection == "exit":
                break
            elif type(self.settings[usrSelection]) == bool:
                c.print("Select New Value")
                self.settings[usrSelection] = toolkit.buildMenu(["Set to True", "Set to False"]) == "Set to True"
            else:
                c.print("Enter a new Value")
                self.settings[usrSelection] = input(">")
        
        with open("statusCheck_Settings.json", "w") as file:
            json.dump(self.settings, file)
        

    def checkWebServer(self, host) -> bool:
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
        
    def ping(self, host, count=1) -> bool:
        command = ['ping', '-n', str(count), host]
        return subprocess.call(command) == 0
    
    def checkDevice(self, host) -> bool:
        if self.checkPing:
            if self.ping(host):
                return "Online"
        if self.checkResponse:
            if not self.checkWebServer(host):
                if self.ping(host):
                    return "Responding"
                else:
                    return "Offline"
            else:
                return "Online"

    def verifyIP(IP=str):
        octets = IP.split(".")

        # Check that There are exactly 4 Octets
        if len(octets) != 4:
            return False, "To Many Octets"

        # Verify each Octet is a number
        for i in octets:
            try:
                octets[octets.index(i)] = int(i)
            except ValueError:
                return False, f"Octet {i} is not a number"

        # Verify each Octet is between 0 and 254
        for i in octets:
            if i > 254 or i < 0:
                return False, f"Octet {i} is outside acceptable range"
        
        # Verify that the first Octet is not 0
        if octets[0] == 0:
            return False, "First Octet is outside of the acceptable range"

        # Verify that the last Octet is not 0
        if octets[3] == 0:
            return False, "Last Octet is outside of the acceptable range"
        
        # All conditions passed
        return True, "Valid"

    
    def getTableFromClipboard(self, ports=False) -> None:
        c.print("[+] Copy the Table")
        self.tools.waitForCopy()
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
            self.database.append({"device": DeviceName, "IP": IP, "responseStatus": "UnKown", "pingStatus": "UnKnown"})

    
    def getTableFromUser(self) -> None:
        self.database = []
        c.print("[+] Enter the IPs to check")
        while True:
            usrInput = input(">>")
            if usrInput != "":
                self.database.append({"device": "", "IP": usrInput, "responseStatus": "UnKnown", "pingStatus": "UnKnown"})
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
        if self.checkPing:
            table.add_column("Ping", justify="center")
        if self.checkResponse:
            table.add_column("HTTP", justify="center")

        if self.portMode:
            table.add_row("Base IP", self.baseIP, "")

        for i in self.database:
            pingStyle = toolkit.getStyle(i["pingStatus"])
            responseStyle = toolkit.getStyle(i["responseStatus"])
                
            if filter == "None" or i["responseStatus"] == filter:
                row = [i["device"]]
                if self.singleIP == None or self.manualEntry:
                    if self.portMode:
                        row.append(i["IP"].replace(self.baseIP, ""))
                    else:
                        row.append(i["IP"])

                if self.checkPing:
                    row.append(Text(i["pingStatus"], style=pingStyle, justify="center"))
                if self.checkResponse:
                    row.append(Text(i["responseStatus"], style=responseStyle, justify="center"))

                table.add_row(*row)
        
        c.print(table)

    def generateStatistics(self, alsoPrint=True) -> dict:
        stats = {'totalDevices': len(self.database)}
        stats['onlineDevices'] = 0
        stats['warningDevices'] = 0
        stats['offlineDevices'] = 0
        for i in self.database:
            if i["responseStatus"] == "Online":
                stats['onlineDevices'] += 1
            elif i["responseStatus"] == "Warning":
                stats['warningDevices'] += 1
            elif i["responseStatus"] == "Offline":
                stats['offlineDevices'] += 1
        #stats['offlineDevices'] = len(self.database) - stats["onlineDevices"]
        onlinePercent = stats['onlineDevices'] / stats['totalDevices']
        offlinePercent = stats['offlineDevices'] / stats['totalDevices']
        warningPercent = stats['warningDevices'] / stats['totalDevices']
        stats['percentOnline'] = str(round((onlinePercent * 100), 1)) + "%"
        stats['percentOffline'] = str(round((offlinePercent * 100), 1)) + "%"
        #stats['percentOffline'] = str(round((100 - float(stats['percentOnline'].replace("%", ""))), 1)) + "%"
        stats['percentWarning'] = str(round((warningPercent * 100), 1)) + "%"

        if alsoPrint:
            c.print(f"Checked a total of {stats['totalDevices']} Devices")
            c.print(f"{stats['onlineDevices']} or {stats['percentOnline']} Online")
            if stats['warningDevices'] > 0:
                c.print(f"{stats['warningDevices']} or {stats['percentWarning']} in Warning")
            c.print(f"{stats['offlineDevices']} or {stats['percentOffline']} Offline")

        return stats
    
    def saveDB(self) -> None:
        with open(self.memoryFilename, 'w') as file:
            json.dump(self.database, file)


    def buildDB(self) -> None:
        if self.singleIP != None:
            self.database = [{"device": "Device", "IP": self.singleIP, "pingStatus": "UnKnown", "reponseStatus": "UnKnown"}]
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

    def getProjectDB(self) -> None:
        with open(self.projectName + ".json", "r") as file:
            self.projectDatabase = json.load(file)
        
        table = Table()
        table.add_column("#")
        table.add_column("Section")
        curOption = 1
        for section in self.projectDatabase:
            table.add_row(str(curOption), section["name"])
            curOption += 1
        table.add_row(str(curOption), "Exit")
        
        c.clear()
        c.print("Which Section do you want to Scan?")
        c.print(table)
        while True:
            try:
                usrSelection = int(input(">"))
                break
            except ValueError:
                c.print("Please enter a number", style="red")

        if usrSelection == curOption:
            sys.exit()
        
        self.database = self.projectDatabase[usrSelection - 1]["data"]
        if self.tableTitle == None:
            self.tableTitle = self.projectDatabase[usrSelection - 1]["name"]
        


    def checkDB(self) -> None:
        for i in self.database:
            try:
                self.clear()
                if self.checkPing:
                    i["pingStatus"] = "Checking"
                    self.showTable()
                    if self.ping(i["IP"]):
                        i["pingStatus"] = "Online"
                    else:
                        i["pingStatus"] = "Offline"
                if self.checkResponse:
                    i["responseStatus"] = "Checking"
                    self.showTable()
                    if self.checkWebServer(i["IP"]):
                        i["responseStatus"] = "Online"
                    else:
                        i["responseStatus"] = "Offline"
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
                i["responseStatus"] = "Checking"
                self.showTable()
                i["responseStatus"] = self.checkDevice(i["IP"])
                if i["responseStatus"] == "Offline":
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
        if self.changeSettings:
            self.modifySettings()
        if self.projectName != None:
            self.getProjectDB()
        else:
            self.buildDB()

        if self.watchMode:
            self.watchDB()
        elif self.filter != None:
            self.checkDB()
            self.clear()
            self.showTable(self.filter)
            self.generateStatistics()
        elif self.buildProjectMode:
            builder = ProjectBuilder()
            builder.buildProjectDB()
        else:
            self.checkDB()
            self.showTable()
            self.generateStatistics()

if __name__ == "__main__":
    scanner = Scanner()
    scanner.run()