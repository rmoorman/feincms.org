from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404
from django.template.defaultfilters import slugify
from feincms.content.application.models import app_reverse
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from .models import AppPromo, AppPromoForm, AppPromoTranslation, CategoryTranslation

PAGINATE_BY = 10

def app_list(request):
    apps = AppPromo.objects.all()

    #pagination
    paginator = Paginator(apps, PAGINATE_BY)
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1

    try:
        paged = paginator.page(page)
    except (EmptyPage, InvalidPage):
        paged = paginator.page(paginator.num_pages)


    context = {'apps': apps, 'page': page, 'paged': paged,
               'is_paginated': paginator.num_pages>1 }

    return render(request, 'app_library/app_list.html', context)

def app_category_list(request, slug):
    category_trans = get_object_or_404(CategoryTranslation, slug=slug)
    apps = AppPromo.objects.filter(category=category_trans.parent)
    context = {'apps': apps }
    return render(request, 'app_library/app_list.html', context)

def app_detail(request, slug):
    app = get_object_or_404(AppPromo, slug=slug)
    return render(request, 'app_library/app_detail.html', {'app': app })

@login_required(login_url='/accounts/login/')
def app_submit(request):
    if request.method == 'POST':
        form = AppPromoForm(request.POST, request.FILES)
        if form.is_valid():
            app = form.save(commit=False)
            app.author = request.user
            app.save()
            translation = AppPromoTranslation(parent=app, language_code='en')
            translation.short_description = form.cleaned_data['short_description']
            translation.long_description = form.cleaned_data['long_description']
            translation.save()
            return HttpResponseRedirect(app.get_absolute_url())
    else:
        form = AppPromoForm()
    action = app_reverse('app_library_submit', 'feincmsorg.app_library.urls')
    return render(request, 'app_library/submit.html', {'form': form, 'action': action })

@login_required(login_url='/accounts/login/')
def app_edit(request, slug):
    app = get_object_or_404(AppPromo, slug=slug)
    if not app.author == request.user:
        return HttpResponseForbidden('Only the original uploader can edit an app.')
    if request.method == 'POST':
        form = AppPromoForm(request.POST, request.FILES, instance=app)
        if form.is_valid():
            app = form.save()
            translation = AppPromoTranslation.objects.get(parent=app, language_code='en')
            translation.short_description = form.cleaned_data['short_description']
            translation.long_description = form.cleaned_data['long_description']
            translation.save()
            return HttpResponseRedirect(app.get_absolute_url())
    else:
        data = {'short_description': app.translation.short_description,
            'long_description': app.translation.long_description }
        form = AppPromoForm(initial=data, instance=app)

    action = app_reverse('app_library_edit', 'feincmsorg.app_library.urls', kwargs={'slug': app.slug})
    return render(request, 'app_library/submit.html', {'form': form, 'action': action })
