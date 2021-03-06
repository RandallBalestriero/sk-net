import tensorflow as tf
from . import Model
from .. import layer


#ToDo models : LeNet LeNet5 smallCNN largeCNN allCNN

class base(Model):
    def __init__(self,input_shape,classes,data_format,**kwargs):
        super().__init__(input_shape,classes,data_format,**kwargs)
        self.name = '-model(cnn.base)'
    def get_layers(self,input_variable,training):
        dnn = [layer.special.input(self.input_shape,input_variable, data_format=self.data_format)]
        #
        dnn.append(layer.transform.Conv2D(dnn[-1],filters=(32,5,5),
            nonlinearity_c = 0, training=training, batch_norm=True))
        dnn.append(layer.pool.Pool(dnn[-1],windows=(1,2,2),strides=(1,2,2),pool_type='MAX'))
        #
        dnn.append(layer.transform.Conv2D(dnn[-1],filters=(64,3,3),
            nonlinearity_c = 0, training=training, batch_norm=True))
        dnn.append(layer.pool.Pool(dnn[-1],windows=(1,2,2),strides=(1,2,2),pool_type='MAX'))
        dnn.append(layer.transform.Dense(dnn[-1], units=128, training=training, batch_norm=True))
        dnn.append(layer.special.output(dnn[-1],classes=self.classes))
        return dnn



class allCNN1:
        def __init__(self,bn=1,classes=10,bias_option='unconstrained',init_W = tf.contrib.layers.xavier_initializer(uniform=True),init_b = tf.constant_initializer(0.)):
                self.bn          = bn
                self.n_classes   = n_classes
                self.layer      = 0
                self.init_W      = init_W
                self.init_b      = init_b
                self.bias_option = bias_option
        def get_layer(self,input_variable,input_shape,training):
                layer = [InputLayer(input_shape,input_variable)]
                layer.append(ConvLayer(layer[-1],5,5,training=training,bn=self.bn,init_W=self.init_W,init_b=self.init_b,bias_option=self.bias_option,first=True))
        # (5 28 28) : 3920
                layer.append(ConvLayer(layer[-1],7,5,training=training,bn=self.bn,init_W=self.init_W,init_b=self.init_b,bias_option=self.bias_option))
        # (7 24 24) : 4032
                layer.append(ConvLayer(layer[-1],9,3,training=training,bn=self.bn,init_W=self.init_W,init_b=self.init_b,bias_option=self.bias_option))
        # (9 22 22) : 4356
                layer.append(DenseLayer(layer[-1],128,training=training,bn=self.bn,init_W=self.init_W,init_b=self.init_b,bias_option=self.bias_option))
        # 128
                layer.append(DenseLayer(layer[-1],self.n_classes,training=training,bn=self.bn,init_W=self.init_W,init_b=self.init_b,bias_option=self.bias_option,nonlinearity=False))
                self.layer = layer
                return self.layer


class allCNN2:
        def __init__(self,bn=1,n_classes=10,bias_option='unconstrained',init_W = tf.contrib.layers.xavier_initializer(uniform=True),init_b = tf.constant_initializer(0.)):
                self.bn          = bn
                self.n_classes   = n_classes
                self.layer      = 0
                self.init_W      = init_W
                self.init_b      = init_b
                self.bias_option = bias_option
        def get_layer(self,input_variable,input_shape,training):
                layer = [InputLayer(input_shape,input_variable)]
                layer.append(ConvLayer(layer[-1],7,5,training=training,bn=self.bn,init_W=self.init_W,init_b=self.init_b,bias_option=self.bias_option,first=True))
        # (7 28 28)  : 5488
                layer.append(ConvLayer(layer[-1],11,5,training=training,bn=self.bn,init_W=self.init_W,init_b=self.init_b,bias_option=self.bias_option))
        # (11 24 24) : 6336
                layer.append(ConvLayer(layer[-1],15,3,training=training,bn=self.bn,init_W=self.init_W,init_b=self.init_b,bias_option=self.bias_option))
        # (15 22 22) : 7260
                layer.append(DenseLayer(layer[-1],128,training=training,bn=self.bn,init_W=self.init_W,init_b=self.init_b,bias_option=self.bias_option))
        # 128
                layer.append(DenseLayer(layer[-1],self.n_classes,training=training,bn=self.bn,init_W=self.init_W,init_b=self.init_b,bias_option=self.bias_option,nonlinearity=False))
                self.layer = layer
                return self.layer


