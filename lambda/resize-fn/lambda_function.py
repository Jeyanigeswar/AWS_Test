# lambda_function.py
import boto3
import os
import io
from PIL import Image

s3 = boto3.client("s3")
DEST_BUCKET = os.environ.get("DEST_BUCKET")

def lambda_handler(event, context):
    try:
        record = event["Records"][0]
        source_bucket = record["s3"]["bucket"]["name"]
        key = record["s3"]["object"]["key"]

        # download object into memory
        obj = s3.get_object(Bucket=source_bucket, Key=key)
        body = obj["Body"].read()
        img = Image.open(io.BytesIO(body))
        img.thumbnail((300, 300))

        buf = io.BytesIO()
        fmt = img.format if img.format else "JPEG"
        img.save(buf, format=fmt)
        buf.seek(0)

        dest_key = f"resized-{key}"
        s3.put_object(
            Bucket=DEST_BUCKET,
            Key=dest_key,
            Body=buf,
            ContentType=obj.get("ContentType", f"image/{fmt.lower()}")
        )

        return {"status": "success", "resized_key": dest_key}
    except Exception as e:
        # log and re-raise so CloudWatch shows the trace
        print("Error in lambda_handler:", e)
        raise
