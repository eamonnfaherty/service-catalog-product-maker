import click
import requests
from cfn_flip import to_yaml
import json
import os


@click.group()
def cli():
    """cli"""
    pass


def generate(type, specification, include_nested, property_types, friendly_name):
    parameters = {}
    resource_properties = {}
    for property_name, property in specification.get('Properties', {}).items():
        if property.get('PrimitiveType') is not None:
            parameters[f"{friendly_name}{property_name}"] = {
                'Type': property.get('PrimitiveType').replace('Integer', "Number").replace("Boolean", "String"),
                'Description': property.get('Documentation')
            }
            if property.get('PrimitiveType') == "Boolean":
                parameters[f"{friendly_name}{property_name}"]['AllowedValues'] = ["true", "false"]
            if not property.get('Required'):
                parameters[f"{friendly_name}{property_name}"]['Default'] = None
            resource_properties[property_name] = {"Ref": property_name}
        elif property.get('Type') == "List":
            pass
        else:
            if include_nested:
                property_type = f"{type}.{property.get('Type')}"
                p, r, o = generate(
                    type,
                    property_types.get(property_type),
                    include_nested,
                    property_types,
                    f"{friendly_name}{property.get('Type')}"
                )
                resource_properties[property.get('Type')] = r
                for p_name, p_value in p.items():
                    if parameters.get(p_name) is not None:
                        raise Exception(f"{property_type}.{p_name} has already been used")
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
@click.option('--include-nested/--no-include-nested', default=False)
def make_me_a(region, type, include_nested):
    result = generate_a(region, type, include_nested)
    click.echo(result)


def generate_a(region, type, include_nested):
    source = f"https://cfn-resource-specifications-{region}-prod.s3.{region}.amazonaws.com/latest/gzip/CloudFormationResourceSpecification.json"
    response = requests.get(source)
    content = response.json()
    property_types = content.get('PropertyTypes')
    resources = content.get('ResourceTypes')
    specification = resources.get(type)
    parameters, resource_properties, outputs = generate(type, specification, include_nested, property_types, "")
    return to_yaml(
        json.dumps(
            {
                "AWSTemplateFormatVersion": "2010-09-09",
                "Description": specification.get('Documentation'),
                "Parameters": parameters,
                "Resources": {
                    "Resource": {
                        "Type": type,
                        "Description": specification.get('Documentation'),
                        "Properties": resource_properties,
                    }
                },
                "Outputs": outputs,
            }
        )
    )

@cli.command()
@click.argument('region')
@click.argument('output', type=click.Path(exists=True))
@click.option('--include-nested/--no-include-nested', default=False)
def make_me_all(region, output, include_nested):
    source = f"https://cfn-resource-specifications-{region}-prod.s3.{region}.amazonaws.com/latest/gzip/CloudFormationResourceSpecification.json"
    response = requests.get(source)
    content = response.json()
    property_types = content.get('PropertyTypes')
    for property_type in property_types.keys():
        resource_type = property_type.split(".")[0]
        result = generate_a(region, resource_type, include_nested)
        with open(os.path.join(output,f"{resource_type}.template.yaml"), 'w') as f:
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
