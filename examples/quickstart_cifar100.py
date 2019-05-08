import sys
sys.path.insert(0, "../")

import sknet
import matplotlib
matplotlib.use('Agg')
import os

# Make Tensorflow quiet.
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

import numpy as np
import pylab as pl
import time
import tensorflow as tf
from sknet.dataset import BatchIterator
from sknet import ops,layers



from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt

# Data Loading
#-------------
dataset = sknet.dataset.load_cifar10()
dataset.split_set("train_set","valid_set",0.15)

standardize = sknet.dataset.Standardize().fit(dataset['images/train_set'])
dataset['images/train_set'] = \
                        standardize.transform(dataset['images/train_set'])
dataset['images/test_set'] = \
                        standardize.transform(dataset['images/test_set'])
dataset['images/valid_set'] = \
                        standardize.transform(dataset['images/valid_set'])

dataset.create_placeholders(batch_size=32,
        iterators_dict={'train_set':BatchIterator("random_see_all"),
                        'valid_set':BatchIterator('continuous'),
                        'test_set':BatchIterator('continuous')},device="/cpu:0")

# Create Network
#---------------

# we use a batch_size of 64 and use the dataset.datum shape to
# obtain the shape of 1 observation and create the input shape

dnn       = sknet.network.Network(name='simple_model')

dnn.append(ops.RandomAxisReverse(dataset.images,axis=[-1]))
dnn.append(ops.RandomCrop(dnn[-1],(28,28),seed=10))
dnn.append(ops.GaussianNoise(dnn[-1],noise_type='additive',sigma=0.01))

sknet.network.ConvLarge(dnn,dataset.n_classes)
prediction = dnn[-1]

loss    = sknet.losses.crossentropy_logits(p=dataset.labels,q=prediction)
accu    = sknet.losses.accuracy(dataset.labels,prediction)

B         = dataset.N('train_set')//32
lr        = sknet.schedules.PiecewiseConstant(0.01,
                                    {100*B:0.002,200*B:0.001,250*B:0.0005})
optimizer = sknet.optimizers.Adam(loss,lr,params=dnn.variables(trainable=True))
minimizer = tf.group(optimizer.updates+dnn.updates)

# Workers
#---------

min1  = sknet.Worker(name='minimizer',context='train_set',op=[minimizer,loss],
        deterministic=False, period=[1,100])

accu1 = sknet.Worker(name='accu',context='test_set', op=accu,
        deterministic=True, transform_function=np.mean,verbose=1)

queue = sknet.Queue((min1,accu1))

# Pipeline
#---------
workplace = sknet.utils.Workplace(dnn,dataset=dataset)
workplace.execute_queue(queue,repeat=350)



#sknet.to_file(output,'test.h5','w')



