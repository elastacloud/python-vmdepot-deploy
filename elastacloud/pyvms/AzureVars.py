
class AzureVars:

    def __init__(self, certificate_path, subscription_id, storage_account_name=None, deploy_location=None, username=None, password=None, vm_name=None):
        self._certificate_path = certificate_path
        self._subscription_id = subscription_id
        self._storage_account_name = storage_account_name
        self._deploy_location = deploy_location
        self._username = username
        self._password = password
        self._virtual_machine_name = vm_name

    @property
    def certificate_path(self):
        return self._certificate_path

    @property
    def subscription_id(self):
        return self._subscription_id

    @property
    def storage_account_name(self):
        return self._storage_account_name

    @property
    def deploy_location(self):
        return self._deploy_location

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

    @property
    def virtual_machine_name(self):
        return self._virtual_machine_name



