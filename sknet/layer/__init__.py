#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tensorflow as tf

from .. import Tensor

class Layer(Tensor):
    """Layer class used as parent of any implemented layer.

    :py:class:`sknet` relies extremely heavily on the :py:class:`sknet.layer`
    modules. The layers store the computations, the losses, the penalties,
    and everything that might be needed for deep learning applications. 
    As such, understanding the parent class :py:class:`sknet.layer.Layer`
    from which all the layers inherit is crucial.

    .. rubric:: Layers are tensors

    The :py:class:`sknet.layer.Layer` class inherits from 
    :py:class:`sknet.ObservedTensor` for two reasons. First, it
    allows the layer to be treater as a tensor in the computational
    graph and thus to be used as a standard variable for computation, such
    as ::

        # Set some arbitrary layer given some previous_layer
        some_layer = sknet.layer.Dense(previous,units = 20)
        # the variable some_layer is a Layer, treated as a
        # standard tf.Tensor and thus can be used as a variable
        some_stats = tf.reduce_sum(some_layer/0.1+4,0)

    this allows great flexibility in the code as well as for customized
    computations without requiring to access to some attribute or method
    from the instanciated layer.

    .. rubric:: Layer variables and variable functions:

    All the variables of a layer (let say :py:data:`W` and :py:data:`b` 
    for example) are access via ``layer_instance._W`` and 
    ``layer_instance._b``.  While those are the variables of the layer (given
    at initialization of created), the ones used for the forward computation
    are ``layer_instance.W`` and ``layer_instance.b``. In fact, those are the
    ones that have the (optional) weight function applied onto them. For
    example, ``layer_instance.W=W_func(layer_instance._W)``. In fact, one can
    pass any arbitrary function to be applied onto any of the variables of the
    layer, the only requirements is that the induces parameter has the required
    shape for the forward pass. For example, if one simply wants to impose
    nonnegative weights for the slope of a :py:class:`sknet.layer.Dense` 
    layer ::
    
        layer = sknet.layer.Dense(previous_layer,units=20, W_func=tf.nn.relu) 
        
    or with a more conventional case of imposing unit
    norm (exact, not as a penalty) to the weights ::

        # define the function to be applied onto the weights to have unit norm
        renorm_func = lambda W:W/tf.sqrt(tf.reduce_sum(tf.square(W)))
        layer = sknet.layer.Dense(previous_layer,units=20,W_func=renorm_func)

    .. rubric:: Variables initialization:

    The _variables are initialized by the layer based on the values given
    for :py:data:`W` and :py:data:`b` during initialization or created is
    none is passed. In ALL cases, if
    the passed argument is an actual variable with values, s.a. a 
    :py:class:`np.ndarray`, a :py:class:`tf.Tensor` etc, then it is considered
    as a given value and not an initialization to the learnable parameter. If a
    function is given, then the constructor calls it with the shape of the
    parameter in question as input to obtain an actual initial value for the
    learnable parameter. This makes it easy to set a parameter learnable or not
    as for example::

        # Random normal (gaussian) initialization, learnable weights,
        # the layer W will be turned into a trainable tf.Variable
        sknet.layer.Dense(previous_layer,units=10,W=tf.random_normal)
        # Random normal weights that won't be learned, the passed value
        # is used as the actual parameter without any transformation
        sknet.layer.Dense(previous_layer,units=10,W=tf.random_normal((764,10)))
        # this allow to use the following case where one pre-determines a 
        # special form for the weights, and thus do not want this to be used
        # just as an initializer of a tf.Variable, but the actual weights to
        # be used by the layer
        W1 = tf.Variable(tf.random_normal((764,10))
        W2 = tf.Variable(tf.random_normal((764,10))
        layer = sknet.layer.Dense(previous_layer,units=10,W=W1*W2)

    Note that if the input shape of the layer is unknown, one can retreive it 
    via ``previous_layer.shape``. This also allows to use a 
    :py:class:`sknet.ObservedVariable` as a layer variable, allowing to set
    manually some values of the variable values hwen desired. For example::

        # set some weights that won't be learned
        fixed_W = tf.random_normal((764,10))
        # set the standard learnable weights
        learnable_W = tf.Variable(tf.random_normal((764,10)))
        # create the W variables used by the layer as an ObservedTensor
        W = sknet.ObservedTensor(learnable_W,observed=True,observation=fixed_W)
        # create the layer
        layer = sknet.layer.Dense(previous_layer,units=10,W=W)
        # this layer will thus either use the (possibly learned) value from
        # learnable_W or the fixed (random but not learned) value from fixed_W
        # depending on the value feed to W.teacher_forcing

    .. rubric:: Loss and penalties

    In sknet, the losses and penalties are part of the layers. Each layer can
    be equipped with any loss or penalty (which can involve the layer
    parameters or any other). A typical example would be to apply a
    Tikhonov regularization to the weights of the layer as ::

        # first the layer is instanciated
        layer = sknet.layer.Dense(previous_layer,units=10)
        # we now add a loss to the W parameters
        layer.add_loss(sknet.loss.l2(layer.W))

    recall that this applies the loss onto ``layer.W`` which might be a
    transformation of the true parameter ``layer._W``, this during
    learning the applied functional will matter in the gradient computation.
    Another important case is the one of the network loss often seen as a 
    global loss, s.a. the classification loss. In this case one would do ::

        # first the layer is instanciated
        layer = sknet.layer.Dense(previous_layer,units=10)
        # we now add a loss to the W parameters
        layer.add_loss(sknet.loss.cross_entropy(p=None,q=layer))

    recall that :py:data:`layer` which is a layer also behaves as a tensor 
    and thus can be used directly as the term to be used for hte loss
    computation. In this case, we did not create a target variable for the
    :py:data:`p` distribution and thus set it to :py:data:`None` to allow
    the loss to create it itself. For training, one would have to
    feed the true labels for ``layer.cross_entropy.p`` since it is now
    a placeholder.


    Parameters
    ----------

    input : tf.Tensor or tf.Layer
        the input to the layer, can eb any arbitrary variable or layer instance
        this allows the user to feed directly a tensorflow variable as input

    """
    def __init__(self,input, deterministic=None, **kwargs):
        
        # Link this tensor to its input
        self._input = input

        # set data_format
        if isinstance(input,Layer):
            self._data_format = input.data_format
        else:
            self._data_format = kwargs["data_format"]

        # set deterministic
        if deterministic is None:
            self._deterministic = tf.Variable(np.float32(0),name='deterministic',trainable=False)
            # create the operation to change the state of self.deterministic
            # this is done only if deterministic was not passed to avoid
            # uncontrollable behavior for example if a single variable is used
            # for all the layers
            self._set_deterministic     = tf.assign(self._deterministic,np.float32(1))
            self._set_not_deterministic = tf.assign(self._deterministic,np.float32(0))
        else:
            self._deterministic = deterministic

        # compute the layer output based on the layer forward method
        output = self.forward(input,self.deterministic)

        # Set the per layer penalty list to empty
        self.losses = []

        # initialize the variable
        super().__init__(output)

    def set_deterministic(self,value, session=None):
        if not hasattr(self,'_set_deterministic'):
            warnings.warn("deterministic not change, should be done manually")
            return
        if session is None:
            session = tf.get_default_session()
        if value:
            session.run(self._set_deterministic)
        else:
            session.run(self._set_not_deterministic)

    def add_loss(self,loss):
        number = 0
        while loss.name+str(number) in self.__dict__:
            number +=1
        self.__dict__[loss.name+str(number)] = loss
        print(loss.name+str(number))
        self.losses.append(loss)

    @property
    def _variables(self):
        """Return a summary of the layer variables as a dictionnary as 
        for example ``{'W':observed_variable_W.'b':observed_variable_b}``
        """
        return self._variables

    @property
    def deterministic(self):
        return tf.cast(self._deterministic,tf.bool)

    @property
    def data_format(self):
        return self._data_format

    @property
    def input(self):
        return self._input

from . import *
from .pool import *
from .perturb import *
from .normalize import *
from .conv import *
from .dense import *
from .shape import *
from .io import *
from .special import *
#from .meta import *
