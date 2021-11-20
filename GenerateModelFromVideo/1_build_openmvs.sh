#! /bin/sh
# For Fedora adapted from an Ubuntu script
# If possible, make your life easier and install a binary ;)

sudo dnf -y install \
  git \
  cmake \
  libpng-devel \
  openjpeg-devel \
  libtiff-devel \
  mesa-libGLU-devel
main_path=`pwd`

#Eigen (Required)
git clone https://gitlab.com/libeigen/eigen.git --branch 3.4
mkdir eigen_build && cd eigen_build
cmake . ../eigen
make && sudo make install
cd ..

#Boost (Required)
sudo dnf -y install \
  boost-iostreams \
  boost-program-options \
  boost-system \
  boost-serialization

#OpenCV (Required)
sudo dnf -y install opencv-devel

#CGAL (Required)
sudo dnf -y install CGAL-devel CGAL-qt5-devel

#VCGLib (Required)
git clone https://github.com/cdcseacave/VCG.git vcglib

#Ceres (Optional)
# sudo apt-get -y install libatlas-base-dev libsuitesparse-dev
# git clone https://ceres-solver.googlesource.com/ceres-solver ceres-solver
# mkdir ceres_build && cd ceres_build
# cmake . ../ceres-solver/ -DMINIGLOG=ON -DBUILD_TESTING=OFF -DBUILD_EXAMPLES=OFF
# make -j2 && sudo make install
# cd ..

#GLFW3 (Optional)
sudo dnf -y install freeglut glew-devel glfw-devel

#OpenMVS
#If you want to use OpenMVS as shared library, add to the CMake command:
# -DBUILD_SHARED_LIBS=ON
git clone https://github.com/cdcseacave/openMVS.git openMVS
mkdir openMVS_build && cd openMVS_build
CGAL_ROOT=/usr/share/cmake/CGAL cmake . ../openMVS -DCMAKE_BUILD_TYPE=Release -DVCG_ROOT="../vcglib" 

#Install OpenMVS library (optional):
make -j2 && sudo make install