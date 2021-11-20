# These parameters are specific to computer 
# For Linux adapted from a Windows script
# Original here: https://peterfalkingham.com/2017/08/14/automating-free-photogrammetry-scripts-i-use/

# Set colmap directory:
COLMAP=/usr/local/bin/COLMAP

# Set openMVS directory
OpenMVS=/usr/local/bin/OpenMVS

$COLMAP feature_extractor --database_path database.db --image_path .
$COLMAP exhaustive_matcher --database_path database.db
mkdir sparse
$COLMAP mapper --database_path database.db --image_path . --output_path sparse
$COLMAP model_converter --input_path sparse/0 --output_path model.nvm --output_type NVM
$OpenMVS/InterfaceVisualSFM model.nvm
$OpenMVS/DensifyPointCloud model.mvs
$OpenMVS/ReconstructMesh model_dense.mvs
$OpenMVS/RefineMesh --resolution-level 1 model_dense_mesh.mvs
$OpenMVS/TextureMesh --export-type obj model_dense_mesh_refine.mvs
mkdir model/
cp *.obj model/
cp *.mtl model/
cp model_dense_mesh_refine*.jpg model/