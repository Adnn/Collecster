from django.db import models
from django.core.exceptions import ValidationError

import collections

import data_manager.models

#TODEL
#import wdb

def compose(*args):
    """ Used to compose category from by extending another category """
    return tuple([element for tupl in args for element in tupl])


def is_material(release):
    """ The notion of immaterial needs to be a core concept, because some core behaviour depends on it"""
    """ eg. define application logic that an immterial cannot have attribute nor nested elements """
    """ Yet not to force having an immaterial field (for cases were there are no immaterials), it is abstracted through this function """
    return not release.immaterial


class ConceptDeploymentBase(models.Model):
    """ An abstract base for the Concept model, allowing to give it deployment-specific fields without introducing """
    """ an additional DB table. """  
    class Meta:
        abstract = True


class ReleaseDeploymentBase(models.Model):
    """ An abstract base for the Release model, allowing to give it deployment-specific fields without introducing """
    """ an additional DB table. """  
    class Meta:
        abstract = True
    
    collecster_material_fields = ("loose", "barcode",)

    immaterial  = models.BooleanField(default=False) 

    loose   = models.BooleanField() 
    #region  = models.CharField(max_length=2, choices=Region.CHOICES, blank=True) #TODO
    version = models.CharField(max_length=20, blank=True) 

    ## Barcode is not mandatory because some nested release will not have a barcode (eg. pad with a console)
    barcode = models.CharField(max_length=20, blank=True)


class OccurrenceDeploymentBase(models.Model):
    class Meta:
        abstract = True

    collecster_material_fields = ("blister",)

    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    #origin = models.CharField(max_length=2, choices=Origin.get_choices()) #TODO
    notes = models.CharField(max_length=256, blank=True) # Not sure if it should not be a TextField ?
    #tag = models.ImageField(upload_to=name_tag, blank=True) #TODO
    blister = models.BooleanField(help_text="Indicates whether a blister is still present.")


class ReleaseSpecific(object):
    """ ReleaseSpecific classes are added to Release instances depending on their nature(s) """

    class AbstractBase(models.Model):
        class Meta:
            abstract = True
        release = models.ForeignKey('Release')

    class Hardware(AbstractBase):
        #TODO : color
        #constructor = models.ForeignKey('Company', blank=True, null=True) #TODO
        model = models.CharField(max_length=20, blank=True) 

        def __str__(self):
           return "Hardware specific for release: {}".format(self.release)

    class Software(AbstractBase):
        #publisher   = models.ForeignKey(Company, blank=True, null=True) # TODO
        #porter      = models.ForeignKey(Company, blank=True, null=True, vebose_name"Company realizing the port") # TODO
        collection_label = models.CharField(max_length=120, blank=True, verbose_name="Released in collection")

#    class Accessory(AbstractBase):
#        accessory_name  = models.CharField(max_length= 60)  
#
#
#    class Console(AbstractBase):
#        release         = models.ForeignKey('Release')
#
#
#    class Game(AbstractBase):
#        pass

    class Demo(AbstractBase):
        issue_number    = models.PositiveIntegerField(blank=True, null=True)
        games_playable  = models.ManyToManyField('Concept', blank=True, related_name='playable_demo_set')
        games_video     = models.ManyToManyField('Concept', blank=True, related_name='video_demo_set')

            ## Not sure if it is possible to query the M2M relationship (ValueError wether there is a provided value or not)
        #def clean(self):
        #    wdb.set_trace()
        #    if not self.games_playable and not self.games_video:
        #        raise ValidationError("The demo must have at least one game, video or playalbe.")

    class Memory(AbstractBase):
        capacity    = models.PositiveIntegerField()
        #unit        = models.ForeignKey(MemoryUnit) #TODO


RelSp = ReleaseSpecific


class ReleaseCategory:
    EMPTY       = ()
    SOFTWARE    = (RelSp.Software,)
    HARDWARE    = (RelSp.Hardware,)
    DEMO        = compose(SOFTWARE, (RelSp.Demo,))
    MEMORY      = compose(HARDWARE, (RelSp.Memory,))


