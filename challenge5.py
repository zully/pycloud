import os
import sys
import time
import pyrax
import getpass


pyrax.set_credential_file(os.path.expanduser("~/.rackspace_cloud_credentials"))
cdb = pyrax.cloud_databases
instance_name = pyrax.utils.random_name(8)

flavors = cdb.list_flavors()

while True:
    nm = raw_input("Enter a name for your new instance: ")
    if nm.isalnum():
        break
    else:
        print "Numbers and letters only, please try again..."
        print

print
print "Available Flavors:"
for pos, flavor in enumerate(flavors):
    print "%s: %s, %s" % (pos, flavor.name, flavor.ram)

flav = int(raw_input("Select a Flavor for your new instance: "))
try:
    selected = flavors[flav]
except IndexError:
    print "Invalid selection; exiting."
    sys.exit()

print
sz = int(raw_input("Enter the volume size in GB (1-50): "))

instance = cdb.create(nm, flavor=selected, volume=sz)
print "Name:", instance.name
print "ID:", instance.id
print "Status:", instance.status
status = instance.status
print "Flavor:", instance.flavor.name

print 'Creating instance, please wait...'
while status == 'BUILD':
    time.sleep(5)
    for inst in cdb.list():
        if inst.name == instance.name:
            status = inst.status
print 'Done.'

while True: 
    db_name = raw_input("Enter the name of the new database to create in this instance: ")
    if db_name.isalnum():
        break
    else:
        print "Names must be letters and numbers, please try again..."
        print

db = instance.create_database(db_name)

print "Database %s has been created." % db_name

while True:
    nm = raw_input("Enter the user name: ")
    if db_name.isalnum():
        break
    else:
        print "Usernames must be letters and numbers, please try again..."
        print

while True:
    pw = getpass.getpass("Enter the password for this user: ")
    if pw.isalnum():
        break
    else:
        print "Passwords must be letters and numbers, please try again..."
        print

user = instance.create_user(nm, pw, database_names=db_name)

print "User created."
print
print "Complete!"
