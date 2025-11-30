# Edge Impulse Hackathon 2025

## ISpot
Every driver knows the frustration of circling a parking lot, hunting for a spot, only to watch someone else swerve in and steal it. What if you knew exactly where open spots were before you even entered the lot?

iSpot detects open parking spaces in real-time and shows users exactly where and how many spots are available. No more endless loops.

How? We deploy low-cost edge devices—Raspberry Pi cameras running machine learning that detect open spots and relay that data over a mesh network (ClusterDuck Protocol) to a live dashboard. Users see availability before they arrive, and head straight to an open space.

## Development Process

### Data Collection

For this project, the dataset was collected ourselves. The data collection process consisted of driving to a local parking lot and taking images of a car in a spot as well as some surrounding empty spots. 134 images were taken total with 208 instances of open parking spaces and 107 instances of used parking spaces. Ideally these numbers should be closer in value. However, out of respect of not using random people's cars as part of the dataset, just personal vehicles were used. The amount and diversity of data would also ideally be greater than 134 images with 315 objects. However, due to the free tier of Edge Impulse restricting training time to one hour, we felt that getting a lot of simple data would be a great proof of concept.  

The labeling process consisted of drawing the bounding boxes around each parking spot and labeling the box open if there was no car in the spot or used if there was a car there. 

**Example of image used for training:**

![Image part of the training dataset](training-ex.png)

### Model Training

Model training started in the `Create Impulse` tab of Edge Impulse. Here the image size was defined at 256 x 256 pixels and the image processing and object detection blocks were added to the impulse. 

In the `Image` tab, grayscale was chosen for color depth. This was chosen over RGB because for this problem, the image features are going to determine if a parking spot is open or used. The color of the image is useless for this. After saving image parameters and running the feature generator, it is time to start model training. 

Finally, in the `Object Detection` tab, the last parameters and set and model training begins. When training this model, the number of training cycles was 100, the learning rate was 0.001, the CPU was used as the training processor, and data augmentation was enabled.

**Training Results:**

![alt text](training-results.png)

### Application Development

The applicaiton development starts with flashing a version of Raspberry Pi OS to an SD that will be used by our Raspberry Pi. Once the Pi is powered on we SSH into its terminal, we install the [Edge Impulse Linux CLI](https://docs.edgeimpulse.com/tools/clis/edge-impulse-linux-cli#edge-impulse-linux).

## Project Demonstration
