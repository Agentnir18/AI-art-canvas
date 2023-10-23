import tensorflow as tf
import numpy as np

import cv2
import PIL

from tensorflow.keras import Model

class Merger():
    def gram_matrix(self,input_tensor):
      result = tf.linalg.einsum('bijc,bijd->bcd', input_tensor, input_tensor)
      gram_matrix = tf.expand_dims(result, axis=0)
      input_shape = tf.shape(input_tensor)
      i_j = tf.cast(input_shape[1]*input_shape[2], tf.float32)
      return gram_matrix/i_j 

    def load_vgg(self):
      vgg = tf.keras.applications.VGG19( include_top=True, weights="imagenet", input_tensor=None, input_shape=None, pooling=None, classes=1000, classifier_activation="softmax", )
      vgg.trainable = False
      content_layers = ['block4_conv2']
      style_layers = ['block1_conv1', 'block2_conv1', 'block3_conv1', 'block4_conv1', 'block5_conv1']
      content_output = vgg.get_layer(content_layers[0]).output 
      style_output = [vgg.get_layer(style_layer).output for style_layer in style_layers]
      gram_style_output = [self.gram_matrix(output_) for output_ in style_output]

      model = Model([vgg.input], [content_output, gram_style_output])
      return model

    def loss_object(self,style_outputs, content_outputs, style_target, content_target):
      style_weight = 1e-2
      content_weight = 1e-1
      content_loss = tf.reduce_mean((content_outputs - content_target)**2)
      style_loss = tf.add_n([tf.reduce_mean((output_ - target_)**2) for output_, target_ in zip(style_outputs, style_target)])
      total_loss = content_weight*content_loss + style_weight*style_loss
      return total_loss

    def train_step(self,image, epoch, vgg_model,style_t,content_t):
        with tf.GradientTape() as tape:
            output = vgg_model(image*255)
            loss = self.loss_object(output[1], output[0], style_t, content_t)
        gradient = tape.gradient(loss, image)
        self.opt.apply_gradients([(gradient, image)])#<--------bug cant merge the 2nd time u put a style 
        image.assign(tf.clip_by_value(image, clip_value_min=0.0, clip_value_max=1.0))
        
        if epoch % 100 ==0:
            tf.print(f"Loss = {loss}")

    opt = tf.optimizers.legacy.Adam(learning_rate=0.01, beta_1=0.99, epsilon=1e-1)
    def process(self,content,style):
      vgg = tf.keras.applications.VGG19(include_top=True, weights="imagenet")

      for layers in vgg.layers:
        print(f"{layers.name} ---> {layers.output_shape}")
      content_image = tf.image.convert_image_dtype(content, tf.float32)
      style_image = tf.image.convert_image_dtype(style, tf.float32)
      vgg_model = self.load_vgg()
      content_target = vgg_model(np.array([content_image*255]))[0]
      style_target = vgg_model(np.array([style_image*255]))[1]
      
      EPOCHS = 25
      image = tf.image.convert_image_dtype(content_image, tf.float32)
      image = tf.Variable([image])
      for i in range(EPOCHS):
          self.train_step(image, i,vgg_model,style_target,content_target)

      tensor = image*255
      tensor = np.array(tensor, dtype=np.uint8)
      if np.ndim(tensor)>3:
          assert tensor.shape[0] == 1
          tensor = tensor[0]
      tensor = tensor[:, :, ::-1]
      tensor =  PIL.Image.fromarray(tensor)
      return tensor
    # plt.imshow(cv2.cvtColor(np.array(tensor), cv2.COLOR_BGR2RGB))
    # plt.show()