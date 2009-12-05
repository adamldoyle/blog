from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from blog.manager import EntryManager
from mixins.models import SlugMixin, UserMixin, DateMixin
import datetime

class EntryCategory(models.Model):
    category = models.CharField(max_length=50)
    
    class Meta:
        ordering = ('category',)
    
    def __unicode__(self):
        return u"%s" %self.category

class Tag(models.Model):
    tag = models.CharField(max_length=20)
    
    class Meta:
        ordering = ('tag',)
    
    def __unicode__(self):
        return u"%s" %self.tag

class Entry(SlugMixin, UserMixin, DateMixin):
    title = models.CharField(max_length=100)
    post = models.TextField()
    blurb = models.TextField()
    category = models.ForeignKey(EntryCategory, null=True, blank=True)
    tags = models.ManyToManyField(Tag, null=True, blank=True)
    members_only = models.BooleanField('only visible to members',default=0)
    visible = models.BooleanField(default=1)
    allow_comments = models.BooleanField(default=1)
    listable = models.BooleanField('show in blog list', default=1)
    show_date = models.BooleanField(default=1)
    order = models.PositiveSmallIntegerField(default=1)
    objects = models.Manager()
    archives = EntryManager()
    slugValue = 'title'
    
    def num_comments(self):
        return len(self.comment_set.all())
    
    def tags_pretty(self):
        return ', '.join([tag.tag for tag in self.tags.all()])

    class Meta:
        ordering = ('order', '-created_at',)
    
    def __unicode__(self):
        return u"%s" %self.title
    
    def get_absolute_url(self):
        return reverse('blog.views.detail', args=(self.id,self.slug,))

class Comment(DateMixin):
    entry = models.ForeignKey(Entry, null=True, blank=True)
    posted_by = models.ForeignKey(User, related_name='blog_author', null=True, blank=True)
    posted_by_name = models.CharField("name", max_length=40, null=True, blank=True)
    posted_by_ip = models.IPAddressField(null=True, blank=True)
    post = models.TextField()
    
    class Meta:
        ordering = ('-created_at',)
    
    def __unicode__(self):
        return u"%s" %self.post
    
class EntryAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Post', {'fields': ['title', 'blurb', 'post', 'user', 'category']}),
        ('Flags/Tags', {'fields': ['tags', 'members_only', 'allow_comments', 'visible', 'listable'], 'classes': ['collapse']}),
    ]
    list_display = ('title','category','user')
    list_filter = ['created_at']
    search_fields = ['title','category','user']
    date_hierarchy = 'created_at'

admin.site.register(Entry, EntryAdmin)
admin.site.register(EntryCategory)
admin.site.register(Tag)
admin.site.register(Comment)