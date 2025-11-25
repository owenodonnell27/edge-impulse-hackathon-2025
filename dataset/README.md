# Exported dataset for owenodonnell27 / Hackathon_2025

To import this data into a new Edge Impulse project, either use:

* The Edge Impulse CLI (https://docs.edgeimpulse.com/docs/edge-impulse-cli/cli-overview), run with:

    edge-impulse-uploader --clean --info-file info.labels

* Or, via the Edge Impulse Studio. Go to **Data acquisition > Upload data**.

About the dataset:

* This dataset contains images of parking spots labeled as open or used for detecting parking availability.

* There are 134 images total with 315 instances of open and used parking spaces split 80/20 between training and test data (Edge Impulse default).

* Bounding boxes are drawn around all parking spaces and labeled open if there is no car in the space and used if there is.

* How images where collected and labeled:
    * Device: iPhone 16 Pro 
    * Collection Tool: Edge Impulse's Data Collection Tool
    * Angle: Eye level
    * Time of day: Afternoon
    * Condition: Cloudy 
    * Labeled using Edge Impulse Labeling Queue
    * Human labeled
 
* Edge Impulse Dataset Format