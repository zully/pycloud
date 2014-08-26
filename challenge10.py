import os
import pyrax
import time


pyrax.set_credential_file(os.path.expanduser("~/.rackspace_cloud_credentials"))

########################################
#CHANGE THESE VALUES TO WHAT YOU WANT!!!
server_convention = 'web'              #
server_num = 2                         #
ram = 512                              #
image = 'CentOS 6.3'                   #
lb_name = 'web-lb'                     #
########################################

cs = pyrax.cloudservers
clb = pyrax.cloud_loadbalancers
dns = pyrax.cloud_dns
cf = pyrax.cloudfiles

cont_list = cf.list_containers()

#Set flavor id from flavor ram
for flv in cs.flavors.list():
    if flv.ram == ram:
        flavor_id = flv.id
#Set image id from image name
for img in cs.images.list():
    if img.name == image:
        image_id = img.id

#Prompt for the fqdn and make sure the domain alrelady exists in DNS
fqdn = raw_input('Enter the FQDN: ')
domain_name = fqdn.split('.')[1] + '.' + fqdn.split('.')[2]

try:
    dom = dns.find(name=domain_name)
except exc.NotFound:
    print "The domain " + domain_name + " was not found.  Exiting."
    quit()

while True:
    cont_name = raw_input("Container Name: ")

    #make sure container does not already exist
    cont_exists = 'false'
    for i in range(len(cont_list)):
        if cont_name == cont_list[i]:
            cont_exists = 'true';
    if cont_exists == 'false':
        print 'Container does not exist, creating it.'
        cont = cf.create_container(cont_name)
        time.sleep(1)
        break
    else:
        print 'Container exists.  Try again'

content = """public ssh key (id_rsa.pub)"""

files = {"/root/.ssh/authorized_keys": content}

print "Creating cloud servers, please wait..."
passwords = ''
#Create servers and store their passwords
for num in range(1,(server_num+1)):
    server_name = server_convention + str(num)
    temp = cs.servers.create(server_name, image_id, flavor_id, files=files)
    time.sleep(5)
    passwords = passwords + str(temp.adminPass) + ":"
    for srv in cs.servers.list():
        if str(srv.name) == server_name:
            last_srv = cs.servers.get(srv.id)

time.sleep(30)

print "Waiting for builds to complete..."

pyrax.utils.wait_until(last_srv, "status", "ACTIVE", interval=10, attempts=100, verbose=False)

print "Servers built!"

#Print output for servers
for num in range (1,(server_num+1)):
    for srv in cs.servers.list():
        if str(srv.name) == (server_convention + str(num)):
            server = cs.servers.get(srv.id)
    print '--------------------------'
    print 'Name: ' + server.name
    print 'Password: ' + passwords.split(':')[(num-1)]
    networks = server.networks
    if "." in networks['public'][0]:
        ip = networks['public'][0]
    else:
        ip = networks['public'][1]
    print 'Public: ' + ip
    print 'Private: ' + networks['private'][0]

print '--------------------------'

print "Creating load balancer..."

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
lb_addr = (lb_str.split('address=')[1]).split(' ')[0]
print 'Address: ' + lb_addr

text = """This is my custom error page"""
print 'Adding health monitor and custom error page...'

pyrax.utils.wait_until(lb, "status", "ACTIVE", interval=5, attempts=30, verbose=False)
lb.add_health_monitor("HTTP", delay=10, timeout=10, attemptsBeforeDeactivation=3, path="/", statusRegex="None", bodyRegex="None")
pyrax.utils.wait_until(lb, "status", "ACTIVE", interval=5, attempts=30, verbose=False)
lb.set_error_page(text)

a_rec = {"type": "A",
        "name": fqdn,
        "data": lb_addr,
        "ttl": 300}
recs = dom.add_records(a_rec)
if recs != '':
    print 'Domain Added.'

with open("error.html", "w") as tmp:
    tmp.write(text)
    nm = os.path.basename("error.html")

print 'Uploading error page to cloud files'
cf.upload_file(cont, nm)

print
print 'Complete!'
