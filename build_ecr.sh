docker build -t rc-club-members-2 https://github.com/tortxof/rc-club-members-2.git
aws ecr-public get-login-password --region us-east-1 | docker login --username AWS --password-stdin public.ecr.aws/m3l3l1j4
docker tag rc-club-members-2:latest public.ecr.aws/m3l3l1j4/rc-club-members-2:latest
docker push public.ecr.aws/m3l3l1j4/rc-club-members-2:latest
