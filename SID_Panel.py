import bpy
from bpy.types import (
    Context,
    Panel,
)
from .SID_Settings import SID_DenoiseRenderStatus, SID_Settings, SID_TemporalDenoiserStatus

class SID_PT_Panel(Panel):

    bl_label = "Create Super Denoiser"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "render"
    bl_category = 'Pidgeon-Tools'

    def draw_header(self, context: Context):
        layout = self.layout
        layout.label(text="", icon='SHADERFX')

    def draw(self, context: Context):
        layout = self.layout
        scene = context.scene
        settings: SID_Settings = scene.sid_settings
        denoise_render_status: SID_DenoiseRenderStatus = settings.denoise_render_status
        temporal_denoiser_status: SID_TemporalDenoiserStatus = settings.temporal_denoiser_status
        RenderEngine = scene.render.engine
        view_layer = context.view_layer
        cycles_view_layer = view_layer.cycles

        # do we have to use the old layout engine?
        legacy_layout = bpy.app.version < (2, 90)

        # currently rendering noisy frames?
        is_rendering = denoise_render_status.is_rendering
        # currently denoising?
        is_denoising = temporal_denoiser_status.is_denoising

        panel_active = not is_rendering and not is_denoising

        layout.use_property_split = True

        #######################
        ### DECIDE DENOISER ###
        #######################

        if RenderEngine == "CYCLES":
            denoiser_type = layout.column(align=True)
            denoiser_type.active = panel_active

            denoiser_type.prop(
                settings,
                "denoiser_type",
                expand=True,
                text="Denoiser Type"
                )

            layout.separator()
        else:
            denoiser_type = "SID"

        if settings.denoiser_type == "SID":

            CompatibleWith = [
                'CYCLES',
                'LUXCORE',
                'octane',
                'PRMAN_RENDER'
            ]

            if not RenderEngine in CompatibleWith:
                cycles_warning = layout.column(align=True)
                cycles_warning.label(
                    text="SID is not yet compatible with this render engine.", icon='ERROR'
                    )
                cycles_warning.label(
                    text="       Please change the render engine to a compatible one."
                    )
                layout.separator()

            quality = layout.column(align=True)
            quality.prop(
                settings,
                "quality",
                text="Quality"
                )
            if settings.quality == 'STANDARD':
                quality.label(
                    text="Denoise the whole image in a single pass.",
                    icon='INFO'
                    )
                quality.label(
                    text="       Maximum compositing speed and least memory consumption."
                    )
            elif settings.quality == 'HIGH':
                quality.label(
                    text="Denoise related render passes in groups.", icon='INFO'
                    )
                quality.label(
                    text="       Moderate compositing speed and increased memory consumption."
                    )
            elif settings.quality == 'SUPER':
                if RenderEngine == 'octane':
                    quality.label(
                        text="Renderer does not support super quality.", icon='INFO'
                        )
                    quality.label(
                        text="       Will use high quality setting instead"
                    )
                else:
                    quality.label(
                        text="Denoise each render pass separately.", icon='INFO'
                        )
                    quality.label(
                        text="       Slowest compositing speed and greatly increased memory consumption."
                        )
            layout.separator()

            if settings.quality != "STANDARD":
                passes = layout.column(align=True)
                passes.label(
                    text="Render passes:"
                    )
                
                subpasses = passes.row(align=True)
                subpasses.use_property_split = False

                ##############
                ### CYCLES ###
                ##############
                if RenderEngine == 'CYCLES':
                    subpasses.prop(
                        settings,
                        "use_emission",
                        text="Emission",
                        toggle=True
                        )
                    subpasses.prop(
                        settings,
                        "use_transmission",
                        text="Transmission",
                        toggle=True
                        )
                    subpasses.prop(
                        settings,
                        "use_environment",
                        text="Environment",
                        toggle=True
                        )

                    subpasses.prop(
                        settings,
                        "use_volumetric",
                        text="Volumetric",
                        toggle=True
                        )
                ###############
                ### LUXCORE ###
                ###############
                if RenderEngine == 'LUXCORE':   
                    subpasses.prop(
                        settings,
                        "use_emission",
                        text="Emission",
                        toggle=True
                        )
                    subpasses.prop(
                        settings,
                        "use_transmission",
                        text="Transmission",
                        toggle=True
                        )
                    if settings.use_transmission and settings.use_emission:
                        subpasses.prop(
                            settings,
                            "use_caustics",
                            text="Caustics",
                            toggle=True
                            )
                ##############
                ### OCTANE ###
                ##############
                if RenderEngine == 'octane':    
                    subpasses.prop(
                        settings,
                        "use_emission",
                        text="Emission",
                        toggle=True
                        )
                    subpasses.prop(
                        settings,
                        "use_refraction",
                        text="Refraction",
                        toggle=True
                        )
                    subpasses.prop(
                        settings,
                        "use_transmission",
                        text="Transmission",
                        toggle=True
                        )
                    subpasses.prop(
                        settings,
                        "use_sss",
                        text="SSS",
                        toggle=True
                        )
                    subpasses.prop(
                        settings,
                        "use_volumetric",
                        text="Volumetric",
                        toggle=True
                        )
                #################
                ### RENDERMAN ###
                #################
                if RenderEngine == 'PRMAN_RENDER':
                    subpasses.prop(
                        settings,
                        "use_emission",
                        text="Emission",
                        toggle=True
                        )
                    subpasses.prop(
                        settings,
                        "use_sss",
                        text="SSS",
                        toggle=True
                        )

                layout.separator()

            advanced = layout.column(align=True)
            advanced.label(
                text="Advanced:"
                )
            
            layout.operator("object.superimagedenoise", icon='SHADERFX', text="Refresh Super Denoiser")
            #advanced.prop(settings,"compositor_reset",text="refresh SID")

            layout.separator()



            if settings.quality != "STANDARD":
                advanced.prop(settings, "use_mlEXR", text="Use Multi-Layer EXR")
                layout.separator()

            layout.operator("object.superimagedenoise", icon='SHADERFX')

        else:
            ##### TEMPORAL #####

            fileio = layout.column(align=True)
            fileio.active = panel_active

            fileio.label(text="Temporal has inferior denoising quality to SID and will be discontinued!", icon='INFO')

            fileio.prop(settings, "inputdir", text="Noisy EXR images")
            fileio.separator()

            fileio.prop(settings, "outputdir", text="Clean EXR images")
            fileio.separator()

            col = fileio.column(align=True)
            col.prop(scene.render, "use_overwrite", text="Overwrite existing files")
            layout.separator()

            tdrender = layout.column(align=True)
            if is_rendering:
                tdrender.operator("object.temporaldenoise_render_stop", icon='CANCEL')
            else:
                tdrender.active = panel_active
                tdrender.operator("object.temporaldenoise_render", icon='RENDER_ANIMATION')

            tdrender.separator()

            tdsettings = layout.row()
            tdsettings.active = panel_active
            tdsettings.prop(cycles_view_layer, "denoising_radius", text="Radius")
            tdsettings.prop(cycles_view_layer, "denoising_neighbor_frames", text="Range")

            tdsettings = layout.column()
            tdsettings.active = panel_active
            tdsettings.prop(cycles_view_layer, "denoising_strength", slider=True, text="Strength")
            tdsettings.prop(cycles_view_layer, "denoising_feature_strength", slider=True, text="Feature Strength")
            tdsettings.prop(cycles_view_layer, "denoising_relative_pca")

            layout.separator()

            tdsettings = layout.column()
            tdsettings.active = panel_active and (cycles_view_layer.use_denoising or cycles_view_layer.denoising_store_passes)

            if legacy_layout:
                split = tdsettings.split(factor=0.5)
                col = split.column()
                col.alignment = 'RIGHT'
                col.label(text="Diffuse")
                row = split.row(align=True)
                row.use_property_split = False
            else:
                row = tdsettings.row(heading="Diffuse", align=True)
            row.prop(cycles_view_layer, "denoising_diffuse_direct", text="Direct", toggle=True)
            row.prop(cycles_view_layer, "denoising_diffuse_indirect", text="Indirect", toggle=True)

            if legacy_layout:
                split = tdsettings.split(factor=0.5)
                col = split.column()
                col.alignment = 'RIGHT'
                col.label(text="Glossy")
                row = split.row(align=True)
                row.use_property_split = False
            else:
                row = tdsettings.row(heading="Glossy", align=True)
            row.prop(cycles_view_layer, "denoising_glossy_direct", text="Direct", toggle=True)
            row.prop(cycles_view_layer, "denoising_glossy_indirect", text="Indirect", toggle=True)

            if legacy_layout:
                split = tdsettings.split(factor=0.5)
                col = split.column()
                col.alignment = 'RIGHT'
                col.label(text="Transmission")
                row = split.row(align=True)
                row.use_property_split = False
            else:
                row = tdsettings.row(heading="Glossy", align=True)
            row.prop(cycles_view_layer, "denoising_transmission_direct", text="Direct", toggle=True)
            row.prop(cycles_view_layer, "denoising_transmission_indirect", text="Indirect", toggle=True)

            layout.separator()

            tddenoise = layout.column(align=True)
            tddenoise.active = True
            if is_denoising:
                tddenoise.operator("object.temporaldenoise_denoise_stop", icon='CANCEL')
                tddenoise.separator()
                tddenoise.label(text=f"{temporal_denoiser_status.files_remaining} files remaining", icon='INFO')
                tddenoise.prop(temporal_denoiser_status, "percent_complete")
            else:
                tddenoise.active = panel_active
                tddenoise.operator("object.temporaldenoise_denoise", icon='SHADERFX')
        
        layout.separator()
        col = layout.column()
        op = col.operator("wm.url_open", text="Support", icon="URL")
        op.url = "https://discord.gg/cnFdGQP"
