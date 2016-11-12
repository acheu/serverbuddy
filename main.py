#!/usr/bin/env python

import csv
import os
import subprocess 
import Tkinter as tk
from ttk import Notebook
from PIL import ImageTk, Image


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
    #root.iconbitmap(default='assets/refresh.png')
    app = frame_make(root)
    
    fileloc = "list.txt"  # Local directory file
    #Format: [short name],[long name],[path to sh file]

    root_buttons= tk.Frame(root)
    root_buttons.pack(side='top')

    bannerLoc = 'assets/banner.png'
    img = ImageTk.PhotoImage(Image.open(bannerLoc))
    
    tk.Label(root_buttons, image = img).pack(side='left', fill='both', expand='yes')
    tk.Button(root_buttons, text='Refresh List',command= lambda : refresh_tabs(note, fileloc, gameID)).pack(side='left', fill='both')
    tk.Button(root_buttons, text='Exit', command=lambda : destroy_all(root)).pack(side='right',fill='both')


    global termID, frameID, winID, gameID
    termID = []     # PIDs in Terminals
    frameID = []    # Frame ID
    winID = []      # Window IDs of the Terminal windows
    gameID = []     # List of short names as we add them
    
    note = Notebook(root)
    
    refresh_tabs(note,fileloc,gameID)

    note.pack(fill='both', expand=True)    
    root.mainloop()

    #PAST THIS POINT, THE USER HAS PRESSED THE "X" CLOSE BUTTON ON THE WINDOW, invoking root.destroy
    send_kill_all() #only need to close the terminals, the root's been destroyed at this point

def destroy_all(root): #destroys all terminals and root
    send_kill_all()
    root.destroy()

def refresh_tabs(note, fileloc, gameID):
    with open(fileloc, 'rb') as csvfile:
        read = csv.reader(csvfile, delimiter=',', quotechar='|')
        for i, row in enumerate(read):
            if (len(row) > 0 and not any(row[0] in s for s in gameID)):
                shortname, longname, command = map(str.strip, row)
                
                frameID.append(tk.Frame(note))
                termID.append(0) #lengthen the termIDS
                note.add(frameID[i], text=shortname)

                note_button = tk.Frame(frameID[i])
                note_button.pack()
                
                lbutton = 'Launch: ' + longname
                launch_command = lambda com, j: lambda : send_launch_game(com, j)
                kill_command = lambda kcom: lambda : send_kill_game(kcom)
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
                panel.pack(fill=tk.BOTH,side='bottom', expand=tk.YES)
                
                wip = panel.winfo_id()
                winID.append(wip)

    note.pack(fill='both', expand = True)
    
def send_kill_all(): #Kill all open terminals - called when program quits
    if len(termID)>0:
        command = "kill " + ' '.join(map(str,termID)) + " &> /dev/null" #kill will apply command to all elements
        subprocess.call(command, shell=True)

def send_launch_game(command, in_term):
    ref_term = winID[in_term]
    if ref_term > 0:
        send_kill_game(in_term)
    command = "/usr/bin/xterm -into " + str(ref_term) + " -geometry 100x20 -sb -hold -e " + os.getcwd() + "/"+ command.strip()
    pid = subprocess.Popen(command,shell=True).pid
    #termID.append(pid + 1) #pid+1 is the PID of the whole window, pid is just the command run in the terminal
    termID[in_term] = pid + 1
    
def send_kill_game(term):
    #command = "kill " + "/proc/" + str(termID[0]) + "/fd/0"
    if termID[term] > 0:
        command = "kill " + str(termID[term]) + " &> /dev/null"
        subprocess.call(command, shell=True)
        #del termID[term]
        termID[term] = 0

if __name__ == '__main__':
    main()
