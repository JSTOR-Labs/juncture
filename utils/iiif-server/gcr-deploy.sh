#!/bin/bash

# GCP_PROJECT='visual-essay'
GCP_PROJECT='juncture-digital'

GCR_SERVICE=${1:-iiif}

gcloud config set project ${GCP_PROJECT}
gcloud config set compute/region us-central1
gcloud config set run/region us-central1

rm -rf build
mkdir build
rsync -va --exclude=venv --exclude=__pycache__ app.py atlas-creds iiifhosting-creds Dockerfile build

cd build
gcloud builds submit --tag gcr.io/${GCP_PROJECT}/${GCR_SERVICE}
gcloud beta run deploy ${GCR_SERVICE} --image gcr.io/${GCP_PROJECT}/${GCR_SERVICE} --allow-unauthenticated --platform managed --memory 1Gi
