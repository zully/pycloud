import os
import pyrax
import pyrax.exceptions as exc


pyrax.set_credential_file(os.path.expanduser("~/.rackspace_cloud_credentials"))
dns = pyrax.cloud_dns

fqdn = raw_input('Enter the FQDN: ')
domain_name = fqdn.split('.')[1] + '.' + fqdn.split('.')[2]

try:
    dom = dns.find(name=domain_name)
except exc.NotFound:
    print "The domain " + domain_name + " was not found.  Exiting."
    quit()

ip_addr = raw_input('Enter the IP: ')
a_rec = {"type": "A",
        "name": str(fqdn),
        "data": str(ip_addr),
        "ttl": 300}

recs = dom.add_records(a_rec)
if recs != '':
    print 'Domain Added.'
print
print 'Complete!'
