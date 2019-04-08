#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import tensorflow as tf

class constant:
    """constant learning rate.
    This case is the most basic learning rate update policy
    agnostic of the current epoch and the current performances.
    Unless used with an optimizer with internal gradient normalization
    such as Adam, a constant learning is in general sub-optimal.
    For convex optimization problems, convergence is only guaranteed
    with a decaying learning rate.
    """
    def __init__(self,lr):
        """Initialize the class with a learning rate

        :param lr: learning rate to use
        :type lr: scalar
        """
        self.lr   = lr
        self.name = '-schedule(constant,lr='+str(init_lr)+')'
    def reset(self):
        """Reset the list of learning rates"""
        self.lrs = [self.lr]
    def update(self,valid_accu,epoch,**kwargs):
        """Update the value of the learning rate, in this case, 
        stay the same"""
        if kwargs['epoch']==0:
            self.reset()
        self.lrs.append(self.lr)

class linear:
    """Linearly changing learning rate.
    This method allows to linearly change the learning rate
    initialized as :math:`lr`.
    It is done by using a given scalar :math:`s` when calling the
    :py:func:`update` method and setting the new learning rate
    to be :math:`lr-s*\kappa` with :math:`\kappa` a step given
    at initialization.
    """
    def __init__(self,lr,step):
        """Initialize the class with a learning rate and the step,
        uses the epoch as the step multiplier

        :param lr: initial learning rate
        :type lr: scalar
        :param step: step to linearly reduce lr
        :type step: scalar
        """
        assert(np.isscalar(lr) and np.isscalar(step))
        self.step = step
        self.lr   = lr
        self.name = '-schedule(linear,lr='+str(init_lr)\
                    +',step='+str(step)+')'
    def reset(self):
        """Reset the class
        """
        self.lrs = [self.lr]
    def update(self,**kwargs):
        if kwargs['epoch']==0:
            self.reset()
        self.lrs.append(self.lr-epoch*kwargs['epoch'])


class exponential:
    """exponential decay of the learning rate.
    This method allows to exponentially change the learning rate
    initialized as :math:`lr`.
    It is done by using a given scalar :math:`s` when calling the
    :py:func:`update` method and setting the new learning rate
    to be :math:`lr-\kappa^s` with :math:`\kappa` a step given
    at initialization.
    """
    def __init__(self,init_lr,step):
        assert(np.isscalar(lr) and npisscalar(step))
        self.step = step
        self.lr   = lr
        self.name = '-schedule(exponential,lr='+str(init_lr)\
                +',step='+str(step)+')'
    def reset(self):
        """reset the class"""
        self.lrs = [self.lr]
    def update(self,**kwargs):
        if kwargs['epoch']==0:
            self.reset()
        self.lrs.append(self.lr-self.step**kwargs['epoch'])


class stepwise:
    """stepwise learning rate strategy.
    This method allows to have stepwise learning rate
    It is done by using a given dictionnary containing the epochs
    at which the learning rate changes (starting at 0).
    
    Example of use::

        stepwise({0:0.1,50:0.01,100:0.0005})


    """
    def __init__(self,dict_lr):
        """initialize the class

        :param lr:dictionnary mapping epoch with learning 
                  rate change -> new learning rate
        :type lr: dict
        """
        self.dict_lr = dict_lr
        # get epoch and values
        epochs = np.asarray(list(dict_lr.keys())).astype('int32')
        values = np.asarray(list(dict_lr.values())).astype('float32')
        # sort them
        arg = np.argsort(epochs)
        print(arg,epochs,values)
        epochs=epochs[arg]
        values=values[arg]
        # set up tf variables
        self.epochs = [tf.constant(e) for e in epochs]
        self.values = [tf.constant(v) for v in values]

    def __call__(self,epoch,*args,**kwargs):
        
        epoch = tf.cast(epoch,tf.int32)
        pairs =[(tf.logical_and(tf.greater_equal(epoch,e),tf.less(epoch,ep)),lambda :v) 
            for e,ep,v in zip(self.epochs[:-1],self.epochs[1:],self.values[:-1])]

        lr = tf.case(pairs,default=lambda :self.values[-1], exclusive=True, strict=False, 
                                    name='case_learningrate')
        return lr
        self.lr   = dict_lr
        self.reset()
        self.name = '-schedule(stepwise,dict='+str(dict_lr).replace(' ','')+')'
    def reset(self):
        """Reset the class
        """
        self.lrs = [self.lr[0]]
    def update(self,**kwargs):
        if kwargs['epoch']==0:
            self.reset()
        if 'epoch' in self.lr.keys():
            self.lrs.append(self.lr[epoch])
        else:
            self.lrs.append(self.lrs[-1])



class adaptive:
    """adaptive learning rate strategy.
    This method allows to have an adaptive learning rate
    with behavior depending on a given metric performance.
    if the performance stagnates from more than patience iterations
    then the learning rate is transformed (linearly or exponentiall)
    by mean of a step parameter
    """
    def __init__(self,lr,step, decay_type = 'exponential', patience = 5,
            metric_name='valid_accuracy', lookback=10):
        """Initialize the class
        :param lr: learning rate initialization
        :type lr: scalar
        :param step: step to be applied to the learning rate when needed either linearly or exponentially
        :type step: scalar
        :param decay_type: the type of decay to apply
        :type decay_type: str, 'exponential' or 'linear'
        :param patience: the minimum number of iteration to wait
        :type patience: int
        :param metric_name:name of the metric to use for adaptive 
                           learning rate, must be given when calling
                           :py:func:`update`.
        :type metric_name: str, (default 'valid_accuracy') 
        :param lookback:how many of the previous iterations to take 
                        into consideration when checking if learning 
                        needs to be adapted
        :type lookback: int
        """
        self.step       = step
        self.lr         = lr
        self.decay_type = decay_type
        self.patience   = patience
        self.name       = '-schedule(adaptive,lr='+str(init_lr)\
                    +',step='+str(step)+',type='+decay_type+')'
        self.metric_name= metric_name
        self.lookback   = lookback
    def reset(self):
        """Reset the class
        """
        self.lrs = [self.lr]
        self._patience = 0
    def update(self,**kwargs):
        if kwargs['epoch']==0:
            self.reset()
        if _adaptive(kwargs[self.metric_name],self.lookback) and self._patience>self.patience:
            if self.decay_type=='exponential':
                self.lrs.append(self.lrs[-1]*self.step)
            else:
                self.lrs.append(self.lrs[-1]-self.step)
            self._patience = 0
        else:
            self._patience+= 1
            self.lrs.append(self.lrs[-1])



def _adaptive(metric,lookback=5):
    """
    Reduce learning rate when a metric has stopped improving. 
    Models often benefit from reducing the learning rate by a 
    factor of 2-10 once learning stagnates. This scheduler reads 
    a metrics quantity and if no improvement is seen for a ‘patience’ 
    number of epochs, the learning rate is reduced.
    """
    if len(metric)<lookback:
        return False
    if np.min(metric[-lookback:-1])<metric[-1]:
        return True
    return False

