""" A Class for defining the ResNet model in Tensorflow. """
import tensorflow as tf
import tensorflow.contrib.slim as slim


import numpy as np
import cv2
import matplotlib.pyplot as plt
import TerminalColors

class CartWheelFlow:
    def __init__(self, trainable_on_device ):
        """ Constructor basically defines the SGD and the variables """
        print 'CartWheelFlow constructor...define trainable variables'
        self.tcol = TerminalColors.bcolors


        # Define all required variables (nightmare :'( )
        with tf.device( trainable_on_device ):
            with tf.variable_scope( 'trainable_vars', reuse=None ):

                #top-level conv
                wc_top = tf.get_variable( 'wc_top', [7,7,3,64], initializer=tf.contrib.layers.xavier_initializer_conv2d() )
                bc_top = tf.get_variable( 'bc_top', [64], initializer=tf.constant_initializer(0.01) )
                with tf.variable_scope( 'bn', reuse=None ):
                    wc_top_beta  = tf.get_variable( 'wc_top_beta', [64], initializer=tf.constant_initializer(value=0.0) )
                    wc_top_gamma = tf.get_variable( 'wc_top_gamma', [64], initializer=tf.constant_initializer(value=1.0) )
                    wc_top_pop_mean  = tf.get_variable( 'wc_top_pop_mean', [64], initializer=tf.constant_initializer(value=0.0), trainable=False )
                    wc_top_pop_varn  = tf.get_variable( 'wc_top_pop_varn', [64], initializer=tf.constant_initializer(value=0.0), trainable=False )



                ## RES2
                with tf.variable_scope( 'res2a', reuse=None ):
                    self._define_resnet_unit_variables( 64, [64,64,256], [1,3,1], False )

                with tf.variable_scope( 'res2b', reuse=None ):
                    self._define_resnet_unit_variables( 256, [64,64,256], [1,3,1], True )

                with tf.variable_scope( 'res2c', reuse=None ):
                    self._define_resnet_unit_variables( 256, [64,64,256], [1,3,1], True )


                ## RES3
                with tf.variable_scope( 'res3a', reuse=None ):
                    self._define_resnet_unit_variables( 256, [128,128,512], [1,3,1], False )

                with tf.variable_scope( 'res3b', reuse=None ):
                    self._define_resnet_unit_variables( 512, [128,128,512], [1,3,1], True )

                with tf.variable_scope( 'res3c', reuse=None ):
                    self._define_resnet_unit_variables( 512, [128,128,512], [1,3,1], True )

                with tf.variable_scope( 'res3d', reuse=None ):
                    self._define_resnet_unit_variables( 512, [128,128,512], [1,3,1], True )

                ## RES4
                with tf.variable_scope( 'res4a', reuse=None ):
                    self._define_resnet_unit_variables( 512, [256,256,1024], [1,3,1], False )

                with tf.variable_scope( 'res4b', reuse=None ):
                    self._define_resnet_unit_variables( 1024, [256,256,1024], [1,3,1], True )

                with tf.variable_scope( 'res4c', reuse=None ):
                    self._define_resnet_unit_variables( 1024, [256,256,1024], [1,3,1], True )

                with tf.variable_scope( 'res4d', reuse=None ):
                    self._define_resnet_unit_variables( 1024, [256,256,1024], [1,3,1], True )

                with tf.variable_scope( 'res4e', reuse=None ):
                    self._define_resnet_unit_variables( 1024, [256,256,1024], [1,3,1], True )

                ## RES5
                with tf.variable_scope( 'res5a', reuse=None ):
                    self._define_resnet_unit_variables( 1024, [512,512,2048], [1,3,1], False )

                with tf.variable_scope( 'res5b', reuse=None ):
                    self._define_resnet_unit_variables( 2048, [512,512,2048], [1,3,1], True )

                with tf.variable_scope( 'res5c', reuse=None ):
                    self._define_resnet_unit_variables( 2048, [512,512,2048], [1,3,1], True )



                ## Fully Connected Layer
                # NOTE: This will make each layer identical, if need be in the
                # future this can be changed to have different structures for
                # prediction variables.
                with tf.variable_scope( 'fully_connected', reuse=None ):
                    for scope_str in ['ZF']:#['x', 'y', 'z', 'yaw']:
                        with tf.variable_scope( scope_str, reuse=None ):
                            w_fc1 = tf.get_variable( 'w_fc1', [2048, 1024], initializer=tf.contrib.layers.xavier_initializer()) #This `2048` better be un-hardcoded. Donno a way to have this number in the constructor
                            w_fc2 = tf.get_variable( 'w_fc2', [1024, 512], initializer=tf.contrib.layers.xavier_initializer())
                            w_fc3 = tf.get_variable( 'w_fc3', [512, 120], initializer=tf.contrib.layers.xavier_initializer())

                            #bias terms
                            b_fc1 = tf.get_variable( 'b_fc1', [ 1024], initializer=tf.constant_initializer(0.01) )
                            b_fc2 = tf.get_variable( 'b_fc2', [ 512], initializer=tf.constant_initializer(0.01) )
                            b_fc3 = tf.get_variable( 'b_fc3', [ 120], initializer=tf.constant_initializer(0.01) )

                            with tf.variable_scope( 'bn' ):
                                w_fc1_beta = tf.get_variable( 'w_fc1_beta', [1024], initializer=tf.constant_initializer(value=0.0) )
                                w_fc1_gamma = tf.get_variable( 'w_fc1_gamma', [1024], initializer=tf.constant_initializer(value=1.0) )
                                w_fc1_pop_mean = tf.get_variable( 'w_fc1_pop_mean', [1024], initializer=tf.constant_initializer(value=1.0), trainable=False )
                                w_fc1_pop_varn = tf.get_variable( 'w_fc1_pop_varn', [1024], initializer=tf.constant_initializer(value=1.0), trainable=False )

                                w_fc2_beta = tf.get_variable( 'w_fc2_beta', [512], initializer=tf.constant_initializer(value=0.0) )
                                w_fc2_gamma = tf.get_variable( 'w_fc2_gamma', [512], initializer=tf.constant_initializer(value=1.0) )
                                w_fc2_pop_mean = tf.get_variable( 'w_fc2_pop_mean', [512], initializer=tf.constant_initializer(value=1.0), trainable=False )
                                w_fc2_pop_varn = tf.get_variable( 'w_fc2_pop_varn', [512], initializer=tf.constant_initializer(value=1.0), trainable=False )





        # Place the towers on each of the GPUs and compute ops for
        # fwd_flow, avg_gradient and update_variables

        print 'Exit successfully, from CartWheelFlow constructor'



    def resnet50_inference(self, x, is_training):
        """ This function creates the computational graph and returns the op which give a
            prediction given an input batch x
        """

        print 'Define ResNet50'
        #TODO: Expect x to be individually normalized, ie. for each image in the batch, it has mean=0 and var=1
        #      batch normalize input (linear scale only)


        with tf.variable_scope( 'trainable_vars', reuse=True ):
            wc_top = tf.get_variable( 'wc_top', [7,7,3,64] )
            bc_top = tf.get_variable( 'bc_top', [64] )
            with tf.variable_scope( 'bn', reuse=True ):
                wc_top_beta  = tf.get_variable( 'wc_top_beta', [64] )
                wc_top_gamma = tf.get_variable( 'wc_top_gamma', [64] )
                wc_top_pop_mean  = tf.get_variable( 'wc_top_pop_mean', [64] )
                wc_top_pop_varn  = tf.get_variable( 'wc_top_pop_varn', [64] )



            conv1 = self._conv2d( x, wc_top, bc_top, pop_mean=wc_top_pop_mean, pop_varn=wc_top_pop_varn, is_training=is_training, W_beta=wc_top_beta, W_gamma=wc_top_gamma, strides=2 )
            with tf.device( '/cpu:0'):
                tf.summary.scalar( 'sparsity_conv1', tf.nn.zero_fraction(conv1) )
                tf.summary.histogram( 'hist_conv1', conv1 )
            conv1 = self._maxpool2d( conv1, k=2 )

            input_var = conv1

            ## RES2
            with tf.variable_scope( 'res2a', reuse=True ):
                conv_out = self.resnet_unit( input_var, 64, [64,64,256], [1,3,1], is_training=is_training, short_circuit=False )

            with tf.variable_scope( 'res2b', reuse=True ):
                conv_out = self.resnet_unit( conv_out, 256, [64,64,256], [1,3,1], is_training=is_training, short_circuit=True )

            with tf.variable_scope( 'res2c', reuse=True ):
                conv_out = self.resnet_unit( conv_out, 256, [64,64,256], [1,3,1], is_training=is_training, short_circuit=True )

                ## MAXPOOL
                with tf.device( '/cpu:0'):
                    tf.summary.scalar( 'sparsity_res2', tf.nn.zero_fraction(conv_out) )
                    tf.summary.histogram( 'hist_res2', conv_out )
                conv_out = self._maxpool2d( conv_out, k=2 )


            ## RES3
            with tf.variable_scope( 'res3a', reuse=True ):
                conv_out = self.resnet_unit( conv_out, 256, [128,128,512], [1,3,1], is_training=is_training, short_circuit=False )

            with tf.variable_scope( 'res3b', reuse=True ):
                conv_out = self.resnet_unit( conv_out, 512, [128,128,512], [1,3,1], is_training=is_training, short_circuit=True )

            with tf.variable_scope( 'res3c', reuse=True ):
                conv_out = self.resnet_unit( conv_out, 512, [128,128,512], [1,3,1], is_training=is_training, short_circuit=True )

            with tf.variable_scope( 'res3d', reuse=True ):
                conv_out = self.resnet_unit( conv_out, 512, [128,128,512], [1,3,1], is_training=is_training, short_circuit=True )

                ## MAXPOOL
                with tf.device( '/cpu:0'):
                    tf.summary.scalar( 'sparsity_res3', tf.nn.zero_fraction(conv_out) )
                    tf.summary.histogram( 'hist_res3', conv_out )
                conv_out = self._maxpool2d( conv_out, k=2 )


            ## RES4
            with tf.variable_scope( 'res4a', reuse=True ):
                conv_out = self.resnet_unit( conv_out, 512, [256,256,1024], [1,3,1], is_training=is_training, short_circuit=False )

            with tf.variable_scope( 'res4b', reuse=True ):
                conv_out = self.resnet_unit( conv_out, 1024, [256,256,1024], [1,3,1], is_training=is_training, short_circuit=True )

            with tf.variable_scope( 'res4c', reuse=True ):
                conv_out = self.resnet_unit( conv_out, 1024, [256,256,1024], [1,3,1], is_training=is_training, short_circuit=True )

            with tf.variable_scope( 'res4d', reuse=True ):
                conv_out = self.resnet_unit( conv_out, 1024, [256,256,1024], [1,3,1], is_training=is_training, short_circuit=True )

            with tf.variable_scope( 'res4e', reuse=True ):
                conv_out = self.resnet_unit( conv_out, 1024, [256,256,1024], [1,3,1], is_training=is_training, short_circuit=True )

                ## MAXPOOL
                with tf.device( '/cpu:0'):
                    tf.summary.scalar( 'sparsity_res4', tf.nn.zero_fraction(conv_out) )
                    tf.summary.histogram( 'hist_res4', conv_out )
                conv_out = self._maxpool2d( conv_out, k=2 )


            ## RES5
            with tf.variable_scope( 'res5a', reuse=True ):
                conv_out = self.resnet_unit( conv_out, 1024, [512,512,2048], [1,3,1], is_training=is_training, short_circuit=False )

            with tf.variable_scope( 'res5b', reuse=True ):
                conv_out = self.resnet_unit( conv_out, 2048, [512,512,2048], [1,3,1], is_training=is_training, short_circuit=True )

            with tf.variable_scope( 'res5c', reuse=True ):
                conv_out = self.resnet_unit( conv_out, 2048, [512,512,2048], [1,3,1], is_training=is_training, short_circuit=True )

                ## MAXPOOL
                with tf.device( '/cpu:0'):
                    tf.summary.scalar( 'sparsity_res5', tf.nn.zero_fraction(conv_out) )
                    tf.summary.histogram( 'hist_res5', conv_out )
                conv_out = self._avgpool2d( conv_out, k1=8, k2=10 )


            # Reshape Activations
            print conv_out.get_shape().as_list()[1:]
            n_activations = np.prod( conv_out.get_shape().as_list()[1:] )
            fc = tf.reshape( conv_out, [-1, n_activations] )

            # Fully Connected Layers

            with tf.variable_scope( 'fully_connected', reuse=True):
                for scope_str in ['ZF']:#['x', 'y', 'z', 'yaw']:
                    with tf.variable_scope( scope_str, reuse=True ):
                        pred = self._define_fc( fc, n_activations, [1024, 512, 120], is_training=is_training )
                        # print pred



            return pred





    def _print_tensor_info( self, display_str, T ):
        print self.tcol.WARNING, display_str, T.name, T.get_shape().as_list(), self.tcol.ENDC


    def resnet_unit( self, input_tensor, n_inputs, n_intermediates, intermediate_filter_size, is_training, short_circuit=True ):
        """ Defines the net structure of resnet unit
                input_tensor : Input of the unit
                n_inputs : Number of input channels
                n_intermediates : An array of intermediate filter outputs (usually len of this array is 3)
                intermediate_filter_size : Same size as `n_intermediates`, gives kernel sizes (sually 1,3,1)
                short_circuit : True will directly connect input to the (+-elementwise). False will add in a convolution before adding

                returns : output of the unit. after addition and relu

        """
        print '<--->'
        a = n_inputs
        b = n_intermediates #note, b[2] will be # of output filters
        c = intermediate_filter_size

        self._print_tensor_info( 'Input Tensor', input_tensor)

        wc1 = tf.get_variable( 'wc1', [c[0],c[0],a,b[0] ] )
        wc2 = tf.get_variable( 'wc2', [c[1],c[1],b[0],b[1]] )
        wc3 = tf.get_variable( 'wc3', [c[2],c[2],b[1],b[2]] )

        # BN variables
        #BN Adopted from http://r2rt.com/implementing-batch-normalization-in-tensorflow.html
        with tf.variable_scope( 'bn', reuse=True ):
            wc1_bn_beta  = tf.get_variable( 'wc1_beta', [b[0]] )
            wc1_bn_gamma = tf.get_variable( 'wc1_gamma', [b[0]] )
            wc1_bn_pop_mean  = tf.get_variable( 'wc1_pop_mean', [b[0]] )
            wc1_bn_pop_varn = tf.get_variable( 'wc1_pop_varn', [b[0]] )

            wc2_bn_beta  = tf.get_variable( 'wc2_beta', [b[1]] )
            wc2_bn_gamma = tf.get_variable( 'wc2_gamma', [b[1]] )
            wc2_bn_pop_mean = tf.get_variable( 'wc2_pop_mean', [b[1]] )
            wc2_bn_pop_varn = tf.get_variable( 'wc2_pop_varn', [b[1]] )

            wc3_bn_beta  = tf.get_variable( 'wc3_beta', [b[2]] )
            wc3_bn_gamma = tf.get_variable( 'wc3_gamma', [b[2]] )
            wc3_bn_pop_mean  = tf.get_variable( 'wc3_pop_mean', [b[2]] )
            wc3_bn_pop_varn  = tf.get_variable( 'wc3_pop_varn', [b[2]] )


        self._print_tensor_info( 'Request Var', wc1 )
        self._print_tensor_info( 'Request Var', wc2 )
        self._print_tensor_info( 'Request Var', wc3 )


        conv_1 = self._conv2d_nobias( input_tensor, wc1, pop_mean=wc1_bn_pop_mean, pop_varn=wc1_bn_pop_varn, is_training=is_training, W_beta=wc1_bn_beta, W_gamma=wc1_bn_gamma )
        conv_2 = self._conv2d_nobias( conv_1, wc2,  pop_mean=wc2_bn_pop_mean, pop_varn=wc2_bn_pop_varn, is_training=is_training, W_beta=wc2_bn_beta, W_gamma=wc2_bn_gamma )
        conv_3 = self._conv2d_nobias( conv_2, wc3, pop_mean=wc3_bn_pop_mean, pop_varn=wc3_bn_pop_varn, is_training=is_training,  W_beta=wc3_bn_beta, W_gamma=wc3_bn_gamma, relu_unit=False )
        self._print_tensor_info( 'conv_1', conv_1 )
        self._print_tensor_info( 'conv_2', conv_2 )
        self._print_tensor_info( 'conv_3', conv_3 )

        if short_circuit==True: #direct skip connection (no conv on side)
            conv_out = tf.nn.relu( tf.add( conv_3, input_tensor ) )
        else: #side connection has convolution
            wc_side = tf.get_variable( 'wc1_side', [1,1,a,b[2]] )
            with tf.variable_scope( 'bn', reuse=True ):
                wc_side_bn_beta = tf.get_variable( 'wc_side_bn_beta', [b[2]] )
                wc_side_bn_gamma = tf.get_variable( 'wc_side_bn_gamma', [b[2]] )
                wc_side_bn_pop_mean = tf.get_variable( 'wc_side_pop_mean', [b[2]] )
                wc_side_bn_pop_varn = tf.get_variable( 'wc_side_pop_varn', [b[2]] )

            self._print_tensor_info( 'Request Var', wc_side )
            conv_side = self._conv2d_nobias( input_tensor, wc_side, pop_mean=wc_side_bn_pop_mean, pop_varn=wc_side_bn_pop_varn, is_training=is_training, W_beta=wc_side_bn_beta, W_gamma=wc_side_bn_gamma, relu_unit=False )
            conv_out = tf.nn.relu( tf.add( conv_3, conv_side ) )

        self._print_tensor_info( 'conv_out', conv_out )
        return conv_out


    def _define_resnet_unit_variables( self, n_inputs, n_intermediates, intermediate_filter_size, short_circuit=True ):
        """ Defines variables in a resnet unit
                n_inputs : Number of input channels
                n_intermediates : An array of intermediate filter outputs (usually len of this array is 3)
                intermediate_filter_size : Same size as `n_intermediates`, gives kernel sizes (sually 1,3,1)
                short_circuit : True will directly connect input to the (+-elementwise). False will add in a convolution before adding

        """
        a = n_inputs
        b = n_intermediates #note, b[2] will be # of output filters
        c = intermediate_filter_size
        wc1 = tf.get_variable( 'wc1', [c[0],c[0],a,b[0]], initializer=tf.contrib.layers.xavier_initializer_conv2d() )
        wc2 = tf.get_variable( 'wc2', [c[1],c[1],b[0],b[1]], initializer=tf.contrib.layers.xavier_initializer_conv2d() )
        wc3 = tf.get_variable( 'wc3', [c[2],c[2],b[1],b[2]], initializer=tf.contrib.layers.xavier_initializer_conv2d() )

        #BN Adopted from http://r2rt.com/implementing-batch-normalization-in-tensorflow.html
        with tf.variable_scope( 'bn', reuse=None ):
            wc1_bn_beta  = tf.get_variable( 'wc1_beta', [b[0]], initializer=tf.constant_initializer(value=0.0) )
            wc1_bn_gamma = tf.get_variable( 'wc1_gamma', [b[0]], initializer=tf.constant_initializer(value=1.0) )
            wc1_bn_pop_mean  = tf.get_variable( 'wc1_pop_mean', [b[0]], initializer=tf.constant_initializer(value=0.0), trainable=False )
            wc1_bn_pop_varn = tf.get_variable( 'wc1_pop_varn', [b[0]], initializer=tf.constant_initializer(value=0.0), trainable=False )


            wc2_bn_beta  = tf.get_variable( 'wc2_beta', [b[1]], initializer=tf.constant_initializer(value=0.0) )
            wc2_bn_gamma = tf.get_variable( 'wc2_gamma', [b[1]], initializer=tf.constant_initializer(value=1.0) )
            wc2_bn_pop_mean = tf.get_variable( 'wc2_pop_mean', [b[1]], initializer=tf.constant_initializer(value=0.0), trainable=False )
            wc2_bn_pop_varn = tf.get_variable( 'wc2_pop_varn', [b[1]], initializer=tf.constant_initializer(value=0.0), trainable=False )


            wc3_bn_beta  = tf.get_variable( 'wc3_beta', [b[2]], initializer=tf.constant_initializer(value=0.0) )
            wc3_bn_gamma = tf.get_variable( 'wc3_gamma', [b[2]], initializer=tf.constant_initializer(value=1.0) )
            wc3_bn_pop_mean  = tf.get_variable( 'wc3_pop_mean', [b[2]], initializer=tf.constant_initializer(value=0.0), trainable=False )
            wc3_bn_pop_varn  = tf.get_variable( 'wc3_pop_varn', [b[2]], initializer=tf.constant_initializer(value=0.0), trainable=False )

        if short_circuit == False:
            wc_side = tf.get_variable( 'wc1_side', [1,1,a,b[2]], initializer=tf.contrib.layers.xavier_initializer_conv2d() )
            with tf.variable_scope( 'bn', reuse=None ):
                wc_side_bn_beta = tf.get_variable( 'wc_side_bn_beta', [b[2]], initializer=tf.constant_initializer(value=0.0) )
                wc_side_bn_gamma = tf.get_variable( 'wc_side_bn_gamma', [b[2]], initializer=tf.constant_initializer(value=1.0) )
                wc_side_bn_pop_mean = tf.get_variable( 'wc_side_pop_mean', [b[2]], initializer=tf.constant_initializer(value=0.0), trainable=False )
                wc_side_bn_pop_varn = tf.get_variable( 'wc_side_pop_varn', [b[2]], initializer=tf.constant_initializer(value=0.0), trainable=False )


    def _BN_fc( self, fc, w_beta, w_gamma, w_pop_mean, w_pop_varn, is_training=True ):
        """
            Does batch-normalization for fully connected layer
                fc: Output after matrix multiply. ie. before relu
                w_beta, w_gamma, w_pop_mean, w_pop_varn : variables for BN
                is_training  phase    """
        if is_training == True: #Phase : Training
            with tf.variable_scope( 'bn' ):
                # compute batch_mean
                batch_mean, batch_var = tf.nn.moments( fc, [0], name='moments' )

                # update population_mean
                decay = 0.999
                train_mean = tf.assign(w_pop_mean, w_pop_mean * decay + batch_mean * (1.0 - decay))
                train_var = tf.assign(w_pop_varn, w_pop_varn * decay + batch_var * (1.0 - decay))

                with tf.control_dependencies( [train_mean, train_var] ):
                    normed_x = tf.nn.batch_normalization( fc, batch_mean, batch_var, w_beta, w_gamma, 1E-3, name='apply_moments_training')
        else : #Phase : Testing
            with tf.variable_scope( 'bn' ):
                normed_x = tf.nn.batch_normalization( fc, w_pop_mean, w_pop_varn, w_beta, w_gamma, 1E-3, name='apply_moments_testing')

        return normed_x


    def _define_fc( self, fc, n_input, interim_input_dim, is_training ):
        """ Define a fully connected layer
                fc : the reshaped array
                n_input : number of inputs
                interim_input_dim : array of intermediate data dims

                Note that this assume, the context is already in correct scope
        """

        a = n_input
        b = interim_input_dim
        w_fc1 = tf.get_variable( 'w_fc1', [a, b[0]])
        w_fc2 = tf.get_variable( 'w_fc2', [b[0], b[1]])
        w_fc3 = tf.get_variable( 'w_fc3', [b[1], b[2]])

        b_fc1 = tf.get_variable( 'b_fc1', [ b[0]])
        b_fc2 = tf.get_variable( 'b_fc2', [ b[1]])
        b_fc3 = tf.get_variable( 'b_fc3', [ b[2]])

        # Get BN variables
        with tf.variable_scope( 'bn' ):
            w_fc1_beta = tf.get_variable( 'w_fc1_beta', [b[0]] )
            w_fc1_gamma = tf.get_variable( 'w_fc1_gamma', [b[0]] )
            w_fc1_pop_mean = tf.get_variable( 'w_fc1_pop_mean', [b[0]] )
            w_fc1_pop_varn = tf.get_variable( 'w_fc1_pop_varn', [b[0]] )

            w_fc2_beta = tf.get_variable( 'w_fc2_beta', [b[1]] )
            w_fc2_gamma = tf.get_variable( 'w_fc2_gamma', [b[1]] )
            w_fc2_pop_mean = tf.get_variable( 'w_fc2_pop_mean', [b[1]] )
            w_fc2_pop_varn = tf.get_variable( 'w_fc2_pop_varn', [b[1]] )



        fc1_pre = tf.add( tf.matmul( fc, w_fc1 ), b_fc1 )
        fc1_pre = self._BN_fc( fc1_pre, w_fc1_beta, w_fc1_gamma, w_fc1_pop_mean, w_fc1_pop_varn, is_training=is_training)
        fc1 = tf.nn.relu( fc1_pre )

        fc2_pre = tf.add( tf.matmul( fc1, w_fc2 ), b_fc2 )
        fc2_pre = self._BN_fc( fc2_pre, w_fc2_beta, w_fc2_gamma, w_fc2_pop_mean, w_fc2_pop_varn, is_training=is_training)
        fc2 = tf.nn.relu( fc2_pre )



        fc3 = tf.mul( 1., tf.add( tf.matmul( fc2, w_fc3 ), b_fc3, name='stacked_fc_out' ) )
        # tf.summary.histogram( 'a_input', fc )
        # tf.summary.histogram( 'fc1', fc1_pre )
        # tf.summary.histogram( 'fc2', fc2_pre )
        # tf.summary.histogram( 'fc3', fc3_pre )
        # tf.summary.histogram( 'fc4', fc4 )
        tf.summary.scalar( 'fc1_non_zeros', tf.nn.zero_fraction(fc1))
        tf.summary.scalar( 'fc2_non_zeros', tf.nn.zero_fraction(fc2))

        # tf.summary.histogram( 'w_fc1', w_fc1 )
        # tf.summary.histogram( 'w_fc2', w_fc2 )
        # tf.summary.histogram( 'w_fc3', w_fc3 )
        # tf.summary.histogram( 'w_fc4', w_fc4 )
        return fc3




    # Create some wrappers for simplicity
    def _conv2d(self, x, W, b, pop_mean, pop_varn, is_training, W_beta=None, W_gamma=None, strides=1):
        # Conv2D wrapper, with bias and relu activation

        x = tf.nn.conv2d(x, W, strides=[1, strides, strides, 1], padding='SAME')
        x = tf.nn.bias_add(x, b)

        if is_training == True: #Phase : Training
            with tf.variable_scope( 'bn' ):
                # compute batch_mean
                batch_mean, batch_var = tf.nn.moments( x, [0,1,2], name='moments' )

                # update population_mean
                decay = 0.999
                train_mean = tf.assign(pop_mean, pop_mean * decay + batch_mean * (1.0 - decay))
                train_var = tf.assign(pop_varn, pop_varn * decay + batch_var * (1.0 - decay))

                with tf.control_dependencies( [train_mean, train_var] ):
                    normed_x = tf.nn.batch_normalization( x, batch_mean, batch_var, W_beta, W_gamma, 1E-3, name='apply_moments_training')
        else : #Phase : Testing
            with tf.variable_scope( 'bn' ):
                normed_x = tf.nn.batch_normalization( x, pop_mean, pop_varn, W_beta, W_gamma, 1E-3, name='apply_moments_testing')


        # NORMPROP
        # return (tf.nn.relu(x) - 0.039894228) / 0.58381937
        # return tf.nn.relu(x)
        return tf.nn.relu(normed_x)


    # Create some wrappers for simplicity
    def _conv2d_nobias(self, x, W, pop_mean, pop_varn, is_training, W_beta=None, W_gamma=None, strides=1, relu_unit=True, ):
        # Conv2D wrapper, with bias and relu activation

        x = tf.nn.conv2d(x, W, strides=[1, strides, strides, 1], padding='SAME')

        # NORMPROP
        # return (tf.nn.relu(x) - 0.039894228) / 0.58381937

        # Batch-Norm (BN)

        #if training then compute batch mean, update pop_mean, do normalization with batch mean
        #if testing, then do notmalization with pop_mean

        if is_training == True: #Phase : Training
            with tf.variable_scope( 'bn' ):
                # compute batch_mean
                batch_mean, batch_var = tf.nn.moments( x, [0,1,2], name='moments' )

                # update population_mean
                decay = 0.999
                train_mean = tf.assign(pop_mean, pop_mean * decay + batch_mean * (1.0 - decay))
                train_var = tf.assign(pop_varn, pop_varn * decay + batch_var * (1.0 - decay))

                with tf.control_dependencies( [train_mean, train_var] ):
                    normed_x = tf.nn.batch_normalization( x, batch_mean, batch_var, W_beta, W_gamma, 1E-3, name='apply_moments_training')
        else : #Phase : Testing
            with tf.variable_scope( 'bn' ):
                normed_x = tf.nn.batch_normalization( x, pop_mean, pop_varn, W_beta, W_gamma, 1E-3, name='apply_moments_testing')



        if relu_unit == True:
            return tf.nn.relu(normed_x)
            # return tf.nn.relu(x)
        else:
            # NOTE : No RELU
            return normed_x
            # return x


    def _maxpool2d(self, x, k=2):
        # MaxPool2D wrapper
        pool_out = tf.nn.max_pool(x, ksize=[1, k, k, 1], strides=[1, k, k, 1],
                              padding='SAME')
        # NORMPROP
        # return (pool_out - 1.4850) / 0.7010
        return pool_out


    def _avgpool2d(self, x, k1=2, k2=2):
        # MaxPool2D wrapper
        pool_out = tf.nn.avg_pool(x, ksize=[1, k1, k2, 1], strides=[1, k1, k2, 1],
                              padding='SAME')
        # NORMPROP
        # return (pool_out - 1.4850) / 0.7010
        return pool_out


