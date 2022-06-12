#!/bin/bash

GCP_PROJECT='juncture-digital'

GCR_SERVICE=${1:-api}
MIN_INSTANCE_LIMIT=1

gcloud config set project ${GCP_PROJECT}
gcloud config set compute/region us-central1
gcloud config set run/region us-central1

gcloud builds submit --tag gcr.io/${GCP_PROJECT}/${GCR_SERVICE}
gcloud beta run deploy ${GCR_SERVICE} \
    --image gcr.io/${GCP_PROJECT}/${GCR_SERVICE} \
    --min-instances ${MIN_INSTANCE_LIMIT} \
    --allow-unauthenticated \
    --platform managed \
    --memory 1Gi
