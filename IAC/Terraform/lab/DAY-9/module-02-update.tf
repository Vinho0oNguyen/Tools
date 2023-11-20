###################
# VARIABLES 
###################
variable "aws_access_key" {}
variable "aws_secret_key" {}

variable "key_name" {}

variable "private_key_path" {}

variable "region" {
    type        = string
    default     = "us-east-1"
}

variable "network_address_space" {
    default     = "10.1.0.0/16"
    description = "Address space for vpc"
}

variable "subnet1_address_space" {
    default     = "10.1.0.0/24"
    description = "Address for subnet1"
}


variable "bucket_name_prefix" {}
variable "billing_code_tag" {}
variable "enviroment_tag" {}
###################
# PROVIDER 
###################
provider "aws" {
    access_key = var.aws_access_key
    secret_key = var.aws_secret_key
    region = var.region
}

###################
# DATAS
###################
data "aws_ami" "ami_linux" {
    most_recent     =   true
    owners          =   ["amazon"]
    filter {
        name    = "name"
        values  = [ "amzn-ami-hvm*" ]
    }

    filter {
        name    = "root-device-type"
        values  = [ "ebs" ]
    }

    filter {
        name    = "virtualization-type"
        values  = [ "hvm" ]
    }
}

data "aws_availability_zones" "available" {}

###################
# LOCALS
###################
locals {
    common_tag = {
        BillingCode = var.billing_code_tag
        Enviroment = var.enviroment_tag
    }
}

locals {
    s3_bucket_name = "${var.bucket_name_prefix}-${var.enviroment_tag}"
}

###################
# RESOURCES 
###################

## random ID ##
resource "random_integer" "rand" {
    min = 10000
    max = 99999
}

resource "aws_vpc" "day02_vpc" {
    cidr_block              =       var.network_address_space
    enable_dns_hostnames    =       true

    tags = merge(local.common_tag, {Name = "day03-${var.enviroment_tag}-vpc"})
}

resource "aws_internet_gateway" "day02_igw" {
    vpc_id          =           aws_vpc.day02_vpc.id 

    tags = merge(local.common_tag, {Name = "day03-${var.enviroment_tag}-igw"})
}

resource "aws_subnet" "day02_subnet1" {
    vpc_id                      =       aws_vpc.day02_vpc.id
    cidr_block                  =       var.subnet1_address_space
    map_public_ip_on_launch     =       true
    availability_zone           =       data.aws_availability_zones.available.names[0]

    tags = merge(local.common_tag, {Name = "day03-${var.enviroment_tag}-subnet1"})
}


resource "aws_route_table" "day02_rtb" {
    vpc_id          =           aws_vpc.day02_vpc.id
    route {
        cidr_block  = "0.0.0.0/0"
        gateway_id  = aws_internet_gateway.day02_igw.id
    }

    tags = merge(local.common_tag, {Name = "day03-${var.enviroment_tag}-rtb"})
}

resource "aws_route_table_association" "day02_rtb_subnet1" {
    subnet_id       =   aws_subnet.day02_subnet1.id
    route_table_id  =   aws_route_table.day02_rtb.id
}


resource "aws_security_group" "day02_allow" {
    name        =   "allow"
    description =   "allow port ssh and nginx"
    vpc_id      =   aws_vpc.day02_vpc.id

    ingress {
        from_port   = 80
        to_port     = 80
        protocol    = "TCP"
        cidr_blocks  = ["0.0.0.0/0"]
    }

    ingress {
        from_port   = 22
        to_port     = 22
        protocol    = "TCP"
        cidr_blocks  = ["0.0.0.0/0"]
    }

    egress {
        from_port   =   0
        to_port     =   0
        protocol    =   "-1"
        cidr_blocks  =   ["0.0.0.0/0"]
    }
    tags = merge(local.common_tag, {Name = "day03-${var.enviroment_tag}-scrg-allow"})
}




resource "aws_iam_role" "day03_allow_nginx_to_s3" {
    name = "allow_nginx_to_s3"
    assume_role_policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "",
            "Effect": "Allow",
            "Principal": {
                "Service": "ec2.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF
}

resource "aws_iam_instance_profile" "day03_nginx_profile" {
    name = "nginx_profile"
    role = aws_iam_role.day03_allow_nginx_to_s3.name
}

resource "aws_iam_role_policy" "day3_allow_s3_all" {
    name = "allow_s3_all"
    role = aws_iam_role.day03_allow_nginx_to_s3.name
    policy = <<EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "",
            "Effect": "Allow",
            "Action": [
                "s3:*"
            ],
            "Resource": [
                "arn:aws:s3:::${local.s3_bucket_name}",
                "arn:aws:s3:::${local.s3_bucket_name}/*"
            ]
        }
    ]
}
EOF
}

resource "aws_s3_bucket" "day03_bucket" {
    bucket = local.s3_bucket_name
    acl = "private"
    force_destroy = true
    tags = merge(local.common_tag, {Name = "day03-${var.enviroment_tag}-s3"})
}

resource "aws_s3_object" "day03_website" {
    bucket = aws_s3_bucket.day03_bucket.bucket
    key = "/website/index.html"
    source = "./index.html"
}

resource "aws_instance" "day02_instance" {
    ami                     =   data.aws_ami.ami_linux.id
    instance_type           =   "t2.micro"
    subnet_id               =   aws_subnet.day02_subnet1.id
    key_name                =   var.key_name
    vpc_security_group_ids  =   [aws_security_group.day02_allow.id]

    connection {
        type = "ssh"
        host = self.public_ip
        user = "ec2-user"
        private_key = file(var.private_key_path)
    }
    
    provisioner "file" {
        content = <<EOF
            access_key =
            secret_key =
            security_token =
            use_https = True
            bucket_location = US
        EOF
        destination = "/home/ec2-user/.s3cfg"
    }

    provisioner "file" {
        content = <<EOF
            /var/log/nginx/*log{
                daily
                rotate 10
                missingok
                compress
                sharescripts
                postrotate
                endscript
                lastaction
                    INSTANCE_ID = `curl --silent http://169.254.169.254/latest/meta-data/instance-id`
                    sudo /usr/local/bin/s3cmd sync --config=/home/ec2-user/.s3cfg /var/log/nginx/ s3://${aws_s3_bucket.day03_bucket.id}/nginx/$INSTANCE_ID/
                endscript
            }
        EOF
        destination = "/home/ec2-user/nginx"
    }

    provisioner "remote-exec" {
        inline = [ 
            "sudo yum install nginx -y",
            "sudo service nginx start",
            "sudo cp /home/ec2-user/.s3cfg /root/.s3cfg",
            "sudo cp /home/ec2-user/nginx /etc/logrotate.d/nginx",
            "sudo pip install s3cmd",
            "s3cmd get s3://${aws_s3_bucket.day03_bucket.id}/website/index.html .",
            "sudo logrotate -f /etc/logrotate.conf",
            "sudo service nginx reload"
        ]
    }

    tags = merge(local.common_tag, {Name = "day03-${var.enviroment_tag}-scrg-elb"})

}