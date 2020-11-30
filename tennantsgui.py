from tkinter import *
import tkinter as tk
import tkinter.messagebox

window = Tk(className="Tennants GUI")
window.geometry('800x600')

tennants = tk.Listbox(window)
tennants.insert(1, "tennants")
tennants.pack(fill=tk.BOTH)
apartments = tk.Listbox(window)
apartments.insert(1, 'apartments')
apartments.pack(fill=tk.BOTH)
landlords = tk.Listbox(window)
landlords.insert(1, 'landlords')
landlords.pack(fill=tk.BOTH)

def genbil():
   tk.messagebox.showinfo( "GenBil", "Bills generated")

def genagr():
	tk.messagebox.showinfo("GenAgr", 'Agreement generated')

agr_button = tk.Button(window, text ="Generate agreement", command = genagr)
agr_button.pack()
bill_button = tk.Button(window, text ="Generate bills", command = genbil)
bill_button.pack()

def df_to_list(df):

    tree["columns"] = df.columns.values.tolist()
    for x in range(len(df.columns.values)):
        self.tree.column(df.columns.values[x], width=100)
        self.tree.heading(df.columns.values[x], text=df.columns.values[x], command=self.populate_selection)

    for index, row in df.iterrows():
        self.tree.insert("",0,text=index,values=list(row))

    self.tree.grid(row=50,column=0,rowspan=1,columnspan=12,sticky=N+E+W+S)

    self.tree.bind("<<TreeviewSelect>>", self.populate_selection)


window.mainloop()