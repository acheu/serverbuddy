#!/usr/bin/env python

import csv
import os
import subprocess
import Tkinter as tk
from collections import namedtuple
from ttk import Notebook
from PIL import ImageTk, Image
from signal import SIGINT
from cmdlist import cmdlist
from notificationbuddy import notificationbuddy
from time import time, sleep
from json import loads
from urllib import urlopen
import socket

class frame_make(tk.Frame):
    def __init__(self, parent):
        # Frame.__init__(self, parent, background="white")
        tk.Frame.__init__(self, parent)
        self.parent = parent
        self.initUI()

    def initUI(self):
        self.parent.title("Server Buddy")
        self.pack(fill=tk.BOTH, expand=1)


class tab_data():
    """ Class filled with functions that handle tab information and function"""
    def __init__(self):
        self.onlineico_obj = []
        self.prev_status = False
        self.ip = '127.0.0.1:00'

    def set_onlineico_obj(self, obj):
        self.onlineico_obj = obj

    def set_ip(self, obj):
        self.ip = obj


    def set_online_status(self, val):
        """ Changes online/offline icon on tab

        Keywords:
        val: boolean, true if server is read to be online, false else
        change_bool: output, true if the server is changing status from offline-> online or
        vice versa, false if there's no change in the previous status

        """
        online_ico = []
        if val:
            loc_on = 'assets/online.png'
            online_ico = ImageTk.PhotoImage(Image.open(loc_on))
        else:
            loc_off = 'assets/offline.png'
            online_ico = ImageTk.PhotoImage(Image.open(loc_off))
        self.onlineico_obj.configure(image=online_ico)
        self.onlineico_obj.image = online_ico  # Keep reference

        change_bool = False
        if self.prev_status != val:
            change_bool = True
            self.prev_status = val
        return change_bool


def main():
    root = tk.Tk()
    root.geometry("620x420+150+150")
    # root.iconbitmap('/home/chewie/Documents/server_buddy/favicon.ico')
    app = frame_make(root)
    # tab_struct = namedtuple('tab_scruct')
    global termID, frameID, winID, gameID, game_config, fileloc, ntfc
    global tabdata_obj  # FIX ME: Need to include other variables
    # tabdata_obj will be the list that holds all the info like GameID and info on online icons
    game_config = [] # Universal information with all games
    termID = []     # PIDs in Terminals
    frameID = []    # Frame ID
    winID = []      # Window IDs of the Terminal windows
    gameID = []     # List of short names as we add them
    srvcmd_loc = "launch_commands/servers_list.json"  # Local directory file
    fileloc = cmdlist(srvcmd_loc)  # Initializes
    ntfc = notificationbuddy()  # Initializes email server
    tabdata_obj = []
    menubar = tk.Menu(root)
    filemenu = tk.Menu(menubar, tearoff=0)
    note = Notebook(root)
    filemenu.add_command(label='Add New Tab', command=lambda: write_new_tab_frame(note, gameID))
    filemenu.add_command(label='Remove Tab', command=lambda: remove_specific_tab_frame(note))
    filemenu.add_command(label='Email Notification', command=lambda: setup_email_notification())
    filemenu.add_separator()
    filemenu.add_command(label='Exit',
                         command=lambda: destroy_all(root))
    menubar.add_cascade(label='File', menu=filemenu)
    root.config(menu=menubar)
    # Format: [short name], [long name], [path to sh file]
    root_buttons = tk.Frame(root)
    root_buttons.pack(side='top')
    bannerLoc = 'assets/banner_2.png'
    img = ImageTk.PhotoImage(Image.open(bannerLoc))
    root.iconbitmap('@candy.xbm')
    rb_img = tk.Label(root_buttons, image=img)
    rb_b1 = tk.Button(root_buttons, text='Refresh List',
                      command=lambda: refresh_tabs(note, game_config))
    rb_b2 = tk.Button(root_buttons, text='Exit', command=lambda: destroy_all(root))
    rb_img.pack(side='left')
    rb_b1.pack(side='left', fill='both', expand='yes')
    rb_b2.pack(side='right', fill='both', expand='yes')
    refresh_tabs(note, gameID)
    root.after(1000, lambda: check_status_tabs(note, game_config))
    # After 120 seconds, check the status of the tabs (ie are they online?)
    root.mainloop()
    # PAST THIS POINT, THE USER HAS PRESSED THE "X" CLOSE
    # BUTTON ON THE WINDOW, invoking root.destroy
    send_kill_all()


