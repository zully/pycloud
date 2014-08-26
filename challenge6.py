import os
import pyrax
import time

pyrax.set_credential_file(os.path.expanduser("~/.rackspace_cloud_credentials"))

cf = pyrax.cloudfiles

cont_list = cf.list_containers()


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

#Check and print container attributes
cont = cf.get_container(cont_name)
print
print "Container Info:"
print "cdn_enabled", cont.cdn_enabled
print "cdn_ttl", cont.cdn_ttl
print "cdn_log_retention", cont.cdn_log_retention
print "cdn_uri", cont.cdn_uri
print "cdn_ssl_uri", cont.cdn_ssl_uri
print "cdn_streaming_uri", cont.cdn_streaming_uri
print
print 'Complete!'
