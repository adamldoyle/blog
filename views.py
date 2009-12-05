from blog.forms import *
from django.contrib.auth.models import User
from django.conf import settings
from django.http import Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from mixins.helpers import render_with_context

def blog_404():
    return HttpResponseRedirect(reverse('blog.views.default'))

def check_date(year, month, day):
    try:
        return datetime.date(int(year), int(month), int(day))
    except ValueError:
        return False

def determine_entries(request, startDate, endDate, **kwargs):
    page = 1
    if request.GET.has_key('p'):
        try:
            page = int(request.GET['p'])
        except ValueError:
            pass
    per_page = 5
    if hasattr(settings, 'BLOG_POSTS_PER_PAGE'):
        per_page = int(settings.BLOG_POSTS_PER_PAGE)
    start = (page - 1) * per_page
    end = start + per_page
    entries = Entry.objects.filter(visible = 1, listable=1, members_only__lte=request.user.is_authenticated(), created_at__range=(startDate, endDate))
    if kwargs.has_key('tag_id'):
        entries = entries.filter(tags__id=kwargs['tag_id'])
    if kwargs.has_key('category_id'):
        entries = entries.filter(category=kwargs['category_id'])
    entries = entries[start:end+1]
    has_next = 0
    if len(entries) > per_page:
        has_next = page + 1
    has_prev = page - 1
    entries = entries[:end]
    return [entries, has_next, has_prev]

def default(request, template_name='blog/defaults/default.html'):
    start = datetime.datetime.min
    end = datetime.datetime.now()
    entries, has_next, has_prev = determine_entries(request, start, end)
    return render_with_context(request, template_name, {'entries': entries, 'has_next': has_next, 'has_prev': has_prev })

def detail(request, entry_id, slug, template_name='blog/defaults/entry_detail.html', **kwargs):
    try:
        entry = Entry.objects.get(pk=entry_id, slug=slug, visible=1, members_only__lte=request.user.is_authenticated(), created_at__lte=datetime.datetime.now())
    except Entry.DoesNotExist:
        return blog_404()
    f = None
    params = {'title': entry.title, 'entry': entry}
    if entry.allow_comments:
        if request.GET.has_key('edit'):
            comment_id = request.GET['edit']
            try:
                comment = Comment.objects.get(pk=comment_id)
                if comment.posted_by == request.user or request.user.has_perm("blog.change_comment"):
                    params['comment_id'] = comment_id
                    f = CommentForm(instance=comment)
            except Comment.DoesNotExist:
                pass
        elif request.GET.has_key('delete'):
            comment_id = request.GET['delete']
            try:
                comment = Comment.objects.get(pk=comment_id)
                if comment.posted_by == request.user or request.user.has_perm("blog.delete_comment"):
                    comment.delete()
            except Comment.DoesNotExist:
                pass
            return HttpResponseRedirect(entry.get_absolute_url())
    
        if f is None:
            if request.user.is_authenticated() or not hasattr(settings, 'BLOG_ALLOW_ANON_COMMENTS') or settings.BLOG_ALLOW_ANON_COMMENTS:
                f = CommentForm()

    params['new_comment'] = f
    return render_with_context(request, template_name, params)
    
def archive_year(request, year, template_name='blog/defaults/default.html'):
    start = check_date(year, 1, 1)
    if not start:
        return blog_404()
    end = check_date(int(year)+1, 1, 1)
    entries, has_next, has_prev = determine_entries(request, start, end)
    return render_with_context(request, template_name, {'title': _('Archive: %(year)s') % {'year': year}, 'entries': entries, 'has_next': has_next, 'has_prev': has_prev })
    
def archive_month(request, year, month, template_name='blog/defaults/default.html'):
    start = check_date(year, month, 1)
    if not start:
        return blog_404()
    end = check_date(year, int(month)+1, 1)
    entries, has_next, has_prev = determine_entries(request, start, end)
    months = (_('January'), _('February'), _('March'), _('April'), _('May'), _('June'), _('July'), _('August'), _('September'), _('October'), _('November'), _('December'))
    return render_with_context(request, template_name, {'title': _('Archive: %(month)s, %(year)s') % {'month': months[int(month)-1], 'year': year}, 'entries': entries, 'has_next': has_next, 'has_prev': has_prev })
    
def archive_day(request, year, month, day, template_name='blog/defaults/default.html'):
    start = check_date(year, month, day)
    if not start:
        return blog_404()
    end = check_date(year, month, int(day)+1)
    entries, has_next, has_prev = determine_entries(request, start, end)
    months = (_('January'), _('February'), _('March'), _('April'), _('May'), _('June'), _('July'), _('August'), _('September'), _('October'), _('November'), _('December'))
    return render_with_context(request, template_name, {'title': _('Archive: %(month)s %(day)s, %(year)s') % {'month': months[int(month)-1], 'day': day, 'year': year}, 'entries': entries, 'has_next': has_next, 'has_prev': has_prev })

def by_category(request, category_id, template_name='blog/defaults/default.html'):
    start = datetime.datetime.min
    end = datetime.datetime.now()
    try:
        category = EntryCategory.objects.get(pk=category_id)
    except EntryCategory.DoesNotExist:
        return blog_404()
    entries, has_next, has_prev = determine_entries(request, start, end, category_id=category_id)
    return render_with_context(request, template_name, {'title': _('Category: %(category)s') % {'category': category}, 'entries': entries, 'has_next': has_next, 'has_prev': has_prev })

def by_tag(request, tag_id, template_name='blog/defaults/default.html'):
    start = datetime.datetime.min
    end = datetime.datetime.now()
    try:
        tag = Tag.objects.get(pk=tag_id)
    except Tag.DoesNotExist:
        return blog_404()
    entries, has_next, has_prev = determine_entries(request, start, end, tag_id=tag_id)
    return render_with_context(request, template_name, {'title': _('Tag: %(tag)s') % {'tag': tag}, 'entries': entries, 'has_next': has_next, 'has_prev': has_prev })

def comment(request, entry_id, template_name='blog/defaults/entry_detail.html'):
    try:
        entry = Entry.objects.get(pk=entry_id, visible=1, allow_comments=1, members_only__lte=request.user.is_authenticated(), created_at__lte=datetime.datetime.now())
    except Entry.DoesNotExist:
        return blog_404()
    if request.POST and entry.allow_comments:
        if request.POST.has_key('comment_id'):
            comment = Comment.objects.get(pk=request.POST['comment_id'])
            if comment.posted_by == request.user or request.user.has_perm("blog.change_comment"):
                f = CommentForm(request.POST)
                if f.is_valid():
                    c = f.save(commit=False)
                    comment.date_updated = datetime.datetime.now()
                    comment.post = c.post
                    comment.save()
                else:
                    return render_with_context(request, template_name, {'title': entry.title, 'entry': entry, 'new_comment': f, 'comment_id': comment.id})
        else:
            f = CommentForm(request.POST)
            if f.is_valid():
                c = f.save(commit=False)
                if not hasattr(settings, 'BLOG_ALLOW_ANON_COMMENTS') or not settings.BLOG_ALLOW_ANON_COMMENTS:
                    if not request.user.is_authenticated():
                        return HttpResponseRedirect(entry.get_absolute_url())
                if request.user.is_authenticated():
                    c.posted_by = request.user
                c.posted_by_ip = request.META['REMOTE_ADDR']
                c.entry_id = entry_id
                c.save()
            else:
                return render_with_context(request, template_name, {'title': entry.title, 'entry': entry, 'new_comment': f})
    return HttpResponseRedirect(entry.get_absolute_url())