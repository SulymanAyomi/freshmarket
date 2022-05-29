from django.forms.widgets import Widget


class PlusMinusNumberInput(Widget):
    template_name = "widgets/plusminusnumber.html"

    class Media:
        css = {"all": ("css/style.css",)}
        js = ("js/plusminusnumber.js",)
