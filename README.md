# StatusCheck
Tools to quickly check the status of a large number of IPs

Built as a class so you can import the functionalty into other projects but intended to be run stand-alone.

# Genral Use
## Arguments
When run from a command line there are serveral optional arguments. Multiple arguments can be run at the same time.
| Short | Long/Name | Function | 
| ----- | --------- | ----------------- |
| `-t` | `--title` | Set custom title for the output table |
| `-s` | `--single` | Activates Single IP Mode. Must be followed by a valid IP address| 
| `-r`| `--recheck` | Re-Checks the last IP(s) scanned |
| `-m` | `--manual` | Manual Enter the IPs, user will be prompted for each IP to check |
| `-w` | `--watch` | Activate Watch Mode |

## Usage
If run with no arguments, the script will output the following
```
> statusCheck.py
> [+] Copy the Table
```
The script will wait until the user copies the desired Device list from a spreadsheet. The List should contain 2 columns, the left column being the Device name to display and the right column being the IP address to scan

Once the list has been copied the script will check each IP and report the status. After all IPs have been checked the full list and online statistics will be displayed.

## Single IP Mode
If run with the `-s` argument, the script will imediatly run a check on that IP and output the result.

## Manual Mode
If run with the `-m` argument, the script will prompt the user to enter as may IPs as they want. Each IP should be followed by the enter key. To finish entering IPs press enter without entering an IP.

## Watch Mode
If run with the `-w` argument, instead of only checking each IP once, the script will continue to run until all IPs are online or the script is stopped manually with `Ctrl+C`. The `.watchCycle` variable controls how many seconds the script will wait after checking the last IP before it starts checking again.

## Repeat Mode
All scan lists are stored in .json format in file. The default filename is `mem_statusCheck.json` and will be created automatically on first launch. You can change the filename with the `.memoryFilename` variable. If the `-r` argument is included, the script will automatically take the contents of that file and use that as the list to scan.

# Dependencies
This script relies on the following dependencies.
| Package |
| ------- |
| [rich](https://github.com/Textualize/rich) |
| [pyperclip](https://pypi.org/project/pyperclip/) |
| [requests](https://pypi.org/project/requests/) |
| [keyboard](https://pypi.org/project/keyboard/) |
