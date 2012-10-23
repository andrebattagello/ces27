# -*- coding: utf-8 -*-
#!/usr/bin/python
"""
Builds a new EC Instance


"""
from boto import ec2
import defaults

KEY_NAME = defaults.KEY_NAME

AMI_IMAGE_ID = defaults.DEFAULT_AMI_IMAGE_ID
INSTANCE_TYPE = defaults.DEFAULT_INSTANCE_TYPE
REGION_NAME = defaults.DEFAULT_REGION


conn = ec2.connect_to_region(REGION_NAME)


print 'Booting up a new instance w/ AMI %s and size %s.\
        It may take a while.' % (AMI_IMAGE_ID,
                                 INSTANCE_TYPE)
reservation = conn.run_instances(image_id=AMI_IMAGE_ID,
                                 key_name=KEY_NAME,
                                 instance_type=INSTANCE_TYPE)

#bootstrap a new instance may take some time
from time import sleep
sleep(30)


dns = None
for r in conn.get_all_instances():
    if r.id == reservation.id:
        dns = r.instances[0].public_dns_name

print 'Done!\nPublic DNS: %s' % dns
print 'SSH Access:  ssh -2 -i ~/.ssh/%s.pem ec2-user@%s' % (KEY_NAME, dns)
