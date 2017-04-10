from cloudmesh_client.common.Shell import Shell
from time import sleep
from write2files import HostsWriter
from IPy import IP
import cmd
import sys


class VMS(cmd.Cmd):
    
    def setup(self, cloud="cloud=chameleon"):
        
        self.cloud = cloud
        print "Ignore Error: \n Please define a key first, e.g.: cm key add --ssh <keyname> \n " \
              "-- If key has been successfully added into the database and uploaded into the cloud \n" \
              "Ignore Error: \n problem uploading key veera to cloud chameleon: Key pair 'veera' already exists.\n " \
              "******************************************************************************************************"
        result = Shell.cm("reset")
        print result
        result = Shell.cm("key add --ssh")
        print result
        result = Shell.cm("key", "upload")
        print result
        result = Shell.cm("default", self.cloud)
        print result
        result = Shell.cm("refresh", "on")
        print result
    
    def __init__(self):
        
        cmd.Cmd.__init__(self)
        self.prompt = '> '
        self.n = 1
        self.floating_ip_list = []
        self.static_ip_list = []
        # self.setup()
        
    
    def do_setCloud(self, cloud):
        
        self.cloud = "cloud="+cloud
        self.setup(cloud=self.cloud)
        
    def do_boot(self, n):
        
        print "Starting to boot", n ,"Virtual Machines"
        
        for i in range(int(n)):
                
            Shell.cm("vm", "boot")
            fip_result = Shell.cm("vm", "ip assign")            # floating IP
            floating_ip = fip_result.split(' ')[-2][:-6]
            try:
                IP(floating_ip)
                # the below cmd is the "cm vm ip show" as ip is not getting updated automatically in the DB
                Shell.cm("vm", "ip assign")
                sip_result = Shell.cm("vm", "ip show")          # static IP
                static_ip = sip_result.split("\n")[3].split(' ')[3]
                
            except:
                print "floating IP error encountered"
                print "Stopping to create further VMs"
                break

            self.floating_ip_list.append(floating_ip)
            self.static_ip_list.append(static_ip)

        if self.floating_ip_list == []:
            print "No VMs created"
        else:
            print "Returning IPs of VMs created"
            print "Floating IPs list    :",self.floating_ip_list
            print "Static IPs list      :",self.static_ip_list
            print "wirting IPs to respective files ..."
        
        HW = HostsWriter()
        HW.writeFIPs(floatingIPs=self.floating_ip_list)

    def do_delete(self, names):
        
        names = str(names).split(' ')
        for name in names:
            delete_machine = "delete "+name
            print delete_machine
            result = Shell.cm("vm", delete_machine)
            print result
    
    def help_boot(self):
        
        print "syntax: boot [count]\n"
        print "usage: "
        print "       |  command   |  description                                        "
        print "        ------------------------------------------------------------------"
        print "          boot [n]     boots 3 vms one after the other"

    def do_quit(self, arg):
        
        sys.exit(1)

    def help_quit(self):
        
        print "syntax: quit or q\n",
        print "usage: "
        print "       |  command   |  description                                        "
        print "        ------------------------------------------------------------------"
        print "          quit         terminates the application"
        print "          q            terminates the application"
        
    def do_getFloatingIPs(self):
        
        print "Floating IPs of all Machines",self.floating_ip_list

    def do_getStaticIPs(self):
        print "Static IPs of all Machines", self.static_ip_list
    
    def help_getFloatingIPs(self):
        
        print "syntax: getFloatingIPs()\n",
        print "usage: "
        print "       |  command          |  description                                        "
        print "        ------------------------------------------------------------------"
        print "          getFloatingIPs()    returns the Floating IPs of all machines"

    def help_getStaticIPs(self):
    
        print "syntax: getStaticIPs()\n",
        print "usage: "
        print "       |  command          |  description                                        "
        print "        ------------------------------------------------------------------"
        print "          getStaticIPs()    returns the Static IPs of all machines"
    
    def help_delete(self):

        print "syntax: delete [names]\n",
        print "usage: "
        print "       |  command        |  description                                        "
        print "        ------------------------------------------------------------------"
        print "          delete v-001      deletes machine v-001"
        print "          delete v-002      deletes machine v-001"
        print "          delete v*         deletes all machines starting with v"
    
    def help_setCloud(self):
    
        print "internal method"

    # shortcuts
    do_q = do_quit
    help_q = help_quit
    
    
if __name__ == "__main__":
    vms = VMS()
    vms.cmdloop()