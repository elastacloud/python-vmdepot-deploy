Deploying a VM depot image using Python
============
Installing a management certificate 
----------------------------
Windows Azure controls access in two ways.
* X509v3 Management Certificates 
* Bearer Token

The former can be created using openssl and uploaded the management portal and the latter through an HTTP auth header given a valid login workflow to a Microsoft Account or Windows Azure Active Directory Account.

For the purposes of this tutorial we’ll focus on the first one.
Creating the Management Certificate

If openssl isn’t installed then use the following from a root prompt:
```sh
yum install openssl
```
The following will create a .pem file which can later be translated in to a .cer, exported and uploaded to Windows Azure.
```sh
openssl req -x509 -nodes -days 365 -newkey rsa:1024 -keyout elasta.pem -out elasta.pem
```
To export the .cer use the following:
```sh
openssl x509 -inform pem -in elasta.pem -outform der -out elasta.cer
```

Uploading the Management Certificate
-----
Login into Windows Azure using your Microsoft Account or Windows Azure Active Directory credentials. The management portal can be located at https://manage.windowsazure.com
Select the settings tab:
 
Select Management Certificates from the menu:
 
The bottom app bar contains an upload button:
 
Select this button and upload the .cer file:
 
You should see something like this for the certificate entry in the results pane.
  
Understanding the deployment script
The deployment script has 3 functions which can be used from the command line:

* setup
* start
* stop

Setup will perform the following steps:

1.	Check to see whether the name image “jasmine-image” exists if it does it will continue to step 7
2.	Check to see whether the subscription has access to the location given in the command line arguments, n.b. some subscriptions don’t have access to certain data centres so this check is a pre-requisite
3.	If it doesn’t exist yet create the name storage account from the command line arguments
4.	Create a container called community in the new storage account
5.	Copy the blob from the vmdepot – the default is the “centos minimal” image – this can take between 1 minute and 20 minutes depending on the time of day as this is 30GB – best to do this in North Europe data centre to avoid latency and copy charges 
6.	Register the OS image with the subscription under the default name of jasmine-image
7.	Create a new cloud service in the same name as the storage account
8.	Create a linux vm using the vm depot copied image 
9.	If a vm exists already in the cloud service it will create another one and increment the SSH port number by 1 such that the first vm is on port 22, the second on port 23 etc.

To run the script please ensure that python is installed.

Ensure that pip is install via the following:

```sh
curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | sudo python
```

Also install the Windows Azure SDK for Python through pip (ensure that pip is installed) via the following (for the following make sure you have root access):

You can pip install from GitHub:
```sh
pip install git+https://github.com/WindowsAzure/azure-sdk-for-python.git (if you use this make sure git is installed with sudo yum install git)
```
or from PyPi:
```sh
pip install azure==0.8.0pr1 
```
On windows replace the certificate path with the location in the certificate store such as CURRENT_USER\my\elastacloud and in Linux just reference the path to the PEM file.

The following command will do the steps specified in Setup:
```sh
python main.py --certificate_path /home/azurecoder/elasta.pem --subscription_id xxxxxx-673d-426c-8c55-xxxxxxxx --storage_account_name nejasmistore9 --deploy_location “North Europe” --type setup --username azurecoder --password Op3nSource
```
This command will restart the virtual machine called elastavm0 (you can get the name of the vms you want to spin up and down from the Windows Azure portal)
```sh
python main.py --certificate_path /home/azurecoder/elasta.pem --subscription_id xxxxxx-673d-426c-8c55-xxxxxxxx --type start --virtual_machine_name elastavm0
```
This command will stop the virtual machine called elastavm0:
```sh
python main.py --certificate_path /home/azurecoder/elasta.pem --subscription_id xxxxxx-673d-426c-8c55-xxxxxxxx --type start --virtual_machine_name elastavm0
```
The passwords in the above don’t need to be specified if they are not they will default to ‘azurecoder’ and ‘Op3nSource’




