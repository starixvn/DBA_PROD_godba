
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
from datetime import datetime
import Applog
import transferfile
import database

FONT_NAME = "Courier"
LBF_WIDTH = 700

class TabShipLog(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.databaseName = ''
        self.initbackupname = ''
        self.kbtserver = ''
        self.localpath = 'G:\BACKUP_LOCAL'
        self.networkpath = r'\\10.1.1.12\LogShipping'

        self.lbTitle_shiplog = Label(self, text="Config Log Shipping", font=(FONT_NAME, 21))
        self.lbTitle_shiplog.grid(column=0, row=0, columnspan=8, sticky="NWES")

        self.kbtgroup = ttk.LabelFrame(self, width=LBF_WIDTH, height=100, text="KBT")
        self.kbtgroup.grid(column=0, row=1, sticky="W")

        self.lbKBTServer = Label(self.kbtgroup, text="Server:")
        self.lbKBTServer.grid(column=0, row=2, sticky="W")

        with open("servers_list.cnf", mode="r") as json_file:
            self.server_dictionary = json.load(json_file)
        server_list = [key for key in self.server_dictionary]

        self.svServer_list = StringVar()
        self.svServer_list.set(server_list[0])

        self.cbKBTServer = ttk.Combobox(self.kbtgroup, width=33, textvariable=self.svServer_list)
        self.cbKBTServer.grid(column=1, row=2, columnspan=3, sticky="W")
        self.cbKBTServer["value"] = server_list
        self.cbKBTServer.bind("<<ComboboxSelected>>", self.cbKBTServer_changed)

        self.lbUsername = Label(self.kbtgroup, text="SQL Login:", font=(FONT_NAME, 8))
        self.lbUsername.grid(column=0, row=3, sticky="W")
        self.entUsername = Entry(self.kbtgroup, width=12)
        self.entUsername.grid(column=1, row=3)

        self.lbPassword = Label(self.kbtgroup, text="Password:", font=(FONT_NAME, 8))
        self.lbPassword.grid(column=2, row=3, sticky="W")
        self.entPassword = Entry(self.kbtgroup, width=12, show="*")
        self.entPassword.grid(column=3, row=3)

        self.btnLoadDB = Button(self.kbtgroup, text="Load databases", highlightthickness=0, command=self.btnLoadDB_click)
        self.btnLoadDB.grid(column=5, row=3, sticky="W")
        self.svDatabase_list = StringVar()
        Database_list = ["Please load databases"]
        self.svDatabase_list.set(Database_list[0])
        self.cbKBTDatabase = ttk.Combobox(self.kbtgroup, width=25, textvariable=self.svDatabase_list)
        self.cbKBTDatabase.grid(column=6, row=3, columnspan=7, sticky="W")

        self.cbKBTDatabase["value"] = Database_list
        self.cbKBTDatabase.bind("<<ComboboxSelected>>", self.cbKBTDatabase_changed)

        self.lbcol01 = Label(self.kbtgroup, text="", padx=3)
        self.lbcol01.grid(column=4, row=2)

        self.lbinfo02 = Label(self.kbtgroup, text=r"template path: \\10.1.1.12\LogShipping\{KBTservername}.{KBTdatabasename}", font=(FONT_NAME, 8), pady=3)
        self.lbinfo02.grid(column=0, row=6, columnspan=8, sticky="W")
        self.lbbackuppath = Label(self.kbtgroup, text="Backup log:", font=(FONT_NAME, 8))
        self.lbbackuppath.grid(column=0, row=7, sticky="W")
        self.entbackuppath = Entry(self.kbtgroup, width=90)
        self.entbackuppath.grid(column=1, row=7, columnspan=8, pady=3)
        self.entbackuppath.delete(0, tk.END)
        self.entbackuppath.insert(0, r"\\10.1.1.12\LogShipping\dbserver.database")


        self.drgroup = ttk.LabelFrame(self, width=LBF_WIDTH, height=100, text="DR")
        self.drgroup.grid(column=0, row=10, sticky="W")

        self.chkCopyLogin_var = IntVar()
        self.chkCopyLogin = Checkbutton(self.drgroup, padx=5, onvalue=1, offvalue=0, command=self.on_chkCopyLogin_toggle,
                                        variable=self.chkCopyLogin_var)
        self.chkCopyLogin.grid(column=0, row=11)

        self.lbDRServer = Label(self.drgroup, text="Server:")
        self.lbDRServer.grid(column=1, row=11, sticky="W")

        drserver_list = [self.server_dictionary[key] for key in self.server_dictionary]
        self.cbDRServer_value = StringVar()
        self.cbDRServer_value.set(drserver_list[0])

        self.cbDRServer = ttk.Combobox(self.drgroup, width=33, textvariable=self.cbDRServer_value)
        self.cbDRServer.config(state="disabled")
        self.cbDRServer.grid(column=2, row=11, columnspan=5, sticky="W")
        self.cbDRServer["value"] = drserver_list

        self.lbDRUsername = Label(self.drgroup, text="SQL Login:", font=(FONT_NAME, 8))
        self.lbDRUsername.grid(column=1, row=12, sticky="W")
        self.entDRUsername = Entry(self.drgroup, width=12)
        self.entDRUsername.config(state="disabled")
        self.entDRUsername.grid(column=2, row=12)

        self.lbDRPassword = Label(self.drgroup, text="Password:", font=(FONT_NAME, 8))
        self.lbDRPassword.grid(column=3, row=12, sticky="W")
        self.entDRPassword = Entry(self.drgroup, width=12, show="*")
        self.entDRPassword.config(state="disabled")
        self.entDRPassword.grid(column=4, row=12)

        self.lbcol02 = Label(self.drgroup, text="", padx=3)
        self.lbcol02.grid(column=5, row=12)

        self.lbDRDBname = Label(self.drgroup, text="database:")
        self.lbDRDBname.grid(column=6, row=12, sticky="W")
        self.entDRDatabase = Entry(self.drgroup, width=25)
        self.entDRDatabase.config(state="disabled")
        self.entDRDatabase.grid(column=7, row=12, columnspan=8, sticky="W")

        self.lbinfo03 = Label(self.drgroup, text=r"template path: G:\BACKUP_LOCAL\{dbname}", font=(FONT_NAME, 8))
        self.lbinfo03.grid(column=2, row=13, columnspan=8, sticky="W")
        self.lbcopypath = Label(self.drgroup, text="Copy log:", font=(FONT_NAME, 8))
        self.lbcopypath.grid(column=1, row=14, sticky="W")
        self.entcopypath = Entry(self.drgroup, width=90)
        self.entcopypath.grid(column=2, row=14, columnspan=8, pady=3)
        self.entcopypath.config(state="disabled")
        self.entcopypath.insert(0, r"\\10.1.1.12\LogShipping\dbserver.database")


        self.tfgroup = ttk.LabelFrame(self, width=LBF_WIDTH, height=100, text="init secondary database")
        self.tfgroup.grid(column=0, row=15, sticky="W")


        self.chkoptbackup_var = IntVar()
        self.chkoptbackup = Checkbutton(self.tfgroup, padx=5, onvalue=1, offvalue=0,
                                        command=self.on_chkoptbackup_toggle, variable=self.chkoptbackup_var,
                                        text='Init backup')
        self.chkoptbackup.grid(column=0, columnspan=1, row=16, sticky="W")

        self.entinitpath = Entry(self.tfgroup, width=90)
        self.entinitpath.config(state="disabled")
        self.entinitpath.grid(column=2, row=16, columnspan=8)
        self.entinitpath.insert(0, r"\\10.1.1.12\LogShipping\dbserver.database")

        self.chkopttransfer_var = IntVar()
        self.chkopttransfer = Checkbutton(self.tfgroup, padx=5, onvalue=1, offvalue=0,
                                          command=self.on_chkopttransfer_toggle, variable=self.chkopttransfer_var,
                                          text='transfer files')
        self.chkopttransfer.grid(column=0, columnspan=1, row=17, sticky="W")

        self.enttopath = Entry(self.tfgroup, width=90)
        self.enttopath.config(state="disabled")
        self.enttopath.grid(column=2, row=17, columnspan=8)
        self.enttopath.insert(0, r"\\10.1.1.12\LogShipping\dbserver.database")


        self.lbkbtaccount = Label(self.tfgroup, text="Oneworks:", font=(FONT_NAME, 8))
        self.lbkbtaccount.grid(column=2, row=18, sticky="W")

        self.lb1wusername = Label(self.tfgroup, text="username:", font=(FONT_NAME, 8))
        self.lb1wusername.grid(column=3, row=18, sticky="W")
        self.ent1wUsername = Entry(self.tfgroup, width=12)
        self.ent1wUsername.config(state="disabled")
        self.ent1wUsername.grid(column=4, row=18)

        self.lb1wPassword = Label(self.tfgroup, text="Password:", font=(FONT_NAME, 8))
        self.lb1wPassword.grid(column=5, row=18, sticky="W")
        self.ent1wPassword = Entry(self.tfgroup, width=12, show="*")
        self.ent1wPassword.config(state="disabled")
        self.ent1wPassword.grid(column=6, row=18)

        self.lbdraccount = Label(self.tfgroup, text="Wuden66:", font=(FONT_NAME, 8))
        self.lbdraccount.grid(column=2, row=19, sticky="W")

        self.lbw6username = Label(self.tfgroup, text="username:", font=(FONT_NAME, 8))
        self.lbw6username.grid(column=3, row=19, sticky="W")
        self.entw6Username = Entry(self.tfgroup, width=12)
        self.entw6Username.config(state="disabled")
        self.entw6Username.grid(column=4, row=19)

        self.lbw6Password = Label(self.tfgroup, text="Password:", font=(FONT_NAME, 8))
        self.lbw6Password.grid(column=5, row=19, sticky="W")
        self.entw6Password = Entry(self.tfgroup, width=12, show="*")
        self.entw6Password.config(state="disabled")
        self.entw6Password.grid(column=6, row=19)


        self.chkoptrestore_var = IntVar()
        self.chkoptrestore = Checkbutton(self.tfgroup, padx=5, onvalue=1, offvalue=0,
                                         command=self.on_chkoptrestore_toggle, variable=self.chkoptrestore_var,
                                         text=f'restore DB (from {self.localpath}\databasename_yyyyMMddhhmm00)')
        self.chkoptrestore.grid(column=0, columnspan=8, row=20, sticky="W")

        self.chkoptconfig_var = IntVar()
        self.chkoptconfig = Checkbutton(self.tfgroup, padx=5, onvalue=1, offvalue=0,
                                        command=self.on_chkoptconfig_toggle, variable=self.chkoptconfig_var,
                                        text='config LS')
        self.chkoptconfig.grid(column=0, columnspan=1, row=21, sticky="W")

        self.btnShipLog = Button(self, text="Ship Log", highlightthickness=0, width=20, pady=10, command=self.btnSync_click)
        self.btnShipLog.grid(column=0, row=22, columnspan=2, sticky="W", pady=5)

        self.cbKBTServer_changed(None)

    def cbKBTServer_changed(self, event):
        self.kbtserver = self.cbKBTServer.get()
        if self.chkCopyLogin_var.get() == 0:
            self.cbDRServer_value.set(self.server_dictionary[self.kbtserver])
        else:
            self.cbDRServer_value.set(self.server_dictionary[self.kbtserver])
        self.shiplog_setpath()

    def setbackupname(self):
        self.initbackupname = '{0}{1}{2}{3}{4}'.format(self.databaseName, '_', datetime.now().strftime('%Y%m%d%H%M'), '00', '.bak')

    def cbKBTDatabase_changed(self, event):
        self.databaseName = self.cbKBTDatabase.get()
        if self.chkCopyLogin_var.get() == 0:
            self.entDRDatabase.config(state="normal")
            self.entDRDatabase.delete(0, tk.END)
            self.entDRDatabase.insert(0, self.databaseName)
            self.entDRDatabase.config(state="disabled")

            self.entDRUsername.config(state="normal")
            self.entDRUsername.delete(0, tk.END)
            self.entDRUsername.insert(0, self.entUsername.get())
            self.entDRUsername.config(state="disabled")

            self.entDRPassword.config(state="normal")
            self.entDRPassword.delete(0, tk.END)
            self.entDRPassword.insert(0, self.entPassword.get())
            self.entDRPassword.config(state="disabled")

        else:
            self.entDRDatabase.delete(0, tk.END)
            self.entDRDatabase.insert(0, self.databaseName)

            self.entDRUsername.delete(0, tk.END)
            self.entDRUsername.insert(0, self.entUsername.get())

            self.entDRPassword.delete(0, tk.END)
            self.entDRPassword.insert(0, self.entPassword.get())

        self.shiplog_setpath()

    def shiplog_setpath(self):
        self.setbackupname()
        initbackupfile = fr'{self.networkpath}\{self.kbtserver}.{self.databaseName}\{self.initbackupname}'
        backuplog = fr'{self.networkpath}\{self.kbtserver}.{self.databaseName}'
        copylog = fr'{self.localpath}\{self.databaseName}'

        self.entbackuppath.delete(0, tk.END)
        self.entbackuppath.insert(0, backuplog)

        if self.chkCopyLogin_var.get() == 0:
            self.entcopypath.config(state="normal")
            self.entcopypath.delete(0, tk.END)
            self.entcopypath.insert(0, copylog)
            self.entcopypath.config(state="disabled")
        else:
            self.entcopypath.delete(0, tk.END)
            self.entcopypath.insert(0, copylog)

        if self.chkoptbackup_var.get() == 0:
            self.entinitpath.config(state='normal')
            self.entinitpath.delete(0, tk.END)
            self.entinitpath.insert(0, initbackupfile)
            self.entinitpath.config(state='disable')
        else:
            self.entinitpath.delete(0, tk.END)
            self.entinitpath.insert(0, initbackupfile)

        if self.chkopttransfer_var.get() == 0:
            self.enttopath.config(state='normal')
            self.enttopath.delete(0, tk.END)
            self.enttopath.insert(0, initbackupfile)
            self.enttopath.config(state='disable')
        else:
            self.enttopath.delete(0, tk.END)
            self.enttopath.insert(0, initbackupfile)

    def on_chktf_toggle(self):
        if self.chktf_var.get() == 1:
            self.entinitpath.config(state="normal")
            self.ent1wUsername.config(state="normal")
            self.ent1wPassword.config(state="normal")
            self.entw6Username.config(state="normal")
            self.entw6Password.config(state="normal")
        else:
            self.entinitpath.config(state="disable")
            self.ent1wUsername.config(state="disable")
            self.ent1wPassword.config(state="disable")
            self.entw6Username.config(state="disable")
            self.entw6Password.config(state="disable")

    def on_chkoptbackup_toggle(self):
        if self.chkoptbackup_var.get() == 1:
            self.entinitpath.config(state="normal")
        else:
            self.entinitpath.config(state="disable")

    def on_chkopttransfer_toggle(self):
        if self.chkopttransfer_var.get() == 1:
            self.enttopath.config(state='normal')
            self.ent1wUsername.config(state="normal")
            self.ent1wPassword.config(state="normal")
            self.entw6Username.config(state="normal")
            self.entw6Password.config(state="normal")
        else:
            self.enttopath.config(state='disable')
            self.ent1wUsername.config(state="disable")
            self.ent1wPassword.config(state="disable")
            self.entw6Username.config(state="disable")
            self.entw6Password.config(state="disable")

    def on_chkoptrestore_toggle(self):
        pass

    def on_chkoptconfig_toggle(self):
        pass

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

    def on_chkCopyLogin_toggle(self):
        if self.chkCopyLogin_var.get() == 1:
            self.cbDRServer.config(state="normal")
            self.entDRUsername.config(state="normal")
            self.entDRPassword.config(state="normal")
            self.entDRDatabase.config(state='normal')
            self.entcopypath.config(state='normal')
        else:
            self.cbDRServer.config(state="disabled")
            self.entDRUsername.config(state="disable")
            self.entDRPassword.config(state="disable")
            self.entDRDatabase.config(state='disable')
            self.entcopypath.config(state='disable')


    def btnSync_click(self):
        # print(self.cbDRServer.get())
        # result = database.config_logshipping_check_backupjob(self.kbtserver, self.entUsername.get(), self.entPassword.get(), 'sysrscols', 3)
        # print(result)

        kbt_server = self.kbtserver
        dr_server = self.cbDRServer.get().split('~')[1]
        dest_server = '{0}{1}'.format(r'\\', self.cbDRServer.get().split('~')[1])
        source_path = self.entbackuppath.get().strip()
        dest_path =  '{0}\{1}'.format(dest_server, self.entcopypath.get().strip().replace(':', '$'))

        drsqllogin = self.entUsername.get().strip()
        drsqlpwd = self.entPassword.get().strip()
        drdatabasename = self.databaseName
        initrestorepath = '{0}\{1}'.format(self.entcopypath.get().strip(), self.initbackupname)
        drcopypath = self.entcopypath.get().strip()

        #step 1: verify
        if database.check_username_pwd(kbt_server, self.entUsername.get(), self.entPassword.get()) == -1:
            messagebox.showerror(f"Error found", "KBT username or password is not valid.")
            return

        if database.check_username_pwd(dr_server, self.entDRUsername.get(), self.entDRPassword.get()) == -1:
            messagebox.showerror(f"Error found", "DR username or password is not valid.")
            return

        #step 2: backup database
        if self.chkoptbackup_var.get() == 1:
            database.backup_a_database(kbt_server, self.entUsername.get(), self.entPassword.get(), self.databaseName, self.entinitpath.get().strip())

        #step 2: copy backup to DR
        if self.chkopttransfer_var.get() == 1:
            source_user = '{0}\{1}'.format('oneworks', self.ent1wUsername.get().strip())
            source_pwd = self.ent1wPassword.get()
            dest_user = '{0}\{1}'.format('wuden66', self.entw6Username.get().strip())
            dest_pwd = self.entw6Password.get()

            transferfile.transfer_files_between_servers(
                source_path= source_path,
                source_username= source_user,
                source_password= source_pwd,
                dest_path= dest_path,
                dest_username= dest_user,
                dest_password= dest_pwd,
                filename= self.initbackupname
            )

        #step 3: restore db to DR
        if self.chkoptrestore_var.get() == 1:
            if dr_server.__contains__("10.14") == False:
                messagebox.showerror(f"Error found", "target server only in subnet 10.14x.yy.zz")
                return
            database.restore_a_database(dr_server, drsqllogin, drsqlpwd, drdatabasename, initrestorepath)

        #step 4: config log shipping primary
        if self.chkoptconfig_var.get() == 1:
            if database.config_logshipping_check_backupjob(kbt_server, self.entUsername.get(), self.entPassword.get(), self.databaseName) == 1:
                database.config_logshipping_primary_add(kbt_server, self.entUsername.get(), self.entPassword.get(), self.databaseName, dr_server, source_path)
            else:
                database.config_logshipping_primary(kbt_server, self.entUsername.get(), self.entPassword.get(), self.databaseName, dr_server, source_path)

            #config log shipping secondary
            database.config_logshipping_secondary(dr_server, drsqllogin, drsqlpwd, drdatabasename, kbt_server, source_path, drcopypath)

        print('finish.')
