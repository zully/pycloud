import os
import pyrax
import time

pyrax.set_credential_file(os.path.expanduser("~/.rackspace_cloud_credentials"))

dns = pyrax.cloud_dns
cs = pyrax.cloudservers
dns = pyrax.cloud_dns

#Prompt for the fqdn and make sure the domain alrelady exists in DNS
fqdn = raw_input('Enter the FQDN: ')
domain_name = fqdn.split('.')[1] + '.' + fqdn.split('.')[2]

try:
    dom = dns.find(name=domain_name)
except exc.NotFound:
    print "The domain " + domain_name + " was not found.  Exiting."
    quit()

#Prompt user to select a flavor
flvs = cs.flavors.list()
flvs_dict = {}
print "Select a Flavor"
for pos, flv in enumerate(flvs):
    print "%s: %s" % (pos, flv.name)
    flvs_dict[str(pos)] = flv.id
selection = None
while selection not in flvs_dict:
    if selection is not None:
        print " -- Invalid choice"
    selection = raw_input("Enter the number for your choice: ")

flavor_id = flvs_dict[selection]

#Prompt user to select an image
imgs = cs.images.list()
imgs_dict = {}
print "Select an Image"
for pos, img in enumerate(imgs):
    print "%s: %s" % (pos, img.name)
    imgs_dict[str(pos)] = img.id
selection = None
while selection not in imgs_dict:
    if selection is not None:
        print " -- Invalid choice"
    selection = raw_input("Enter the number for your choice: ")

image_id = imgs_dict[selection]

#Build the server
print "Creating cloud server, please wait..."
server = cs.servers.create(fqdn, image_id, flavor_id)

time.sleep(60)

print "Waiting for build to complete..."
finished = 'false'
#Wait for server to be listed as active
while finished == 'false':
    if str(server.status) != 'ACTIVE':
        finished = 'true'
        time.sleep(10)
    else:
        time.sleep(30)

print "Server build complete, creating DNS A record..."

#Get the public ipv4 address of the server
networks = server.networks

if "." in networks['public'][0]:
    ip = networks['public'][0]
else:
    ip = networks['public'][1]

a_rec = {"type": "A",
        "name": fqdn,
        "data": ip,
        "ttl": 300}
recs = dom.add_records(a_rec)
if recs != '':
    print 'Domain Added.'
print
print "Complete!"
