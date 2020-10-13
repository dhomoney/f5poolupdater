###################################################################################################
#                                                                                                 #
#  Name: F5 Pool Updater                                                                          #
#                                                                                                 #
#  Description: This will add a large number of pool members with contiguous IPs to the defined   #
#               pool or it will remove all members to a pool. This was to support a testing       #
#               project I was on.                                                                 #
#                                                                                                 #
#  Usage: Adding -a for adding -d for deleting members. -h for help                               #
#                                                                                                 #
#  Version: 0.1b                                                                                  #
#                                                                                                 #
#  Date: 10-13-2020                                                                               #
#                                                                                                 #
#  Author: David Homoney - Technical Solutions Architect @ WWT                                    #
#                                                                                                 #
###################################################################################################

#Importation of needed modules
import sys
import ipaddress
from f5.bigip import ManagementRoot

#Variable Definitions
mgmt = ManagementRoot('10.253.252.128', 'admin', 'WWT_F5_Velos')
poolname = sys.argv[2]
numofaddr = 0


#This function checks to ensure the pool provided by the user actually exists
def poolexistcheck(poolname):
    doespoolexist = mgmt.tm.ltm.pools.pool.exists(name=poolname)
    #print(poolname)
    #print(doespoolexist)
    if (doespoolexist != True):
        print("The pool name provided " + poolname + " doesn't exist. Please try again.")
        # print(exit)
        sys.exit(0)
        return

#This function confirms desire to delete pool members and then deletes them all
def clearpool(poolname):
    global numofaddr
    pool = mgmt.tm.ltm.pools.pool.load(partition='Common', name=poolname)
    delallmem = input ("Are you sure you want to delete all pool members in " + str(poolname) + "? (y/n): ")
    if (delallmem == "y"):
        print("")
        print("")
        print("Deleting all members from " + str(poolname))
        for member in pool.members_s.get_collection():
            print("Deleting Member: " + member.name)
            member.delete()
            numofaddr = numofaddr + 1

    elif (delallmem == "n"):
        sys.exit(0)
    else:
        print("Dude seriously, it is a yes or no question. Dolt.")
        sys.exit(0)
    return

#This displays basic data about the pool member load and confirms with the user
def userquestion(poolname, startaddr, numofaddr, portnum, mask, network):
    print("Run with the following parameters?")
    print("")
    print("Pool Name: " + poolname)
    print("Starting Address: ", str(startaddr))
    print("Number of addresses: " + str(numofaddr))
    numofaddr = int(numofaddr)
    print("Pool Member Netmask: " + str(mask))
    print("Pool Member Network: " + str(network))
    print("")
    useranswer = input("Is this correct? (y/n): ")
    if (useranswer == "y"):
        print("")
        print("")
        print ("Validating Addresses....")
        print("")
        print("")
        testaddrs(startaddr, numofaddr, network)
    elif (useranswer == "n"):
        print ("Try Again")
        sys.exit(0)
    else:
        print ("Seriously? It is a yes or no question dumbass. Try again.")
        userquestion(poolname, startaddr, numofaddr, portnum)
    return

#This function ensures that the IP addresses are valid
def testaddrs(startaddr, numofaddr, network):
    for x in range(numofaddr):
        if (startaddr in network.network ):
            #print("Valid IP: " + str(startaddr))
            startaddr = ipaddress.ip_address(startaddr) + 1
        else:
            print("IP is not valid. Try again.")
            sys.exit(0)

    print("")
    print("")
    print("All IP Addresses are Valid. Continuing.")
    print("")
    print("")
    return

#This function loads all the members in to the pool
def addmembers(poolname, startaddr, numofaddr, portnum):
    pool_obj = mgmt.tm.ltm.pools.pool
    pool = pool_obj.load(partition='Common', name=poolname)
    members = pool.members_s
    member = pool.members_s.members

    for x in range(int(numofaddr)):
        memaddr = str(startaddr) + ":" + str(portnum)
        print ("Adding " + str(startaddr) + " on port " + str(portnum) + " in pool " + poolname + ".")
        m = pool.members_s.members.create(partition='Common', name=memaddr)
        m = pool.members_s.members.load(partition='Common', name=memaddr)
        startaddr = ipaddress.ip_address(startaddr) + 1

    print("")
    print("")
    print("")
    print("")
    return

#Main Program

if (sys.argv[1] == "-a"):
    if (len(sys.argv) != 7):
        print("6 Arguments Required for Adding Members - Action, Pool Name, Starting Address, Number of Addresses, Port, and CIDR Mask")
        sys.exit(0)
    else:
        startaddr = ipaddress.ip_address(sys.argv[3])
        numofaddr = sys.argv[4]
        portnum = sys.argv[5]
        mask = sys.argv[6]
        network = str(startaddr) + "/" + sys.argv[6]
        network = ipaddress.ip_interface(network)
        poolexistcheck(poolname)
        userquestion(poolname, startaddr, numofaddr, portnum, mask, network)
        addmembers(poolname, startaddr, numofaddr, portnum)
        print("Congratulations, you have added " + str(numofaddr) + " members to " + str(poolname))
elif (sys.argv[1] == "-d"):
    if (len(sys.argv) != 3):
        print("2 Arguments Require for Deleting Members - Action and Pool Name")
        sys.exit(0)
    else:
        poolexistcheck(poolname)
        clearpool(poolname)
        print("Congratulations, you have deleted " + str(numofaddr) + " members to " + str(poolname))

else:
    print("Incorrect Action Selected!")
    print("Use -a to Add Pool Members")
    print("Use -d to Delete Pool Members")
    sys.exit(0)
