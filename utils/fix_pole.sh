#!/bin/sh
#
# Script will process folder and fix polar warp on cloud images
# Required: gimp-2.8, python_fu_fix_polar, python_fu_fix_polar, python_fu_heal_selection (registry)
#

dir=$1

[ -d "$dir" ] || exit 1

cd "$dir"

for file in *.jpg; do
    gimp -i --batch-interpreter python-fu-eval -b 'image = gimp.image_list()[0]; print("%s ..." % image.filename); pdb.python_fu_fix_polar(image, image.active_drawable); pdb.gimp_file_save(image, image.active_drawable, image.filename.replace(".jpg","_pol.jpg"), "?")' -b 'pdb.gimp_quit(0)' $file
done
