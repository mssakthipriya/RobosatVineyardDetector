# RobosatVineyardDetector
## Data Preparation
Collect satellite imagery or aerial photographs covering the target vineyard areas.
RoboSat offers an extract command to directly extract data from an OpenStreetMap .pbf dump file.
However, it is limited to default example features like buildings, parking lots, and roads.
Overpass Turbo was used to build a custom query for selecting and downloading vineyard polygons from OpenStreetMap for a specific region of France (Jura).
```
[out:json];
(
area["name"="Jura"]->.region;
way["landuse"="vineyard"](area.region);
relation["landuse"="vineyard"](area.region);
);
out body;
>;
out skel qt;
```
The geojason file that get exported mught have multipolygons, which cannot be handled by robosat. The multipolygons need to be converted to individual polygons and added as separate features before inputting the data into Robosat.
 
## Data Preprocessing
Download robosat from github and follow the installation process. I used a linux system for the whole process and manually installed it.
Convert the imagery to a suitable format compatible with RoboSat.
```
# Make folder structure for dataset
mkdir -p dataset
mkdir -p dataset/training
mkdir -p dataset/training/images
mkdir -p dataset/training/labels
mkdir -p dataset/validation
mkdir -p dataset/validation/images
mkdir -p dataset/validation/labels
mkdir -p myanmar/holdout
mkdir -p myanmar/holdout/images
mkdir -p myanmar/holdout/labels

#Writing cover CSV
# I gave the zoom level as 18
    ./rs cover --zoom ZOOM vineyard_jura_small.geojson vineyards-cover.csv

#Downloading tiles
./rs download --ext png https://api.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}@2x.png?access_token=ACCESS_TOCKEN vineyards-cover.csv vineyards/dataset/holdout/images

#Rasterizing
./rs rasterize --zoom ZOOM --dataset vineyards/config/model-unet.toml vineyard_jura_small.geojson vineyards-cover.csv vineyards/dataset/holdout/labels

```

## Dataset Creation
Prepare a training dataset by combining the preprocessed imagery with annotations.
Divide the dataset into training and validation subsets for model development and evaluation.
## Model Training
Utilize RoboSat's training capabilities to train a deep learning model for vineyard detection.
## Model Evaluation
Assess the trained model's performance by evaluating it on the validation dataset.
Utilize RoboSat's object detection or semantic segmentation capabilities to identify vineyards within the imagery.
## Post-processing
Smooth boundaries, remove false positives, and improve the overall accuracy of the vineyard detection results.
## Visualization and Analysis
Visualize the detected vineyard areas on maps or imagery for further analysis.
## Result Interpretation and Application
Apply the findings to create your desired application
