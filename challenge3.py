import os
import pyrax
import time

pyrax.set_credential_file(os.path.expanduser("~/.rackspace_cloud_credentials"))

cf = pyrax.cloudfiles

cont_list = cf.list_containers()

cont_name = raw_input("Container Name: ")

#Get the directory to be uploaded
while True:
    dir_name = raw_input("Directory to Upload: ")
    dir_name = os.path.abspath(dir_name)
    if os.path.isdir(dir_name) != True:
        print('Directory does not exist!')
    else:
        break

#if container doesnt exist, create it
cont_exists = 'false'
for i in range(len(cont_list)):
    if cont_name == cont_list[i]:
        cont_exists = 'true';
if cont_exists == 'false':
    print 'Container does not exist, creating it.'
    cont = cf.create_container(cont_name)

#upload files to container
ignore = []
print "Beginning Folder Upload"
upload_key, total_bytes = cf.upload_folder(dir_name, cont_name, ignore=ignore)
    
print "Total bytes to upload:", total_bytes
uploaded = 0
while uploaded < total_bytes:
    uploaded = cf.get_uploaded(upload_key)
    print "Progress: %4.2f%%" % ((uploaded * 100.0) / total_bytes)
    time.sleep(1)

print "Complete!"
