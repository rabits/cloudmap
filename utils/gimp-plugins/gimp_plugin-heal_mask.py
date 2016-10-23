#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os, re, glob
from gimpfu import *
from gimpenums import *

def my_script_function(image, layer, mask_image):
    new_layer = gimp.Layer(image, image.active_drawable.name + " mask", image.width, image.height, RGBA_IMAGE, 100.0, layer.mode)
    image.add_layer(new_layer, 0)
    pdb.gimp_edit_copy_visible(mask_image)
    pdb.gimp_floating_sel_anchor(pdb.gimp_edit_paste(new_layer, TRUE))
    pdb.gimp_image_select_item(image, CHANNEL_OP_REPLACE, image.layers[0])
    image.remove_layer(new_layer)

    pdb.python_fu_heal_selection(image, layer, 50, 0, 0)

    #newname = image.filename.replace('.jpg', '_fix.jpg')
    #pdb.gimp_file_save(image, layer, newname, '?')
    return

register(
    "python-fu-heal-mask",
    "Healing by mask image",
    "Will heal image by mask",
    "Rabit",
    "Rabits",
    "Oct 2016",
    "<Image>/MyScripts/Heal Mask",
    "RGB*, GRAY*",
    [
        (PF_IMAGE, "mask",       "Input mask", None)
    ],
    [],
    my_script_function
)

main()
