import os
import pyrax
import time

pyrax.set_credential_file(os.path.expanduser("~/.rackspace_cloud_credentials"))
clb = pyrax.cloud_loadbalancers
cs = pyrax.cloudservers

########################################
#CHANGE THESE VALUES TO WHAT YOU WANT!!!
server_convention = 'web'              #
server_num = 2                         #
ram = 512                              #
image = 'CentOS 6.3'                   #
lb_name = 'web-lb'                     #
########################################

#Set flavor id from flavor ram
for flv in cs.flavors.list():
    if flv.ram == ram:
        flavor_id = flv.id
#Set image id from image name
for img in cs.images.list():
    if img.name == image:
        image_id = img.id

passwords = ''
#Create servers and store their passwords
print "Building cloud servers, please wait..."
for num in range(1,(server_num+1)):
    server_name = server_convention + str(num)
    temp = cs.servers.create(server_name, image_id, flavor_id)
    time.sleep(5)
    passwords = passwords + str(temp.adminPass) + ":"
    for srv in cs.servers.list():
        if str(srv.name) == server_name:
            last_srv = cs.servers.get(srv.id)

time.sleep(60)

finished = 'false'
#Wait for last server created to be listed as active
while finished == 'false':
    if str(last_srv.status) != 'ACTIVE':
        finished = 'true'
        time.sleep(10)
    else:
        time.sleep(30)

print "Servers built, creating load balancer..."

priv_ips = ''
for num in range (1,(server_num+1)):
    for srv in cs.servers.list():
        if str(srv.name) == (server_convention + str(num)):
            server = cs.servers.get(srv.id)
            priv_ips = priv_ips + str(server.networks['private'][0]) + '/'

#create load balancer with first node
first_node = clb.Node(address=priv_ips.split('/')[0], port=80, condition="ENABLED")
vip = clb.VirtualIP(type="PUBLIC")
lb = clb.create(lb_name, port=80, protocol="HTTP", nodes=[first_node], virtual_ips=[vip])
pyrax.utils.wait_until(lb, "status", "ACTIVE", interval=5, attempts=30, verbose=False)
time.sleep(5)

print "Load balancer with first node created, adding additional nodes..."

for num in range (1,server_num):
    new_node = clb.Node(address=priv_ips.split('/')[num], port=80, condition="ENABLED")
    lb.add_nodes([new_node])
    pyrax.utils.wait_until(lb, "status", "ACTIVE", interval=5, attempts=30, verbose=False)
    time.sleep(5)
    print "Node " + str(num) + " added..."

pyrax.utils.wait_until(lb, "status", "ACTIVE", interval=5, attempts=30, verbose=False)

for lbs in clb.list():
    if lbs.name == lb_name:
        lb_str = str(lbs)
        nodes_str = str(lbs.nodes)
print
print "Load Balancer: " + (lb_str.split('name=')[1]).split(',')[0]
print 'Address: ' + (lb_str.split('address=')[1]).split(' ')[0]

num = 1
node_ips = '|  '
for nodes in lbs.nodes:
    node_ips = node_ips + ((nodes_str.split('Node')[num]).split('address=')[1]).split(',')[0] + '  |  '
    num = num + 1
print 'Nodes: ' + node_ips
print
print 'Complete!'
