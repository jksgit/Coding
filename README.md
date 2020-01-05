#### 1. weblog_helper

This is a simple script to get IP/CIDR matches from a log file

Usage:  ./weblog_helper --ip <IP/CIDR>

Example:

./weblog_helper --ip 157.55.39.22

./weblog_helper --ip 157.55.39.1/24

#### 2. Account Reset Script

You can find the script "account_reset.py" under the "scripts" folder. This will help you to delete the following resources.
- CloudFormation Stack
- S3 Buckets
- EBS Snapshots
- AMIs

#### 3. Excel/Ansible Inventory script

This script helps you to convert an Excel Spreadsheet into an Ansible Inventory.

Find the script - scripts/patching/excel_inventory.py

##### Configuration

 Create excel_inventory.cfg file by running:

    python3 excel_inventory.py --config --file sample.xlsx --hostname-col A
	--group-by-col B --sheet Sheet1


A Typical configuration file looks like this and is rather self explanatory:

    [excel_inventory]
    excel_inventory_file = ./sample.xlsx
    sheet = Sheet1
    hostname_col = A
    group_by_col = B


#### Usage

Once you  have the "excel_inventory.cfg" file, Inventory script can be used like any other Dynamic Inventory by specifying it as the inventory in your ansible/ansible-playbook commands:

	python3 excel_inventory.py --config --file example.xlsx --group-by-col B --hostname-col A --sheet Sheet2
	ansible -i excel_inventory.py -m ping server_name

#### List Inventory
	python3 excel_inventory.py --list
