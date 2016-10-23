#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gimpfu import *
from gimpenums import *

def my_script_function(image, layer):
    pdb.gimp_image_select_rectangle(image, CHANNEL_OP_REPLACE, 0, 0, image.width, 400)
    pdb.gimp_image_select_rectangle(image, CHANNEL_OP_ADD, 0, image.height-400, image.width, 400)

    print("Healing poles...")
    pdb.python_fu_heal_selection(image, layer, 50, 0, 0)
    pdb.gimp_edit_copy(layer)

    print("Creating new image to fix poles...")
    new_img = pdb.gimp_edit_paste_as_new()
    pdb.gimp_image_select_rectangle(new_img, CHANNEL_OP_ADD, 0, new_img.height-400, new_img.width, 400)
    pdb.gimp_edit_cut(new_img.active_drawable)
    pdb.gimp_selection_none(new_img)
    pasted_layer = pdb.gimp_edit_paste(new_img.active_layer, TRUE)
    pasted_layer.set_offsets(0,400)
    pdb.gimp_floating_sel_anchor(pasted_layer)
    pdb.gimp_image_crop(new_img, new_img.width, 400*2, 0, 0)

    pdb.gimp_context_set_gradient('FG to Transparent')
    c = pdb.gimp_context_get_foreground()
    c.set(1.0, 1.0, 1.0, 1.0)
    pdb.gimp_context_set_foreground(c)

    print("Drawing gradients...")
    pdb.gimp_blend(new_img.active_drawable, FG_TRANSPARENT_MODE, NORMAL_MODE, GRADIENT_LINEAR, 100.0, 60.0, REPEAT_NONE, FALSE, FALSE, 1, 0.0, TRUE, 0, 0, 0, new_img.height/2)
    pdb.gimp_blend(new_img.active_drawable, FG_TRANSPARENT_MODE, NORMAL_MODE, GRADIENT_LINEAR, 100.0, 60.0, REPEAT_NONE, FALSE, FALSE, 1, 0.0, TRUE, 0, new_img.height, 0, new_img.height/2)

    print("Correcting polars...")
    pdb.python_fu_polar_correction(new_img, new_img.active_drawable)

    pdb.gimp_edit_copy_visible(new_img)

    print("Paste to the original image...")
    pdb.gimp_selection_none(image)
    image.new_layer("poles", image.width, image.height, RGBA_IMAGE)
    image.active_layer.set_offsets(0,0)

    pasted_layer = pdb.gimp_edit_paste(image.active_layer, TRUE)
    pasted_layer.set_offsets(0,0)
    pdb.gimp_floating_sel_anchor(pasted_layer)

    pdb.gimp_image_select_rectangle(image, CHANNEL_OP_REPLACE, 0, new_img.height/2, image.width, new_img.height/2)
    pdb.gimp_edit_cut(image.active_drawable)
    pdb.gimp_selection_none(image)
    pasted_layer = pdb.gimp_edit_paste(image.active_layer, TRUE)
    pasted_layer.set_offsets(0,image.height-new_img.height/2)
    pdb.gimp_floating_sel_anchor(pasted_layer)
    pdb.gimp_image_merge_down(image, image.active_drawable, CLIP_TO_IMAGE)

    #newname = image.filename.replace('.jpg', '_fix.jpg')
    #pdb.gimp_file_save(image, layer, newname, '?')
    return

register(
    "python-fu-fix-polar",
    "Prepare clouds polar 400px from top and from bottom to use on texture",
    "Prepare clouds polar 400px from top and from bottom to use on texture",
    "Rabit",
    "Rabits",
    "Oct 2016",
    "<Image>/MyScripts/Fix Polar",
    "RGB*, GRAY*",
    [
    ],
    [],
    my_script_function
)

main()
