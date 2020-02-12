# EC2 List Script

## This script created to list ec2 instances in all region 

Prerequisites:

1. Using python 3.6.8 or python3
1. Using pip package manager
1. Using venv


Steps to run:

```
python -m venv env

source env/bin/activate

pip install -r requirements.txt

export AWS_PROFILE=default && python 01_ec2_list.py // Enable switch profile using AWS_PROFILE environment variable
```

P.S. `I made an alias on bash for python3 so that can be called as python`