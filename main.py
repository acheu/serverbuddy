#!/usr/bin/env python

import csv
import os
import subprocess
import Tkinter as tk
from collections import namedtuple
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
    # tab_struct = namedtuple('tab_scruct')
    global termID, frameID, winID, gameID
    termID = []     # PIDs in Terminals
    frameID = []    # Frame ID
    winID = []      # Window IDs of the Terminal windows
    gameID = []     # List of short names as we add them
    fileloc = "launch_commands/list.txt"  # Local directory file
    menubar = tk.Menu(root)
    filemenu = tk.Menu(menubar, tearoff=0)
    note = Notebook(root)
    filemenu.add_command(label='Add New Tab', command=lambda: write_new_tab_frame(note, fileloc, gameID))
    filemenu.add_command(label='Remove Tab', command=lambda: remove_specific_tab_frame(note, fileloc))
    filemenu.add_separator()
    filemenu.add_command(label='Exit',
                         command=lambda: destroy_all(root))
    menubar.add_cascade(label='File', menu=filemenu)
    root.config(menu=menubar)
    # Format: [short name], [long name], [path to sh file]
    root_buttons = tk.Frame(root)
    root_buttons.pack(side='top')
    bannerLoc = 'assets/banner.png'
    img = ImageTk.PhotoImage(Image.open(bannerLoc))
    rb_img = tk.Label(root_buttons, image=img)
    rb_b1 = tk.Button(root_buttons, text='Refresh List',
                      command=lambda: refresh_tabs(note, fileloc, gameID))
    rb_b2 = tk.Button(root_buttons, text='Exit', command=lambda: destroy_all(root))
    rb_img.pack(side='left')
    rb_b1.pack(side='left', fill='both', expand='yes')
    rb_b2.pack(side='right', fill='both', expand='yes')
    refresh_tabs(note, fileloc, gameID)
    root.mainloop()
    # PAST THIS POINT, THE USER HAS PRESSED THE "X" CLOSE
    # BUTTON ON THE WINDOW, invoking root.destroy
    send_kill_all()


def remove_specific_tab_frame(note, fileloc):
    """The frame displaying a list of all games with a delete button"""
    remove_tab_frame = tk.Tk()
    remove_tab_frame.geometry('200x300+200+200')
    remove_tab_frame.title('Remove Tab Select')
    rm_tb = tk.Listbox(remove_tab_frame)
    rm_tb.pack(expand='yes')
    for item in gameID:
        rm_tb.insert(tk.END, item)
    del_b = tk.Button(remove_tab_frame, text='Delete selected',
                      command=lambda: remove_specific_tab(note, rm_tb, fileloc))
    del_b.pack()


def remove_specific_tab(note, rm_tb, fileloc):
    """The function called by the remove_specific_tab_frame to delete games"""
    game_lists = rm_tb.curselection()
    num = map(int, game_lists)
    for it in num:
        lines = []
        commands = []
        with open(fileloc, 'r') as csvfile:
            read = csv.reader(csvfile, delimiter=',', quotechar='|')
            for i, row in enumerate(read):
                shortname, longname, commandname = map(str.strip, row)
                if shortname != gameID[it]:
                    lines.append(row)
                else:
                    commands.append(commandname)
        with open(fileloc, 'w') as csvfile:
            for line in lines:
                towrite = line[0] + ',' + line[1] + ',' + line[2] + '\n'
                csvfile.write(towrite)
        for com in commands:
            os.remove(com)
        refresh_tabs(note, fileloc, gameID)
        rm_tb.delete(tk.ANCHOR)


def write_new_tab_frame(note, fileloc, gameID):
    new_tab_frame = tk.Tk()
    new_tab_frame.title('Add New Tab Form')
    text_one = tk.Frame(new_tab_frame)
    text_two = tk.Frame(new_tab_frame)
    text_three = tk.Frame(new_tab_frame)
    new_tab_frame.geometry('640x150+200+200')
    tk.Label(text_one, text='Tab Name').pack(side='left')
    text_short = tk.Text(text_one, height=1)
    tk.Label(text_two, text='Full Name').pack(side='left')
    text_long = tk.Text(text_two, height=1)
    tk.Label(text_three, text='Command').pack(side='left')
    text_command = tk.Text(text_three, height = 5)
    text_short.pack(fill='both', side='left')
    text_long.pack(fill='both', side='left')
    text_command.pack(fill='both', side='left')
    text_one.pack(fill='both')
    text_two.pack(fill='both')
    text_three.pack(fill='both')
    submit_button = tk.Button(new_tab_frame, text='Add Tab',
                              command=lambda: write_new_tab(new_tab_frame,
                                                            note, gameID, fileloc, text_short,
                                                            text_long, text_command))
    submit_button.pack()
    new_tab_frame.mainloop()


def error_prompt(err_text):
    """Error prompt message, send any input string and it'll display a prompt."""
    widget = tk.Tk()
    widget.title('Error Message')
    text_frame = tk.Frame(widget)
    widget.geometry('300x100+200+200')
    tk.Label(text_frame, text=err_text).pack(pady=(20, 20), padx=(10, 10))
    text_frame.pack()
    tk.Button(widget, text='  OK  ', command=lambda: widget.destroy()).pack()


