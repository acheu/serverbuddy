#!/usr/bin/env python

import csv
import os
import subprocess 
import Tkinter as tk
from ttk import Notebook


class mainframe(tk.Frame):

    def __init__(self, parent):
        # Frame.__init__(self, parent, background="white")
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.parent.title("Server Buddy")
        self.pack(fill=tk.BOTH, expand=1)


def main():
    root = tk.Tk()
    root.geometry("800x500+200+200")
    app = mainframe(root)

    fileloc = "list.txt"  # Local directory file

    note = Notebook(root)

    termID = []  # ID's of the terminals with respect to their number tab
    frameID = []  # Frame ID
    winID = []  # Window IDs

    with open(fileloc, 'rb') as csvfile:
        read = csv.reader(csvfile, delimiter=',', quotechar='|')
        itt = 0
        for row in read:
            if len(row) > 0:
                game = row
                frameID.append(tk.Frame(note))

                note.add(frameID[itt], text=game[0])

                lbutton = 'Launch: ' + game[1]

                tk.Button(frameID[itt],
                          text=lbutton,
                          command=lambda: send_launch_game(game[2], wip, termID)).pack(padx=10, pady=10)

                term = tk.Frame(frameID[itt], height=400, width=500)
                term.pack(fill=tk.BOTH, expand=tk.YES)

                wip = term.winfo_id()
                winID.append(wip)
                
                itt += 1

    tk.Button(root, text='Exit', command=root.destroy).pack(padx=10, pady=10)
    note.pack()
    root.mainloop()
    # print termID
    kill_xterm(termID)

def kill_xterm(ids):
    for termid in ids:
        os.system('kill -9 ' + str(termid))


def send_launch_game(command, window_ID, termIDs):
    print command
    command = "/usr/bin/xterm -into " + str(window_ID) + " -geometry 80x20 -sb -hold -e " + os.getcwd() + "/"+ command.strip()
    #print command
    pid = subprocess.Popen(command.split(" ")).pid
    termIDs.append(pid)


if __name__ == '__main__':
    main()
