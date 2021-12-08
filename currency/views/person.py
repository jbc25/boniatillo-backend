from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse

import helpers
from currency.forms.PersonForm import PersonForm
from currency.models import Person

@login_required
def user_profile(request):
    person = get_object_or_404(Person, user=request.user)
    can_edit = request.user.is_superuser or request.user == person.user
    form = PersonForm(instance=person)
    return render(request, 'profile/detail.html', {
        'person': person,'form':form, 'can_edit':can_edit
    })


@login_required
def profile_list(request):
    persons = Person.objects.all()
    query_string = ''
    if ('q' in request.GET) and request.GET['q'].strip():
        query_string = request.GET['q']
        entry_query = helpers.get_query(query_string, ['name', 'surname', 'email'])
        if entry_query:
            persons = persons.filter(entry_query)

    page = request.GET.get('page')
    persons = helpers.paginate(persons, page, elems_perpage=10)

    params = {
        'ajax_url': reverse('profile_list'),
        'query_string': query_string,
        'profiles': persons,
        'page': page
    }

    if request.is_ajax():
        response = render(request, 'profile/profile_query.html', params)
        response['Cache-Control'] = 'no-cache'
        response['Vary'] = 'Accept'
        return response
    else:
        return render(request, 'profile/list.html', params)


@login_required
def profile_detail(request, pk):
    person = get_object_or_404(Person, pk=pk)
    can_edit = request.user.is_superuser or request.user == person.user
    form = PersonForm(instance=person)
    return render(request, 'profile/detail.html', {
        'person': person, 'form':form, 'can_edit':can_edit
    })


@login_required
def profile_edit(request, pk):
    person = get_object_or_404(Person, pk=pk)
    can_edit = request.user.is_superuser or request.user == person.user

    if not can_edit:
        messages.add_message(request, messages.ERROR, 'No tienes permisos para editar esta consumidora')
        return redirect('profile_detail', pk=person.pk )

    if request.method == "POST":
        form = PersonForm(request.POST, request.FILES, instance=person)
        if form.is_valid():
            person = form.save(commit=False)
            person.save()
            form.save_m2m()

            return redirect('profile_detail', pk=person.pk)
        else:
            print(form.errors.as_data())
    else:
        form = PersonForm(instance=person)

    return render(request, 'profile/edit.html', {
        'form': form,
        'person': person,
        'can_edit':can_edit
    })


@helpers.superuser_required
def add_person(request):
    can_edit = request.user.is_superuser

    if not can_edit:
        messages.add_message(request, messages.ERROR, 'No tienes permisos para editar esta consumidora')
        return redirect('profile_list')

    if request.method == "POST":
        form = PersonForm(request.POST, request.FILES)
        if form.is_valid():
            person = form.save(commit=False)

            owner_id = form.cleaned_data['owner_id']
            new_user_username = form.cleaned_data['new_user_username']
            new_user_password = form.cleaned_data['new_user_password']

            if owner_id:
                user = User.objects.get(pk=owner_id)
                person.user = user

            elif new_user_username and new_user_password:
                user_email = person.email
                user, created = User.objects.get_or_create(username=new_user_username, email=user_email,
                                                           password=new_user_password)
                user.set_password(new_user_password)
                user.save()
                person.user = user
            else:
                person.user = request.user

            send_email = form.cleaned_data['send_welcome_email']
            if send_email:
                helpers.mailing.send_template_email(
                    'Bienvenid@ a la app del Boniatillo',
                    person.email,
                    'welcome_person',
                    {'person': person, 'password': new_user_password}
                )

            person.save()
            form.save_m2m()

            return redirect('profile_detail', pk=person.pk)
        else:
            print(form.errors.as_data())
    else:
        form = PersonForm()

    return render(request, 'profile/add.html', {
        'form': form,
        'can_edit':can_edit
    })
