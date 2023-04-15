from django.views.generic import TemplateView


class IndexPageView(TemplateView):
    template_name = "tree_menu/index.html"
