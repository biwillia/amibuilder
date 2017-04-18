amibuilder
==========

Build an AMI from a shell script or Dockerfile

Configuration
=============

A configuration file should be created for each server type you want to
make. Here is a sample configuration file:

::

    [main]

    # The AWS region you want to use
    region = us-east-1

    # Your AWS Access Key ID goes here
    access_key = ANLK3UHQKIAJF4MLBVF7

    # Your AWS Secret Key goes here
    secret_key = vhhHzsDIzMbFgTDMWEYIbYyUaFFIY0cyBh

    # the host tag contains the Name tag that will be applied to
    # the temporary EC2 server instance used during AMI creation
    host_tag = flexio-build

    # the target_name is the name of the AMI that is created.
    # By default, an existing AMI with the same name will not be
    # overwritten.  See the overwrite configuration option
    target_name = flexio-build

    # the type of instance you want to use during AMI creation
    instance_type = t2.micro

    # optional EC2 subnet id
    subnet_id =

    # The source AMI you want to start with
    source_ami = ami-80861296

    # The script file you would like to execute after the temporary
    # instance is created.  This script file can either be a Dockerfile
    # or any script containing a shebang line, such as a bash script
    file = ./Dockerfile

    # security groups that the temporary instance should belong to
    security_groups = securitygroup1, securitygroup2

    # By default, overwrite is off.  If you want to overwrite an AMI
    # with the same name that already exists, set the overwrite to true
    # overwrite = true

Usage
=====

::

    usage: amibuilder [-h] [-a SOURCE_AMI] [-c CONFIG] [-d DEBUG] [-f FILE]
                      [-g SECURITY_GROUPS] [-i INSTANCE_TYPE] [-n TARGET_NAME]
                      [-m TARGET_DESCRIPTION] [-r REGION] [-s SUBNET_ID]
                      [-t HOST_TAG] [-o OVERWRITE] [-u SSH_USER]

    optional arguments:
      -h, --help            show this help message and exit
      -a SOURCE_AMI, --source-ami SOURCE_AMI
                            source AMI image id
      -c CONFIG, --config CONFIG
                            configuration file
      -d DEBUG, --debug DEBUG
                            print debug info
      -f FILE, --file FILE  script file
      -g SECURITY_GROUPS, --security-groups SECURITY_GROUPS
                            one or more security groups (comma-delimited)
      -i INSTANCE_TYPE, --instance-type INSTANCE_TYPE
                            EC2 instance type
      -n TARGET_NAME, --target-name TARGET_NAME
                            target AMI image name
      -m TARGET_DESCRIPTION, --target-description TARGET_DESCRIPTION
                            target AMI description
      -r REGION, --region REGION
                            AWS region
      -s SUBNET_ID, --subnet-id SUBNET_ID
                            AWS subnet id
      -t HOST_TAG, --host-tag HOST_TAG
                            tag that will be applied to temporary instance
      -o OVERWRITE, --overwrite OVERWRITE
                            set to true if you want to overwrite an existing AMI
      -u SSH_USER, --ssh-user SSH_USER
                            SSH user name

Limitations
===========

If you use Dockerfile scripts, only the RUN and COPY commands are
supported at this time. The COPY commands are only recommended for
smaller files, such as .conf files. If you want to transfer large data
payloads, a more robust solution would be to store them in an S3 bucket,
for example.

