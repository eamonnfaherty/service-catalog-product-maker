import click
import requests
from cfn_flip import to_yaml
import json
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.basicConfig(
    format="%(levelname)s %(threadName)s [%(filename)s:%(lineno)d] %(message)s",
    datefmt="%Y-%m-%d:%H:%M:%S",
    level=logging.INFO,
)


@click.group()
def cli():
    """cli"""
    pass


def generate(type, specification, include_optional, property_types, friendly_name):
    logger.info(f"Generating: {type}")
    parameters = {}
    resource_properties = {}
    for property_name, property in specification.get('Properties', {}).items():
        logger.info(f"looking at property: {property_name}")
        is_optional = not property.get('Required')
        required = property.get('Required')
        if required or (is_optional and include_optional):
            if property.get('PrimitiveType') is not None:
                parameters[f"{friendly_name}{property_name}"] = {
                    'Type': property.get('PrimitiveType').replace('Integer', "Number").replace("Boolean", "String"),
                    'Description': property.get('Documentation')
                }
                if property.get('PrimitiveType') == "Boolean":
                    parameters[f"{friendly_name}{property_name}"]['AllowedValues'] = ["true", "false"]
                if not property.get('Required'):
                    parameters[f"{friendly_name}{property_name}"]['Default'] = None
                resource_properties[property_name] = {"Ref": f"{friendly_name}{property_name}"}
            elif property.get('Type') == "List":
                pass
            elif property.get('Type') == "Map":
                pass
            else:
                property_type = f"{type}.{property.get('Type')}"
                spec = property_types.get(property_type)
                logger.info(f"spec for {property_type} was {spec}")
                p, r, o = generate(
                    type,
                    property_types.get(property_type),
                    include_optional,
                    property_types,
                    f"{friendly_name}{property.get('Type')}"
                )
                resource_properties[property_name] = r
                parameters.update(p)

    outputs = {}
    for attribute in specification.get('Attributes', []):
        outputs[f"{friendly_name}{attribute}"] = {
            "Value": {"GetAtt": ["Resource", attribute]}
        }

    return parameters, resource_properties, outputs


@cli.command()
@click.argument('region')
@click.argument('type')
@click.option('--include-optional/--no-include-optional', default=False)
def make_me_a(region, type, include_optional):
    source = f"https://cfn-resource-specifications-{region}-prod.s3.{region}.amazonaws.com/latest/gzip/CloudFormationResourceSpecification.json"
    response = requests.get(source)
    content = response.json()
    result = generate_a(content, type, include_optional)
    click.echo(result)


def generate_a(content, type, include_optional):
    property_types = content.get('PropertyTypes')
    resources = content.get('ResourceTypes')
    specification = resources.get(type)
    parameters, resource_properties, outputs = generate(type, specification, include_optional, property_types, "")
    result = dict(
        AWSTemplateFormatVersion="2010-09-09",
        Description=specification.get('Documentation'),
    )
    if len(parameters.keys()) > 0:
        result['Parameters'] = parameters
    result['Resources'] = {
        "Resource": {
            "Type": type,
            "Description": specification.get('Documentation'),
        }
    }
    if len(resource_properties.items()) > 0:
        result['Resources']["Resource"]["Properties"] = resource_properties
    if len(outputs.keys()) > 0:
        result['Outputs'] = outputs
    return to_yaml(json.dumps(result))


@cli.command()
@click.argument('region')
@click.argument('output', type=click.Path(exists=True))
@click.option('--include-optional/--no-include-optional', default=False)
def make_me_all(region, output, include_optional):
    source = f"https://cfn-resource-specifications-{region}-prod.s3.{region}.amazonaws.com/latest/gzip/CloudFormationResourceSpecification.json"
    response = requests.get(source)
    content = response.json()
    version = content.get('ResourceSpecificationVersion')
    resource_types = content.get('ResourceTypes')
    for resource_type in resource_types.keys():
        result = generate_a(content, resource_type, include_optional)
        out = os.path.join(output, resource_type.replace("::", "-"), version)
        if not os.path.exists(out):
            os.makedirs(out)
        with open(os.path.join(out, f"product.template-{region}.yaml"), 'w') as f:
            f.write(result)


@cli.command()
@click.argument('region')
def get_current_resource_specification_version(region):
    source = f"https://cfn-resource-specifications-{region}-prod.s3.{region}.amazonaws.com/latest/gzip/CloudFormationResourceSpecification.json"
    response = requests.get(source)
    content = response.json()
    click.echo(content.get('ResourceSpecificationVersion'))


if __name__ == "__main__":
    cli()
