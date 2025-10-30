from django.conf import settings
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .s3_client import s3_client, flight_key

class ListFlightsView(APIView):
    """
    GET /api/storage/flights
    Lists distinct flight IDs from the S3 bucket.
    Looks for prefixes like: flights/<flightId>/flight.log
    """
    def get(self, request):
        s3 = s3_client()
        bucket = settings.AWS_S3_BUCKET
        prefix = settings.AWS_S3_FLIGHT_PREFIX.strip("/") + "/"

        flights = []
        token = None

        # Use Delimiter to treat subfolders as "flights"
        while True:
            kwargs = {"Bucket": bucket, "Prefix": prefix, "Delimiter": "/"}
            if token:
                kwargs["ContinuationToken"] = token

            resp = s3.list_objects_v2(**kwargs)

            for cp in resp.get("CommonPrefixes", []):
                subprefix = cp.get("Prefix")  # e.g. flights/flight-001/
                flight_id = subprefix[len(prefix):].strip("/")
                # Ensure the expected log exists
                try:
                    s3.head_object(Bucket=bucket, Key=flight_key(flight_id))
                    flights.append(flight_id)
                except s3.exceptions.ClientError:
                    pass  # skip folders with no flight.log

            if resp.get("IsTruncated"):
                token = resp["NextContinuationToken"]
            else:
                break

        flights.sort()
        return Response({"flights": flights})


class ListVersionsView(APIView):
    """
    GET /api/storage/versions/<flight_id>
    Lists all versions for a specific flight log object.
    """
    def get(self, request, flight_id: str):
        s3 = s3_client()
        bucket = settings.AWS_S3_BUCKET
        key = flight_key(flight_id)

        resp = s3.list_object_versions(Bucket=bucket, Prefix=key)
        versions = [
            {
                "version_id": v.get("VersionId"),
                "is_latest": v.get("IsLatest"),
                "size": v.get("Size"),
                "last_modified": v.get("LastModified").isoformat(),
                "etag": v.get("ETag"),
            }
            for v in resp.get("Versions", []) if v.get("Key") == key
        ]
        versions.sort(key=lambda x: x["last_modified"], reverse=True)
        return Response({"flight_id": flight_id, "key": key, "versions": versions})

def home(request):
    return render(request, "base.html")
