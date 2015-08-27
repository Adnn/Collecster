from django import forms, utils


class LabelWidget(forms.widgets.Select):
    """ Custom widget class, implementing a label instead of a user input """
    def __init__(self, attrs=None, choices=()):
        super(LabelWidget, self).__init__(attrs, choices)
        self.can_add_related = False


    def render(self, name, value, attrs):
        if value is None:
            html = u"LABEL WIDGET RENDER: EMPTY ERROR"
        else:
            html = u"{}{}".format(super(LabelWidget, self).render(name, value, dict(hidden=1, **attrs)),
                                  self.model.objects.get(pk=value))
        return utils.safestring.SafeText(html)


#    def bound_data(self, data, initial):
#        return initial

def labelwidget_factory(Model):
    classname = "{}{}".format(Model.__name__, "LabelWidget")
    return type(classname, (LabelWidget,), {"model": Model})
