.. role:: instance(emphasis)

====
User
====

.. _supervisor_user:

**********************
supervisor application
**********************

The supervisor special application is responsible for managing the different :instance:`configuration`\s that are deployed on the server.
It knows about all the users, and which collections they have access to.

*****************
data_manager base 
*****************

**data_manager** should be seen as an abstract application, which is not installed on deployments of Collecster, 
but which serves as the base on which each :instance:`configuration` is built.

It provides the base logic and several utility functions, alongside the base versions of several models 
that will be specialized by the different configurations to meet their specific requirements.

Models
======

The base models, provided by **data_manager**, will be specialized by the configurations by adding custom fields.
The base models provide some base fields, that are likely to be usefull in all configurations.

Concept
-------

* common name
* distinctive name
* primary nature
* [additional nature set]{0..n}

Release
-------

* concept
* name
* partial date
* [attributes]{0..n}
* [nested releases]{0..n}

Distinction
^^^^^^^^^^^

* name
* note

Release distinction
^^^^^^^^^^^^^^^^^^^

* ->release
* ->distinction
* value

Occurrence
----------

* release

An :instance:`occurrence` also presents fields for attributes and for nested occurrences.
Those fields are automatically controlled by the attributes and nested releases on the correponding :instance:`release`.

Attributes
----------
Attributes are defined by:

* category
* name
* value type
* [description]

There are two types of release attributes:

* (plain) ``Attribute``\s exist on their own, and can be assigned to several :instance:`release`\s. They are shared.
* ``CustomAttribute``\s are assigned to a single :instance:`release`, which owns it.

The :instance:`attribute`\s are designed to be explicitly attached to a :instance:`release` by the user. There are nonetheless some additional mechanism that could potentially add such attributes without user interaction:

* **automoatic attributes** are prepopulated on the :instance:`release` form, depending on the :instance:`nature`\(s). It can be changed by the user.
* **implicit attributes** (NOT IMPLEMENTED) attributes that are not attached to any specific :instance:`release`, but that are forced on some :instance:`occurence`\s.


.. _data_manager_usage_recommandations:

Usage recommandations
=====================

* Immaterial :instance:`release`\s are instantiated as :instance:`occurrence`\s, even though there is no physical
  entity matching such instances. There are a few reasons motivating this choice:

  * An immaterial could nonetheless be non-functional in some cases (eg. corrupt memory for a game embedded in a console)
  * It should allow for more natural requests (eg. counting the number of occurrences for a given release)
  * An immaterial can still contain ``Attribute``\s in some cases (eg. the manual for a game embedded in a console)

.. _advideogame_user:

***********
advideogame
***********

.. py:module:: advideogame.models

**advideogame** is a configuration for collections of video games. It adresses the systems (eg. consoles),
their peripherals (eg. pads) and their software (eg. games).

Model customizations
====================

.. autoclass:: Release
   :members: 

Color
-----

StorageUnit
-----------

Usage recommandations
=====================

Additionally to the general :ref:`data_manager_usage_recommandations`, some are specifics to **advideogame**

* For collected entities, another color is always another :instance:`release`.

* Following Wikipedias approach to disambiguate colliding names, if several distinct :instance:`concept`\s have the same
  unique name, they can be followed by a pair of parentheses containing disambiguation info
  (eg. the '8bit' distinction on `Sonic the Hedgehog <https://en.wikipedia.org/wiki/Sonic_the_Hedgehog_(8-bit_video_game)>`_).
  This can also be used when a product name is too generic, to make the unique name more descriptive
  (eg. the Sega Saturn *3D Control Pad* could have the target system added in parentheses).

  * If a parenthese symbol is appearing in the actual unique name, it should be escaped by doubling it.
  * There are separate fields for disambuiguation info regarding 'year' or 'region'
    (no need to rely on parentheses in those 2 specific cases).

* A **loose** object is a physical entity that was acquired without the packaging (and possibly without the manuals).
  This usually prevents identifying the actual release it was part of.
  A loose object **should be released** nonetheless (using the **loose** :py:attr:`Release.special_case_release`),
  because it still has platform, color, etc.
 
