from django import forms

import collections


class Attribute:
    class Type:
        RATING      = u"RTN" # The complete rating, with possibility to indicate absence
        PRESENCE    = u"PRS" # Limited to present / absence

        @classmethod
        def get_choices(cls):
            """ Return the Type choices for Attributes """
            return [(key, value_tuple.ui_value) for key, value_tuple in Attribute.DATA.items()]

        @classmethod
        def choices_maxlength(cls):
            """ Returns the number of characters required to store any Attribute Type into the DB """
            return max ([len(db_value) for db_value in Attribute.DATA])

        to_form_field = {}# dictionary mapping Type to form fields, assigned after the class definition


    class Value:
        RATING_CHOICES = (
            ("M", "Mint"),
            ("A", "A"),
            ("B", "B"),
            ("C", "C"),
            ("D", "D"),
            ("E", "E"),
        )

        NULL_CHOICE     = ("", "----")
        ABSENT_CHOICE   = ("0", "ABSENT")
        PRESENT_CHOICE  = ("1", "PRESENT")


        @classmethod
        def get_rating_choices(cls):
            return (cls.NULL_CHOICE, cls.ABSENT_CHOICE,) + cls.RATING_CHOICES

        @classmethod
        def get_presence_choices(cls):
            return (cls.ABSENT_CHOICE, cls.PRESENT_CHOICE)

        @classmethod
        def choices_maxlength(cls):
            return 1


    #class CustBool(forms.BooleanField):
    #    def prepare_value(self, value):
    #        if value == "0":
    #            return ""
    #        return value

    #    def to_python(self, value):
    #        value = super(Attribute.CustBool, self).to_python(value)
    #        return "1" if value else "0"
    #    pass


    DataTuple = collections.namedtuple("DataTuple", ["ui_value", "form_field"])
    DATA = collections.OrderedDict((
        (Type.RATING,   DataTuple("Rating",     forms.ChoiceField( choices=Value.get_rating_choices()),      )),
        (Type.PRESENCE, DataTuple("Presence",   forms.ChoiceField( choices=Value.get_presence_choices(),
                                                                    widget=forms.RadioSelect) )),
            # This would work, modulo the fact that, on "New occurence save", if the checkbox is not checked,
            # there is no value saved in the DB (but there is one saved when edition, going from true to false)
        #Type.PRESENCE:  DataTuple("Presence",   CustBool() ),
    ))


# Maps attribute types to the form field that should be used to populate values of this type.
Attribute.Type.to_form_field = {key: tuple_value.form_field for key, tuple_value in Attribute.DATA.items()}


#    @classmethod
#    def get_choices(cls):
#        return [(key, value[0]) for key, value in cls.DICT.items()]
#
#    @classmethod
#    def get_class_and_options(cls, attribute_type):
#        value = cls.DICT[attribute_type][1]
#        return value[0], value[1]


class PartialDate:
    YEAR="YYYY"
    MONTH="MM"
    DAY="DD"

    DATA = collections.OrderedDict((
        (DAY,    "Day"),
        (MONTH,  "Month"),
        (YEAR,   "Year"),
    ))

    @classmethod
    def get_choices(cls):
        """ Return the precision choices for partial dates """
        return [(key, value) for key, value in cls.DATA.items()]

    @classmethod
    def choices_maxlength(cls):
        """ Returns the number of characters required to store any partial date precision in the DB """
        return max ([len(db_value) for db_value in cls.DATA])


class Country:
    LITHUANIA   = "LT"
    FRANCE      = "FR"
    BELGIUM     = "BE"
    GERMANY     = "DE"
    ITALY       = "IT"
    NETHERLANDS = "NL"
    PORTUGAL    = "PT"
    SPAIN       = "ES"
    IRELAND     = "IE"
    SWITZERLAND = "CH"
    UK          = "UK"
    MOROCCO     = "MA"
    ALGERIA     = "DZ"
    TUNISIA     = "TN"
    CHINA       = "CN"
    KOREA       = "KR"
    JAPAN       = "JP"
    USA         = "US"
    CANADA      = "CA"
    BRAZIL      = "BR"

    CHOICES = (
        (SWITZERLAND, "Switzerland"),
        (UK, "UK"),
        (IRELAND, "Ireland"),
        ("Asia",
            ((CHINA, "China"),
            (KOREA, "Korea"),
            (JAPAN, "Japan"),)
        ),
        ("Europe",
            ((LITHUANIA, "Lithuania"),
            (BELGIUM, "Belgium"),
            (FRANCE, "France"),
            (GERMANY, "Germany"),
            (ITALY, "Italy"),
            (NETHERLANDS, "Netherlands"),
            (PORTUGAL, "Portugal"),
            (SPAIN, "Spain"),)
        ),
        ("America",
            ((USA, "USA"),
            (CANADA, "Canada"),
            (BRAZIL, "Brazil"),) 
        ),
        ("Maghreb",
            ((ALGERIA, "Algeria"),
            (MOROCCO, "Morocco"),
            (TUNISIA, "Tunisia"),)
        ),
    )

    @classmethod
    def get_choices(cls):
        return cls.CHOICES

    @classmethod
    def choices_maxlength(cls):
        return 2
