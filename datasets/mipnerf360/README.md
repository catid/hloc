# Custom data demo with hloc

This shows how to use a folder of JPG images from a camera to localize the photos relative to eachother with hloc.


## Install hloc before anything else:

```
git clone https://github.com/catid/hloc
git submodule update --init --recursive
cd hloc

conda create -n hloc python=3.10
conda activate hloc
pip install -e .
```


## Requires COLMAP 3.8 with CUDA support

To run the `colmap patch_match_stereo` command you'll need to install colmap from source from https://github.com/colmap/colmap with CUDA support.

Newer master version of colmap does not work with Pixel Perfect SfM so we must use the last stable release 3.8.

I needed to install the following Ubuntu packages and set a config option to build COLMAP:

```
sudo apt install -y libboost-all-dev libeigen3-dev libflann-dev libsqlite3-dev libopengl-dev libglx-dev libgl-dev libceres-dev libcgal-dev libglew-dev libfreeimage-dev libmetis-dev

sudo apt install -y qtcreator qtbase5-dev qt5-qmake cmake

git clone https://github.com/colmap/colmap.git

cd colmap
git checkout 3.8
git submodule update --init --recursive

mkdir build
cd build

cmake -DCMAKE_CUDA_ARCHITECTURES=native -DCMAKE_BUILD_TYPE=Release ..

make -j20

sudo make install
```


## Requires pycolmap v0.4.0

```
git clone https://github.com/colmap/pycolmap.git
cd pycolmap
git checkout v0.4.0
git submodule update --init --recursive

conda activate hloc
pip install -e .
```


## Requires Pixel Perfect SfM

I had to make some changes to this repo to get it working so please clone from my github.

Install pixel-perfect-sfm in the hloc conda environment:

```
git clone https://github.com/catid/pixel-perfect-sfm
cd pixel-perfect-sfm
git submodule update --init --recursive

conda activate hloc
pip install -e .
```

In order to get this to work I had to edit the COLMAP installed scripts.  Maybe try without doing this first in case someone fixed it.  I edited this file:

```
sudo vi /usr/local/share/colmap/cmake/FindDependencies.cmake
```

To set the default architecture, which seems to be missing from the Python wheel build:

```
if(CUDA_ENABLED AND CUDA_FOUND)
    set(CMAKE_CUDA_ARCHITECTURES "native")    <- add this line
    if(NOT DEFINED CMAKE_CUDA_ARCHITECTURES)
        message(
            FATAL_ERROR "You must set CMAKE_CUDA_ARCHITECTURES to e.g. 'native', 'all-major', '70', etc. "
            "More information at https://cmake.org/cmake/help/latest/prop_tgt/CUDA_ARCHITECTURES.html")
    endif()
```


## Demo

Extract the test images:

```
cd datasets/mipnerf360/
wget http://storage.googleapis.com/gresearch/refraw360/360_v2.zip
unzip 360_v2.zip
```


Run the demo:

```
cd datasets/mipnerf360/
conda activate hloc

python map_bicycle.py

# This runs the Pixel-Perfect SfM step for sparse reconstruction, so now we proceed with the rest of the normal pipeline for a dense pointcloud reconstruction:

colmap image_undistorter \
   --image_path bicycle/images \
   --input_path outputs/bicycle/sfm \
   --output_path outputs/bicycle/sfm/dense \
   --output_type COLMAP
```


## Discussion

The feature points and matching benefit from a fast GPU.  Running two RTX 4090s in one PC is totally doable, especially if one of them is a water-cooled variety.  COLMAP makes good use of multiple GPUs if you have them during the `patch_match_stereo` step, which is the longest step by far.

You don't need a server-class CPU.  Only a few steps are fully parallel on CPU, so a desktop gaming PC with a fast consumer CPU/GPU optimized for single-core performance is ideal for running this software in terms of price/performance trade-offs.

It caches the results of the feature point/matching steps so you don't need to perform that again, but the 3D reconstruction is run anew if you execute the script again.  So, to incorporate more pictures into the folder, you'll have to delete the outputs to make it run all the steps from the top.

It seems like it supports multiple cameras in a capture rig since it's treating each photo as coming from a unique camera, and the focal length and other intrinsics are optimized independently for each camera.
