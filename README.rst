amibuilder
==========

Build an AMI from a shell script or Dockerfile

Installation
=============

You can easily install the latest version of amibuilder with pip.  Alternitavely, you can download the source directly from this repository.

::

    pip install amibuilder


Configuration
=============

A configuration file should be created for each server type you want to
make. Here is a sample configuration file:

::

    [main]

    # You can specify either an AWS profile name here,
    # or manually specify region, access_key and secret_key.
    # AWS profiles are usually stored in the ~/.aws/config file
    aws_profile = profile
    
    # The AWS credentials to use; if aws_profile is specified,
    # the following three settings are ignored
    #region = us-east-1
    #access_key = ANLK3UHQKIAJF4MLBVF7
    #secret_key = vhhHzsDIzMbFgTDMWEYIbYyUaFFIY0cyBh

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

    usage: local.py [-h] [-a SOURCE_AMI] [-b [BUILD_ARG [BUILD_ARG ...]]]
                    [-c CONFIG] [-d DEBUG] [-f FILE] [-g SECURITY_GROUPS]
                    [-i INSTANCE_TYPE] [-n TARGET_NAME] [-m TARGET_DESCRIPTION]
                    [-p AWS_PROFILE] [-r REGION] [-s SUBNET_ID] [-t HOST_TAG]
                    [-T TARGET_TYPE] [-o]

    optional arguments:
    -h, --help            show this help message and exit
    -a SOURCE_AMI, --source-ami SOURCE_AMI
                            source AMI image id
    -b [BUILD_ARG [BUILD_ARG ...]], --build-arg [BUILD_ARG [BUILD_ARG ...]]
                            specify values for ARG arguments in Dockerfiles
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
    -p AWS_PROFILE, --aws-profile AWS_PROFILE
                            Use credentials from profile stored in AWS
                            configuration file
    -r REGION, --region REGION
                            AWS region
    -s SUBNET_ID, --subnet-id SUBNET_ID
                            AWS subnet id
    -t HOST_TAG, --host-tag HOST_TAG
                            tag that will be applied to temporary instance
    -T TARGET_TYPE, --target-type TARGET_TYPE
                            ami (default) to build an AMI; instance to just build
                            an instance
    -o, --overwrite       set to true if you want to overwrite an existing AMI

Limitations
===========

If you use Dockerfile scripts, only the ARG, RUN and COPY commands are
supported at this time. The COPY commands are only recommended for
smaller files, such as .conf files. If you want to transfer large data
payloads, a more robust solution would be to store them in an S3 bucket,
for example.

