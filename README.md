# edge-impulse-hackathon-2025

## Development Process

### Data Collection

The data collection process consisted of driving to a local parking lot and taking images of a car in a spot as well as some empty spots. 134 images were taken total with 208 instances of open parking spaces and 107 instances of used parking spaces. Ideally these numbers should be closer in value. However, out of respect of not using random people's cars as part of the dataset, just personal vehicles were used. 

The labeling process consisted of drawing the bounding boxes around each parking spot and labeling the box open if there was no car in the spot or used if there was a car there. 

**Example of image used for training:**

![Image part of the training dataset](training-ex.png)

### Model Training

Model training started in the `Create Impulse` tab of Edge Impulse. Here the image size was defined at 256 x 256 pixels and the image processing and object detection blocks were added to the impulse. 

In the `Image` tab, grayscale was chosen for color depth. This was chosen over RGB because for this problem, the image features are going to determine if a parking spot is open or used. The color of the image is useless for this. After saving image parameters and running the feature generator, it is time to start model training. 

Finally, in the `Object Detection` tab, the finaly parameters and set and model training begins. For training this model, the number of training cycles was 100, the learning rate was 0.001, the CPU was used as the training processor, and data augmentation was enabled.

**Training Results:**

![alt text](training-results.png)

### Application Development

## Project Demonstration
