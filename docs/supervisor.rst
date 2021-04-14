.. role:: instance(emphasis)

======================
supervisor application
======================

********
Features
********

The supervisor special application is responsible for managing the different :instance:`configuration`\s that are deployed on the server (through Deployment_).
It also knows about all the users, and which collections they have access to (through UserCollection_).

Another feature of the **supervisor** is providing an indirection layer between the application Occurrence stored in the database of a specific deployement, and the logic occurrence owned by a user.
This makes it is possible to migrate :instance:`occurrence`\s to another Django installation which deploys the corresponding application.
This migration happens without changing the user's occurrences' **logic** id, whereas the :instance:`occurrence` id in the database could require a modification
(for example: if the current :instance:`occurrence` id is already used by another :instance:`occurrence` in the destination deployment).
This immutability of the logic id is essential as this value is made available outside of the system, where the system cannot update its value: eg. printed on a tag.


******
Models
******

.. py:module:: supervisor.models

Deployment
==========

.. autoclass:: Deployment

UserCollection
==============

.. autoclass:: UserCollection

Person
======

.. autoclass:: Person


UserExtension
=============

.. autoclass:: UserExtension


*************
Use scenarios
*************

.. _tag_to_occurrence:

Tag to occurrence
=================

On a tag, the following information are made available in the QR code (and potentially as human readable text):

* user_collec_id
* objecttype_id
* user_guid (important: the creating user, not necessarily the owner)
* user_occurrence_id.

#. This allows to find the :instance:`UserCollection` from ``user_guid`` and and ``user_collection_id``
#. The :instance:`UserCollection` directly gives the :instance:`Deployment`, which in turn directly gives the **application** corresponding to this :instance:`Deployment`.
#. Once the application is known, it is possible to query its ``TagToOccurrence`` model:
   from the ``user_guid`` and the ``user_occurrence_id``, find the :instance:`occurrence` on the local installation.

Adding a user
=============

Add a :instance:`userextension`, which requires a :instance:`user` and a :instance:`person`, while assigning a ``guid``.

Give the :instance:`user` access to some collections by creating :instance:`usercollection` insances.

.. note::
   This is a description of the low-level operations of user management. They should never be conducted directly, but through
   :ref:`users_management` commands.

Collections migration
=====================

.. warning::
   Since a given user ``guid`` should be active on a single Django installation at a time, and migrating :instance:`occurrence`\s requires
   to use their creators ``guid`` on the destination installation, all :instance:`occurrence`\s of the corresponding creator must be migrated
   at once ! (so the creator is removed from the source installation)


Migrating :instance:`occurrence`\s from an installation to another has to be conducted without touching the fields printed on the tag,
listed in :ref:`tag_to_occurrence`.

First thing is that the destination installation should have a :instance:`deployment` for the configuration corresponding
to the migrated :instance:`occurrence`\s.

#. Add a :instance:`userextension` corresponding to the creator of the :instance:`occurrence`, thus taking the same user GUID.
#. Add a :instance:`usercollection` associating the original ``user_collection_id`` and the :instance:`userextension` from previous step
   to the local deployment of the corresponding collection.
#. The :instance:`occurrence` (and all the instances related to it) should be created in the destination installation.
   This is likely to change the primary key assigned to the :instance:`occurrence`.
#. A :instance:`tagtooccurrence` entry is created in the destination,
   associating the 'new' ``occurrence_pk``, to the original ``user_creator`` and ``user_occurrence_id``.


