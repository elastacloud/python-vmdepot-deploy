from azure.storage import *
from azure.servicemanagement import *
from time import sleep

from elastacloud.pyvms import Constants

class Setup:

    def __init__(self):
        self.blob_service = None
        self.sms = None

    def execute(self, vars):
        # set the subscription id and the certificate path to the .pem file here OR if running on Windows the canonical representation
        # of the certificate store path
        # create the service management client
        self.sms = ServiceManagementService(vars.subscription_id, vars.certificate_path)
        # if we have this image name then we won't want to do any of this
        image_exists = self._image_by_name(Constants.image_name)
        if not image_exists:
            # check to see whether we can deploy to the chosen location - if not then bail
            self._check_locations(vars.deploy_location)
            print "continuing to deploy to " + vars.deploy_location
            # if the storage account doesn't exist already we'll create it - if it does we assume we own it!!!
            self._create_storage_account_if_not_exists(vars.storage_account_name, vars.deploy_location)
            # check to see whether the container exists and if not create it
            account_key = self._get_primary_account_key(vars.storage_account_name)
            self._create_container_if_not_exists()
            # add the os image from the blob copy
            self.blob_service.copy_blob(container_name=Constants.storage_container_name, blob_name=Constants.vhd_blob_name, x_ms_copy_source=Constants.centos_minimal_image)
            self._wait_for_async_copy(Constants.storage_container_name, Constants.vhd_blob_name)
            storageimage_uri = self._make_blob_url(container_name=Constants.storage_container_name, blob_name=Constants.vhd_blob_name, account_name=vars.storage_account_name, protocol="https")
            print "finished copying blob with new uri " + Constants.image_name
            # the operation takes a while but when it finishes the image should be registered so that we can create a vm from it
            # add the image using add_os_image add_os_image(self, label, media_link, name, os)
            print "registering image with Windows Azure subscription"
            # check to see whether the image exists first of all otherwise we'll add the image
            self.sms.add_os_image(label=Constants.image_name, media_link=storageimage_uri, name=Constants.image_name, os='Linux')
            print "image has been registered with Azure Subscription"
            # The virtual machine will need to be created from here
        else:
            print "image already exists - either change the image name to copy a newer version of the image or discard this message"

        # this will initialise the blob_service if we haven't done it already
        account_key = self._get_primary_account_key(vars.storage_account_name)
        # create the Linux virtual machine from this
        index = -1
        blob_exists = True
        while blob_exists:
            index += 1
            blob_exists = self._blob_exists(Constants.storage_container_name, "elastavm" + str(index) + ".vhd")

        vm_media_link = self._make_blob_url(vars.storage_account_name, Constants.storage_container_name, "elastavm" + str(index) + ".vhd")

        self._create_vm_linux(vars.storage_account_name, vars.storage_account_name, "elastavm" + str(index), vm_media_link, vars.deploy_location, index, vars.username, vars.password)
        print "setup operation complete .. The virtual machine is now running and you can login using the credentials in code"

    def _blob_exists(self, container_name, blob_name):
        try:
            props = self.blob_service.get_blob_properties(container_name, blob_name)
            return props is not None
        except:
            return False

    def _make_blob_url(self, account_name, container_name, blob_name):
        return 'https://{0}.blob.core.windows.net/{1}/{2}'.format(account_name, container_name, blob_name)

    def _wait_for_async_copy(self, container_name, blob_name):
        props = self.blob_service.get_blob_properties(container_name, blob_name)
        while props['x-ms-copy-status'] != 'success':
            sleep(10)
            props = self.blob_service.get_blob_properties(container_name, blob_name)
            print "number of bytes copied: " + props['x-ms-copy-progress']

    def _create_container_if_not_exists(self):
         # Create a community container to put the community image in - this won't exist given the storage checks
        # if the container exists already we'll discard it - if the blob exists we won't do any of the next section
        try:
            self.blob_service.create_container(container_name=Constants.storage_container_name)
            sleep(10)
            print "container created with the following name: " + Constants.storage_container_name
        except:
            print "container exists already continuing with the setup process"

    def _create_storage_account_if_not_exists(self, storage_account_name, deploy_location):
        # If the location is present then we want to check whether there is a storage account with the name already
        is_storage_name_available = self.sms.check_storage_account_name_availability(storage_account_name)
        if not is_storage_name_available:
            print "unable to create storage account - name is unavailable"
        else:
            print "storage account name " + storage_account_name + " is available"
              # Since the name is available we'll create the account
            print "creating storage account " + storage_account_name + " in " + deploy_location
        try:
            self.sms.create_storage_account(storage_account_name, "created by Elastacloud script", storage_account_name, location=deploy_location)
            # we need to add the delay in - sometimes the DNS resolution takes longer so it returns early falsely
            sleep(90)
            print "created storage account " + storage_account_name + " in " + deploy_location
        except:
            print "error creating storage account " + storage_account_name + ", continuing and assuming storage account is already owned by you"

    def _check_locations(self, deploy_location):
         # In the first place we'll want to check whether the storage account name is available
        locations = self.sms.list_locations()
        location_present = False
        for location in locations:
            print "found location: " + location.name
            if location.name == deploy_location:
                location_present = True
        if not location_present:
            print "unable to deploy in your chosen location " + deploy_location + " as it's not associated with your subscription"
            exit(1)

    def _get_primary_account_key(self, storage_account_name):
        # When the storage account is created we want to use the blob endpoint for the minimal storage
        # We need the CentOS minimal image here just grabbing this but could make dynamic if needed
        # vm depot has an OData endpoint here we can exploit http://vmdepot.msopentech.com/OData.svc/ResolveUid?uid='vmdepot-21919-1-16'
        # Get the primary key first from the newly created storage account
        storage_response = self.sms.get_storage_account_keys(storage_account_name)
        azure_storage_service = CloudStorageAccount(account_name=storage_account_name, account_key=storage_response.storage_service_keys.primary)
        self.blob_service = azure_storage_service.create_blob_service()
        print "finished getting primary key " + storage_response.storage_service_keys.primary
        return storage_response.storage_service_keys.primary

    def _image_by_name(self, name):
        # return the first one listed, which should be the most stable
        for i in self.sms.list_os_images():
            if name in i.name:
                return True
        return False

    def _create_vm_linux(self, service_name, deployment_name, role_name, media_link, deployment_location, index, username, password):
        user = username if not None else 'azurecoder'
        passw = password if not None else 'Op3nSource'
        system = LinuxConfigurationSet('jasmine' + str(index), user, passw, True)
        system.ssh = None
        system.disable_ssh_password_authentication = False
        os_hd = OSVirtualHardDisk(source_image_name=Constants.image_name, media_link=media_link)
        network = ConfigurationSet()
        network.configuration_set_type = 'NetworkConfiguration'
        network.input_endpoints.input_endpoints.append(ConfigurationSetInputEndpoint('SSH', 'tcp', str(22 + index), '22'))
        # create the hosted service if it doesn't exist - currently this will only support a single VM in a cloud service
        # we'll have to use add_role with the correct deployment_name to append VMs to a cloud service
        # check here whether the cloud service exists or not
        if not self.sms.check_hosted_service_name_availability(service_name):
            result = self.sms.create_hosted_service(service_name, service_name + 'elasta', 'Created by Elastacloud script', deployment_location, None, {'Author': 'azurecoder'})
            print "created cloud service " + service_name
        try:
            # this will create the deployment for the first time if we want to add extra machines to the cloud service
            result = self.sms.create_virtual_machine_deployment(service_name, deployment_name, 'production',
                deployment_name + 'label', role_name, system, os_hd, network_config=network, role_size='Small')
        except:
            # we'll use add role for this - as long as we have the correct deployment name this should work okay
            result = self.sms.add_role(service_name, deployment_name, role_name, system, os_hd, network)

        self._wait_for_async(result.request_id)
        self._wait_for_deployment_status(service_name, deployment_name, 'Running')

    def _wait_for_async(self, request_id):
        result = self.sms.get_operation_status(request_id)
        while result.status == 'InProgress':
            sleep(10)
            result = self.sms.get_operation_status(request_id)
        print "successfully completed role deployment operation"

    def _wait_for_deployment_status(self, service_name, deployment_name, status):
        props = self.sms.get_deployment_by_name(service_name, deployment_name)
        while props.status != status:
            sleep(10)
            props = self.sms.get_deployment_by_name(service_name, deployment_name)
        print "deployment operation complete - vm is now in " + status + " state"
