from os import path
from json import dump, load


class cmdlist(object):
    def __init__(self, cmdsrv_file):
        if not path.isfile(cmdsrv_file):
            with open(cmdsrv_file, 'w+') as f:
                print 'cmdlist created'
        self.loc = cmdsrv_file

    def return_list(self):
        data = []
        with open(self.loc, 'r') as f:
            try:
                data = load(f)
            except ValueError, e:
                print e
                data = []
        return data


    # Add-----------------------------------------
    def add_entry(self, entry):
        data = cmdlist.return_list(self)
        keys = ['shortname', 'longname', 'command', 'isonline', 'ispublic', 'port', 'date_created', 'date_prevlaunch', 'date_offlinesince']
        for __key in keys:
            if not __key in entry:
                entry[__key] = 'NaN'
        # FIXME: Right now I expect object_entry to be formatted correctly in the main file
        data.append(entry)
        with open(self.loc, 'w') as f:
            dump(data, f)


    # Remove--------------------------------------
    def remove_entry(self, entry):
        data = cmdlist.return_list(self)
        ent = -1
        for a in range(len(data)):
            if data[a]['shortname'] == entry:
                ent = a
                break
        if ent >= 0:
            # print data[ent]['shortname']
            data.remove(data[ent])
        with open(self.loc, 'w') as f:
            dump(data, f)


    # Edit----------------------------------------
    def edit_field(self, sn, field, value):
        """ Edits any field

        Keywoard arguments:
        -self:
        -sn: shortname of chosen service
        -field: field you want to change
        -value: value you want to set that field of the sn to
        """
        data = cmdlist.return_list(self)
        __at = cmdlist.get_iterator(self, sn)
        data[__at][field] = value
        with open(self.loc, 'w') as f:
            dump(data, f)


    # Is------------------------------------------
    def is_online(self, check_shortname):
        res = False
        with open(self.loc, 'r') as f:
            data = cmdlist.return_list(self)
            for a in range(len(data)):
                if data[a]['shortname'] == check_shortname:
                    if data[a]['isonline'] == '1':
                        res = True
                    break
        return res


    # Get-----------------------------------------
    def get_all_shortname(self):
        data = cmdlist.return_list(self)
        snames = []
        for a in range(len(data)):
            snames.append(data[a]['shortname'])
        return snames


    def get_field(self, sn, field):
        # Given a shortname give any field of that game object
        data = cmdlist.return_list(self)
        res = []
        for itt in range(len(data)):
            if data[itt]['shortname'] == sn:
                res = data[itt][field]
        return res


    def get_iterator(self, sn):
        """ From shortname, get the iterator, ie data[itt] of the JSON return_list """
        data = cmdlist.return_list(self)
        itt = 0  # iterator to be returned
        for a in range(len(data)):
            if data[a]['shortname'] == sn:
                itt = a
                break
        return itt


    def get_all_longnames(self):
        data = cmdlist.return_list(self)
        snames = []
        for a in range(len(data)):
            snames.append(data[a]['longname'])
        return snames
