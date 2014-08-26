import os
import pyrax
import time

pyrax.set_credential_file(os.path.expanduser("~/.rackspace_cloud_credentials"))

########################################
#CHANGE THESE VALUES TO WHAT YOU WANT!!!
server_convention = 'web'              #
server_num = 3                         #
ram = 512                              #
image = 'CentOS 6.3'                   #
########################################

cs = pyrax.cloudservers

#Set flavor id from flavor ram
for flv in cs.flavors.list():
    if flv.ram == ram:
        flavor_id = flv.id
#Set image id from image name
for img in cs.images.list():
    if img.name == image:
        image_id = img.id

print "Creating cloud servers, please wait..."
passwords = ''
#Create servers and store their passwords
for num in range(1,(server_num+1)):
    server_name = server_convention + str(num)
    temp = cs.servers.create(server_name, image_id, flavor_id)
    time.sleep(5)
    passwords = passwords + str(temp.adminPass) + ":"
    for srv in cs.servers.list():
        if str(srv.name) == server_name:
            last_srv = cs.servers.get(srv.id)

time.sleep(30)

print "Waiting for builds to complete..."
pyrax.utils.wait_until(last_srv, "status", "ACTIVE", interval=30, attempts=500, verbose=False)

print "Servers built!"
print
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

print
print "Complete!"
