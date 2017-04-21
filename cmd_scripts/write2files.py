import os

class HostsWriter():
    
    def __init__(self):
        
        # removing Ip config files
        
        # delete hosts
        if os.path.isfile("./zeppelin/hosts") == True:
            os.remove("./zeppelin/hosts")
        
        # delete sprak-defaults.conf
        if os.path.isfile("./zeppelin/spark-defaults.conf") == True:
            os.remove("./zeppelin/spark-defaults.conf")
            
        # delete spark-env.sh
        if os.path.isfile("./zeppelin/spark-env.sh") == True:
            os.remove("./zeppelin/spark-env.sh")

        # delete spark-env.sh
        if os.path.isfile("./zeppelin/slaves") == True:
            os.remove("./zeppelin/slaves")
    
    def writeIPs(self, staticIPs, floatingIPs):
        
        # hosts recreation
        file = open("./zeppelin/hosts", "w")
        file.write("[All_nodes]\n")
        
        for sip,fip in zip(staticIPs,floatingIPs):
            file.write(sip+" ansible_host="+fip+" ansible_ssh_user=cc \n")

        file.write("\n\n")
        file.write("[Master_node]\n")
        file.write(staticIPs[-1]+" ansible_host="+floatingIPs[-1]+ " ansible_ssh_user=cc \n")

        file.write("\n\n")
        file.write("[Zeppelin_node]\n")
        file.write(staticIPs[-1]+" ansible_host="+floatingIPs[-1]+ " ansible_ssh_user=cc \n")
        
        file.close()
        
        # sprak-defaults.conf recreation
        file = open("./zeppelin/spark-defaults.conf", "w")
        file.write("spark.master    spark://"+ staticIPs[-1] +":8081")
        file.close()
        
        # spark-env.sh recreation
        file = open("./zeppelin/spark-env.sh", "w")
        file.write("# config file to be distributed across cluster \n")
        file.write("SPARK_MASTER_HOST="+staticIPs[-1]+"\n")
        file.write("SPARK_MASTER_PORT=8081\n")
        file.write("SPARK_MASTER_WEBUI_PORT=8082\n")
        file.close()
        
        # slaves recreation
        file = open("./zeppelin/slaves", "w")
                
        if len(staticIPs) > 1:
            for sip in staticIPs[:-1]:
                file.write(sip+"\n")
        elif len(staticIPs) == 1:
            file.write(staticIPs[-1])
        file.close()
            