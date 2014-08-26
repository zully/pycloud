import os
import pyrax
import time

pyrax.set_credential_file(os.path.expanduser("~/.rackspace_cloud_credentials"))
cs = pyrax.cloudservers
servers = cs.servers.list()
srv_dict = {}

#Get server to image, name for the image, and name for the server to create
print "Choose a server to image: "
for pos, srv in enumerate(servers):
    print "%s: %s" % (pos, srv.name)
    srv_dict[str(pos)] = srv.id
selection = None
while selection not in srv_dict:
    if selection is not None:
        print "Invalid option."
    selection = raw_input("Enter the number for your choice: ")

server_id = srv_dict[selection]
nm = raw_input("Enter a name for the image: ")
server_name = raw_input("Enter a name for your new server: ")

img_id = cs.servers.create_image(server_id, nm)

#get the flavor of the original server
for server in cs.servers.list():
    if server.id == server_id:
        flavor_id = server.flavor['id']

print "Image '%s' is being created. ID: %s" % (nm, img_id)

#Monitor the image for completion
img_complete = 'false'
while img_complete == 'false':
    for img in cs.images.list():
        if img.name == nm:
            if img.status == 'ACTIVE':
                img_complete = 'true'
                time.sleep(10)
            else: 
                time.sleep(30)

#Build the server from the image taken
print "Image complete, building server..."

server = cs.servers.create(server_name, img_id, flavor_id)
password = str(server.adminPass)

time.sleep(30)

finished = 'false'
#Wait for last server created to be listed as active
pyrax.utils.wait_until(server, "status", "ACTIVE", interval=30, attempts=500, verbose=False)

for srv in cs.servers.list():
    if str(srv.name) == server_name:
        server = cs.servers.get(srv.id)

print "Server build complete!"
print
print '--------------------------'
print 'Name: ' + server.name
print 'Password: ' + password
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
