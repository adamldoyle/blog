from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from itertools import chain
from blog.models import *

attrs_dict_req = { 'class': 'required' }
attrs_dict_add = { 'rel': 'add_new' }

class EntryForm(forms.ModelForm):
    class Meta:
        model = Entry
        exclude = ('user','created_at','modified_at')
        
class CommentForm(forms.ModelForm):
    post = forms.CharField(widget=forms.Textarea(attrs={'class': 'longer wider'}))
    class Meta:
        model = Comment
        from django.conf import settings
        # If attribute doesn't exist, allow anonymous comments by default
        if not hasattr(settings, 'BLOG_ALLOW_ANON_COMMENTS') or settings.BLOG_ALLOW_ANON_COMMENTS:
            exclude = ('posted_by','entry','posted_by_ip','created_at','modified_at')
        else:
            exclude = ('posted_by','entry','posted_by_name','posted_by_ip','created_at','modified_at')