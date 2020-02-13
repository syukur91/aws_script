# Dependency defintition
import boto3, pprint, json, csv, os

# Setup & Variable definition
aws_profile     = os.environ.get('AWS_PROFILE', 'default')
boto3.setup_default_session(profile_name=aws_profile)
data            = {}
pretty_print    = pprint.PrettyPrinter(indent=4)
csv_header      = ['Region','Instance ID','Instance Type','Instance State','Launch Time','Vpc ID','Image ID','Subnet ID','Public IP Address','Private IP Address','Availability Zone', 'Tag', 'Volume AZ', 'Volume ID', 'Volume Size', 'Volume State', 'Volume Type', 'Volume Status', "Volume Device Name"]
ec2_client      = boto3.client('ec2')
regions         = [region['RegionName'] for region in ec2_client.describe_regions()['Regions']]

print("Script running using profile: "+aws_profile)

# Loop through all region
for region in regions:
    print("Scanning for region: "+region)
    client      = boto3.client('ec2', region_name=region)
    response    = client.describe_instances()
    ec2_data    = response["Reservations"]

    # Get instance details
    if ec2_data:
        print("    Getting ec2 instance details for region: "+region)
        for reservation in ec2_data:
            for instance in reservation["Instances"]:
                instance_dict       = {}
                volume_ids          = ""
                volume_status       = ""
                volume_device_name  = ""
                tags                = ""

                # This handle if the block device mapping list is more than one item
                for volume in instance["BlockDeviceMappings"]:
                    volume_ids          +=  volume["Ebs"]["VolumeId"]  + ":" if len(instance["BlockDeviceMappings"]) > 1 else volume["Ebs"]["VolumeId"]
                for volume in instance["BlockDeviceMappings"]:
                    volume_status       +=  volume["Ebs"]["Status"]  + ":" if len(instance["BlockDeviceMappings"]) > 1 else volume["Ebs"]["Status"]
                for volume in instance["BlockDeviceMappings"]:
                    volume_device_name  +=  volume["DeviceName"] + ":" if len(instance["BlockDeviceMappings"]) > 1 else volume["DeviceName"] 
               

                # Checking if the tag is exist or not               
                if instance.get("Tags", "none") != "none":
                    for tag in instance["Tags"]:
                        tags    +=  tag["Key"]+":"+tag["Value"] + ";" 
                else:
                        tags     = "tag doesn't exist"  

                # Assign the value to generic dictionary
                instance_dict["Instance"] = { 
                                              "Region"              : region,
                                              "InstanceType"        : instance.get('InstanceType','N/A'),
                                              "InstanceID"          : instance.get('InstanceId','N/A'),
                                              "InstanceState"       : instance.get('State', {}).get('Name', 'N/A'),
                                              "LaunchTime"          : instance.get('LaunchTime','N/A'),
                                              "VpcId"               : instance.get('VpcId','N/A'),
                                              "ImageId"             : instance.get('ImageId','N/A'),
                                              "SubnetId"            : instance.get('SubnetId','N/A'),
                                              "PublicIpAddress"     : instance.get('PublicIpAddress','N/A'),
                                              "PrivateIpAddress"    : instance.get('PrivateIpAddress','N/A'),                                       
                                              "AvailabilityZone"    : instance.get('Placement', {}).get('AvailabilityZone', 'N/A'),                                           
                                              "VolumeID"            : volume_ids,
                                              "VolumeStatus"        : volume_status,
                                              "VolumeDeviceName"    : volume_device_name,
                                              "Tag"                 : tags} 
                data[instance["InstanceId"]] = instance_dict


    # Get additional volume details
    volumes     = client.describe_volumes()
    volume_data = volumes["Volumes"]
    if volume_data:
        for volume in volumes["Volumes"]:
            volume_dict = {}
            instance_id = volume.get('Attachments', {})[0].get('InstanceId', 'N/A')
            if instance_id != 'N/A':
                # Assign the value to generic dictionary
                volume_dict["Volume"]  =  { 
                                            "VolumeType"        : volume.get('VolumeType','N/A'),
                                            "VolumeState"       : volume.get('State','N/A'),
                                            "VolumeAZ"          : volume.get('AvailabilityZone','N/A'),
                                            "VolumeSize"        : volume.get('Size','N/A') } 

                data[instance_id].update(volume_dict) 



# Write instance details to csv
with open('instance.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(i for i in csv_header)
    for a in data:
        # Put all the value to the writer based on header sequence
        writer.writerow([
                         data[a].get('Instance', {}).get('Region', 'N/A'),
                         data[a].get('Instance', {}).get('InstanceID', 'N/A'),
                         data[a].get('Instance', {}).get('InstanceType', 'N/A'),
                         data[a].get('Instance', {}).get('InstanceState', 'N/A'),
                         data[a].get('Instance', {}).get('LaunchTime', 'N/A'),
                         data[a].get('Instance', {}).get('VpcId', 'N/A'),
                         data[a].get('Instance', {}).get('ImageId', 'N/A'),
                         data[a].get('Instance', {}).get('SubnetId', 'N/A'),
                         data[a].get('Instance', {}).get('PublicIpAddress', 'N/A'),
                         data[a].get('Instance', {}).get('PrivateIpAddress', 'N/A'),
                         data[a].get('Instance', {}).get('AvailabilityZone', 'N/A'),
                         data[a].get('Instance', {}).get('Tag', 'N/A'),
                         data[a].get('Volume', {}).get('VolumeAZ', 'N/A'),   
                         data[a].get('Instance', {}).get('VolumeID', 'N/A'),   
                         data[a].get('Volume', {}).get('VolumeSize', 'N/A'),   
                         data[a].get('Volume', {}).get('VolumeState', 'N/A'),
                         data[a].get('Volume', {}).get('VolumeType', 'N/A'),
                         data[a].get('Instance', {}).get('VolumeStatus', 'N/A'),
                         data[a].get('Instance', {}).get('VolumeDeviceName', 'N/A')
                         ])

print("")
print("Scanning completed")
print("")
pretty_print.pprint(data)
