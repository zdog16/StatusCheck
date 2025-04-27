from rich.traceback import install
from rich.console import Console
from rich.prompt import Prompt
import keyboard
import pyperclip
import json
import sys
install()
c = Console()

database = [] 

def waitForCopy() -> bool:
    while True:
        if keyboard.is_pressed('ctrl'):
            if keyboard.is_pressed('c'):
                while keyboard.is_pressed('c'):
                    pass
                return True
        elif keyboard.is_pressed('esc'):
            c.print("[+] Escape Key Detected, Program terminated", style="red")
            sys.exit()

def buildMenu(options: list):
    curSel = 1
    for item in options:
        c.print(f"{curSel}) {item}")
        curSel += 1
    
    usrSelection = int(input(">"))
    return options[usrSelection - 1]

def saveDB():
    with open(filename, 'w') as file:
        json.dump(database, file)

filename = Prompt.ask("What is the Project Name?") + ".json"
sectionNames = []
while True:
    if len(sectionNames) > 0:
        c.print("Current Sections")
        for name in sectionNames:
            c.print(name)
        c.print(" ")
    c.print("Select an Option")
    usrSelection = buildMenu(["Add Section", "Build DB"])
    if usrSelection == "Add Section":
        name = Prompt.ask("What is the Section Name")
        sectionNames.append(name)
        c.print("Copy the Section Data")
        waitForCopy()

        pasteDump = pyperclip.paste()
        RowSplit = pasteDump.split('\n')
        tempDatabase = []
        for i in RowSplit:
            tempList = i.split('\t')
            DeviceName = tempList[0]
            IP = tempList[1].replace('\r', '')
            tempDatabase.append({"device": DeviceName, "IP": IP, "status": "UnKown"})

        database.append({"name": name, "data": tempDatabase})
        saveDB()


    elif usrSelection == "Build DB":
        saveDB()
        exit()