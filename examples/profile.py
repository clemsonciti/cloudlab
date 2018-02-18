import geni.portal as portal
import geni.rspec.pg as rspec
import geni.rspec.igext as IG

pc = portal.Context()
request = rspec.Request()

pc.defineParameter("workerCount",
                   "Number of Hadoop DataNodes",
                   portal.ParameterType.INTEGER, 3)

pc.defineParameter("controllerHost", "Name of NameNode",
                   portal.ParameterType.STRING, "node0", advanced=True,
                   longDescription="The short name of the Hadoop NameNode.  You shold leave \
                   this alone unless you really want the hostname to change.")

params = pc.bindParameters()

tourDescription = "This profile provides a configurable Hadoop testbed with one NameNode \
and customizable number of DataNodes."

tourInstructions = \
  """
### Basic Instructions
Once your experiment nodes have booted, and this profile's configuration scripts \
have finished deploying Hadoop inside your experiment, you'll be able to visit 
[the HDFS Web UI](http://{host-%s}:9870) (approx. 5-15 minutes).  
""" % (params.controllerHost)

#
# Setup the Tour info with the above description and instructions.
#  
tour = IG.Tour()
tour.Description(IG.Tour.TEXT,tourDescription)
tour.Instructions(IG.Tour.MARKDOWN,tourInstructions)
request.addTour(tour)

# Create a link with type LAN
link = request.LAN("lan")

# Generate the nodes
for i in range(params.workerCount + 1):
    node = request.XenVM("node" + str(i))
    node.disk_image = "urn:publicid:IDN+emulab.net+image+emulab-ops:UBUNTU16-64-STD"
    iface = node.addInterface("if" + str(i))
    iface.component_id = "eth1"
    iface.addAddress(rspec.IPv4Address("192.168.1." + str(i + 1), "255.255.255.0"))
    link.addInterface(iface)
    
    node.addService(rspec.Execute(shell="/bin/sh",
                                  command="sudo wget http://apache.cs.utah.edu/hadoop/common/hadoop-3.0.0/hadoop-3.0.0.tar.gz"))
    node.addService(rspec.Execute(shell="/bin/sh",
                                  command="sudo tar xzf hadoop-3.0.0.tar.gz -C /opt/"))
    node.addService(rspec.Execute(shell="/bin/sh",
                                  command="sudo cp /local/repository/master /opt/hadoop-3.0.0/ect/hadoop/"))
    node.addService(rspec.Execute(shell="/bin/sh",
                                  command="sudo cp /local/repository/slaves /opt/hadoop-3.0.0/etc/hadoop/workers"))
    node.addService(rspec.Execute(shell="/bin/sh",
                                  command="sudo cp /local/repository/core-site.xml /opt/hadoop-3.0.0/etc/hadoop/core-site.xml"))
    node.addService(rspec.Execute(shell="/bin/sh",
                                  command="sudo apt-get update -y"))
    node.addService(rspec.Execute(shell="/bin/sh",
                                  command="sudo apt-get install -y default-jdk"))
    node.addService(rspec.Execute(shell="/bin/sh",
                                  command="export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64/"))    
    if i != 0:
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo sleep 30"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo /opt/hadoop-3.0.0/bin/hadoop-daemon.sh start datanode"))
    else:
        node.routable_control_ip = True
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo /opt/hadoop-3.0.0/bin/hdfs namenode -format PEARC18"))
        node.addService(rspec.Execute(shell="/bin/sh",
                                      command="sudo /opt/hadoop-3.0.0/bin/hdfs --daemon start namenode"))

# Print the RSpec to the enclosing page.
portal.context.printRequestRSpec(request)