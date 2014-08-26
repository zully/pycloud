#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pyrax
import pyrax.exceptions as exc
import urllib

username = "usernamehere"
apikey = "apikeyhere"
domain_name = "domain.com"
fqdn = "host.domain.com"

try:
    pyrax.set_credentials(username, apikey)
except exc.AuthenticationFailed:
    print "Something went wrong with authentication"

dns = pyrax.cloud_dns

dom = dns.find(name=domain_name)

records = dom.list_records()

ext_ip = urllib.urlopen('http://ifconfig.me/ip').read()
ext_ip = ext_ip.strip()

for record in records:
    if record.name == fqdn:
        if record.data != ext_ip:
            record.update(data=ext_ip)