class OccurrenceSpecific(object):
    """ OccurrenceSpecific classes are added to Occurrence instances depending on their nature(s) """

    class AbstractBase(models.Model):
        class Meta:
            abstract = True
        release = models.ForeignKey('Occurrence')

    class Operational(AbstractBase):
        #working_condition = models.CharField(max_length=1, choices=WorkingState.CHOICES, default=WorkingState.UNKNOWN) #TODO
        pass

    class Console(AbstractBase):
        region_modded = models.BooleanField()
        copy_modded = models.BooleanField()


OccSp = OccurrenceSpecific


class OccurrenceCategory:
    EMPTY       = ()
    OPERATIONAL = (OccSp.Operational,)
    CONSOLE     = (OccSp.Operational, OccSp.Console,)


def get_attribute_category(category_name):
    models = data_manager.models
    return models.AttributeCategory.objects.get(name=category_name)

def get_attribute(category_name, attribute_name):
    models = data_manager.models
    return models.Attribute.objects.get(category=get_attribute_category(category_name), name=attribute_name)


def automatic_self():
    return (get_attribute("content", "self"), )

# Intended to be used for implicit occurence attributes (unused now)
def self_software(release):
    try:
        material = not ReleaseSpecific.Software.objects.get(release=release).immaterial
    except ReleaseSpecific.Software.DoesNotExist:
        # The Software specific is not created id its form stayed empty (=> 'immaterial' was not checked)
        material = True
    return implicit_self(release) if material else ()


class ConceptNature:
    class UIGroup:
        _HIDDEN         = "_HIDDEN"
        _TOPLEVEL       = ""
        ACCESSORY       = "Accessory"
        SOFT            = "Software"

    COMBO = "_COMBO"

    CONSOLE = "CONSOLE"
    DEMO = "DEMO"
    GAME = "GAME"
    OS = "OS"

    GUN = "GUN"

    #DATA = {
    #    UIGroup._TOPLEVEL: (
    #        (CONSOLE,   'Console', ReleaseCategory.HARDWARE),
    #    ),
    #    UIGroup.SOFT: (
    #        (GAME,      'Game',    ReleaseCategory.SOFTWARE, UIGroup.SOFT),
    #    ),
    #}
    DataTuple = collections.namedtuple("DataTuple", ["ui_value", "ui_group", "release_category", "occurrence_category", "automatic_attributes"])
    DATA = {
        COMBO:      DataTuple(COMBO,        UIGroup._HIDDEN,    ReleaseCategory.EMPTY,     OccurrenceCategory.EMPTY,    (),             ),

        CONSOLE:    DataTuple('Console',    UIGroup._TOPLEVEL,  ReleaseCategory.HARDWARE,  OccurrenceCategory.CONSOLE,      automatic_self ),
        GAME:       DataTuple('Game',       UIGroup.SOFT,       ReleaseCategory.SOFTWARE,  OccurrenceCategory.OPERATIONAL,  automatic_self ),
        DEMO:       DataTuple('Demo',       UIGroup.SOFT,       ReleaseCategory.DEMO,      OccurrenceCategory.OPERATIONAL,  automatic_self ),
        GUN:        DataTuple('Gun',        UIGroup.ACCESSORY,  ReleaseCategory.HARDWARE,  OccurrenceCategory.OPERATIONAL,  automatic_self ),
    }


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
        sorted_groups = collections.defaultdict(list)
        for db_value, data in cls.DATA.items():
            pair = (db_value, data.ui_value)
            (toplevel if (data.ui_group is cls.UIGroup._TOPLEVEL) else sorted_groups[data.ui_group]).append(pair)
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
    def get_release_specifics(cls, nature_set):
        return cls._get_specifics(nature_set, "release")

    @classmethod
    def get_occurrence_specifics(cls, nature_set):
        return cls._get_specifics(nature_set, "occurrence")

    @classmethod
    def get_concept_automatic_attributes(cls, concept):
        unique_automatic_attribs = collections.OrderedDict()
        models = data_manager.models

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
    ## and to make utils.all_release_attributes() to call this function.
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
