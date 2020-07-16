#!/usr/bin/env bash

set -e

for REGION in $(aws ec2 describe-regions --all-regions --query 'Regions[].RegionName' --output text)
do
  VERSION=$(servicecatalog-product-maker get-current-resource-specification-version ${REGION})
  mkdir -p output/include-optional
  mkdir -p output/no-include-optional

  servicecatalog-product-maker make-me-all ${REGION} --include-optional output/include-optional/
  servicecatalog-product-maker make-me-all ${REGION} --no-include-optional output/no-include-optional/
done