class allCNN3:
        def __init__(self,bn=1,n_classes=10,bias_option='unconstrained',init_W = tf.contrib.layers.xavier_initializer(uniform=True),init_b = tf.constant_initializer(0.)):
                self.bn          = bn
                self.n_classes   = n_classes
                self.layer      = 0
                self.init_W      = init_W
                self.init_b      = init_b
                self.bias_option = bias_option
        def get_layer(self,input_variable,input_shape,training):
                layer = [InputLayer(input_shape,input_variable)]
                layer.append(ConvLayer(layer[-1],12,5,training=training,bn=self.bn,init_W=self.init_W,init_b=self.init_b,bias_option=self.bias_option,first=True))
        # (12 28 28) : 9408
                layer.append(ConvLayer(layer[-1],16,5,training=training,bn=self.bn,init_W=self.init_W,init_b=self.init_b,bias_option=self.bias_option))
        # (16 24 24) : 9216
                layer.append(ConvLayer(layer[-1],20,3,training=training,bn=self.bn,init_W=self.init_W,init_b=self.init_b,bias_option=self.bias_option))
        # (20 22 22) : 9680
                layer.append(DenseLayer(layer[-1],128,training=training,bn=self.bn,init_W=self.init_W,init_b=self.init_b,bias_option=self.bias_option))
        # 128
                layer.append(DenseLayer(layer[-1],self.n_classes,training=training,bn=self.bn,init_W=self.init_W,init_b=self.init_b,bias_option=self.bias_option,nonlinearity=False))
                self.layer = layer
                return self.layer

class allCNN4:
        def __init__(self,bn=1,n_classes=10,bias_option='unconstrained',init_W = tf.contrib.layers.xavier_initializer(uniform=True),init_b = tf.constant_initializer(0.)):
                self.bn          = bn
                self.n_classes   = n_classes
                self.layer      = 0
                self.init_W      = init_W
                self.init_b      = init_b
                self.bias_option = bias_option
        def get_layer(self,input_variable,input_shape,training):
                layer = [InputLayer(input_shape,input_variable)]
                layer.append(ConvLayer(layer[-1],20,5,training=training,bn=self.bn,init_W=self.init_W,init_b=self.init_b,bias_option=self.bias_option,first=True))
        # (20 28 28) : 15680
                layer.append(ConvLayer(layer[-1],32,5,training=training,bn=self.bn,init_W=self.init_W,init_b=self.init_b,bias_option=self.bias_option))
        # (32 24 24) : 18432
                layer.append(ConvLayer(layer[-1],48,5,training=training,bn=self.bn,init_W=self.init_W,init_b=self.init_b,bias_option=self.bias_option))
        # (48 20 20) : 19200
                layer.append(DenseLayer(layer[-1],256,training=training,bn=self.bn,init_W=self.init_W,init_b=self.init_b,bias_option=self.bias_option))
        # 2048
                layer.append(DenseLayer(layer[-1],256,training=training,bn=self.bn,init_W=self.init_W,init_b=self.init_b,bias_option=self.bias_option))
        # 256
                layer.append(DenseLayer(layer[-1],self.n_classes,training=training,bn=self.bn,init_W=self.init_W,init_b=self.init_b,bias_option=self.bias_option,nonlinearity=False))
                self.layer = layer
                return self.layer