class VGGFlow:
    def __init__(self):
        x=0

    # vggnet16. is_training is a placeholder boolean
    def vgg16( self, inputs, is_training ):
        with slim.arg_scope([slim.conv2d, slim.fully_connected],\
                          activation_fn=tf.nn.relu,\
                          #weights_initializer=tf.truncated_normal_initializer(0.0, 0.01),\
                          weights_regularizer=slim.l2_regularizer(0.05),
                          normalizer_fn=slim.batch_norm, \
                          normalizer_params={'is_training':is_training, 'decay': 0.9, 'updates_collections': None}\
                          ):
            net = slim.repeat(inputs, 2, slim.conv2d, 64, [3, 3], scope='conv1')
            net = slim.max_pool2d(net, [2, 2], scope='pool1')
            net = slim.repeat(net, 2, slim.conv2d, 128, [3, 3], scope='conv2')
            net = slim.max_pool2d(net, [2, 2], scope='pool2')
            net = slim.repeat(net, 3, slim.conv2d, 256, [3, 3], scope='conv3')
            net = slim.max_pool2d(net, [2, 2], scope='pool3')
            net = slim.repeat(net, 3, slim.conv2d, 512, [3, 3], scope='conv4')
            net = slim.max_pool2d(net, [2, 2], scope='pool4')
            net = slim.repeat(net, 3, slim.conv2d, 512, [3, 3], scope='conv5')
            net = slim.max_pool2d(net, [15, 20], scope='pool5')
            fc_dat = slim.flatten( net )

            pred_x   = slim.stack( fc_dat, slim.fully_connected, [128, 16, 1], scope='fcx' )
            pred_y   = slim.stack( fc_dat, slim.fully_connected, [128, 16, 1], scope='fcy' )
            pred_z   = slim.stack( fc_dat, slim.fully_connected, [128, 16, 1], scope='fcz' )
            pred_yaw = slim.stack( fc_dat, slim.fully_connected, [128, 16, 1], scope='fcyaw' )

            # net = slim.fully_connected(net, 4096, scope='fc6')
            # net = slim.fully_connected(net, 4096, scope='fc7')
            # net = slim.fully_connected(net, 4, activation_fn=None, scope='fc8')

            return pred_x, pred_y, pred_z, pred_yaw


