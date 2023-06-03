import API.server_entry_point as server
from threading import Thread
from API.util import PORT_GENERAL_ENTRY

class ShellServerEntry():

    def __init__(self):
        self.server = server.EntryPointServerTheaded(PORT_GENERAL_ENTRY, 10,10,0.1,None)
        self.server.start_server()

s = ShellServerEntry()