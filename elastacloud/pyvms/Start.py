from azure.servicemanagement import *

class Start:

    def __init__(self):
        self.sms = None

    def execute(self, vars):
        self.sms = ServiceManagementService(vars.subscription_id, vars.certificate_path)
        print "cloud service and deployment is: " + vars.storage_account_name + " and role is " + vars.virtual_machine_name
        self.sms.restart_role(vars.storage_account_name, vars.storage_account_name, vars.virtual_machine_name)
        print "role " + vars.virtual_machine_name + " has been started"