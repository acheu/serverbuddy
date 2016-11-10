#!/usr/bin/env python

import csv
import os
import subprocess 
import Tkinter as tk
from ttk import Notebook


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
    root.geometry("600x400+150+150")
    app = frame_make(root)

    fileloc = "list.txt"  # Local directory file
    #Format: [short name],[long name],[path to sh file]

    global termID, frameID, winID 
    termID = []     # PIDs in Terminals
    frameID = []    # Frame ID
    winID = []      # Window IDs of the Terminal windows
    gameID = []     # List of short names as we add them

    note = Notebook(root)
    with open(fileloc, 'rb') as csvfile:
        read = csv.reader(csvfile, delimiter=',', quotechar='|')
        for i, row in enumerate(read):
            if len(row) > 0:
                shortname, longname, command = map(str.strip, row)

                frameID.append(tk.Frame(note))
                note.add(frameID[i], text=shortname)
                               
                lbutton = 'Launch: ' + longname
                launch_command = lambda com, j: lambda : send_launch_game(com, j)
                lg = tk.Button(frameID[i],
                          text=lbutton,
                          command=launch_command(command, i))
                #kg = tk.Button(frameID[i],
                #          text="Stop Game",
                #          command=lambda: send_kill_game(wip,i))

                gameID.append(shortname)
                
                lg.pack(in_=frameID[i])
                #kg.pack(in_=frameID[i])

                term = tk.Frame(frameID[i], height=300, width=500)
                term.pack(fill=tk.BOTH,side='top', expand=tk.YES)
                
                wip = term.winfo_id()
                winID.append(wip)

    note.pack(fill='both', expand=True)            
    tk.Button(root, text='Refresh List',command= lambda : refresh_tabs(note, fileloc, gameID)).pack(side='left')
    tk.Button(root, text='Exit', command=root.destroy).pack(side='right')
    #tk.Button(root, text='Exit',command=destroy_all(root)).pack(side='right')
    
    root.mainloop()
    
    send_kill_all() #At end of program, kill all open terminal processes
    #destroy_all(root)

def destroy_all(root): #destroys all terminals and root
    send_kill_all()
    root.destroy


def refresh_tabs(note, fileloc, gameID):
    with open(fileloc, 'rb') as csvfile:
        read = csv.reader(csvfile, delimiter=',', quotechar='|')
        for i, row in enumerate(read):
            if (len(row) > 0 and not any(row[0] in s for s in gameID)):
                shortname, longname, command = map(str.strip, row)

                frameID.append(tk.Frame(note))
                note.add(frameID[i], text=shortname)
                               
                lbutton = 'Launch: ' + longname
                launch_command = lambda com, j: lambda : send_launch_game(com, j)
                lg = tk.Button(frameID[i],
                          text=lbutton,
                          command=launch_command(command, i))

                gameID.append(shortname)
                
                lg.pack(in_=frameID[i])

                term = tk.Frame(frameID[i], height=300, width=500)
                term.pack(fill=tk.BOTH,side='top', expand=tk.YES)
                
                wip = term.winfo_id()
                winID.append(wip)
                
    note.pack(fill='both', expand = True)
    
def open_tabs(): #opens tabs - called also to refresh tabs for any new ones
    print "hello"
    

#open terminal is not being used atm
def open_terminal(wip): #opens terminals
    command = "/usr/bin/xterm -into " + str(wip) + " -geometry 80x20 -sb -hold -e " + os.getcwd() + "/"
    pid = subprocess.Popen(command.split(" ")).pid
    termID.append(pid)
    
def send_kill_all(): #Kill all open terminals - called when program quits
    if len(winID)>0:
        command = "kill " + ' '.join(map(str,winID)) + " &> /dev/null" #kill will apply command to all elements
        subprocess.call(command, shell=True)

def send_launch_game(command, in_term):
    in_term = winID[in_term]
    command = "/usr/bin/xterm -into " + str(in_term) + " -geometry 100x20 -sb -hold -e " + os.getcwd() + "/"+ command.strip()
    pid = subprocess.Popen(command,shell=True).pid
    termID.append(pid)
    
def send_kill_game(window_ID,terminal_call):
    #command = "kill " + "/proc/" + str(termID[0]) + "/fd/0"
    command = "kill -2 " + str(termID[0])
    subprocess.call(command, shell=True)
    
    

if __name__ == '__main__':
    main()
