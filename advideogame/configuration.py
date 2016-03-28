from .config_utils import *

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError

import collections


##
## IMPORTANT: tagging the fiels were it is debatable if it is a specific for the Release of for the Concept with DEB
##

##
## Specifics
##
class ConceptSpecific(object):
    """ ConceptSpecific classes are added to Concept instances depending on their nature(s) """

    class AbstractBase(models.Model):
        class Meta:
            abstract = True
        concept = models.OneToOneField('Concept')

        def get_parent_instance(self):
            return self.concept

    class Remote(AbstractBase): # for consoles and accessories
        battery_type = models.ForeignKey("BatteryType", blank=True, null=True)

    class RemoteAccessory(AbstractBase): # for something that is remote to the main system (wireless introducing the "link" notion)
        wireless        = models.BooleanField()

    class Shell(AbstractBase):
        is_shell = models.BooleanField(help_text="If this concept is simply a plastic shell.")

    class Controller(AbstractBase):
        force_feedback  = models.BooleanField()
        rumble_feedback = models.BooleanField()

        #turbo    = models.BooleanField() ## same thing as autofire, is not it ?
        autofire = models.BooleanField()
        slow     = models.BooleanField()

    class DirectionalController(AbstractBase): 
        direction_input_type = models.ManyToManyField("InputType") # DEB


ConSp = ConceptSpecific

class ConceptCategory:
    EMPTY       = ()
    HANDHELD    = (ConSp.Remote, ConSp.DirectionalController, ConSp.Controller, )
    REMOTE      = (ConSp.Remote, ConSp.RemoteAccessory)
    CONTROLLER  = compose(REMOTE,       (ConSp.Shell, ConSp.Controller,))
    DIR_INPUT   = compose(CONTROLLER,   (ConSp.DirectionalController,))


class ReleaseSpecific(object):
    """ ReleaseSpecific classes are added to Release instances depending on their nature(s) """
    ## Fields that are debatable (could be on Concept) are marke with DEB

    class AbstractBase(models.Model):
        class Meta:
            abstract = True
        release = models.OneToOneField('Release')

        def get_parent_instance(self):
            return self.release


    class Combo(AbstractBase):
        brand = models.ForeignKey('Company', blank=True, null=True)

    class Hardware(AbstractBase): # Almost any physical occurrence is hardware (even bags and cases)
        color = models.ManyToManyField("Color")
        manufacturer = models.ForeignKey('Company', blank=True, null=True) # DEB (in cases of accessories, not consoles)
        #model = models.CharField(max_length=20, blank=True)  ## Probably useless, since there is already 'version'

        def __str__(self):
           return "Hardware specific for release: {}".format(self.release)

    class Software(AbstractBase):
        publisher   = models.ForeignKey("Company", blank=True, null=True, related_name="published_software_set")
        porter      = models.ForeignKey("Company", blank=True, null=True, related_name="ported_software_set", verbose_name="Company realizing the port")
        collection_label = models.CharField(max_length=120, blank=True, verbose_name="Released in collection")

    class Demo(AbstractBase):
        issue_number    = models.PositiveIntegerField(blank=True, null=True)
        games_playable  = models.ManyToManyField('Concept', blank=True, related_name='playable_demo_set')
        games_video     = models.ManyToManyField('Concept', blank=True, related_name='video_demo_set')

            ## Not sure if it is possible to query the M2M relationship (ValueError wether there is a provided value or not)
        #def clean(self):
        #    wdb.set_trace()
        #    if not self.games_playable and not self.games_video:
        #        raise ValidationError("The demo must have at least one game, video or playalbe.")

    class Media(AbstractBase):
        media_types = models.ManyToManyField("MediaType") # DEB, but kept here in case some release of media do not have the same content

    class Memory(AbstractBase):
        capacity    = models.PositiveIntegerField()
        unit        = models.ForeignKey("StorageUnit") # DEB, but the capacity is not, and it is tighlty coupled to it.


RelSp = ReleaseSpecific


class ReleaseCategory:
    EMPTY       = ()
    COMBO       = (RelSp.Combo,)
    SOFTWARE    = (RelSp.Software,)
    HARDWARE    = (RelSp.Hardware,)
    CONSOLE     = (RelSp.Hardware,)
    DEMO        = compose(SOFTWARE,     (RelSp.Demo,))
    MEDIA       = compose(SOFTWARE,     (RelSp.Media,))
    MEMORY      = compose(HARDWARE,     (RelSp.Memory,))


