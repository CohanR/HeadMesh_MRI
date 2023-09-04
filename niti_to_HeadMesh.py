import nibabel as nib
import numpy as np
import matplotlib.pyplot as plt
from skimage import measure, filters, morphology 
from vedo import Mesh, write
from skimage.measure import label, regionprops

# Load the T1 image
img = nib.load("/Volumes/Remy_Neuro/T1s_mesh_tbs/sub-001_rc_T1w.nii.gz")
data = img.get_fdata()

# Visualise the T1 image in axial, sagittal, and coronal views
fig, axes = plt.subplots(1, 4, figsize=(20, 5))

# Axial
axes[0].imshow(data[data.shape[0] // 2], cmap="gray")
axes[0].set_title("Axial")

# Sagittal
axes[1].imshow(data[:, data.shape[1] // 2, :], cmap="gray")
axes[1].set_title("Sagittal")

# Coronal
axes[2].imshow(data[:, :, data.shape[2] // 2], cmap="gray")
axes[2].set_title("Coronal")

# Histogram with Otsu's threshold
threshold_otsu = filters.threshold_otsu(data)
axes[3].hist(data.ravel(), bins=100, color='gray', alpha=0.7)
axes[3].axvline(threshold_otsu, color='red', linestyle='--')
axes[3].set_title("Histogram (Otsu's threshold in red)")

plt.tight_layout()
plt.show()

print(f"Suggested threshold based on Otsu's method: {threshold_otsu:.4f}")
threshold = float(input("Enter threshold value based on visualisation: "))


# Convert the data to binary based on the threshold
binary_data = np.where(data > threshold, 1, 0)

# Apply morphological closing to the binary data to create a more solid object
selem = morphology.ball(3)  # Adjust the size if needed based on the quality of the output
closed_data = morphology.binary_closing(binary_data, selem)

# Label connected components
from skimage.measure import label, regionprops  # <-- Importing label and regionprops
label_data = label(closed_data)

# Find the largest connected component (assumed to be the brain)
regions = regionprops(label_data)
largest_region = max(regions, key=lambda x: x.area)

# Create a new binary image where only the largest connected component is retained
cleaned_data = np.where(label_data == largest_region.label, 1, 0)

# Extract the mesh from the cleaned binary data for the hollow mesh
verts, faces, normals, values = measure.marching_cubes(cleaned_data)
hollow_mesh = Mesh([verts, faces])

# For the full mesh, use the original binary data
verts_full, faces_full, normals_full, values_full = measure.marching_cubes(binary_data)
full_mesh = Mesh([verts_full, faces_full])

# Save the meshes in multiple formats
mesh_name_base = "/Volumes/Remy_Neuro/T1s_mesh_tbs/sub-001_mesh_bxtract"
write(full_mesh, mesh_name_base + ".vtk")
write(full_mesh, mesh_name_base + ".stl")
write(full_mesh, mesh_name_base + ".ply")

hollow_mesh_name_base = mesh_name_base + "_hollow"
write(hollow_mesh, hollow_mesh_name_base + ".vtk")
write(hollow_mesh, hollow_mesh_name_base + ".stl")
write(hollow_mesh, hollow_mesh_name_base + ".ply")

print("Saved meshes successfully.")
