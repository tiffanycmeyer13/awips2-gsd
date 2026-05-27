#!/awips2/python/bin/python
import subprocess as sub
import os, time, glob
import tkinter as tk
from tkinter import font

def getSQL_Queries():

    return sorted(glob.glob(os.path.join("sql", "*.sql")))

def callback(sqlQueryDict):

    # Determine which queries were selected
    sqlQueryList = getSQL_Queries()
    queriesToRun = []
    for queryName in sqlQueryList:
        if sqlQueryDict[queryName].get():
            queriesToRun.append(queryName)

    # Exit if no queries chosen
    if not queriesToRun:
        print("No queries chosen...exiting...")
        exit()

    # Determine if postgres is running
    syscmd = '''ps -ef | grep "postgres: " | grep -v grep'''
    p = sub.Popen(syscmd,shell=True,stdout=sub.PIPE,stderr=sub.PIPE)
    out = p.communicate()[0].decode("utf-8")


    # Start postgres if not running
    killPostgres = False
    if not out:
        killPostgres = True
        os.system("sudo systemctl start postgresql@awips")
        # Sleep so postgres can start fully
        time.sleep(3)

    # Import all tables selected
    for q in queriesToRun:
        syscmd = f'psql -a -c "`cat {q}`" metadata;'
        print(syscmd)
        os.system(syscmd)
        time.sleep(3)

    # Kill postgres if this script started it up
    if killPostgres:
        os.system("sudo systemctl stop postgresql@awips")
    exit()

def buildButtons(master):

    # Tkinter font information
    fontLabel = font.Font(family='Helvetica',size=20, weight='bold')
    fontButton = font.Font(family='Helvetica',size=16, weight='bold')
    fontCheck = font.Font(family='Helvetica',size=12, weight='bold')

    # Build dictionary containing activation flags for each table
    sqlQueryList = getSQL_Queries()
    queryActivationDict = {}
    for queryName in sqlQueryList:
        queryActivationDict[queryName] = tk.IntVar()
        queryActivationDict[queryName].set(0)

    # Info label
    label = tk.Label(master, text="Select the SQL queries you wish to run:",font=fontLabel)
    label.pack(anchor=tk.CENTER)

    # List of shapefiles as checkboxes
    for queryPath in sqlQueryList:
        queryName = os.path.basename(queryPath)
        b = tk.Checkbutton(master, text=f"{queryName}", variable=queryActivationDict[queryPath], indicatoron=1, font=fontButton)
        b.pack(side=tk.TOP,anchor=tk.W,expand=tk.YES)

    # Submit and Exit buttons
    tk.Button(master, text="Submit", width=30, command=lambda i=queryName : callback(queryActivationDict),font=fontButton).pack(padx=5,pady=5)
    tk.Button(master, text="Exit", width=30, command = close_window, font=fontButton).pack(padx=5,pady=5)
    return master

def main():
    # Build GUI framework
    global master
    master = tk.Tk()
    master.wm_title("AWIPS-2 SQL Query Launcher")
    master = buildButtons(master)
    tk.mainloop()
    try:
        master.protocol("WM_DELETE_WINDOW",appShutdown())
    except:
        print("Window destroyed...")

def close_window():
    master.destroy()

if __name__ == "__main__":
    global curDir ; curDir = os.path.dirname(os.path.realpath(__file__))
    main()
