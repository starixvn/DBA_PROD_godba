

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
import tkinter as tk
import pyodbc
import re
import Applog
import database


FONT_NAME = "Courier"

class TabShipSP(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)

        # ============ add widgets for tab shipSP
        self.lbTitle = Label(self, text="Sync SP/Func & permission to DR", font=(FONT_NAME, 21))
        self.lbTitle.grid(column=0, row=0, columnspan=8, sticky="NWES")

        self.lbKBT = Label(self, text="KBT", font=(FONT_NAME, 15))
        self.lbKBT.grid(column=0, row=1, columnspan=3, sticky="W")

        self.lbKBTServer = Label(self, text="Server:")
        self.lbKBTServer.grid(column=0, row=2, sticky="W")

        with open("servers_list.cnf", mode="r") as json_file:
            self.server_dictionary = json.load(json_file)
        server_list = [key for key in self.server_dictionary]
        self.svServer_list = StringVar()
        self.svServer_list.set(server_list[0])

        self.cbKBTServer = ttk.Combobox(self, width=33, textvariable=self.svServer_list)
        self.cbKBTServer.grid(column=1, row=2, columnspan=3, sticky="W")
        self.cbKBTServer["value"] = server_list
        self.cbKBTServer.bind("<<ComboboxSelected>>", self.cbKBTServer_changed)

        self.lbUsername = Label(self, text="SQL Login:", font=(FONT_NAME, 8))
        self.lbUsername.grid(column=0, row=3, sticky="W")
        self.entUsername = Entry(self, width=12)
        self.entUsername.grid(column=1, row=3)

        self.lbPassword = Label(self, text="Password:", font=(FONT_NAME, 8))
        self.lbPassword.grid(column=2, row=3, sticky="W")
        self.entPassword = Entry(self, width=12, show="*")
        self.entPassword.grid(column=3, row=3)

        self.chkCopyLogin_var = IntVar()
        self.chkCopyLogin = Checkbutton(self, padx=5, onvalue=1, offvalue=0, command=self.on_chkCopyLogin_toggle,
                                   variable=self.chkCopyLogin_var)
        self.chkCopyLogin.grid(column=4, row=1)

        self.lbDR = Label(self, text="DR", font=(FONT_NAME, 15))
        self.lbDR.grid(column=5, row=1, sticky="W")

        self.lbDRServer = Label(self, text="Server:")
        self.lbDRServer.grid(column=5, row=2, sticky="W")

        drserver_list = [self.server_dictionary[key] for key in self.server_dictionary]
        self.cbDRServer_value = StringVar()
        self.cbDRServer_value.set(drserver_list[0])

        self.cbDRServer = ttk.Combobox(self, width=36, textvariable=self.cbDRServer_value)
        self.cbDRServer.config(state="disabled")
        self.cbDRServer.grid(column=6, row=2, columnspan=8, sticky="W")
        self.cbDRServer["value"] = drserver_list

        self.lbDRUsername = Label(self, text="SQL Login:", font=(FONT_NAME, 8))
        self.lbDRUsername.grid(column=5, row=3, sticky="W")
        self.entDRUsername = Entry(self, width=12)
        self.entDRUsername.config(state="disabled")
        self.entDRUsername.grid(column=6, row=3)

        self.lbDRPassword = Label(self, text="Password:", font=(FONT_NAME, 8))
        self.lbDRPassword.grid(column=7, row=3, sticky="W")
        self.entDRPassword = Entry(self, width=12, show="*")
        self.entDRPassword.config(state="disabled")
        self.entDRPassword.grid(column=8, row=3)

        self.lbline01 = Label(self, text="", padx=10)
        self.lbline01.grid(column=0, row=4)

        self.btnLoadDB = Button(self, text="Load databases", highlightthickness=0, command=self.btnLoadDB_click)
        self.btnLoadDB.grid(column=0, row=5, sticky="W")
        self.svDatabase_list = StringVar()
        Database_list = ["Please load databases"]
        self.svDatabase_list.set(Database_list[0])
        self.cbKBTDatabase = ttk.Combobox(self, width=25, textvariable=self.svDatabase_list)
        self.cbKBTDatabase.grid(column=1, row=5, columnspan=4, sticky="W")

        self.cbKBTDatabase["value"] = Database_list
        self.cbKBTDatabase.bind("<<ComboboxSelected>>", self.cbKBTDatabase_changed)

        self.chkCopyDB_var = IntVar()
        self.chkCopyDB = Checkbutton(self, padx=5, onvalue=1, offvalue=0, variable=self.chkCopyDB_var,
                                command=self.on_chkCopyDB_toggle)
        self.chkCopyDB.grid(column=4, row=5)

        self.lbDRDBname = Label(self, text="database:")
        self.lbDRDBname.grid(column=5, row=5, sticky="W")
        self.entDRDatabase = Entry(self, width=25)
        self.entDRDatabase.config(state="disabled")
        self.entDRDatabase.grid(column=6, row=5, columnspan=8, sticky="W")

        self.txtSPList = Text(self, height=12, width=80)
        self.txtSPList.insert("1.0", "input your SP list here...")
        self.txtSPList.grid(column=0, row=8, columnspan=8, sticky="W")

        self.syncType = StringVar()
        self.rdSchema = Radiobutton(self, text="Schemas only", variable=self.syncType)
        self.rdSchema.config(value="schema")
        self.rdSchema.grid(column=0, columnspan=1, row=9, sticky="W")
        self.rdPermission = Radiobutton(self, text="Permissions only", variable=self.syncType)
        self.rdPermission.config(value="permission")
        self.rdPermission.grid(column=2, columnspan=3, row=9, sticky="W")
        self.rdBoth = Radiobutton(self, text="Schema & Permission", variable=self.syncType)
        self.rdBoth.config(value="both")
        self.rdBoth.grid(column=4, columnspan=5, row=9, sticky="W")

        self.lbLine02 = Label(self, text="", pady=2)
        self.lbLine02.grid(column=0, row=10)

        self.btnSync = Button(self, text="Sync to DR", highlightthickness=0, width=20, pady=2, height=3, command=self.btnSync_click)
        self.btnSync.grid(column=0, row=11, columnspan=2, sticky="W")

        # set default value
        self.syncType.set("schema")
        self.cbKBTServer_changed(None)

    def cbKBTServer_changed(self, event):
        kbtserver = self.cbKBTServer.get()
        if self.chkCopyLogin_var.get() == 0:
            self.cbDRServer_value.set(self.server_dictionary[kbtserver])
        else:
            self.cbDRServer_value.set(self.server_dictionary[kbtserver])

    def btnLoadDB_click(self):
        dbserver = self.cbKBTServer.get()
        username = self.entUsername.get()
        pwd = self.entPassword.get()

        if username == "" or pwd == "":
            messagebox.showerror(f"Error found", "username or password is not valid. please try again.")
            return
        try:
            database_list = database.server_get_databases(dbserver, username, pwd)
            self.cbKBTDatabase["value"] = database_list
            self.svDatabase_list.set("master")
            self.cbKBTDatabase_changed(None)
        except Exception as e:
            messagebox.showerror(f"Error found", e)
            Applog.write_log(str(e))

    def cbKBTDatabase_changed(self, event):
        current_value = self.cbKBTDatabase.get()
        if self.chkCopyDB_var.get() == 0:
            self.entDRDatabase.config(state="normal")
            self.entDRDatabase.delete(0, tk.END)
            self.entDRDatabase.insert(0, current_value)
            self.entDRDatabase.config(state="disabled")
        else:
            self.entDRDatabase.delete(0, tk.END)
            self.entDRDatabase.insert(0, current_value)
        if self.chkCopyLogin_var.get() == 0:
            self.entDRUsername.config(state='normal')
            self.entDRUsername.delete(0, tk.END)
            self.entDRUsername.insert(0, self.entUsername.get())
            self.entDRUsername.config(state='disable')
            self.entDRPassword.config(state='normal')
            self.entDRPassword.delete(0, tk.END)
            self.entDRPassword.insert(0, self.entPassword.get())
            self.entDRPassword.config(state='disable')
        else:
            self.entDRUsername.delete(0, tk.END)
            self.entDRUsername.insert(0, self.entUsername.get())
            self.entDRPassword.delete(0, tk.END)
            self.entDRPassword.insert(0, self.entPassword.get())

    def btnSync_click(self):

        FullSPList = self.txtSPList.get(1.0, tk.END)
        SPList = FullSPList.splitlines()
        kbtserver = self.cbKBTServer.get()
        kbtusername = self.entUsername.get()
        kbtpwd = self.entPassword.get()
        kbtdbname = self.cbKBTDatabase.get()

        drdbname = self.entDRDatabase.get()
        drserver = self.cbDRServer.get().split("~")[1]
        drusername = self.entDRUsername.get()
        drpwd = self.entDRPassword.get()


        # step 1: verify
        if database.check_username_pwd(kbtserver, kbtusername, kbtpwd) == -1:
            messagebox.showerror(f"Error found", "KBT username or password is not valid.")
            return

        if drserver.__contains__("10.14") == False:
            messagebox.showerror(f"Error found", "target server only in subnet 10.14x.yy.zz")
            return

        if database.check_username_pwd(drserver, drusername, drpwd) == -1:
            messagebox.showerror(f"Error found", "DR username or password is not valid.")
            return

        option = self.syncType.get()
        failedcount = database.sync_SPList_to_destination(kbtserver, kbtusername, kbtpwd, kbtdbname, drserver, drusername, drpwd, drdbname, SPList, option)
        if failedcount > 0:
            messagebox.showinfo("information", "sync to DR done with some SP failed.")
        else:
            messagebox.showinfo("information", "sync to DR done with successful.")
        # try:
        #     for SP in SPList:
        #         objdefiniton = database.get_obj_definition(kbtserver, kbtusername, kbtpwd, kbtdbname, SP.strip())
        #         if objdefiniton is not None:
        #             objtype = database.check_objecttype(kbtserver, kbtusername, kbtpwd, SP.strip(), kbtdbname)
        #             if database.check_existingobject(drserver, drusername, drpwd, SP, drdbname):
        #                 if objtype.strip() == 'P':
        #                     objdefiniton = re.sub(r'\bCREATE([ \t]+)(PROCEDURE)\b',
        #                                           lambda match: 'ALTER' + match.group(1) + match.group(2),
        #                                           objdefiniton, flags=re.IGNORECASE)
        #                     objdefiniton = re.sub(r'\bCREATE([ \t]+)(PROC)\b',
        #                                           lambda match: 'ALTER' + match.group(1) + match.group(2),
        #                                           objdefiniton, flags=re.IGNORECASE)
        #                 elif objtype in ('FN', 'IF', 'TF'):
        #                     objdefiniton = re.sub(r'\bCREATE([ \t]+)(FUNCTION)\b',
        #                                           lambda match: 'ALTER' + match.group(1) + match.group(2),
        #                                           objdefiniton, flags=re.IGNORECASE)
        #             database.set_obj_definition(drserver, drusername, drpwd, drdbname, objdefiniton)
        #         else:
        #             print(f"{SP} does not exists at source")
        #     messagebox.showinfo("information", "sync to DR done.")
        # except Exception as e:
        #     messagebox.showerror(f"error found at {SP}", e)
        #     Applog.write_log(str(e))

    def on_chkCopyLogin_toggle(self):
        if self.chkCopyLogin_var.get() == 1:
            self.cbDRServer.config(state="normal")
            self.entDRUsername.config(state="normal")
            self.entDRPassword.config(state="normal")
        else:
            self.cbDRServer.config(state="disable")
            self.entDRUsername.config(state="disable")
            self.entDRPassword.config(state="disable")

    def on_chkCopyDB_toggle(self):
        if self.chkCopyDB_var.get() == 1:
            self.entDRDatabase.config(state="normal")
        else:
            self.entDRDatabase.config(state="disable")