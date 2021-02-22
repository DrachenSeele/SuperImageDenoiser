import bpy

from . import SID_Settings
from .Cycles.SID_Create_Links_Cycles import create_links_cy
from .LuxCore.SID_Create_Links_LuxCore import create_links_lc
from .Octane.SID_Create_Links_Octane import create_links_o

def create_sid_super_denoiser_group(sid_denoiser_tree, settings: SID_Settings):

    RenderEngine = bpy.context.scene.render.engine

    if settings.quality == "STANDARD":
        settings.use_mlEXR = False 


    ##############
    ### CYCLES ###
    ##############
    if RenderEngine == 'CYCLES':
        sid_tree = create_links_cy(sid_denoiser_tree, settings)

    ###############
    ### LUXCORE ###
    ###############
    if RenderEngine == 'LUXCORE':
        sid_tree = create_links_lc(sid_denoiser_tree, settings)

    ##############
    ### OCTANE ###
    ##############
    if RenderEngine == 'octane':
        sid_tree = create_links_o(sid_denoiser_tree, settings)

    return sid_tree
