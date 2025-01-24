
import json
from tkinter import messagebox
from tkinter import ttk
from tkinter import Label
from tkinter import Checkbutton
from tkinter import StringVar
from tkinter import IntVar
from tkinter import Radiobutton
from tkinter import Entry
from tkinter import Button
from tkinter import Text
from tkinter import WORD
import tkinter as tk
import pyodbc
import re
from datetime import datetime
import Applog
import transferfile
import database
import configParser
import os
import fnmatch

FONT_NAME = "Courier"
LBF_WIDTH = 700

class TabRestorePointInTime(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        cf = configParser.configParser()
        self.server_dictionary = cf.servers
        server_list = [key for key in self.server_dictionary]
        self.backup_dictionary = cf.backupDir
        backup_key = [key for key in self.backup_dictionary]
        #print(self.backup_dictionary["DB052"][0])
        
        
        self.databaseName = ''
        self.initbackupname = ''
        self.kbtserver = ''
        self.localpath = 'G:\BACKUP_LOCAL'
        self.networkpath = r'\\10.1.1.12\LogShipping'

        self.lbTitle_shiplog = Label(self, text="Restore Point In Time", font=(FONT_NAME, 21))
        self.lbTitle_shiplog.grid(column=0, row=0, columnspan=2, sticky="NWES")

        self.kbtgroup = ttk.LabelFrame(self, width=LBF_WIDTH, height=100, text="DBSPARE")
        self.kbtgroup.grid(column=0, row=1, sticky="NWES")

        self.lbKBTServer = Label(self.kbtgroup, text="Server:")
        self.lbKBTServer.grid(column=0, row=2, sticky="W")

        self.svServer_list = StringVar()
        self.svServer_list.set(server_list[0])

        self.cbKBTServer = ttk.Combobox(self.kbtgroup, width=33, textvariable=self.svServer_list)
        self.cbKBTServer.grid(column=1, row=2, columnspan=3, sticky="W")
        self.cbKBTServer["value"] = server_list
        self.cbKBTServer.bind("<<ComboboxSelected>>", self.cbKBTServer_changed)
        self.cbKBTServer.delete(0, tk.END)
        self.cbKBTServer.insert(0, r"db052")
        

        self.lbDatabase = Label(self.kbtgroup, text="DB Name:", font=(FONT_NAME, 8))
        self.lbDatabase.grid(column=5, row=2, sticky="W")
        self.entDatabase = Entry(self.kbtgroup, width=24)
        self.entDatabase.grid(column=6, row=2, pady=3,sticky="W")
        self.entDatabase.delete(0, tk.END)
        self.entDatabase.insert(0, r"affiliate_12B")

        self.lbTime = Label(self.kbtgroup, text="Before Time:", font=(FONT_NAME, 8))
        self.lbTime.grid(column=0, row=3, sticky="W")
        self.entTime = Entry(self.kbtgroup, width=90)
        self.entTime.grid(column=1, row=3, columnspan=8, pady=3)
        self.entTime.delete(0, tk.END)
        self.entTime.insert(0, r"2050-01-01 00:00:00")
        
        self.lbRestorePath = Label(self.kbtgroup, text="Restore Path:", font=(FONT_NAME, 8))
        self.lbRestorePath.grid(column=0, row=4, sticky="W")
        self.entRestorePath = Entry(self.kbtgroup, width=90)
        self.entRestorePath.grid(column=1, row=4, columnspan=8, pady=3)
        self.entRestorePath.delete(0, tk.END)
        self.entRestorePath.insert(0, r"\\devdb061\G$\Brice\\"+self.cbKBTServer.get().strip()+"_"+self.entDatabase.get().strip())
        
        self.lbBackupFullPath = Label(self.kbtgroup, text="BK Full Path:", font=(FONT_NAME, 8))
        self.lbBackupFullPath.grid(column=0, row=5, sticky="W")
        self.entBackupFullPath = Entry(self.kbtgroup, width=90)
        self.entBackupFullPath.grid(column=1, row=5, columnspan=8, pady=3)
        self.entBackupFullPath.delete(0, tk.END)
        self.entBackupFullPath.insert(0, r"\\devdb061\G$\Brice")

        self.lbBackupDiffPath = Label(self.kbtgroup, text="BK Diff Path:", font=(FONT_NAME, 8))
        self.lbBackupDiffPath.grid(column=0, row=6, sticky="W")
        self.entBackupDiffPath = Entry(self.kbtgroup, width=90)
        self.entBackupDiffPath.grid(column=1, row=6, columnspan=8, pady=3)
        self.entBackupDiffPath.delete(0, tk.END)
        self.entBackupDiffPath.insert(0, r"\\devdb061\G$\Brice")

        self.lbBackupLogPath = Label(self.kbtgroup, text="BK Log Path:", font=(FONT_NAME, 8))
        self.lbBackupLogPath.grid(column=0, row=7, sticky="W")
        self.entBackupLogPath = Entry(self.kbtgroup, width=90)
        self.entBackupLogPath.grid(column=1, row=7, columnspan=8, pady=3)
        self.entBackupLogPath.delete(0, tk.END)
        self.entBackupLogPath.insert(0, r"")
        self.entBackupLogPath.config(state="disable")



        
        self.chkoptRestoreLog_var = IntVar()
        self.chkoptRestoreLog = Checkbutton(self.kbtgroup, padx=5, onvalue=1, offvalue=0,
                                        command=self.on_chkoptRestoreLog_toggle, variable=self.chkoptRestoreLog_var,
                                        text='Restore Log')
        self.chkoptRestoreLog.grid(column=10, row=7,sticky="W")
        



        self.scriptgroup = ttk.LabelFrame(self, width=LBF_WIDTH, height=100, text="Script")
        self.scriptgroup.grid(column=0, row=2,padx=10, pady=10, sticky="NSEW")
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.text_output = Text(self.scriptgroup, height=9, width=80)
        self.text_output.grid(column=0, row=0,padx=10, pady=10 , sticky="NSEW" )
        
        self.copy_button = Button(self.scriptgroup, text="Copy", command=self.copy_to_clipboard)
        self.copy_button.grid(column=0,row=1,padx=10, sticky="W")
        
        self.chkoptExecute_var = IntVar(value=1)
        self.chkoptExecute = Checkbutton(self, padx=5, onvalue=1, offvalue=0,
                                        command=self.on_chkoptExecute_toggle, variable=self.chkoptExecute_var,
                                        text='Export scripts only')
        self.chkoptExecute.grid(column=0, row=3, sticky="W")
        self.btnRUN = Button(self, text="RUN", highlightthickness=0, width=20, pady=10, command=self.btnRUN_click)
        self.btnRUN.grid(column=0, row=4, columnspan=2, sticky="W", pady=5)



        self.cbKBTServer_changed(None)
        self.entDatabase.bind("<FocusOut>", self.entDatabase_change)
    
    def setRestorePath (self):
        self.entRestorePath.delete(0, tk.END)
        self.entRestorePath.insert(0, r"\\dbspare\E$\USER_DB"+"\\"+self.cbKBTServer.get().strip()+"_"+self.entDatabase.get().strip()+"\\")
        
    def setBKPath(self):
        self.entBackupFullPath.delete(0, tk.END)
        self.entBackupFullPath.insert(0, self.backup_dictionary[self.cbKBTServer.get().strip()][0])
        self.entBackupDiffPath.delete(0, tk.END)
        self.entBackupDiffPath.insert(0, self.backup_dictionary[self.cbKBTServer.get().strip()][1])
        
        if self.chkoptRestoreLog_var.get() == 1:
            logSubDir = "\\"+self.cbKBTServer.get().strip()+"."+self.entDatabase.get().strip()
            self.entBackupLogPath.delete(0, tk.END)
            self.entBackupLogPath.insert(0, self.backup_dictionary[self.cbKBTServer.get().strip()][2]+logSubDir)

    def checkPath(self,path):
        return 0

    def cbKBTServer_changed(self, event):
        self.kbtserver = self.cbKBTServer.get()
        self.setRestorePath()
        
    def entDatabase_change(self,event):
        self.setRestorePath()
        self.setBKPath()
        

    def on_chkoptRestoreLog_toggle(self):
        if self.chkoptRestoreLog_var.get() == 1:
            self.entBackupLogPath.config(state="normal")
            logSubDir = "\\"+self.cbKBTServer.get().strip()+"."+self.entDatabase.get().strip()
            self.entBackupLogPath.delete(0, tk.END)
            self.entBackupLogPath.insert(0, self.backup_dictionary[self.cbKBTServer.get().strip()][2]+logSubDir)
        else:
            self.entBackupLogPath.delete(0, tk.END)
            self.entBackupLogPath.insert(0, r"")
            self.entBackupLogPath.config(state="disable")
   

    def on_chkoptExecute_toggle(self):
        pass


    def copy_to_clipboard(self):
        try:
            # Get the content of the Text widget (from line 1, character 0 to the end)
            text_content = self.text_output.get("1.0", tk.END).strip()
            
            # Check if there is any content in the Text widget
            if text_content:
                # Clear the current clipboard content
                self.clipboard_clear()
                # Append the new content to the clipboard
                self.clipboard_append(text_content)
                # Update the clipboard
                self.update()
                # Show a success message to the user
                messagebox.showinfo("Notification", "Content has been copied to clipboard!")
            else:
                # Show a warning if there is no content to copy
                messagebox.showwarning("Warning", "There is no content to copy!")
        except Exception as e:
            # Show an error message if something goes wrong
            messagebox.showerror("Error", f"An error occurred: {e}")
     
    def get_newest_file(self,directory,time_limit, patterns=["*"]):
        # Create an empty list to store files matching all patterns
        matched_files = []
        # Loop through all files in the directory
        for f in os.listdir(directory):
            file_path = os.path.join(directory, f)
            
            
            
            # Check if it is a file and matches all the patterns
            if os.path.isfile(file_path) and all(fnmatch.fnmatch(f, pattern) for pattern in patterns):
                matched_files.append(f)
        
        # If there are no matching files, return None
        if not matched_files:
            return None, None
    
        # exclude files having modify date > time_limit
        matched_files = [f for f in matched_files if os.path.getmtime(os.path.join(directory, f)) < time_limit.timestamp()]

        # Get the file with the most recent modification time
        newest_file = max(matched_files, key=lambda f: os.path.getmtime(os.path.join(directory, f)))
        newest_file_path = os.path.join(directory, newest_file)
    
        # Get the modification time
        mod_time = os.path.getmtime(newest_file_path)
    
        # Convert the modification time to a human-readable format
        mod_time_str = datetime.fromtimestamp(mod_time).strftime('%Y-%m-%d %H:%M:%S')
    
        return newest_file_path, mod_time_str
            
    def btnRUN_click(self):
        restorePath = self.entRestorePath.get().strip()
        backupFullPath = self.entBackupFullPath.get().strip()
        backupDiffPath = self.entBackupDiffPath.get().strip()
        backupLogPath = self.entBackupLogPath.get().strip()
        time_limit = datetime.strptime(self.entTime.get().strip(),"%Y-%m-%d %H:%M:%S")

        if os.path.exists(restorePath) == False:
            os.makedirs(restorePath)
            print ("created destinatino restore Path:"+ restorePath)
        if os.path.exists(backupFullPath) == False:
            print("invalid backup Full Path...")
            return
        if os.path.exists(backupDiffPath) == False:
            print("invalid backup Diff Path...")
            return
        if self.chkoptRestoreLog_var.get() == 1 and os.path.exists(backupLogPath) == False:
            print("invalid backup Log Path...")
            return
        BKPatterns = self.cbKBTServer.get().strip()+"."+self.entDatabase.get().strip()+"_20*"
        latestBackupFullFile,latestBackupFullDate = self.get_newest_file(backupFullPath,time_limit,[BKPatterns,"*.bak"])
        latestBackupDiffFile,latestBackupDiffDate = self.get_newest_file(backupDiffPath,time_limit,[BKPatterns,"*.dif"])

        
        #set backup diff = None if backup full after backup diff
        if latestBackupFullDate > latestBackupDiffDate:
            latestBackupDiffFile =""
        
        #prepare execute command
        sql_command = "EXECUTE [dbo].[vnDBA_autoCS_restoreDB_brice] @restoreDBName ='%s'\
                                                                    ,@restorePath = '%s'\
                                                                    ,@fullBKPath = '%s' \
                                                                    ,@diffBKPath = '%s' \
                                                                    ,@trnBKDir = '%s'\
                                                                    ,@fromTRNFile = '%s'\
                                                                    ,@toTRNFile = '%s'\
                                                                    ,@isExcuted = %s\
        " % (self.cbKBTServer.get().strip()+"_"+self.entDatabase.get().strip()+datetime.now().strftime("_%Y%m%d")
            , restorePath
            , latestBackupFullFile
            , latestBackupDiffFile
            , backupLogPath
            , ""
            , ""
            , 1-self.chkoptExecute_var.get()
            )
        results = database.execute_a_query(dbserver="devdb061", sqllogin=None, pwd=None, dbname="mondb", querytext=sql_command,trustedConnection=1)
        #print(messages)
        #self.text_output.delete(0, tk.END)
        print(results)
        for result in results:
            for rows in result:
                for row in rows:
                    self.text_output.insert(tk.END, row)
                    self.text_output.insert(tk.END, "\n")
        print('finish.')
