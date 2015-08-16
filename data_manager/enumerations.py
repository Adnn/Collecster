class AttributeValue:
    class Type:
        RATING      = u'RTN' # The complete rating, with possibility to indicate absence
        PRESENCE    = u'PRS' # Limited to present / absence

        @classmethod
        def get_choices(cls):
            return ((cls.RATING, "Rating"), (cls.PRESENCE, "Presence"))

        @classmethod
        def choices_maxlength(cls):
            return 3

    RATING_CHOICES = (
        (u'0', u'---'),     # Absent
        (u'M', u'Mint'),
        (u'A', u'A'),
        (u'B', u'B'),
        (u'C', u'C'),
        (u'D', u'D'),
        (u'E', u'E'),
    )

#    DICT = {
#        RATING : (u'Rating', (widgets.Select, {'choices':RATING_CHOICES,}) ),
#        RATING_NULL : (u'Rating w/ null', (widgets.Select, {'choices':RATING_NULL_CHOICES,}) ),
#        PRESENCE : (u'Presence', (widgets.CheckboxInput, None) ),
#    }

    @classmethod
    def choices_maxlength(cls):
        return 1

#    @classmethod
#    def get_choices(cls):
#        return [(key, value[0]) for key, value in cls.DICT.items()]
#
#    @classmethod
#    def get_class_and_options(cls, attribute_type):
#        value = cls.DICT[attribute_type][1]
#        return value[0], value[1]
