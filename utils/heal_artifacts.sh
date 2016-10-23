#!/bin/sh
#
# Will heal common issues with map top and bottom
# Required: gimp 2.8, python_fu_heal_mask, python_fu_heal_selection (registry)
#

for f in heal_top/*; do
    gimp -i --batch-interpreter python-fu-eval -b 'image = gimp.image_list()[1]; mask_image = gimp.image_list()[0]; print("Image: %s..." % image.filename); print("Mask: %s..." % mask_image.filename); pdb.python_fu_heal_mask(image, image.active_layer, mask_image); pdb.gimp_file_save(image, image.active_layer, image.filename.replace(".jpg", "_fix.jpg"), "?")' -b 'pdb.gimp_quit(0)' "${f}" mask_artifact_top.png
done
for f in heal_bottom/*; do
    gimp -i --batch-interpreter python-fu-eval -b 'image = gimp.image_list()[1]; mask_image = gimp.image_list()[0]; print("Image: %s..." % image.filename); print("Mask: %s..." % mask_image.filename); pdb.python_fu_heal_mask(image, image.active_layer, mask_image); pdb.gimp_file_save(image, image.active_layer, image.filename.replace(".jpg", "_fix.jpg"), "?")' -b 'pdb.gimp_quit(0)' "${f}" mask_artifact_bottom.png
done
