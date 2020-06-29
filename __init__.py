# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name": "Super Image Denoiser (SID)",
    "author": "Kevin Lorengel, Chris Bond (Kamikaze)",
    "version": (2, 2),
    "blender": (2, 83, 0),
    "location": "Properties > Render > Create Super Denoiser",
    "description": "SID denoises your Cycles renders near-perfectly, with only one click!",
    "warning": "",
    "wiki_url": "https://discord.gg/cnFdGQP",
    "category": "Compositor",
}
import bpy
from bpy.props import (
    PointerProperty,
)
from .SuperImageDenoiser import SID_Create
from .SID_Create_DenoiserGroup import create_sid_super_denoiser_group
from .SID_Create_Group import create_sid_super_group
from .SID_QualityStandart import create_sid_denoiser_standard
from .SID_QualityHigh import create_sid_denoiser_high
from .SID_QualitySuper import create_sid_denoiser_super
from .SID_Settings import SID_Settings
from .SID_Panel import SID_PT_Panel

# Register classes
classes = (
    SID_Settings,
    SID_PT_Panel,
    SID_Create,
)

def register():
    from bpy.utils import register_class

    for cls in classes:
        register_class(cls)

    bpy.types.Scene.sid_settings = PointerProperty(type=SID_Settings)

def unregister():
    from bpy.utils import unregister_class

    del bpy.types.Scene.sid_settings

    for cls in reversed(classes):
        unregister_class(cls)

if __name__ == "__main__":
    register()