* The accessories that are nested in a system pack, distributed without their own packaging, are **not loose**,
  because the actual release is well identified. They should be marked **nested without discrete box** instead. 
  (see :py:attr:`Release.special_case_release`)

 
* The different versions of a system (eg. Master System I, Master System II, Sega Merk III) are belonging to a 
  **single** :instance:`Concept`. Thoses versions are modelled as distinct :ref:`system_variants` by the application.

* For accessories with several parts, the main part is the *self* attributes. Other modules, even connected to it,
  are recorded as a specialized attributes (eg. the pedals of a racing wheel, or the RF receiver of a pad, are both
  a distinct attribute).

*  If there are several main parts, the *self* attribute is duplicated,
   and the ``note`` field is used to disambiguate between the different *self* attributes. In particular, if the 
   different main parts have distinct color, it should be recorded in the ``note``.
   This *self* duplication would notably be used in the case of:

   * several wireless pads sold in the same packaging
   * a software distributed on several medias (because it does not fit on a single one, or for different systems)

.. note::
   This approach is chosen because the case is exceptional, and it leverages existing logic instead of requiring
   special case handling. It has drawbacks, notably that it does not duplicate the fields that should be separately
   stored for each *self*, as in the example of colors given above.
   Those information can still be saved in the ``note``, though in a non-structured manner.


Concepts
--------

Sometimes, it can be tricky to decide if two closely resembling entites should be modelled as distinct :instance:`concept`\s,
or simply should be considered different :instance:`release`\s of the same concept.
Ideally, a ``Concept`` should be the idea of something being *conceived* once by a design/development team.
Ultimately, this is the collecter's call to make this decisions, but here are some propositions to help making the call:

* For **Games**:
  A game, independently of the platform it is released onto, is a single concept
  *as long as it is just a port between the different platforms*.
  When it is obviously a rewrite despite sharing the same, it is a different concept (like Sonic The Hedgehog 8bit).
  Usually a practical criterion to decide can be "is it on the same wikipedia page" ;)
  When there are versions (as in patches of the original game, 1.1 and 1.2, etc... ), they are the same Concept,
  but this version number is a Release field.

* For **Demo** medias:
  The concept is the name of the "serie" (eg. *Sega Flash*) independently of its iteration.
  Iterations make different :instance:`release`\s of the same demo :instance:`concept`,
  iteration number being a ``Release`` field.
  
