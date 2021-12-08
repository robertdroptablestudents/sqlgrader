from django import template
import os

register = template.Library()


@register.simple_tag(name='buildid')
def buildid():
    # environment variable BUILDNUMER
    return os.environ['BUILDNUMBER']
