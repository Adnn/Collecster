from .config_utils import *

from django.db import models
from django.conf import settings

import collections


##
## Specifics
##
class ReleaseSpecific(object):
    """ ReleaseSpecific classes are added to Release instances depending on their nature(s) """

    class AbstractBase(models.Model):
        class Meta:
            abstract = True
        release = models.ForeignKey('Release')

    class Combo(AbstractBase):
        brand = models.ForeignKey('Company', blank=True, null=True)

    class Hardware(AbstractBase):
        color = models.ManyToManyField("Color")
        manufacturer = models.ForeignKey('Company', blank=True, null=True)
        wireless = models.BooleanField(default=False)
        battery_type = models.ForeignKey("BatteryType", blank=True, null=True)
        #model = models.CharField(max_length=20, blank=True)  ## Probably useless, since there is already 'version'

        def __str__(self):
           return "Hardware specific for release: {}".format(self.release)

    class DirectionalController(AbstractBase):
        direction_input_type = models.ManyToManyField("InputType")

    class Software(AbstractBase):
        publisher   = models.ForeignKey("Company", blank=True, null=True, related_name="published_software_set")
        porter      = models.ForeignKey("Company", blank=True, null=True, related_name="ported_software_set", verbose_name="Company realizing the port")
        collection_label = models.CharField(max_length=120, blank=True, verbose_name="Released in collection")

    class Accessory(AbstractBase):
        wireless        = models.BooleanField()
        force_feedback  = models.BooleanField()
        rumble_feedback = models.BooleanField()

        #turbo    = models.BooleanField() ## same thing as autofire, is not it ?
        autofire = models.BooleanField()
        slow     = models.BooleanField()

    class Console(AbstractBase):
       console_on_chip = models.BooleanField(default=False, help_text="Is this a (re-)implementation of a system on a single chip ?")
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
        unit        = models.ForeignKey("StorageUnit")


RelSp = ReleaseSpecific


class ReleaseCategory:
    EMPTY       = ()
    COMBO       = (RelSp.Combo,)
    SOFTWARE    = (RelSp.Software,)
    HARDWARE    = (RelSp.Hardware,)
    CONSOLE     = compose(HARDWARE, (RelSp.Console,))
    DEMO        = compose(SOFTWARE, (RelSp.Demo,))
    MEMORY      = compose(HARDWARE, (RelSp.Memory,))
    DIR_INPUT   = compose(HARDWARE, (RelSp.DirectionalController,))


class OccurrenceSpecific(object):
    """ OccurrenceSpecific classes are added to Occurrence instances depending on their nature(s) """

    class AbstractBase(models.Model):
        class Meta:
            abstract = True
        occurrence = models.ForeignKey('Occurrence')

    class OperationalOcc(AbstractBase):
        YES = "Y"
        NO = "N"
        UNKNOWN = "?"

        CHOICES = (
            (UNKNOWN, "N/A"),
            (YES, "Yes"),
            (NO, "No"),
        )
        working_condition = models.CharField(max_length=1, choices=CHOICES, default=UNKNOWN)

    class ConsoleOcc(AbstractBase):
        region_modded = models.BooleanField()
        copy_modded = models.BooleanField()


OccSp = OccurrenceSpecific


class OccurrenceCategory:
    EMPTY       = ()
    OPERATIONAL = (OccSp.OperationalOcc,)
    CONSOLE     = (OccSp.OperationalOcc, OccSp.ConsoleOcc,)


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


##
## Defines the natures and all their associeted data
##
class ConfigNature(ConfigNature):
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

    PAD = "PAD"
    GUN = "GUN"

    DataTuple = collections.namedtuple("DataTuple", ["ui_value", "ui_group", "tag_color", "release_category", "occurrence_category", "automatic_attributes"])
    DATA = collections.OrderedDict((
        (COMBO,     DataTuple(COMBO,        UIGroup._HIDDEN,    "grey",     ReleaseCategory.COMBO,     OccurrenceCategory.EMPTY,    (),             )),

        (CONSOLE,   DataTuple('Console',    UIGroup._TOPLEVEL,  "red",      ReleaseCategory.CONSOLE,   OccurrenceCategory.CONSOLE,      automatic_self )),
        (GAME,      DataTuple('Game',       UIGroup.SOFT,       "green",    ReleaseCategory.SOFTWARE,  OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (DEMO,      DataTuple('Demo',       UIGroup.SOFT,       "palegreen",ReleaseCategory.DEMO,      OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (GUN,       DataTuple('Gun',        UIGroup.ACCESSORY,  "blue",     ReleaseCategory.HARDWARE,  OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (PAD,       DataTuple('Pad',        UIGroup.ACCESSORY,  "blue",     ReleaseCategory.DIR_INPUT, OccurrenceCategory.OPERATIONAL,  automatic_self )),
        # application -> purple
    ))