## construct the VGG descriptor at 5 layers
class VGGDescriptor:
    def __init__(self):
        x=0

    # vggnet16. is_training is a placeholder boolean
    def vgg16( self, inputs, is_training ):
        with slim.arg_scope([slim.conv2d, slim.fully_connected],\
                          activation_fn=tf.nn.relu,\
                          weights_initializer=tf.contrib.layers.xavier_initializer_conv2d(),\
                          weights_regularizer=slim.l2_regularizer(0.0005),
                          normalizer_fn=slim.batch_norm, \
                          normalizer_params={'is_training':is_training, 'decay': 0.9, 'updates_collections': None, 'scale': True}\
                          ):
            # tf.summary.histogram( 'xxxx_inputs', inputs )
            net = slim.repeat(inputs, 2, slim.conv2d, 64, [3, 3], scope='conv1')
            # tf.summary.histogram( 'xxxx_blk1', net )
            net = slim.max_pool2d(net, [2, 2], scope='pool1')
            net = slim.repeat(net, 2, slim.conv2d, 128, [3, 3], scope='conv2')
            # tf.summary.histogram( 'xxxx_blk2', net )
            net = slim.max_pool2d(net, [2, 2], scope='pool2')
            net = slim.repeat(net, 1, slim.conv2d, 256, [3, 3], scope='conv3')
            # tf.summary.histogram( 'xxxx_blk3', net )


            # MAX POOLING
            # TODO: To be replaced with NetVLAD-layer
            net = slim.max_pool2d(net, kernel_size=[10, 10], stride=10, scope='pool3')
            sh = tf.shape(net)
            # print sh
            # print net
            net = tf.reshape( net, [sh[0], sh[1]*sh[2]*sh[3] ])




            return net


    def svm_hinge_loss( self,tf_vlad_word, nP, nN, margin ):
        sp_q, sp_P, sp_N = tf.split_v( tf_vlad_word, [1,nP,nN], 0 )
        #sp_q=query; sp_P=definite_positives ; sp_N=definite_negatives
        #q:1x16k;   P:5x16k;    N:10x16k


        # distance between sp_q and each of sp_P
        one_a = tf.ones( [nP,1], tf.float32 )
        a_ = tf.sub( tf.matmul( one_a, sp_q ), sp_P ) #   (1 * q - P)**2  ==> (q-P)**2
        tf_dis_q_P = tf.reduce_mean( tf.mul( a_, a_ ), axis=1 ) #row-wise norm (L2)


        # distance between sp_q and each of sp_N
        one_b = tf.ones( [nN,1], tf.float32 )
        b_ = tf.sub( tf.matmul( one_b, sp_q ), sp_N ) #   (1 * q - P)**2  ==> (q-P)**2
        tf_dis_q_N = tf.reduce_mean( tf.mul( b_, b_ ), axis=1 ) #row-wise norm (L2)

        # SVM-hinge loss
        # max( tf_dis_q_P ): Farthest positive sample
        # min( tf_dis_q_N ): Nearest
        tf_margin = tf.constant(margin, name='margin')
        cost_ = tf.sub( tf.add( tf.reduce_max(tf_dis_q_P), tf_margin),  tf.reduce_min(tf_dis_q_N), name='svm_margin_loss' ) # max_i a - max_j b + m
        tf_cost = tf.maximum( cost_, tf.constant(0.0), name='hinge_loss' )

        return tf_cost