def check_status_tabs(note, game_config):
    #""" Called periodically to check the running status and set the dict isonline"""
    # FIX ME: idk why, but uncommenting the above line sends an EOL syntax error
    entries = cmdlist.return_list(fileloc)
    
    ip = []
    try:
        __data = loads(urlopen("http://ip.jsontest.com/").read())
        ip = __data['ip']
    except:
        print 'Unable to resolve host IP'
        ip = 'UNKOWN'
    
   
    for itt in range(len(entries)):
        port = entries[itt]['port']
        result = []
        addr = ip + ':' + port
        sn = entries[itt]['shortname']
        last_line = ''
        try:
            logfile = 'logs/' + sn + '.log'
            fileHandle = open ( logfile ,"r" )
            log_lines = fileHandle.readlines()
            fileHandle.close()
            last_line = log_lines[-1]
        except:
            last_line = ''
        __write = False
        if last_line == 'EOS' or last_line == 'EOS\n':
            __write = False
        else:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex((ip,int(port)))
                #if result:
                #    result = subprocess.Popen(['/bin/ping', '-c1', '-w100', addr], stdout=subprocess.PIPE).stdout.read()
                #    print result
            except:
                print 'Unable to reach internet'
                result = 0

            tabdata_obj[itt].ip.set(addr)
            
            if result is not 0:
                __write = True    
        cmdlist.edit_field(fileloc, sn, 'isonline', __write)

    # for itt2 in termID:
    #    if itt2 is not 0:
    #        print itt2.stdout
    refresh_tabs(note, game_config)
    note.after(10000, lambda: check_status_tabs(note, game_config))
    # FIX ME: I'm worried after prolong use this recursion will overload memory

def edit_server_tab(itt):
    """ Tab info for editing the server information"""
    editsrv_tab = tk.Tk()
    editsrv_tab.geometry('390x220+200+200')
    editsrv_tab.title('Edit Server Information')
    listbound = tk.Frame(editsrv_tab)
    __data = cmdlist.return_list(fileloc)
    tabinfo = __data[itt]
    valuelabels = []
    
    for i in range(len(tabinfo)):
        keys = tabinfo.keys()
        tk.Label(listbound, text=keys[i]).grid(row=i, sticky='W')
        valuelabels.append(tk.Entry(listbound))
        valuelabels[i].grid(row=i, column=1)
        valuelabels[i].insert(0, tabinfo[keys[i]])
    submit_b = tk.Button(editsrv_tab, text='Submit Changes',
                         command=lambda:edit_server_submit_changes(editsrv_tab, itt, keys, valuelabels))
    listbound.pack()
    submit_b.pack()


def edit_server_submit_changes(submit_frame, game, keys, values):
    for itt in range(len(keys)):
        #print keys[itt]
        #print values[1].get()
        cmdlist.edit_field(fileloc, gameID[game], keys[itt], values[itt].get())
    submit_frame.destroy()

def setup_email_notification():
    email_frame = tk.Tk()
    email_frame.geometry('300x200+200+200')
    email_frame.title('Email Notification Setup')
    # FIX ME: finish


def remove_specific_tab_frame(note):
    """The frame displaying a list of all games with a delete button"""
    remove_tab_frame = tk.Tk()
    remove_tab_frame.geometry('200x300+200+200')
    remove_tab_frame.title('Remove Tab Select')
    rm_tb = tk.Listbox(remove_tab_frame)
    rm_tb.pack(expand='yes')
    for item in gameID:
        rm_tb.insert(tk.END, item)
    del_b = tk.Button(remove_tab_frame, text='Delete selected',
                      command=lambda: remove_specific_tab(note, rm_tb))
    del_b.pack()


def remove_specific_tab(note, rm_tb):
    """The function called by the remove_specific_tab_frame to delete games"""
    game_lists = rm_tb.curselection()
    num = map(int, game_lists)
    for it in num:
        lines = []
        com = cmdlist.get_field(fileloc, gameID[it], 'command')
        cmdlist.remove_entry(fileloc, gameID[it])
        #with open(fileloc, 'r') as csvfile:
        #   read = csv.reader(csvfile, delimiter=',', quotechar='|')
        #    for i, row in enumerate(read):
        #        shortname, longname, commandname = map(str.strip, row)
        #        if shortname != gameID[it]:
        #            lines.append(row)
        #        else:
        #            commands.append(commandname)
        #with open(fileloc, 'w') as csvfile:
        #    for line in lines:
        #        towrite = line[0] + ',' + line[1] + ',' + line[2] + '\n'
        #        csvfile.write(towrite)
        try:
            # Remove command files associated with removed games
            #print com
            os.remove(com)
        except ValueError, e:
            error_prompt(e)
        
        refresh_tabs(note, gameID)
        rm_tb.delete(tk.ANCHOR)


