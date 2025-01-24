
import TabShipLog
import TabShipSP
import TabRestorePointInTime as re
import tkinter as tk
from tkinter import ttk


class MainApplication(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("DRShipper - OnewaySync")
        self.iconbitmap("icon.ico")
        self.geometry("800x560")
        self.maxsize(800, 560)

        # Notebook để chứa các tab
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, expand=True)


        # Thêm tab3 vào notebook
        self.tab3 = re.TabRestorePointInTime(self.notebook)
        self.notebook.add(self.tab3, text="Restore Point In Time", padding=20)

        # Thêm tab1 vào notebook
        self.tab1 = TabShipSP.TabShipSP(self.notebook)
        self.notebook.add(self.tab1, text="DB Schemas", padding=20)

        # Thêm tab2 vào notebook
        self.tab2 = TabShipLog.TabShipLog(self.notebook)
        self.notebook.add(self.tab2, text="Transaction Log", padding=20)
        


if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()
