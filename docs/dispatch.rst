Dispatching
===========

Dispatching in ``tinyrpc`` is very similiar to url-routing in web frameworks.
Functions are registered with a specific name and made public, i.e. callable,
to remote clients.

Examples
--------

Exposing a few functions:
~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from tinyrpc.dispatch import RPCDispatcher

   dispatch = RPCDispatcher()

   @dispatch.public
   def foo():
       # ...

   @dispatch.public
   def bar(arg):
       # ...

   # later on, assuming we know we want to call foo(*args, **kwargs):

   f = dispatch.get_method('foo')
   f(*args, **kwargs)

Using prefixes and instance registration:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   from tinyrpc.dispatch import public

   class SomeWebsite(object):
       def __init__(self, ...):
           # note: this method will not be exposed

       def secret(self):
           # another unexposed method

       @public
       def get_user_info(self, user):
           # ...

       # using a different name
       @public('get_user_comment')
       def get_comment(self, comment_id):
           # ...

The code above declares an RPC interface for ``SomeWebsite`` objects,
consisting of two visible methods: ``get_user_info(user)`` and
``get_user_comment(commend_id)``.

These can be used with a dispatcher now:

.. code-block:: python

   def hello():
       # ...

   website1 = SomeWebsite(...)
   website2 = SomeWebsite(...)

   from tinyrpc.dispatch import RPCDispatcher

   dispatcher = RPCDispatcher()

   # directly register version method
   @dispatcher.public
   def version():
       # ...

   # add earlier defined method
   dispatcher.add_method(hello)

   # register the two website instances
   dispatcher.register_instance(website1, 'sitea.')
   dispatcher.register_instance(website2, 'siteb.')

In the example above, the :py:class:`~tinyrpc.dispatch.RPCDispatcher` now knows
a total of six registered methods: ``version``, ``hello``,
``sitea.get_user_info``, ``sitea.get_user_comment``, ``siteb.get_user_info``,
``siteb.get_user_comment``.

Automatic dispatching
~~~~~~~~~~~~~~~~~~~~~

When writing a server application, a higher level dispatching method is
available with :py:func:`~tinyrpc.dispatch.RPCDispatcher.dispatch`:

.. code-block:: python

   from tinyrpc.dispatch import RPCDispatcher

   dispatcher = RPCDispatcher()

   # register methods like in the examples above
   # ...
   # now assumes that a valid RPCRequest has been obtained, as `request`

   response = dispatcher.dispatch(request)

   # response can be directly processed back to the client, all Exceptions have
   # been handled already


API reference
-------------

.. autoclass:: tinyrpc.dispatch.RPCDispatcher
   :members:

Classes can be made to support an RPC interface without coupling it to a
dispatcher using a decorator:

.. autofunction:: tinyrpc.dispatch.public
