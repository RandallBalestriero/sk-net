import sknet
from sknet.optimize import loss
import matplotlib
matplotlib.use('Agg')
import os

# Make Tensorflow quiet.
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '5'

import numpy as np
import pylab as pl
import time
import tensorflow as tf



# Data Loading
#-------------

dataset = sknet.dataset.load_mini()
dataset.split_set("train_set","test_set",0.25)
dataset.split_set("train_set","valid_set",0.1)

# Create Network
#---------------

# we use a batch_size of 64 and use the dataset.datum shape to
# obtain the shape of 1 observation and create the input shape
input_shape = [64]+list(dataset.datum_shape)


# to create the first layer, one could use the following
# layers = [sknet.layer.Input(input_shape=input_shape,
#            data_format=dataset.data_format, input=None)]
# which explicitly specifies all the variables, or use:
layers = [sknet.layer.Input(batch_size=64,dataset=dataset, input=None)]
layers.append(sknet.layer.Dense(layers[-1],units=450))
layers.append(sknet.layer.Activation(layers[-1],0))
layers.append(sknet.layer.Dense(layers[-1],units=300))
layers.append(sknet.layer.Activation(layers[-1],0))
layers.append(sknet.layer.Dense(layers[-1],units=4))

network = sknet.network.Network(layers,name='-model(cnn.base)',dataset = dataset)

# Loss and Optimizer
#-------------------

# Compute some quantities that we want to keep track and/or act upon
entropy_loss  = loss.crossentropy_logits(p=None,q=network[-1])
sparsity_loss = loss.l2_norm(network[1].W)
loss          = entropy_loss+sparsity_loss*0.000001

# accuracy = sknet.optimize.loss.accuracy(labels=entropy_loss.labels,prediction=network[-1])
accuracy = sknet.optimize.loss.accuracy(labels=None,predictions=network[-1])

# we only need one minimize in this case, applied on the training_loss
update_op = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
optimizer = sknet.optimize.optimizer.Adam(schedule = sknet.optimize.schedule.stepwise({0:0.01,5000:0.001,100000:0.0001}))
with tf.control_dependencies(update_op):
    minimizer = optimizer.minimize(loss)



# Pipeline
#---------


pipeline = sknet.utils.Pipeline(network,dataset=dataset,
                        linkage={network[0].name:"images",
                        entropy_loss.p.name:"labels",
                        accuracy.labels.name:"labels"})

# to use the pipeline.fit method, one should feed a
# op descriptor for each case of dataset.sets
# in this case, it is just the train, test and valid set



work1 = sknet.Worker(name='minimizer',context='train_set',op=minimizer, 
        instruction='execute every batch', deterministic=False)

work2 = sknet.Worker(name='loss',context='train_set',op=loss,
        instruction='save & print every 300 batch', deterministic=True)

work3 = sknet.Worker(name='test accuracy',context='test_set',op=accuracy,
        instruction='execute every batch and save & print & average', deterministic=True)

work4 = sknet.Worker(name='valid accuracy',context='valid_set',op=accuracy,
        instruction='execute every batch and save & print & average', deterministic=True)


pool_training = sknet.WorkerPool([work1,work2],name='training')


# will fit the model for 50 epochs and return the gathered op
# outputs given the above definitions
outputs = pipeline.execute_queue((pool_training,work3,work4),repeat=50)
train_output, valid_output, test_output = outputs












h = 200
X = dataset['images']['train_set']
Y = dataset['labels']['train_set']

x_min, x_max = X[:, 0].min() - .15, X[:, 0].max() + .15
y_min, y_max = X[:, 1].min() - .15, X[:, 1].max() + .15
xx, yy = np.meshgrid(np.linspace(x_min, x_max, h),np.linspace(y_min, y_max, h))
xxx=xx.flatten()
yyy=yy.flatten()
XX = np.asarray([xxx,yyy]).astype('float32').T

linkage     = [[pipeline.network[0],XX]]
predictions = pipeline.predict([pipeline.network[2].mask,pipeline.network[4].mask,pipeline.network[5]],linkage=linkage,concat=True)

others = pipeline.predict([pipeline.network[2],pipeline.network[4],pipeline.network[5]],linkage=linkage,concat=True)


for i in range(45):
    pl.figure(figsize=(6,6))
    pl.imshow(np.flipud(others[0][:,i].reshape((200,200))),aspect='auto',extent=[x_min,x_max,y_min,y_max])
    pl.xticks([])
    pl.yticks([])

    pl.savefig('layer1_unit'+str(i)+'.png')
    pl.close



for i in range(3):
    pl.figure(figsize=(6,6))
    pl.imshow(np.flipud(others[1][:,i].reshape((200,200))),aspect='auto',extent=[x_min,x_max,y_min,y_max])
    pl.xticks([])
    pl.yticks([])

    pl.savefig('layer2_unit'+str(i)+'.png')
    pl.close


for i in range(4):
    pl.figure(figsize=(6,6))
    pl.imshow(np.flipud(others[2][:,i].reshape((200,200))),aspect='auto',extent=[x_min,x_max,y_min,y_max])
    pl.xticks([])
    pl.yticks([])

    pl.savefig('layer3_unit'+str(i)+'.png')
    pl.close



exit()




indices = predictions[2].argmax(1)
predictions[2]*=0
predictions[2][range(predictions[0].shape[0]),indices]=1
predictions[2] = predictions[2].astype('bool')

plot1  = sknet.utils.geometry.get_input_space_partition(predictions[0],h,h)
plot2  = sknet.utils.geometry.get_input_space_partition(predictions[1],h,h)
plot3  = sknet.utils.geometry.get_input_space_partition(predictions[2],h,h)

plot12  = sknet.utils.geometry.get_input_space_partition(np.concatenate([predictions[0],predictions[1]],1),h,h)
plot123 = sknet.utils.geometry.get_input_space_partition(np.concatenate([predictions[0],
                                        predictions[1],predictions[2]],1),h,h)



pl.figure(figsize=(6,6))
pl.imshow(np.flipud(plot1),aspect='auto',cmap='Greys',extent=[x_min,x_max,y_min,y_max],alpha=0.5)
for k in range(4):
    indices = pl.where(Y==k)[0]
    print(np.shape(X))
    indices = indices[::16]
    pl.plot(X[indices,0],X[indices,1],'x',alpha=0.3)

pl.xticks([])
pl.yticks([])

#pl.show()
pl.savefig('layer1.png')
pl.close


#exit()

pl.figure(figsize=(6,6))
pl.imshow(np.flipud(plot12),aspect='auto',cmap='Greys',extent=[x_min,x_max,y_min,y_max],alpha=0.5)
for k in range(4):
    indices = pl.where(Y==k)[0]
    print(np.shape(X))
    indices = indices[::16]
    pl.plot(X[indices,0],X[indices,1],'x',alpha=0.3)

pl.xticks([])
pl.yticks([])

pl.savefig('layer12.png')
pl.close


pl.figure(figsize=(6,6))
pl.imshow(np.flipud(plot123),aspect='auto',cmap='Greys',extent=[x_min,x_max,y_min,y_max],alpha=0.5)

for k in range(4):
    indices = pl.where(Y==k)[0]
    print(np.shape(X))
    indices = indices[::16]
    pl.plot(X[indices,0],X[indices,1],'x',alpha=0.3)

pl.xticks([])
pl.yticks([])

pl.savefig('layer123.png')
pl.close