def error_prompt(err_text):
    """Error prompt message, send any input string and it'll display a prompt."""
    widget = tk.Tk()
    widget.title('Error Message')
    text_frame = tk.Frame(widget)
    widget.geometry('300x100+200+200')
    tk.Label(text_frame, text=err_text).pack(pady=(20, 20), padx=(10, 10))
    text_frame.pack()
    tk.Button(widget, text='  OK  ', command=lambda: widget.destroy()).pack()


def write_new_tab_frame(note, gameID):
    new_tab_frame = tk.Tk()
    new_tab_frame.title('Add New Tab Form')
    text_one = tk.Frame(new_tab_frame)
    text_two = tk.Frame(new_tab_frame)
    text_three = tk.Frame(new_tab_frame)
    text_four = tk.Frame(new_tab_frame)
    text_five = tk.Frame(new_tab_frame)
    new_tab_frame.geometry('670x190+200+200')
    tk.Label(text_one, text='Tab Name').pack(side='left')
    text_short = tk.Text(text_one, height=1)
    tk.Label(text_two, text='Full Name').pack(side='left')
    text_long = tk.Text(text_two, height=1)
    tk.Label(text_three, text='Command').pack(side='left')
    text_command = tk.Text(text_three, height = 5)
    tk.Label(text_four, text='Port').pack(side='left')
    text_port = tk.Text(text_four, height = 1)
    tk.Label(text_five, text='Is Public? [T/F]').pack(side='left')
    #text_ispublic = tk.Text(text_five, height = 1)
    __var = tk.StringVar(text_five)
    __var.set('True')
    option_var = tk.OptionMenu(text_five, __var, 'True', 'False')
    text_short.pack(fill='both', side='right')
    text_long.pack(fill='both', side='right')
    text_command.pack(fill='both', side='right')
    text_port.pack(fill='both', side='right')
    option_var.pack(fill='both', side='left')
    text_one.pack(fill='both')
    text_two.pack(fill='both')
    text_three.pack(fill='both')
    text_four.pack(fill='both')
    text_five.pack(fill='both')
    submit_button = tk.Button(new_tab_frame, text='Add Tab',
                              command=lambda: write_new_tab(new_tab_frame,
                                                            note, gameID, text_short,
                                                            text_long, text_command, text_port,
                                                            __var))
    submit_button.pack()
    new_tab_frame.mainloop()


def write_new_tab(new_tab_frame, note, gameID, ts, tl, tc, tp, ti):
    short_name = ts.get('1.0', tk.END).strip()
    long_name = tl.get('1.0', tk.END).strip()
    command_text = tc.get('1.0', tk.END).strip()
    port = tp.get('1.0', tk.END).strip()
    __data = loads(urlopen("http://ip.jsontest.com/").read())
    __ip = __data['ip']
    ti = ti.get()
    if ti == 'True':
        ispublic = True
    else:
        ispublic = False
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
        with open(file_command_name, 'a') as t:
            # Write the command file
            logname = 'logs/' + short_name + '.log'
            __bashline = '#!/bin/bash\n'
            __logstart = "echo 'START' > " +logname + '\n'
            __logend = "echo 'EOS' >> " + logname
            command_text = __bashline + __logstart + command_text + '\n' + __logend
            t.write(command_text)
            with open(logname, 'w+') as l:
                # Initialize server log with the End of Service delimeter
                l.write('EOS')
            
        tab_entry = {
            'shortname': short_name,
            'longname': long_name,
            'command': file_command_name,
            'isonline': False,  # Default added field
            'ispublic': ispublic, # Default added field
            'port': port,
            'date_created': time(),  # In floating sec from unix epoch
            'date_prevlaunch': 0,
            'date_offlinesince': time()
        }
        # Commented out old r/w process ad replaced with cmdlist.addentry below
        cmdlist.add_entry(fileloc, tab_entry)
        #cmdlist.addentry expects object as second entry with longname, shortname, and command
        refresh_tabs(note, gameID)
        new_tab_frame.destroy()