* For **Systems**:
  The concept would be a base system, indepently of its variants 
  (i.e., Master System is the :instance:`concept` of which both MSI and MSII (and SEGA mark III) would be releases.
  It seems closer to the mental model (when looking for a Master System, the variant is secondary).
  It also gets closer to the image of a concept as something "conceived" once:
  in the SMS example, the architecture of the Master System, and its realisation as a PCB with chips,
  are mostly shared by all non-SoC releases of the SMS.
  This way, different constructor can indeed manufacture release of the same concept (by licensing the design). 

.. note::
   Console-on-chip versions should still be recorded as a distinct :instance:`concept`: it is diverging at the
   hardware design level, and is also probably different in a collector's mental model.
   It is even a **different nature**.

* For **Accessories**:

  * On a game pad, differing number of buttons, different features (eg. analog stick), and wired/wireless variations
    should make different :instance:`concept`\s. (as those information is recorded as ``Concept`` level *specific*).
  * Some accessories are released for different consoles, with little to no change appart from the connection interface
    (eg. Activision guitars were released on PC, XBox, Wii, ...). They should be considere the same :instance:`concept`.
  * When a memory card/memory extension of the same model exist in different sizes,
    they are different :instance:`release` of the same :instance:`concept`. The capacity is a ``Release`` specific.

Additional modules
==================

.. _system_variants:

Variants
--------

As the different versions and revisions of a given system (eg. Mega Drive I, Mega Drive II) are attached to the same
:instance:`Concept`, the application needs another model to record this information.
The **variants** system addresses this need, inspired by the **variants** entry found on `segaretro <http://segaretro.org/Sega_Mark_III>`_.

.. autoclass:: SystemVariant


Defect
------

The **Defect** module provides a way to document defects on entities, or any of they attribute.
It is a very simple module:
a list of text fields can optionally be attached to any :instance:`attribute` of the :instance:`occurrence`.
Each such text field can be used to record a discrete defect of the related :instance:`attribute`.

It is a better alternative than directly documenting defects in the notes, as it provides better structure and specificity.

.. note::
   The *edit defects* links are available in the ``Occurrence`` form, inside each inline attribute form.
   It only appears once the :instance:`occurrence` has been saved.


Platform
--------

There is a quite detailed platform and compatiblity management system, added as a module to **advideogame**.

It tries to generalize the approach for all collectible entities (i.e. systems, peripherals and software)
by seing any of them as providing [0..n] interfaces, and requiring [0..m] interfaces.

It also provides a framework for recording the regional lockouts imposed by some constructors.

A ``SystemSpecification`` is refered from ``Release``/s. It will be shared by all :instance:`release`/s with the same
specifications, making updates easier.

A ``SystemSpecification`` allows to list *advertised systems* through ``InterfaceSpecification``.
Each *advertised system* can then be attached lists of *provided* and *required* interfaces, through ``SystemInterfaceDetail``.
Such interface is the pairing of a ``BaseSystem`` with a *media* name (eg. CD-ROM, cartrdige, controller, ...),
in a ``SystemMediaPair`` instance.
Additionally, it is possible to attach some interface(s) to **all** *advertised system* using the ``CommonInterfaceDetail`` 
instance attached to the ``InterfaceSpecification``.

.. note::
   In an ``InterfaceSpecification``, it becomes possible to edit the list of *provided* and *required* interfaces 
   attached to the *advertised system*\s only **after** the :instance:`interface specification` has been saved.

   Saving it makes an *edit interface* link appear in front of each *advertised system*. 

Usage recommendations
^^^^^^^^^^^^^^^^^^^^^

* Inside an ``InterfaceSpecification``, there should be a single *provided* interface corresponding to a physical interface
  of the corresponding entity.

  * In case the same ``SystemMediaPair`` is provided by different *advertised system*\s, this interface should not appear
    in each *advertised system* providing it, but only once in the ``CommonInterfaceDetail`` attached to the ``InterfaceSpecification``.
    (eg. With PS3 able to play PS1 games, the PS3 pad interface can be used with both *advertised system*\s).
  
  * On the other hand, if the same physical interface is used as different ``SystemMediaPair``\s by different *advertised system*\s,
    then in the additional *advertised system*\s the provided interface corresponding to the same physical interface 
    should be makred with a *reused interface* to the cannonical interface.
    (eg. Some Wii can also be used to play GameCube games, reusing the same disc interface)

  It is possible to mark as *reused interface* an interface that is not provided in the current ``InterfaceSpecification``.
  (eg. the Sega Saturn ST-Key is providing an zone-free Saturn Disc interface, by reusing the originally region-locked one)

Advertised system(s)
^^^^^^^^^^^^^^^^^^^^

An *advertised system* is thus attached a list of interfaces through ``SystemInterfaceDetail``.
It should be noted that the ``BaseSystem`` in those interfaces does not need to match the *advertised system* they are part of.

This nuance can come in handy in some situations.  For example when a system N provides controller retrocompatibility 
with controllers of system M while allowing to use them with game of system N: the *advertised system* is system N,
but one of its interfaces will be controller ports of system M.

The rule of thumb to determine the *advertised system*\s is quite natural. 

* For **systems**, it would be the different software platforms it implements.
* For **software**, it would be the ``BaseSystem``\s it is compatible with. In particular, if a software is compatible
  with several platforms, they would be listed as distinct *advertised system*\s.
* For **accessories**, it would be the **host** system(s) it connects to. In particular for adapters, the *advertised system*\s
  would not be the adapted system(s), but the system(s) it is adapted for.

Bundles
-------

The **bundles system** is a satellite part of **advideogame**, allowing to optionally record different information
regarding the acquisition of collected entities:

* Donation (and Donator) or Purchase
* Date
* Location and Context
* How the bundle was retrieved
* List of entities acquired together (hence **bundle**)
* Bundle price and shippint cost

There are two top level models ``Donation`` and ``Purchase`` (both deriving from ``Bundle``), which are the entry
points for users to record those information.

In particular, ``Purchase`` specifies a ``PurchaseContext``

.. autoclass:: PurchaseContext
   :members: category, name, url, location, address_complement
