###############################################################
# Copyright 2014 under Apache license by Elastacloud
# No warranties given on code

# This code file will create a virtual machine based on a vmdepot image
# it doesn't assume that you have any azure services running in an account
# It will do the following
# 1. Create a Windows Azure Storage account
# 2. Get the storage keys and copy a blob from the vm depot
# 3. Register the image using the newly copied local blob
# 4. Create a virtual machine from the local image
# 5. Start the virtual machine
# 6. Stop the virtual machine and wait thirty seconds
# 7. Restart the virtual machine
# The following is a description of the parameters (these will need to be customised for your subscription) - others can be if you want but are not essential:
#
#   "certificate_path" is the path to the subscription management certficate in windows it could be
#   'CURRENT_USER\\my\\elastacloud' and linux /home/azurecoder/elasta.pem (for example)
#
#   "subscription_id" is the guid that is associated with your Windows Azure subscription
#
#   "storage_account_name" is the name of the storage account which will be created and use to register the image
#   and hold the vhd of the virtual machine which will be created
#
#   "deploy_location" is the location of the Windows Azure deployment for Europhiles like me it should be
#   North Europe or West Europe
#################################################################
from elastacloud.pyvms import Setup, Start, Stop
from elastacloud.pyvms import AzureVars

__author__ = 'Richard Conway aka azurecoder'

import argparse

# set the subscription id and the certificate path to the .pem file here OR if running on Windows the canonical representation
# of the certificate store path


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--certificate_path')
    parser.add_argument('--subscription_id')
    # this is also the cloud service name
    parser.add_argument('--storage_account_name')
    parser.add_argument('--virtual_machine_name')
    parser.add_argument('--deploy_location')
    parser.add_argument('--username')
    parser.add_argument('--password')
    parser.add_argument('--type')
    args = parser.parse_args()
    vars = AzureVars.AzureVars(args.certificate_path, args.subscription_id, args.storage_account_name, args.deploy_location,
                               args.username, args.password, args.virtual_machine_name)

    if args.type == 'setup':
        entry = Setup.Setup()
        entry.execute(vars)
    elif args.type == 'start':
        start = Start.Start()
        start.execute(vars)
    else:
        stop = Stop.Stop()
        stop.execute(vars)