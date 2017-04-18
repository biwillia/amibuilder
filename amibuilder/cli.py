import boto3
import argparse
import configparser
import re
import os
import sys
import uuid
import io
import csv
import base64
import time


def convert_to_bash(script_file):
    cmds = []
    joinline = False

    # search for a shebang
    with open(script_file) as fp:
        content = fp.read()
        if content[:3] == '#!/':
            return content

    # shebang not found, so use Dockerfile format;
    # read in the lines from the Dockerfile and consolidate
    # commands split on multiple lines
    with open(script_file) as fp:
        for line in fp:
            line = line.strip()

            # ignore comment or empty lines
            if line[:1] == '#' or line == '':
                continue

            if joinline:
                joinline = False
            else:
                cmd = ''

            match = re.match("(.*)\\\\$", line)
            if match:
                cmd += match.group(1) + ' '
                joinline = True
            else:
                cmd += line
            
            cmds.append(cmd)

    # next, run each individual command
    bash = '#!/bin/bash\n'

    for cmd in cmds:
        if cmd[:4] == 'RUN ':
            bash += cmd[4:] + '\n'
        if cmd[:5] == 'COPY ':
            # use csv to get COPY parameters delimiteds with space, while respecting quoted strings
            f = io.StringIO(cmd[5:])
            reader = csv.reader(f, delimiter=' ')
            line = None
            for l in reader:
                line = [x for x in l if x] # filter out empty values
            if not line or len(line) != 2:
                sys.stdout.write("could not parse line: " + cmd + "\n")
                sys.exit(1)

            inf = os.path.expanduser(line[0])
            if not os.path.isfile(inf):
                sys.stdout.write("could not open file: " + cmd + "\n")
                sys.exit(1)
            with open(line[0], 'rb') as fp:
                content = fp.read()
                b64 = base64.b64encode(content).decode('utf-8')
                bash += "echo " + b64 + " | base64 -d > " + line[1] + "\n"
            
    return bash




