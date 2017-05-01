from django.shortcuts import render, redirect
from django.urls.base import reverse
from django.views.generic import View

from django.http import HttpResponseNotFound, HttpResponse

from interp.models import User, Task, Translation
from interp.utils import StaffCheckMixin, is_translate_in_editing


class UserTranslations(StaffCheckMixin, View):
    def get(self, request, username):
        user = User.objects.get(username=username)
        # tasks = Task.objects.filter(is_published=True).values_list('id', 'title')
        translations = []
        for task in Task.objects.filter(is_published=True):
            translation = Translation.objects.filter(user=user, task=task).first()
            is_editing = translation and is_translate_in_editing(translation)
            if translation:
                translations.append((task.id, task.title, True, translation.id, translation.freeze, is_editing ))
            else:
                translations.append((task.id, task.title, False, 'None', False, False))
        return render(request, 'user_translates.html', context={'translations': translations, 'language': user.credentials()})


class UsersList(StaffCheckMixin, View):
    def get(self, request):
        users = User.objects.filter(is_staff=False)
        return render(request, 'users_list.html', context={'users': users})


class FreezeTranslation(StaffCheckMixin, View):
    def post(self, request, id):
        freeze = request.POST.get('freeze', False)
        trans = Translation.objects.filter(id=id).first()
        if trans is None:
            return HttpResponseNotFound("There is no task")
        trans.freeze = freeze
        trans.save()
        return redirect(to=reverse('user_trans', kwargs={'username' : trans.user.username}))
