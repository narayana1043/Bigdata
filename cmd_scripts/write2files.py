class HostsWriter():
    
    def __init__(self):
        self.file = open("hosts", "w")
        self.file.write("[Zeppelin_hosts]\n")
    
    def writeFIPs(self, floatingIPs):
        
        for fip in floatingIPs:
            self.file.write(fip+" ansible_ssh_user=cc \n")
        self.file.close()
            