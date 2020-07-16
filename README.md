## service catalog product builder

builds AWS CloudFormation templates that can be used as a seed for Service Catalog products


## Usage

### make-me-a

servicecatalog-product-maker make-me-a ${REGION} AWS::S3::Bucket --include-optional
servicecatalog-product-maker make-me-a ${REGION} AWS::S3::Bucket --no-include-optional

### make-me-all

servicecatalog-product-maker make-me-all ${REGION} --include-optional output
servicecatalog-product-maker make-me-all ${REGION} --no-include-optional output