def destroy_all(root):  # destroys all terminals and root
    send_kill_all()
    root.destroy()


def refresh_tabs(note, game_config):
    entries = cmdlist.return_list(fileloc)
    for itt in range(len(entries)):
        shortname = entries[itt]['shortname']
        longname = entries[itt]['longname']
        command = entries[itt]['command']
        online_pic = []
        if not any(shortname in s for s in gameID):
            # If JSON file has a new game listed not in gameID, add it
            frameID.append(tk.Frame(note))
            termID.append(0)  # lengthen the termIDS
            note.add(frameID[itt], text=shortname)
            note_button = tk.Frame(frameID[itt])
            note_button.pack()
            lbutton = 'Launch: ' + longname
            #__data = loads(urlopen("http://ip.jsontest.com/").read())
            #__ip = __data['ip']
            # Reference http://stackoverflow.com/questions/24508730/finding-network-external-ip-addresses-using-python
            launch_command = lambda com, j: lambda: send_launch_game(com, j)
            edit_command = lambda eg, k: lambda: send_misc_command(eg, k)
            kill_command = lambda kcom: lambda: send_kill_game(kcom)
            edit_tab = lambda l: lambda: edit_server_tab(l)
            lg = tk.Button(note_button,
                           text=lbutton,
                           command=launch_command(command, shortname))
            kg = tk.Button(note_button,
                           text="Kill Terminal",
                           command=kill_command(shortname))
            eg = tk.Button(note_button,
                           text='Edit Script',
                           command=edit_command('/bin/nano ' + command, shortname))
            i = tk.Button(note_button,
                          text= 'i', command=edit_tab(itt))
            #__loc = tk.StringVar()
            #__loc.set('')
            address = '127.0.0.1' + ':' + entries[itt]['port']
            __newtab = tab_data()  # Initialize new tab_data
            __newtab.ip = tk.StringVar()
            __newtab.ip.set(address)
            pi = tk.Label(note_button, textvariable = __newtab.ip)
            photo = ImageTk.PhotoImage(Image.open('assets/online.png'))
            online_pic = tk.Label(note_button, image=photo)
            online_pic.image = photo  # Keep reference
            tabdata_obj.append(__newtab)  # Then store it in the list of all tab objects
            tab_data.set_onlineico_obj(__newtab, online_pic)
            
            gameID.append(shortname)
            lg.pack(side="left")
            eg.pack(side='left')
            kg.pack(side="left")
            i.pack(side='left')
            pi.pack(side='right')
            online_pic.pack(side='right')
            panel = tk.Frame(frameID[itt], height=300, width=500)
            panel.pack(fill=tk.BOTH, side='bottom', expand=tk.YES)
            wip = panel.winfo_id()
            winID.append(wip)
        
        __onl = cmdlist.is_online(fileloc, shortname)
        # __onl is True if the tab is online, False else
        prevchange = tab_data.set_online_status(tabdata_obj[itt], __onl)
        if prevchange:
            if __onl:
                msg = shortname + ' is now online'
                ntfc.send_email(msg)
                cmdlist.edit_field(fileloc, shortname, 'date_prevlaunch', time())
            else:
                msg = shortname + ' has gone offline'
                ntfc.send_email(msg)
                cmdlist.edit_field(fileloc, shortname, 'date_offlinesince', time())
            
    for itt2 in range(len(gameID)):  # FIX ME: switch to enumerate
        __jsonshorts = cmdlist.get_all_shortname(fileloc)
        if not any(gameID[itt2] in s for s in __jsonshorts):
            # IF gameID has a game no longer in the JSON, delete that game
            # Game was removed from JSON list, so kill game on that tab and destroy tab
            send_kill_game(gameID[itt2])
            termID.remove(termID[itt2])
            frameID[itt2].destroy()
            frameID.remove(frameID[itt2])
            winID.remove(winID[itt2])
            gameID.remove(gameID[itt2])

            # Remove tabdata_obj
            # Remove game_config
            tabdata_obj.remove(tabdata_obj[itt2])
            #game_config.remove(game_config[itt2])
            
            break  # FIX ME: Based off the assumption that you can only delete one at a time
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
    cmdlist.edit_field(fileloc, sn, 'date_prevlaunch', time())
    

def send_kill_game(term):
    """term is the short name"""
    term = gameID.index(term)
    if termID[term] > 0:
        os.killpg(termID[term].pid, SIGINT)
        termID[term] = 0


if __name__ == '__main__':
    main()
