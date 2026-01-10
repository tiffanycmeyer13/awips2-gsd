#!/awips2/python/bin/python
import subprocess as sub
import os, time, glob
import tkinter as tk
from tkinter import font

def getTableList():
    return ["cwa", "cwa (Restore to NWS Baseline)", "flinn_engdahl", "ntwc_atfm1_forecast_points",
            "ntwc_sift_forecast_points", "ptwc_alert_regions", "ptwc_rift_forecast_points", "ptwc_warning_points",
            "tsunami_analysis_regions", "tsunami_aor_regions", "tsunami_break_points", "tsunami_break_point_segments",
            "tsunami_dual_procedure_regions", "tsunami_forecast_points", "tsunami_procedural_regions", "tsunami_sealevel_stations",
            "tsunami_seismic_stations", "tsunami_tectonic_boundaries", "tsunami_threat_db_source_regions", "zone",
            "zone (Restore to NWS Baseline)"]

def tablesToNotDrop():
    return ["zone", "cwa"]

def shapefileScript():
    return os.path.join(curDir, "map_updater_atoms", "importSingleShapefile.py")

def callback(tableActivationDict):

    # Determine which tables were selected
    tableList = getTableList()
    activationList = []
    for tableName in tableActivationDict:
        if tableActivationDict[tableName].get():
            activationList.append(tableName)

    # Exit if no tables chosen
    if not activationList:
        print("No tables chosen...exiting...")
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
    for tableName in activationList:
        tableRootDir = tableName
        if "cwa (Restore" in tableName:
            tableRootDir = "NWS_Baseline_cwa"
            tableName = "cwa"
        elif "zone (Restore" in tableName:
            tableRootDir = "NWS_Baseline_zone"
            tableName = "zone"
        shapefileRootPath = os.path.join(curDir, "map_updater_atoms", tableRootDir)
        shapefilePaths = sorted(glob.glob(os.path.join(shapefileRootPath, "*.shp")))

        # Drop table if it already exists and is allowed to be dropped
        if tableName not in tablesToNotDrop():
            syscmd = f'psql -a -c "select count(*) from mapdata.{tableName}" maps;'
            p = sub.Popen(syscmd,shell=True,stdout=sub.PIPE,stderr=sub.PIPE)
            out = p.communicate()[0].decode("utf-8")
            if "row)" in out:
                os.system(f'psql -a -c "drop table mapdata.{tableName}" maps;')

        firstRun = True
        for shapefilePath in shapefilePaths:
            syscmd = f"{shapefileScript()} -s {shapefilePath} -t {tableName}"
            if not firstRun:
                syscmd += " -a"
            else:
                firstRun = False
            os.system(syscmd)
            time.sleep(3)

    # Kill postgres if this script started it up
    if killPostgres:
        os.system("sudo systemctl stop postgresql@awips")
    exit()

def buildButtons(master):

    # Tkinter font information
    fontLabel = font.Font(family="Helvetica",size=20, weight="bold")
    fontButton = font.Font(family="Helvetica",size=16, weight="bold")
    fontCheck = font.Font(family="Helvetica",size=12, weight="bold")

    # Build dictionary containing activation flags for each table
    tableList = getTableList()
    tableActivationDict = {}
    for tableName in tableList:
        tableActivationDict[tableName] = tk.IntVar()
        tableActivationDict[tableName].set(0)

    # Info label
    label = tk.Label(master, text="Select the shapefile(s) you wish to import:",font=fontLabel)
    label.pack(anchor=tk.CENTER)

    # List of shapefiles as checkboxes
    for tableName in tableList:
        b = tk.Checkbutton(master, text=f"{tableName}", variable=tableActivationDict[tableName], indicatoron=1, font=fontButton)
        b.pack(side=tk.TOP,anchor=tk.W,expand=tk.YES)

    # Submit and Exit buttons
    tk.Button(master, text="Submit", width=30, command=lambda i=tableName : callback(tableActivationDict),font=fontButton).pack(padx=5,pady=5)
    tk.Button(master, text="Exit", width=30, command = close_window, font=fontButton).pack(padx=5,pady=5)
    return master

def main():
    # Build GUI framework
    global master
    master = tk.Tk()
    master.wm_title("AWIPS-2 Shapefile Importer")
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