def write_new_tab(new_tab_frame, note, gameID, fileloc, ts, tl, tc):
    short_name = ts.get('1.0', tk.END).strip()
    long_name = tl.get('1.0', tk.END).strip()
    command_text = tc.get('1.0', tk.END).strip()
    check_names = True
    if (' ' in short_name):
        error_prompt('Error: Cannot have spaces in Tab Name')
        check_names = False
    if ('.' in short_name):
        error_prompt('Error: Cannot have . in Tab Name')
        check_names = False
    if short_name in gameID:
        error_prompt('Error: Short name already taken')
        check_names = False
    if check_names:
        file_command_name = 'launch_commands/' + short_name + '_launch.sh'
        write_line = short_name + ',' + long_name + ',' + file_command_name + '\n'
        with open(fileloc, 'a') as lists:
            lists.write(write_line)
        with open(file_command_name, 'a') as t:
            command_text = '#!/bin/bash\n' + command_text
            t.write(command_text)
        refresh_tabs(note, fileloc, gameID)
        new_tab_frame.destroy()


def destroy_all(root):  # destroys all terminals and root
    send_kill_all()
    root.destroy()


def refresh_tabs(note, fileloc, gameID):
    with open(fileloc, 'rb') as csvfile:
        read = csv.reader(csvfile, delimiter=',', quotechar='|')
        cnt = 0
        for i, row in enumerate(read):
            shortname = []
            if len(row) > 0:
                shortname, longname, command = map(str.strip, row)
                if not any(row[0] in s for s in gameID):
                    frameID.append(tk.Frame(note))
                    termID.append(0)  # lengthen the termIDS
                    note.add(frameID[i], text=shortname)
                    note_button = tk.Frame(frameID[i])
                    note_button.pack()
                    lbutton = 'Launch: ' + longname
                    launch_command = lambda com, j: lambda: send_launch_game(com, j)
                    edit_command = lambda eg, k: lambda: send_misc_command(eg, k)
                    kill_command = lambda kcom: lambda: send_kill_game(kcom)
                    lg = tk.Button(note_button,
                                   text=lbutton,
                                   command=launch_command(command, shortname))
                    kg = tk.Button(note_button,
                                   text="Kill Terminal",
                                   command=kill_command(shortname))
                    eg = tk.Button(note_button,
                                   text='Edit Script',
                                   command=edit_command('/bin/nano ' + command, shortname))
                    gameID.append(shortname)
                    lg.pack(side="left")
                    eg.pack(side='left')
                    kg.pack(side="right")
                    panel = tk.Frame(frameID[i], height=300, width=500)
                    panel.pack(fill=tk.BOTH, side='bottom', expand=tk.YES)
                    wip = panel.winfo_id()
                    winID.append(wip)
                elif shortname != gameID[i]:
                    send_kill_game(shortname)
                    termID.remove(termID[i])
                    frameID[i].destroy()
                    frameID.remove(frameID[i])
                    winID.remove(winID[i])
                    gameID.remove(gameID[i])
            cnt += 1
        if cnt < len(gameID):
            # Remove the last entry
            shortname = gameID[-1]
            send_kill_game(shortname)
            termID.remove(termID[-1])
            frameID[-1].destroy()
            frameID.remove(frameID[-1])
            winID.remove(winID[-1])
            gameID.remove(gameID[-1])
        
    note.pack(fill='both', expand=True)


def send_kill_all():
    """Kill all open terminals - called when program quits."""
    for i in range(0, len(termID)):
        if termID[i] > 0:
            os.killpg(termID[i].pid, SIGINT)


def send_misc_command(command, in_term):
    """Duplicate of send_launch_game but does not default look inside its own directory.

    Keyword arguments:
    command -- String, text of command to be passed to terminal
    in_term -- String, short tab name of game to be referenced
    """
    in_term = gameID.index(in_term)
    ref_term = winID[in_term]
    if ref_term > 0:
        send_kill_game(gameID[in_term])
    command = "/usr/bin/xterm -into " + str(ref_term) + " -geometry 100x21 -sb -hold -e " + "/" + command.strip()
    process = subprocess.Popen(command, preexec_fn=os.setpgrp,  shell=True)
    termID[in_term] = process


def send_launch_game(command, sn):
    """Launches the game based off the command given and the short name, sn """
    in_term = gameID.index(sn)
    ref_term = winID[in_term]
    if ref_term > 0:
        send_kill_game(gameID[in_term])
    command = "/usr/bin/xterm -into " + str(ref_term) + " -geometry 100x21 -sb -hold -e " + 'sudo sh ' + os.getcwd() + "/" + command.strip()
    process = subprocess.Popen(command, preexec_fn=os.setpgrp,  shell=True)
    termID[in_term] = process


def send_kill_game(term):
    """term is the short name"""
    term = gameID.index(term)
    if termID[term] > 0:
        os.killpg(termID[term].pid, SIGINT)
        termID[term] = 0


if __name__ == '__main__':
    main()
