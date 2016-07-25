import collections

#TODEL
#import wdb


##
## Utils
##
def compose(*args):
    """ Used to compose category from by extending another category """
    return tuple([element for tupl in args for element in tupl])

def get_attribute_category(category_name):
    from . import models # Circular import from models otherwise
    return models.AttributeCategory.objects.get(name=category_name)

def get_attribute(category_name, attribute_name):
    from . import models
    return models.Attribute.objects.get(category=get_attribute_category(category_name), name=attribute_name)

# Intended to be used for implicit occurence attributes (unused now)
def self_software(release):
    try:
        material = not ReleaseSpecific.Software.objects.get(release=release).immaterial
    except ReleaseSpecific.Software.DoesNotExist:
        # The Software specific is not created id its form stayed empty (=> 'immaterial' was not checked)
        material = True
    return implicit_self(release) if material else ()


NatureData = collections.namedtuple("NatureData", ["ui_value", "ui_group", "tag_color",
                                                   "concept_category", "release_category", "occurrence_category",
                                                   "automatic_attributes"])
class ConfigNature:
    """ 
    Use should extend this class by deriving it from itself (http://stackoverflow.com/a/15526901/1027706) 
    And define a DATA class member 
    """

    ##
    ## Generic methods (no need for customization)
    ##
    @classmethod
    def choices_maxlength(cls):
        """ Returns the number of characters required to store any Nature into the DB """
        return max ([len(db_value) for db_value in cls.DATA])

    @classmethod
    def get_choices(cls):
        """ Returns the Nature choices for Concepts """
        #grouped = [(group, tuple([(line[0], line[1]) for line in tupl])) for group, tupl in cls.DATA.items() if group]
        #toplevel = [(line[0], line[1]) for line in [tupl for tupl in cls.DATA.get(cls.UIGroup._TOPLEVEL, ())]]
        #return tuple(toplevel) + tuple(grouped)
        toplevel = []
        #sorted_groups = collections.defaultdict(list) # The default dict is not ordered, generating uneccessary migrations
        sorted_groups = collections.OrderedDict()
        for db_value, data in cls.DATA.items():
            pair = (db_value, data.ui_value)
            (toplevel if (data.ui_group is cls.UIGroup._TOPLEVEL) else sorted_groups.setdefault(data.ui_group, [])).append(pair)
        return tuple(toplevel + [(ui_group, tuple(pairs)) for ui_group, pairs in sorted_groups.items() if ui_group != cls.UIGroup._HIDDEN])

        #return (
        #    ("console", "console"),
        #    ( "ACCESSORY", (("pad", "pad"), ("gun", "gun")) ),
        #)


    @classmethod
    def _get_specifics(cls, nature_set, model_name):
        unique_specific_set = collections.OrderedDict()
        for nature in nature_set:
            for specific in getattr(cls.DATA[nature], "{}_category".format(model_name)):
                unique_specific_set[specific] = None
        return unique_specific_set.keys()    

    @classmethod
    def get_concept_specifics(cls, nature_set):
        return cls._get_specifics(nature_set, "concept")
       
    @classmethod
    def get_release_specifics(cls, nature_set):
        return cls._get_specifics(nature_set, "release")

    @classmethod
    def get_occurrence_specifics(cls, nature_set):
        return cls._get_specifics(nature_set, "occurrence")

    @classmethod
    def get_concept_automatic_attributes(cls, concept):
        unique_automatic_attribs = collections.OrderedDict()

        for nature in concept.all_nature_tuple:
            automatics = cls.DATA[nature].automatic_attributes 
            if callable(automatics):
                automatics = automatics()
            for attribute in automatics:
                 unique_automatic_attribs[attribute] = None

        return list(unique_automatic_attribs.keys())

    ##
    ## Note: This method implemented proper implicit attributes, that are not shown on the Release add page
    ## but are then attributes attached to each Occurence instantiated from the Release.
    ## Implicit attributes are is disabled for the moment.
    ## To re-enable, it requires to allow ReleaseAttribute.release to be nullable
    ## and to make utils.shared_release_attributes() to call this function.
    ##
    #@classmethod
    #def get_release_implicit_attributes(cls, release):
    #    unique_implicit_attribs = collections.OrderedDict()
    #    models = data_manager.models

    #    for nature in release.concept.all_nature_tuple:
    #        implicits = cls.DATA[nature].implicit_attributes 
    #        if callable(implicits):
    #            implicits = implicits(release)

    #        for attribute in implicits:
    #            release_attribute = models.ReleaseAttribute.objects.get_or_create(release=None, attribute=attribute)[0]
    #            unique_implicit_attribs[release_attribute] = None

    #    return list(unique_implicit_attribs.keys())
