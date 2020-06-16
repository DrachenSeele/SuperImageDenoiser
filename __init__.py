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

from . import SuperImageDenoiser

def register():
    SuperImageDenoiser.register()

def unregister():
    SuperImageDenoiser.unregister()
