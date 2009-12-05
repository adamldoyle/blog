from django import template
from blog.models import Entry
from mixins.helpers import VariableNode, VariableTag
import re

register = template.Library()

class BlogArchiveNode(VariableNode):
    def setVariable(self, context):
        request = context['request']
        return Entry.archives.get_archives(request.user.is_authenticated())

def blog_archives(parser, token):
    return VariableTag(parser, token, BlogArchiveNode)
register.tag('blog_archives', blog_archives)

def entry_count():
    return Entry.objects.count()
register.simple_tag(entry_count)