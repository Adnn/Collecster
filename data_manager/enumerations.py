from django import forms

import collections


class Attribute:
    class Type:
        RATING      = u"RTN" # The complete rating, with possibility to indicate absence
        PRESENCE    = u"PRS" # Limited to present / absence

        @classmethod
        def get_choices(cls):
            return [(key, value_tuple.ui_value) for key, value_tuple in Attribute.DATA.items()]

        @classmethod
        def choices_maxlength(cls):
            return 3

        to_form_field = {}# dictionary mapping Type to form fields, assigned after the class definition


    class Value:
        RATING_CHOICES = (
            (u'M', u'Mint'),
            (u'A', u'A'),
            (u'B', u'B'),
            (u'C', u'C'),
            (u'D', u'D'),
            (u'E', u'E'),
        )

        NULL_CHOICE     = ("", "----")
        ABSENT_CHOICE   = (u'0', u'ABSENT')
        PRESENT_CHOICE  = (u'1', u'PRESENT')


        @classmethod
        def get_rating_choices(cls):
            return (cls.NULL_CHOICE, cls.ABSENT_CHOICE,) + cls.RATING_CHOICES

        @classmethod
        def get_presence_choices(cls):
            return (cls.ABSENT_CHOICE, cls.PRESENT_CHOICE)

        @classmethod
        def choices_maxlength(cls):
            return 1


    class CustBool(forms.BooleanField):
        def prepare_value(self, value):
            if value == "0":
                return ""
            return value

        def to_python(self, value):
            value = super(Attribute.CustBool, self).to_python(value)
            return "1" if value else "0"
        pass


    DataTuple = collections.namedtuple("DataTuple", ["ui_value", "form_field"])
    DATA = {
        Type.RATING:    DataTuple(u'Rating',     forms.ChoiceField( choices=Value.get_rating_choices()),      ),
        Type.PRESENCE:  DataTuple(u'Presence',   forms.ChoiceField( choices=Value.get_presence_choices(),
                                                                    widget=forms.RadioSelect) ),
            # This would work, modulo the fact that, on "New occurence save", if the checkbox is not checked,
            # there is no value saved in the DB (but there is one saved when edition, going from true to false)
        #Type.PRESENCE:  DataTuple(u'Presence',   CustBool() ),
    }


Attribute.Type.to_form_field = {key: tuple_value.form_field for key, tuple_value in Attribute.DATA.items()}


#    @classmethod
#    def get_choices(cls):
#        return [(key, value[0]) for key, value in cls.DICT.items()]
#
#    @classmethod
#    def get_class_and_options(cls, attribute_type):
#        value = cls.DICT[attribute_type][1]
#        return value[0], value[1]

