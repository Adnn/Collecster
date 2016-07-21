.. role:: instance(emphasis)

============
Introduction
============

************
Presentation
************

Collecster is a `Django <https://www.djangoproject.com/>`_ web application intended for managing, organizing and inventoring collections.

Even though it was born out of the need to manage a video game collection, Collester's aim is to propose a generic model that can be adapted to different collections: it is probably a good fit for collections of most sort of concrete commercial products.

It is customized on a per-deployment basis to fit the specific requirements of the collection(s) it will handle, based on the collection topic, its scope, and the effort invested by the collector. Several collections can be managed on the same server.


Who should read this ?
======================

Because of the intented genericity and configuratibility of Collecster, its is possible to see 3 different roles emerge:

* **user**: The collector is a user of the system: it is given credentials to access the web application through which it manages its collection.
  He does not require technical knowledge regarding the internals of the application to use it.
* **deployer**: The deployer is the person that configures collecster, tailoring it for the needs of a specific collection.
  Configuration is done through `Python <https://www.python.org/>`_ scripts, where settings value can be set and custom models declared.
  He requires some detailed knowledge of the technical settings available, and how to define Django models if he needs to create new ones.
* **developer**: He is a software developer willing to help ;)

This page is a recommanded read for everyone. More specialized pages then address the needs of specific roles.

********
Overview
********

This section will give an overview of the notions on which Collecster is built. It should be a usefull read, whichever of the roles defined above you intend to play.


.. _three_base_models:

The 3 central notions
=====================

The **generic model** is realized through 3 hierarchized classes, which are its most essential concepts:

#. ``Concept``: the top level notion, it is intended as an umbrella to allow grouping of releases. It can be seen as a ''Production'', or ''Master Record'' in certain industries: several distinct releases could be issued from this single concept, yet all those releases have are logically grouped in the eyes of the collector.
#. ``Release``: a release is the realization of a given concept, by a given editor. (in a given packaging with a given content, in a given language, etc...) It can be seen as the blueprint used to produce a batch of goods, mostly indistinguishable from one another (Note: the physical goods themselve being the occurrences defined below). There is potentially different releases corresponding to what is perceived as "the same collectible": they should be grouped under the same ''concept''.
#. ``Occurrence`` : an occurrence is the physical artifact you own in your collection. Each occurrence corresponds to a single release, but several occurrences can correspond to the same release (the ''goods'' produced in a same batch as evoked above are several occurrences of a given release).

Each collected objects thus correspond to a separate :instance:`occurrence` in the application.
Each :instance:`occurrence` **materializes** a :instance:`release` which **realizes** a :instance:`concept`.

Other notions
=============

* ``Configuration``: A specialization of Collecster for a specific type of collection, with its own rules.
* ``Field``: A field is the atomic data-entry point. It corresponds to the storage for a single value.
* ``Form``: A page presenting several fields for the user input. A form is the primary interface to add or edit an object in the database.
* ``Nature``: One (or several) nature(s) are associated with a :instance:`concept`. They define its ''type''. (eg: "Music album", "Control pad", ...)
* ``Distinction``: Mechanism to add values with specific meanings to a given release, effectively emulating user-controlled fields. The list of possible meanings is controlled at runtime.
* ``Specific``: A specific is an extra group of fields that can be attached to a :instance:`concept`, a :instance:`release` or an :instance:`occurrence`.
  The list of attached :instance:`specific`\s depends on the :instance:`nature`\(s) of the corresponding :instance:`concept`.
* ``Attribute``:  Attributes are attached by the user to a :instance:`release`. All :instance:`occurrence`\s materializing this :instance:`release` will need to provide values for those attributes.
* ``Composition``: A :instance:`release` can optionally be composed of other :instance:`release`\(s).  All :instance:`occurrence`\s materializing this :instance:`release` will have the opportunity to be composed by :instance:`occurrence`\s materializing the appropriate :instance:`release`\s.
* ``Immaterial``: Is a boolean property of :instance:`release`\s, dictating whether the :instance:`occurrence`\s materializing them are ''material'' or ''virtual''. Some ``Release`` and ``Occurrence`` fields are only available for ''material'' :instance:`release`\s
.. _tag_glossary:
* ``Tag``: A special kind of document that can be generated for each material :instance:`occurrence` in a collection. 
  It is intended to be printed and attached to the physical occurrence, to provide some information plus
  a way to match the object against the logic :instance:`occurrence` in the DB.

********
Features
********

* **A friendly and guided top-down approach**: To add a new :instance:`occurrence` to the collection, the corresponding :instance:`concept` is first created (or retrieved if it exists). The :instance:`concept` will adapt the form for the :instance:`release`, that is created next. Finally, the :instance:`occurrence`\'s form is influenced by both previous elements.

  * **Dynamic list of fields**: A power-tool is not best described using the same fields than for a handtool.
    For this reason, the nature(s) of a :instance:`concept` controls which fields are available on the different forms 
    (This is implemented by :ref:`mapping specific to natures <specific_mapping>`.)
  * **Releases are templates for Occurrences**: A :instance:`release` can be seen as a template driving the creation of all :instance:`occurrence` materializing it. Both the ``Attribute`` and  ``Composition`` that are filled-in on a :instance:`release` will automatically create corresponding fields on all :instance:`occurrence`\s of this :instance:`release`: they cascades down from the :instance:`release` to all :instance:`occurrence`\s materializing it.

    If you have an object-oriented programming background, you can map the ``Release`` notion to **class**, and the ``Occurrence`` notion to **instance**.

* **Allows entries to have multiple Natures**

* **Configurability & Extensibility**: The system is designed to allow creation of new configuration, either by extension/edition of an existing one,
  or by writing the configuration for a new type of collection from scratch.
  It is possible to make small modifications to the model easily : adding a field is most of the time simply adding one line of code.
  Bigger changes are also permitted, allowing to configure Collecster for your custom collection.
  Extensiblity means you can easily add more models than the basic "concept/release/occurrence" trinity: 
  as an example, :ref:`advideogame_user` provides additional models to store information 
  regarding systems' compatibility, acquisitions, system variants, etc. 

  * **Customizable required/forbidden fields**

* **Data consistency with clear errors**: The rules implemented by a collection configuration are enforced before entries are created in the database.
  When a situation is inconsistent with the rules, the user is presented with the data he entered ready for edition, accompanined with clear indications regarding which data is not allowed.
  An optional offline tool allows to ensure the global consistency of the entries, crawling all of them, offering additional peace of mind.
