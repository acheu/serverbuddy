#!/usr/bin/env python

import csv
import os
import subprocess
import Tkinter as tk
from ttk import Notebook
from PIL import ImageTk, Image
from signal import SIGINT


class frame_make(tk.Frame):

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
    root.geometry("620x400+150+150")
    # root.iconbitmap(default='assets/refresh.png')
    app = frame_make(root)
    fileloc = "list.txt"  # Local directory file
    # Format: [short name], [long name], [path to sh file]
    root_buttons = tk.Frame(root)
    root_buttons.pack(side='top')
    bannerLoc = 'assets/banner.png'
    img = ImageTk.PhotoImage(Image.open(bannerLoc))
    rb_img = tk.Label(root_buttons, image=img)
    rb_b1 = tk.Button(root_buttons, text='Refresh List', command=lambda: refresh_tabs(root, fileloc, gameID))
    rb_b2 = tk.Button(root_buttons, text='Exit', command=lambda: destroy_all(root))
    rb_img.pack(side='left', fill='both', expand='yes')
    rb_b1.pack(side='left', fill='both')
    rb_b2.pack(side='right', fill='both')
    global termID, frameID, winID, gameID
    termID = []     # PIDs in Terminals
    frameID = []    # Frame ID
    winID = []      # Window IDs of the Terminal windows
    gameID = []     # List of short names as we add them
    refresh_tabs(root, fileloc, gameID)
    root.mainloop()
    # PAST THIS POINT, THE USER HAS PRESSED THE "X" CLOSE BUTTON ON THE WINDOW, invoking root.destroy
    send_kill_all()  # only need to close the terminals, the root's been destroyed at this point


def destroy_all(root):  # destroys all terminals and root
    send_kill_all()
    root.destroy()


def refresh_tabs(root, fileloc, gameID):
    note = Notebook(root)
    with open(fileloc, 'rb') as csvfile:
        read = csv.reader(csvfile, delimiter=',', quotechar='|')
        for i, row in enumerate(read):
            if (len(row) > 0 and not any(row[0] in s for s in gameID)):
                shortname, longname, command = map(str.strip, row)
                frameID.append(tk.Frame(note))
                termID.append(0)  # lengthen the termIDS
                note.add(frameID[i], text=shortname)
                note_button = tk.Frame(frameID[i])
                note_button.pack()
                lbutton = 'Launch: ' + longname
                launch_command = lambda com, j: lambda: send_launch_game(com, j)
                kill_command = lambda kcom: lambda: send_kill_game(kcom)
                lg = tk.Button(note_button,
                               text=lbutton,
                               command=launch_command(command, i))
                kg = tk.Button(note_button,
                               text="Kill Terminal",
                               command=kill_command(i))
                gameID.append(shortname)
                lg.pack(side="left")
                kg.pack(side="right")
                panel = tk.Frame(frameID[i], height=300, width=500)
                panel.pack(fill=tk.BOTH, side='bottom', expand=tk.YES)
                wip = panel.winfo_id()
                winID.append(wip)
    note.pack(fill='both', expand=True)


def send_kill_all():  # Kill all open terminals - called when program quits
        # command = "kill " + ' '.join(map(str,termID)) + " &> /dev/null"
        # print command
        # Kill will apply command to all elements
        # subprocess.call(command, shell=True)
    for i in range(0,len(termID)):
        if termID[i] > 0:
            os.killpg(termID[i].pid, SIGINT)
        


def send_launch_game(command, in_term):
    ref_term = winID[in_term]
    if ref_term > 0:
        send_kill_game(in_term)
    command = "/usr/bin/xterm -into " + str(ref_term) + " -geometry 100x21 -sb -hold -e " + os.getcwd() + "/" + command.strip()
    process = subprocess.Popen(command, preexec_fn=os.setpgrp,  shell=True)
    termID[in_term] = process


def send_kill_game(term):
    if termID[term] > 0:
        os.killpg(termID[term].pid, SIGINT)
        termID[term] = 0


if __name__ == '__main__':
    main()