class OccurrenceSpecific(object):
    """ OccurrenceSpecific classes are added to Occurrence instances depending on their nature(s) """

    class AbstractBase(models.Model):
        class Meta:
            abstract = True
        occurrence = models.OneToOneField('Occurrence')

        def get_parent_instance():
            return self.occurrence


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

    # Systems
    CONSOLE = "CONSOLE"
    CONSOLE_CHIP = "CONSOLE_CHIP" # Console-on-chip
    HANDHELD_CONSOLE = "HANDHELD_CONSOLE"

    # Software
    GAME = "GAME"
    ADD_ON = "ADD_ON"
    MOD = "MOD"
    DEMO = "DEMO"
    OS = "OS"
    WEB_BROWSER = "WEB_BROWSER"
    APPLICATION = "APPLICATION"
    MEDIA = "MEDIA"

    # Accessories
    PAD =               "PAD" # Kept in hands, both analog and digitial (distinction made in a specific)
    ARCADE_STICK =      "ARCADE_STICK" # Left on the table, with the characteristic handle
    JOYSTICK =          "JOYSTICK" # A la flight simulator
    GUN =               "GUN"
    STEERINGWHEEL =     "STEERINGWHEEL"

    DRUM =              "DRUM"
    GUITAR =            "GUITAR"
    TURNTABLE =         "TURNTABLE"

    BATTERY_CHARGER =   "BATTERY_CHARGER"
    BATTERY_ELEC =      "BATTERY_ELEC"
    BUZZER =            "BUZZER"
    CAMERA =            "CAMERA"
    CHEAT_DEV =         "CHEAT_DEV"
    DANCEMAT =          "DANCEMAT"
    FISHING_ROD =       "FISHING_ROD"
    MOTION_SENSING =    "MOTION_SENSING"
    HEADPHONES =        "HEADPHONES"
    KEYBOARD =          "KEYBOARD"
    LINK_CABLE =        "LINK_CABLE" # Connects two or more systems (eg. GameBoy's "Game Link Cable")
    MAGNIFIER =         "MAGNIFIER"
    MEMORYCARD =        "MEMORYCARD"
    MICROPHONE =        "MICROPHONE" # Could be used as instrument, but not necessarily (eg. microphone in EyeToy)
    MODEM =             "MODEM"
    MOUSE =             "MOUSE"
    MULTITAP =          "MULTITAP"
    PRINTER =           "PRINTER"
    PROTECTIVE_CASE =   "PROTECTIVE_CASE" # Anything that fits on a material device, allowing to use the device while attached
    RAM_PACK =          "RAM_PACK"
    REGION_UNLOCK =     "REGION_UNLOCK"
    RUMBLE_PACK =       "RUMBLE_PACK" # A rumble pack to extend a controller, NOT for controllers with builtin rumble feedback
    SCANNER =           "SCANNER"
    SCREEN_MAIN =       "SCREEN_MAIN"
    SCREEN_INDIV =      "SCREEN_INDIV"
    SPEAKERS =          "SPEAKERS"
    STEREOGLASSES =     "STEREOGLASSES"
    TRANSIT_CONTAINER = "TRANSIT_CONTAINER" # A hard carry case or a bag

    DataTuple = collections.namedtuple("DataTuple", ["ui_value", "ui_group", "tag_color", "concept_category", "release_category", "occurrence_category", "automatic_attributes"])
    DATA = collections.OrderedDict((
        (COMBO,             DataTuple(COMBO,               UIGroup._HIDDEN,    "grey",     ConceptCategory.EMPTY,       ReleaseCategory.COMBO,     OccurrenceCategory.EMPTY,         (),            )),

        (CONSOLE,           DataTuple("Console",           UIGroup._TOPLEVEL,  "red",      ConceptCategory.EMPTY,       ReleaseCategory.CONSOLE,    OccurrenceCategory.CONSOLE,      automatic_self )),
        (CONSOLE_CHIP,      DataTuple("Console-on-chip",   UIGroup._TOPLEVEL,  "red",      ConceptCategory.EMPTY,       ReleaseCategory.CONSOLE,    OccurrenceCategory.CONSOLE,      automatic_self )),
        (HANDHELD_CONSOLE,  DataTuple("Handheld Console",  UIGroup._TOPLEVEL,  "red",      ConceptCategory.HANDHELD,     ReleaseCategory.CONSOLE,   OccurrenceCategory.CONSOLE,      automatic_self )),

        (GAME,              DataTuple("Game",              UIGroup.SOFT,       "green",    ConceptCategory.EMPTY,       ReleaseCategory.SOFTWARE,   OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (ADD_ON,            DataTuple("AddOn",             UIGroup.SOFT,       "seagreen", ConceptCategory.EMPTY,       ReleaseCategory.SOFTWARE,   OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (MOD,               DataTuple("Mod",               UIGroup.SOFT,       "seagreen", ConceptCategory.EMPTY,       ReleaseCategory.SOFTWARE,   OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (DEMO,              DataTuple("Demo",              UIGroup.SOFT,       "palegreen",ConceptCategory.EMPTY,       ReleaseCategory.DEMO,       OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (OS,                DataTuple("Os",                UIGroup.SOFT,       "purple",   ConceptCategory.EMPTY,       ReleaseCategory.SOFTWARE,   OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (WEB_BROWSER,       DataTuple("Web browser",       UIGroup.SOFT,       "purple",   ConceptCategory.EMPTY,       ReleaseCategory.SOFTWARE,   OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (APPLICATION,       DataTuple("Application",       UIGroup.SOFT,       "purple",   ConceptCategory.EMPTY,       ReleaseCategory.SOFTWARE,   OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (MEDIA,             DataTuple("Media",             UIGroup.SOFT,       "purple",   ConceptCategory.EMPTY,       ReleaseCategory.MEDIA,      OccurrenceCategory.OPERATIONAL,  automatic_self )),

        (PAD,               DataTuple("Pad",               UIGroup.ACCESSORY,  "blue",     ConceptCategory.DIR_INPUT,   ReleaseCategory.HARDWARE,   OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (ARCADE_STICK,      DataTuple("Arcade stick",      UIGroup.ACCESSORY,  "blue",     ConceptCategory.DIR_INPUT,   ReleaseCategory.HARDWARE,   OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (JOYSTICK,          DataTuple("Joystick",          UIGroup.ACCESSORY,  "blue",     ConceptCategory.DIR_INPUT,   ReleaseCategory.HARDWARE,   OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (GUN,               DataTuple("Gun",               UIGroup.ACCESSORY,  "blue",     ConceptCategory.CONTROLLER,  ReleaseCategory.HARDWARE,   OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (STEERINGWHEEL,     DataTuple("Steeringwheel",     UIGroup.ACCESSORY,  "blue",     ConceptCategory.CONTROLLER,  ReleaseCategory.HARDWARE,   OccurrenceCategory.OPERATIONAL,  automatic_self )),

        (DRUM,              DataTuple("Drum",              UIGroup.ACCESSORY,  "blue",     ConceptCategory.CONTROLLER,  ReleaseCategory.HARDWARE,   OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (GUITAR,            DataTuple("Guitar",            UIGroup.ACCESSORY,  "blue",     ConceptCategory.CONTROLLER,  ReleaseCategory.HARDWARE,   OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (TURNTABLE,         DataTuple("Turntable",         UIGroup.ACCESSORY,  "blue",     ConceptCategory.CONTROLLER,  ReleaseCategory.HARDWARE,   OccurrenceCategory.OPERATIONAL,  automatic_self )),

        (BATTERY_CHARGER,   DataTuple("Battery charger",   UIGroup.ACCESSORY,  "blue",     ConceptCategory.EMPTY,       ReleaseCategory.HARDWARE,   OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (BATTERY_ELEC,      DataTuple("Electric battery",  UIGroup.ACCESSORY,  "blue",     ConceptCategory.EMPTY,       ReleaseCategory.HARDWARE,   OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (BUZZER,            DataTuple("Buzzer",            UIGroup.ACCESSORY,  "blue",     ConceptCategory.REMOTE,      ReleaseCategory.HARDWARE,   OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (CAMERA,            DataTuple("Camera",            UIGroup.ACCESSORY,  "blue",     ConceptCategory.REMOTE,      ReleaseCategory.HARDWARE,   OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (CHEAT_DEV,         DataTuple("Cheat device",      UIGroup.ACCESSORY,  "blue",     ConceptCategory.EMPTY,       ReleaseCategory.HARDWARE,   OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (DANCEMAT,          DataTuple("Dancemat",          UIGroup.ACCESSORY,  "blue",     ConceptCategory.CONTROLLER,  ReleaseCategory.HARDWARE,   OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (FISHING_ROD,       DataTuple("Fishing rod",       UIGroup.ACCESSORY,  "blue",     ConceptCategory.CONTROLLER,  ReleaseCategory.HARDWARE,   OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (HEADPHONES,        DataTuple("Headphones",        UIGroup.ACCESSORY,  "blue",     ConceptCategory.EMPTY,       ReleaseCategory.HARDWARE,   OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (KEYBOARD,          DataTuple("Keyboard",          UIGroup.ACCESSORY,  "blue",     ConceptCategory.CONTROLLER,  ReleaseCategory.HARDWARE,   OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (LINK_CABLE,        DataTuple("Link cable",        UIGroup.ACCESSORY,  "blue",     ConceptCategory.EMPTY,       ReleaseCategory.HARDWARE,   OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (MAGNIFIER,         DataTuple("Magnifier",         UIGroup.ACCESSORY,  "blue",     ConceptCategory.EMPTY,       ReleaseCategory.HARDWARE,   OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (MEMORYCARD,        DataTuple("Memorycard",        UIGroup.ACCESSORY,  "blue",     ConceptCategory.EMPTY,       ReleaseCategory.MEMORY,     OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (MICROPHONE,        DataTuple("Microphone",        UIGroup.ACCESSORY,  "blue",     ConceptCategory.REMOTE,      ReleaseCategory.HARDWARE,   OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (MODEM,             DataTuple("Modem",             UIGroup.ACCESSORY,  "blue",     ConceptCategory.EMPTY,       ReleaseCategory.HARDWARE,   OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (MOTION_SENSING,    DataTuple("Motion sensing",    UIGroup.ACCESSORY,  "blue",     ConceptCategory.CONTROLLER,  ReleaseCategory.HARDWARE,   OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (MOUSE,             DataTuple("Mouse",             UIGroup.ACCESSORY,  "blue",     ConceptCategory.CONTROLLER,  ReleaseCategory.HARDWARE,   OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (MULTITAP,          DataTuple("Multitap",          UIGroup.ACCESSORY,  "blue",     ConceptCategory.EMPTY,       ReleaseCategory.HARDWARE,   OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (PRINTER,           DataTuple("Printer",           UIGroup.ACCESSORY,  "blue",     ConceptCategory.EMPTY,       ReleaseCategory.HARDWARE,   OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (PROTECTIVE_CASE,   DataTuple("Protective case",   UIGroup.ACCESSORY,  "blue",     ConceptCategory.EMPTY,       ReleaseCategory.HARDWARE,   OccurrenceCategory.EMPTY,        automatic_self )),
        (RAM_PACK,          DataTuple("Ram pack",          UIGroup.ACCESSORY,  "blue",     ConceptCategory.EMPTY,       ReleaseCategory.MEMORY,     OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (REGION_UNLOCK,     DataTuple("Region unlock",     UIGroup.ACCESSORY,  "blue",     ConceptCategory.EMPTY,       ReleaseCategory.HARDWARE,   OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (RUMBLE_PACK,       DataTuple("Rumble pack",       UIGroup.ACCESSORY,  "blue",     ConceptCategory.EMPTY,       ReleaseCategory.HARDWARE,   OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (SCANNER,           DataTuple("Scanner",           UIGroup.ACCESSORY,  "blue",     ConceptCategory.EMPTY,       ReleaseCategory.HARDWARE,   OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (SCREEN_MAIN,       DataTuple("Screen main",       UIGroup.ACCESSORY,  "blue",     ConceptCategory.REMOTE,      ReleaseCategory.HARDWARE,   OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (SCREEN_INDIV,      DataTuple("Screen individual", UIGroup.ACCESSORY,  "blue",     ConceptCategory.REMOTE,      ReleaseCategory.HARDWARE,   OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (SPEAKERS,          DataTuple("Speakers",          UIGroup.ACCESSORY,  "blue",     ConceptCategory.EMPTY,       ReleaseCategory.HARDWARE,   OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (STEREOGLASSES,     DataTuple("Stereo glasses",    UIGroup.ACCESSORY,  "blue",     ConceptCategory.REMOTE,      ReleaseCategory.HARDWARE,   OccurrenceCategory.OPERATIONAL,  automatic_self )),
        (TRANSIT_CONTAINER, DataTuple("Transit container", UIGroup.ACCESSORY,  "blue",     ConceptCategory.EMPTY,       ReleaseCategory.HARDWARE,   OccurrenceCategory.EMPTY,        automatic_self )),
    ))
