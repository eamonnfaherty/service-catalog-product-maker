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



for TYPE in $(ls output/)
do
  echo """# Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: Apache-2.0

Schema: factory-2019-04-01
Portfolios:
  Components:""" > output/${TYPE}/portfolio.yaml
  for PRODUCT in $(ls output/${TYPE})
  do
    for VERSION in $(ls output/${TYPE}/${PRODUCT})
    do
      echo """
      - Name: ${PRODUCT}
        Owner: central-it@customer.com
        Description: ${PRODUCT}
        Distributor: central-it-team
        SupportDescription: Contact us on Chime for help #central-it-team
        SupportEmail: central-it-team@customer.com
        SupportUrl: https://wiki.customer.com/central-it-team/self-service/${PRODUCT}
        Tags:
          - Key: product-type
            Value: ${PRODUCT}
        Versions:
          - Name: ${VERSION}
            Description: ${PRODUCT}-${VERSION}
            Active: True
            Source:
              Provider: CodeCommit
              Configuration:
                RepositoryName: ${PRODUCT}
                BranchName: ${VERSION}
      """ >> output/${TYPE}/portfolio.yaml
    done
  done
done