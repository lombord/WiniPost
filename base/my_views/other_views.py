from django.views.generic import TemplateView

# other views
class CreateMenuView(TemplateView):
    template_name = 'base/forms/create_menu.html'
