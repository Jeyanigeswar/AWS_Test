# create bucket (replace region if needed)
aws s3api create-bucket \
--bucket demo-bucket313 \
--region ap-south-1 \
--create-bucket-configuration LocationConstraint=ap-south-1

# upload files (from current folder)
aws s3 sync ./ s3://demo-bucket313

# attach the bucket policy

aws s3api put-bucket-policy \
--bucket demo-bucket313 \
--policy /workspaces/AWS_Test/s3/policy.json


aws s3 sync ./ s3://demo-bucket313 --exclude "*" --include "*.html"