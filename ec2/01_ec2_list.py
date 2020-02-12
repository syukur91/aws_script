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
                                              "InstanceType"        : instance["InstanceType"],
                                              "InstanceID"          : instance["InstanceId"],
                                              "InstanceState"       : instance["State"]["Name"],
                                              "LaunchTime"          : instance["LaunchTime"],
                                              "VpcId"               : instance["VpcId"],
                                              "ImageId"             : instance["ImageId"],
                                              "SubnetId"            : instance["SubnetId"],
                                              "PublicIpAddress"     : instance["PublicIpAddress"],
                                              "PrivateIpAddress"    : instance["PrivateIpAddress"],                                           
                                              "AvailabilityZone"    : instance["Placement"]["AvailabilityZone"],                                           
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

            # Assign the value to generic dictionary
            volume_dict["Volume"]  =  { 
                                        "VolumeType"        : volume["VolumeType"],
                                        "VolumeState"       : volume["State"],
                                        "VolumeAZ"          : volume["AvailabilityZone"],
                                        "VolumeSize"        : volume["Size"] } 

            data[volume["Attachments"][0]["InstanceId"]].update(volume_dict) 



# Write instance details to csv
with open('instance.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(i for i in csv_header)
    for a in data:
        # Put all the value to the writer based on header sequence
        writer.writerow([
                         data[a]["Instance"]["Region"], 
                         data[a]["Instance"]["InstanceID"], 
                         data[a]["Instance"]["InstanceType"], 
                         data[a]["Instance"]["InstanceState"], 
                         data[a]["Instance"]["LaunchTime"], 
                         data[a]["Instance"]["VpcId"], 
                         data[a]["Instance"]["ImageId"], 
                         data[a]["Instance"]["SubnetId"], 
                         data[a]["Instance"]["PublicIpAddress"], 
                         data[a]["Instance"]["PrivateIpAddress"], 
                         data[a]["Instance"]["AvailabilityZone"], 
                         data[a]["Instance"]["Tag"], 
                         data[a]["Volume"]["VolumeAZ"], 
                         data[a]["Instance"]["VolumeID"],
                         data[a]["Volume"]["VolumeSize"],
                         data[a]["Volume"]["VolumeState"],
                         data[a]["Volume"]["VolumeType"],
                         data[a]["Instance"]["VolumeStatus"],
                         data[a]["Instance"]["VolumeDeviceName"]])

print("")
print("Scanning completed")
print("")
pretty_print.pprint(data)