def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--source-ami', help='source AMI image id')
    parser.add_argument('-c', '--config', help='configuration file')
    parser.add_argument('-d', '--debug', help='print debug info')
    parser.add_argument('-f', '--file', help='script file')
    parser.add_argument('-g', '--security-groups', help='one or more security groups (comma-delimited)')
    parser.add_argument('-i', '--instance-type', help='EC2 instance type')
    parser.add_argument('-n', '--target-name', help='target AMI image name')
    parser.add_argument('-m', '--target-description', help='target AMI description')
    parser.add_argument('-r', '--region', help='AWS region')
    parser.add_argument('-s', '--subnet-id', help='AWS subnet id')
    parser.add_argument('-t', '--host-tag', help='tag that will be applied to temporary instance')
    parser.add_argument('-o', '--overwrite', help='set to true if you want to overwrite an existing AMI')
    parser.add_argument('-u', '--ssh-user', help='SSH user name')
    args = parser.parse_args()


    # set defaults for config object
    config = configparser.ConfigParser()
    config.add_section('main')
    config.set('main', 'host_tag', 'ami-builder')
    config.set('main', 'target_name', 'ami-builder')
    config.set('main', 'target_description', '')
    config.set('main', 'region', 'us-east-1')
    config.set('main', 'instance_type', 't2.small')
    config.set('main', 'subnet_id', '')
    config.set('main', 'source_ami', 'ami-80861296')
    config.set('main', 'ssh_user', 'ubuntu')
    config.set('main', 'security_groups', '')
    config.set('main', 'overwrite', 'false')
    config.set('main', 'access_key', '')
    config.set('main', 'secret_key', '')


    # load config file
    if args.config:
        config_file = args.config
    else:
        if os.path.isfile(os.path.expanduser('~/.ami-builder.conf')):
            config_file = os.path.expanduser('~/.ami-builder.conf')
        else:
            config_file = '/etc/ami-builder.conf'

    config_file = os.path.expanduser(config_file)
    if not config.read(config_file):
        sys.stdout.write("Could not open config file.  Use --help for help screen\n")
        sys.exit(1)


    # load values from config file and command line
    host_tag           = args.host_tag           if args.host_tag           else config.get('main', 'host_tag')
    filepath           = args.file               if args.file               else config.get('main', 'file')
    target_name        = args.target_name        if args.target_name        else config.get('main', 'target_name')
    target_description = args.target_description if args.target_description else config.get('main', 'target_description')
    region             = args.region             if args.region             else config.get('main', 'region')
    instance_type      = args.instance_type      if args.instance_type      else config.get('main', 'instance_type')
    subnet_id          = args.subnet_id          if args.subnet_id          else config.get('main', 'subnet_id')
    source_ami         = args.source_ami         if args.source_ami         else config.get('main', 'source_ami')
    ssh_user           = args.ssh_user           if args.ssh_user           else config.get('main', 'ssh_user')
    security_groups    = args.security_groups    if args.security_groups    else config.get('main', 'security_groups')
    overwrite          = args.overwrite          if args.overwrite          else config.get('main', 'overwrite')
    access_key         = config.get('main', 'access_key')
    secret_key         = config.get('main', 'secret_key')

    security_groups = list(map(str.strip, security_groups.split(',')))
    security_groups = [x for x in security_groups if x] # filter out empty values

    if not access_key:
        sys.stdout.write("an access_key must be specified in the config file")
        sys.exit(1)
    
    if not secret_key:
        sys.stdout.write("an secret_key must be specified in the config file")
        sys.exit(1)

    start_time = int(time.time())

    script = convert_to_bash(filepath)

    ec2 = boto3.resource('ec2',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )

    ec2client = boto3.client('ec2',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )


    # before we start, see if an image already exists
    result = ec2client.describe_images(Filters=[{'Name':'name','Values':[target_name]}])
    image = None
    if 'Images' in result and len(result['Images']) > 0:
        image = ec2.Image(result['Images'][0]['ImageId'])

    overwrite = str(overwrite).lower()
    overwrite = True if overwrite == 'true' or overwrite == 'yes' else False
    
    if image and not overwrite:
        sys.stdout.write("An image with the name of " + image.name + " already exists with the id " + image.id + "\n")
        sys.exit(0)



    # create an instance

    params = {
        'ImageId':source_ami,
        'MinCount':1,
        'MaxCount':1,
        'KeyName':'flexio',
        'InstanceType':instance_type,
        'UserData':script
    }

    if security_groups:
        params['SecurityGroups'] = security_groups

    sys.stdout.write("Creating temporary instance\n")
    instances = ec2.create_instances(**params)
    if not instances:
        sys.stdout.write("Could not start instance")
        sys.exit(1)
    instance = instances[0]

    instance.create_tags(Tags=[{'Key':'Name','Value':host_tag}])

    sys.stdout.write("Waiting until temporary instance " + instance.id + " is running...\n")
    instance.wait_until_running()

    sys.stdout.write("Instance is running.  Public DNS name is " + instance.public_dns_name + "\n")


    # wait until initialization is done and status checks return ok

    sys.stdout.write("Waiting until status checks return ok...\n")

    status = None
    counter = 20  # wait a max of 10 minutes
    while (status != 'ok' and counter > 0):
        time.sleep(30)
        status_response = ec2client.describe_instance_status(InstanceIds=[ instance.id ])
        status = status_response['InstanceStatuses'][0]['SystemStatus']['Status']
        counter = counter - 1

    if status != 'ok':
        std.stdout.write("Instance status was not ok...terminating and exiting...\n")
        instance.terminate()
        sys.exit(1)
    
    # stop the instance in preparation for making an image (ami)

    time.sleep(30) # for good measure
    sys.stdout.write("Instance status checked returned ok.  Stopping instance...\n")
    instance.stop()
    instance.wait_until_stopped()
    time.sleep(5)

    # delete previous AMI if overwrite is set to True
    if image and overwrite:
        sys.stdout.write("Deregistering previous AMI " + image.id + " with the name " + image.name + "...\n")
        image.deregister()
        time.sleep(5)

    # create an AMI

    sys.stdout.write("Creating AMI image...\n")
    image = instance.create_image(
        Name=target_name,
        Description=target_description
    )
    image.wait_until_exists()

    time.sleep(30)

    sys.stdout.write("Terminating temporary instance...\n")
    instance.terminate()

    finish_time = int(time.time())
    sys.stdout.write("Image " + image.name + " (" + image.id + ") created successfully!  Total run time: " + str(finish_time-start_time) + " seconds.\n")

