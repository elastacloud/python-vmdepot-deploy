from azure.servicemanagement import *

class Stop:

    def __init__(self):
        self.sms = None

    def execute(self, vars):
        self.sms = ServiceManagementService(vars.subscription_id, vars.certificate_path)
        self.sms.shutdown_role(vars.storage_account_name, vars.storage_account_name, vars.virtual_machine_name)
        print "role " + vars.virtual_machine_name + " has been shutdown"
