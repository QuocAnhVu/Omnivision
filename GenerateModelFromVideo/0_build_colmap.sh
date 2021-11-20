#! /bin/sh
# For Fedora adapted from an Ubuntu script
# If possible, make your life easier and install a binary ;)

# Install COLMAP Dependencies
sudo dnf install \
    git \
    cmake \
    make automake gcc gcc-c++ kernel-devel \
    boost-program-options \
    boost-filesystem \
    boost-graph \
    boost-system \
    boost-test \
    boost-static \
    eigen3-devel \
    suitesparse-devel \
    freeimage-devel \
    glog-devel \
    gflags-devel \
    glew-devel \
    qt5-qtbase \
    qt5-qtbase-devel \
    CGAL-devel

# Install Ceres Solver - Nonlinear Optimization Library
sudo dnf install atlas-devel
git clone https://ceres-solver.googlesource.com/ceres-solver
cd ceres-solver
git checkout $(git describe --tags) # Checkout the latest release
mkdir build
cd build
cmake .. -DBUILD_TESTING=OFF -DBUILD_EXAMPLES=OFF
make -j
sudo make install

# Install COLMAP
git clone https://github.com/colmap/colmap.git
cd colmap
git checkout dev
mkdir build
cd build
cmake ..
make -j
sudo make install