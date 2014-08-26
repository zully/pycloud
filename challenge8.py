import os
import pyrax
import time
import pyrax.utils as utils

pyrax.set_credential_file(os.path.expanduser("~/.rackspace_cloud_credentials"))

cf = pyrax.cloudfiles
dns = pyrax.cloud_dns

cont_list = cf.list_containers()

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


#make container public
cont.make_public(ttl=900)

print cont.cdn_uri

text = """This is my index.html file
"""
with open("index.html", "w") as tmp:
    tmp.write(text)
    nm = os.path.basename("index.html")

new_meta = {"X-Container-Meta-Web-Index": "index.html"}
cf.upload_file(cont, nm)
cf.set_container_metadata(cont, new_meta)

cname_rec = {"type": "CNAME",
        "name": str(fqdn),
        "data": (str(cont.cdn_uri)).split('//')[1],
        "ttl": 300}
recs = dom.add_records(cname_rec)
if recs != '':
    print 'Domain Added.'
print
print 'Complete!'
