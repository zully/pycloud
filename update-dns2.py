#!/usr/bin/env python
# -*- coding: utf-8 -*-

from warnings import filterwarnings; filterwarnings("ignore")
from socket import gethostbyaddr
import os
import pyrax
import pyrax.exceptions as exc
from urllib2 import urlopen

# Set Domain name here
domain_name = 'domain.com'
host_name = 'host.domain.com'

try:
    my_ip = urlopen('http://ip.devcube.org').read().strip('\n')
except:
    print "Unable to get Public IP!"
    raise SystemExit

#print my_ip

try:
    dns_ip = str(gethostbyaddr(host_name)[-1]).strip("[']")
except:
    print "Unable to get DNS IP!"
    raise SystemExit

#print dns_ip

if my_ip != dns_ip:
    pyrax.set_setting("identity_type", "rackspace")
    creds_file = os.path.expanduser("/root/.rackspace_cloud_credentials")
    try:
        pyrax.set_credential_file(creds_file)
    except exc.AuthenticationFailed:
        print "Bad Username or Password"
        raise SystemExit

    dns = pyrax.cloud_dns

    try:
        dom = dns.find(name=domain_name)
    except exc.NotFound:
        print "Unable to find domain by that name: " + domain_name
        raise SystemExit

    try:
        recs = dom.list_records()
    except:
        print "Unable to list records!"
        raise SystemExit

    for rec in recs:
        if rec.name == host_name:
            try:
                rec.update(data=my_ip)
            except:
                print "Unable to update record!"
                raise SystemExit
