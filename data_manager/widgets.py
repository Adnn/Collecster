from django import forms, utils


class LabelWidget(forms.widgets.TextInput):
    """ Custom widget class, implementing a label instead of a user input """
    #def __init__(self, attrs=None):
    #    super(LabelWidget, self).__init__(attrs)
    #    self.can_add_related = False


    def render(self, name, value, attrs):
        if value is None:
            html = u"LABEL WIDGET RENDER: EMPTY ERROR"
        else:
            html = u"{}{}".format(super(LabelWidget, self).render(name, value, dict(hidden=1, **attrs)),
                                  self.get_display_value(value))
        return utils.safestring.SafeText(html)

    def get_display_value(self, value):
        # Nota: to be overriden when another behaviour is needed (see labelwidget_factory)
        return value

#    def bound_data(self, data, initial):
#        return initial

def labelwidget_factory(Model):
    classname = "{}{}".format(Model.__name__, "LabelWidget")

    def get_display_value(self, value):
        return self.model.objects.get(pk=value)

    return type(classname, (LabelWidget,), {"get_display_value": get_display_value, "model": Model})


class SimpleLabelWidget(forms.widgets.TextInput):
    # Nota: This approach, intended to replace LabelWidget, does not work:
    #       The absence of proper value in an html input element makes it reveive 'None' value on form errors redisplay
    def render(self, name, value, attrs):
        if value is None:
            html = u"LABEL WIDGET RENDER: EMPTY ERROR"
        else:
            html = value
        return utils.safestring.SafeText(html)


##
## Radio select
##
class RadioSelectOneLineRenderer(forms.widgets.RadioFieldRenderer):
    """ Custom renderer for RadioSelect widget, displaying the option on a single line instead of inside of <ul> """
    outer_html = '<span{id_attr}>{content}</span>'
    inner_html = '{choice_value}{sub_widgets}'
        
class RadioSelectOneLine(forms.widgets.RadioSelect):
    renderer = RadioSelectOneLineRenderer
