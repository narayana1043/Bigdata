import time
from cloudmesh_client.common.Shell import Shell
from write2files import HostsWriter
from IPy import IP
import cmd
import os, sys
import getpass

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
        self.prompt = '>> '
        self.n = 1
        self.floating_ip_list = []
        self.static_ip_list = []
        # self.setup()
    
    def do_setCloud(self, cloud):
        
        self.cloud = "cloud="+cloud
        self.setup(cloud=self.cloud)
        
    def do_boot(self, n):
    
        self.floating_ip_list = []
        self.static_ip_list = []
        try:
        
            for i in range(int(n)):
    
                print "Starting to boot Virtual Machine : ",i+1
                Shell.cm("vm", "boot --secgroup=naveen-def")
                fip_result = Shell.cm("vm", "ip assign")            # floating IP
                floating_ip = fip_result.split(' ')[-2][:-6]
                
                try:
                
                    IP(floating_ip)
                    # the below cmd is the "cm vm ip show" as ip is not getting updated automatically in the DB
                    Shell.cm("vm", "ip assign")
                    
                    while True:
                        
                        sip_result = Shell.cm("vm", "ip show")          # static IP
                        static_ip = sip_result.split("\n")[3].split(' ')[3]
                        if IP(static_ip):
                            
                            break
                    
                except:
                
                    print "floating IP error encountered"
                    print "Stopping to create further VMs"
                    break
    
                self.floating_ip_list.append(floating_ip)
                self.static_ip_list.append(static_ip)
        
        except ValueError:
            
            self.help_boot()

        if self.floating_ip_list == []:
            
            print "No VMs created"
        
        else:
            
            print "Returning IPs of VMs created"
            print "Floating IPs list    :",self.floating_ip_list
            print "Static IPs list      :",self.static_ip_list
            print "wirting IPs to respective files ..."
        
            HW = HostsWriter()
            HW.writeIPs(staticIPs=self.static_ip_list, floatingIPs=self.floating_ip_list)
            
            # starting ansible
            if os.path.exists(os.environ['HOME']+'/.ssh/known_hosts'):
                os.remove(os.environ['HOME']+'/.ssh/known_hosts')
                
            print "Running the ansible-playbook for zepplin"
            
            # taking password
            password = getpass.getpass("Enter ansible valut password: ")
            tempPassFile = open('.log.txt', 'w')
            tempPassFile.write(password)
            tempPassFile.close()
            startTime = time.time()
            deployment_logs = os.popen(
                'ansible-playbook zeppelin/Zeppelin.yml -i zeppelin/hosts --vault-password-file .log.txt').read()
            os.remove('.log.txt')
            endTime = time.time()
            
            totalDeployTime = endTime - startTime
            print "Time taken to depoly ",n," virtual machines for zeppelin is ",totalDeployTime
            
            # writing logs
            tempDepLog = open('deployment_logs','w')
            tempDepLog.write(deployment_logs)
            tempDepLog.close()

            # checking logs
            deployment_logs_lines = deployment_logs.splitlines()

            wordList = []
            for line in deployment_logs_lines:
                words = line.split(' ')
                for word in words:
                    wordList.append(word)

            if "fatal" in wordList or '"Decryption' in wordList or "failed" in wordList or 'fatal:' in wordList:
                print "Check deployment logs for errors during deployment"
            else:
                print "Deployment Successful"

    def do_delete(self, names):
        
        names = str(names).split(' ')
        for name in names:
            
            delete_machine = "delete "+name
            print delete_machine
            result = Shell.cm("vm", delete_machine)
            print result

    def do_quit(self, arg):
        
        sys.exit(1)
        
    def do_getFloatingIPs(self):
        
        print "Floating IPs of all Machines",self.floating_ip_list

    def do_getStaticIPs(self):
        print "Static IPs of all Machines", self.static_ip_list
    
    def default(self, line):
        """Called on an input line when the command prefix is not recognized.
           In that case we execute the line as Python code.
        """
        self.stdout.write('*** Unknown syntax: %s\n'%line)

    # ---------Documentation-----------------

    def help_boot(self):
    
        print "syntax: boot [count]\n"
        print "usage: "
        print "       |  command   |  description                                        "
        print "        ------------------------------------------------------------------"
        print "          boot [n]     boots 3 vms one after the other"

    def help_quit(self):
    
        print "syntax: quit or q\n",
        print "usage: "
        print "       |  command   |  description                                        "
        print "        ------------------------------------------------------------------"
        print "          quit         terminates the application"
        print "          q            terminates the application"
    
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

    # ---------shortcuts----------------------
    do_q = do_quit
    do_exit = do_quit
    help_q = help_quit
    help_exit = help_quit
    
    
if __name__ == "__main__":
    vms = VMS()
    vms.cmdloop()