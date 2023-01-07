import bpy
import os
from bpy.types import NodeTree, Node, NodeLink, NodeSocket
from typing import Callable
from ..SID_Settings import SID_Settings
def find_node(start_node: Node, predicate: Callable[[Node], bool], recursive: bool = False):
    #Finds the first Node attached to start_node that matches a predicate condition.
    #If recursive is True, this function will recursively search via all linked Output sockets.

    # Search all Outputs of provided starting Node
    for output in start_node.outputs:
        # Search all Nodes linked to this Output socket
        link: NodeLink
        for link in output.links:
            if not link.is_valid:
                continue

            if predicate(link.to_node):
                return link.to_node

            if recursive:
                node = find_node(link.to_node, predicate, recursive)
                if node:
                    return node
    return None

def is_sid_super_group(node: Node):
    #Predicate that returns True if node is a SuperImageDenoiser
    return (
        node.bl_idname == 'CompositorNodeGroup'
        and node.name.startswith(("sid_node", ".SuperImageDenoiser"))
        )
def is_composite_output(node: Node):
    #Predicate that returns True if node is a Composite Output
    return node.bl_idname == 'CompositorNodeComposite'
def is_sid_mlexr_file_output(node: Node):
    #Predicate that returns True if node is a SID Multi-Layer EXR File Output
    return (
        node.bl_idname == 'CompositorNodeOutputFile'
        and node.name.startswith("mlEXR Node")
        )
def is_sid_temporal_output(node: Node):
    #Predicate that returns True if node is a SID Temporal Output
    return (
        node.bl_idname == 'CompositorNodeOutputFile'
        and node.name.startswith("Temporal Output")
        )

def create_temporal_median(Minimum: bool):
    #Create median value node group
    if Minimum:
        MinOrMax = "MINIMUM"
        MedianName = ".MedianMin"
    else:
        MinOrMax = "MAXIMUM"
        MedianName = ".MedianMax"

    median_value_tree: NodeTree = bpy.data.node_groups.new(type="CompositorNodeTree", name=MedianName)
    median_value_tree_input = median_value_tree.nodes.new("NodeGroupInput")
    median_value_tree_input.location = (-200, 0)

    median_value_tree.inputs.new("NodeSocketColor", "a")
    median_value_tree.inputs.new("NodeSocketColor", "b")
    median_value_tree.outputs.new("NodeSocketColor", "Median Image")

    separate_color_0 = median_value_tree.nodes.new(type="CompositorNodeSeparateColor")
    separate_color_0.location = (0, 0)
    
    separate_color_1 = median_value_tree.nodes.new(type="CompositorNodeSeparateColor")
    separate_color_1.location = (0, -200)

    median_r = median_value_tree.nodes.new(type="CompositorNodeMath")
    median_r.operation = MinOrMax
    median_r.location = (200, 0)
    
    meidan_g = median_value_tree.nodes.new(type="CompositorNodeMath")
    meidan_g.operation = MinOrMax
    meidan_g.location = (200, -200)
    
    median_b = median_value_tree.nodes.new(type="CompositorNodeMath")
    median_b.operation = MinOrMax
    median_b.location = (200, -400)
    
    median_a = median_value_tree.nodes.new(type="CompositorNodeMath")
    median_a.operation = MinOrMax
    median_a.location = (200, -600)

    combine_color = median_value_tree.nodes.new(type="CompositorNodeCombineColor")
    combine_color.location = (400, 0)

    median_value_tree_output = median_value_tree.nodes.new("NodeGroupOutput")
    median_value_tree_output.location = (600, 0)

    # Link nodes
    median_value_tree.links.new(
        median_value_tree_input.outputs["a"],
        separate_color_0.inputs[0]
        )
    median_value_tree.links.new(
        median_value_tree_input.outputs["b"],
        separate_color_1.inputs[0]
        )
    
    median_value_tree.links.new(
        separate_color_0.outputs[0],
        median_r.inputs[0]
        )
    median_value_tree.links.new(
        separate_color_0.outputs[1],
        meidan_g.inputs[0]
        )
    median_value_tree.links.new(
        separate_color_0.outputs[2],
        median_b.inputs[0]
        )
    median_value_tree.links.new(
        separate_color_0.outputs[3],
        median_a.inputs[0]
        )
    
    median_value_tree.links.new(
        separate_color_1.outputs[0],
        median_r.inputs[1]
        )
    median_value_tree.links.new(
        separate_color_1.outputs[1],
        meidan_g.inputs[1]
        )
    median_value_tree.links.new(
        separate_color_1.outputs[2],
        median_b.inputs[1]
        )
    median_value_tree.links.new(
        separate_color_1.outputs[3],
        median_a.inputs[1]
        )
    
    median_value_tree.links.new(
        median_r.outputs[0],
        combine_color.inputs[0]
        )
    median_value_tree.links.new(
        meidan_g.outputs[0],
        combine_color.inputs[1]
        )
    median_value_tree.links.new(
        median_b.outputs[0],
        combine_color.inputs[2]
        )
    median_value_tree.links.new(
        median_a.outputs[0],
        combine_color.inputs[3]
        )

    median_value_tree.links.new(
        combine_color.outputs[0],
        median_value_tree_output.inputs['Median Image']
        )

    return median_value_tree

def create_temporal_align():
    #create temporal align node group
    align_tree: NodeTree = bpy.data.node_groups.new(type="CompositorNodeTree", name=".Align")
    align_tree_input = align_tree.nodes.new("NodeGroupInput")
    align_tree_input.location = (-200, 0)

    align_tree.inputs.new("NodeSocketColor", "Frame + 0")
    align_tree.inputs.new("NodeSocketVector", "Vector + 0")
    align_tree.inputs.new("NodeSocketColor", "Frame + 1")
    align_tree.inputs.new("NodeSocketColor", "Frame + 2")
    align_tree.inputs.new("NodeSocketVector", "Vector + 2")

    align_tree.outputs.new("NodeSocketColor", "Temporal Aligned")

    displace_frame_0 = align_tree.nodes.new(type="CompositorNodeDisplace")
    displace_frame_0.location = (0, 0)
    displace_frame_0.inputs["X Scale"].default_value = -1
    displace_frame_0.inputs["Y Scale"].default_value = -1
    
    displace_frame_2 = align_tree.nodes.new(type="CompositorNodeDisplace")
    displace_frame_2.location = (0, -200)
    displace_frame_2.inputs["X Scale"].default_value = 1
    displace_frame_2.inputs["Y Scale"].default_value = 1

    median_max_0 = align_tree.nodes.new("CompositorNodeGroup")
    median_max_0.node_tree = create_temporal_median(False)
    median_max_0.location = (200, 0)
    median_min_2 = align_tree.nodes.new("CompositorNodeGroup")
    median_min_2.node_tree = create_temporal_median(True)
    median_min_2.location = (200, -200)
    median_min_a = align_tree.nodes.new("CompositorNodeGroup")
    median_min_a.node_tree = create_temporal_median(True)
    median_min_a.location = (400, 0)
    median_max_a = align_tree.nodes.new("CompositorNodeGroup")
    median_max_a.node_tree = create_temporal_median(False)
    median_max_a.location = (600, 0)

    align_tree_output = align_tree.nodes.new("NodeGroupOutput")
    align_tree_output.location = (800, 0)

    # Link nodes
    align_tree.links.new(
        align_tree_input.outputs["Frame + 0"],
        displace_frame_0.inputs[0]
        )
    align_tree.links.new(
        align_tree_input.outputs["Vector + 0"],
        displace_frame_0.inputs[1]
        )
    align_tree.links.new(
        align_tree_input.outputs["Frame + 1"],
        median_max_0.inputs[0]
        )
    align_tree.links.new(
        align_tree_input.outputs["Frame + 1"],
        median_min_2.inputs[0]
        )
    align_tree.links.new(
        align_tree_input.outputs["Frame + 2"],
        displace_frame_2.inputs[0]
        )
    align_tree.links.new(
        align_tree_input.outputs["Vector + 2"],
        displace_frame_2.inputs[1]
        )

    align_tree.links.new(
        displace_frame_0.outputs[0],
        median_min_a.inputs[1]
        )

    align_tree.links.new(
        displace_frame_2.outputs[0],
        median_max_0.inputs[1]
        )
    align_tree.links.new(
        displace_frame_2.outputs[0],
        median_min_2.inputs[1]
        )
    
    align_tree.links.new(
        median_max_0.outputs[0],
        median_min_a.inputs[0]
        )
    align_tree.links.new(
        median_min_2.outputs[0],
        median_max_a.inputs[1]
        )
    align_tree.links.new(
        median_min_a.outputs[0],
        median_max_a.inputs[0]
        )
    
    align_tree.links.new(
        median_max_a.outputs[0],
        align_tree_output.inputs["Temporal Aligned"]
        )

    return align_tree

def create_temporal_setup(scene,settings):
    #setup node groups
    
    scene.use_nodes = True
    ntree = scene.node_tree
    path_noisy = settings.inputdir + "noisy/"
    path_denoised = settings.inputdir + "denoised/"

    # Clear Compositor Output
    for node in ntree.nodes:
        ntree.nodes.remove(node)
    
    #count files rendered
    file_count = 0
    for file in os.listdir(path_noisy):
        if file.endswith(".exr"):
            file_count += 1

    Frame_0 = ntree.nodes.new(type="CompositorNodeImage")
    Frame_0.image = bpy.data.images.load(path_noisy + str(0).zfill(6) + ".exr")
    Frame_0.location = (-200, 400)

    Frame_1 = ntree.nodes.new(type="CompositorNodeImage")
    Frame_1.image = bpy.data.images.load(path_noisy + str(1).zfill(6) + ".exr")
    Frame_1.location = (-200, 0)

    Frame_2 = ntree.nodes.new(type="CompositorNodeImage")
    Frame_2.image = bpy.data.images.load(path_noisy + str(2).zfill(6) + ".exr")
    Frame_2.location = (-200, -400)

    TempAlign = ntree.nodes.new("CompositorNodeGroup")
    TempAlign.node_tree = create_temporal_align()
    TempAlign.location = (0, 0)

    OutputNode = ntree.nodes.new(type="CompositorNodeComposite")
    OutputNode.location = (200, 0)

    #link frame_0 node with tempalign node in the compositor
    ntree.links.new(Frame_0.outputs[1], TempAlign.inputs[0])
    ntree.links.new(Frame_0.outputs[0], TempAlign.inputs[1])
    
    ntree.links.new(Frame_1.outputs[1], TempAlign.inputs[2])
    
    ntree.links.new(Frame_2.outputs[1], TempAlign.inputs[3])
    ntree.links.new(Frame_2.outputs[0], TempAlign.inputs[4])

    ntree.links.new(TempAlign.outputs[0], OutputNode.inputs[0])

    #go through each file and render frame

    for frame in range(0, file_count - 2):
        Frame_0.image = bpy.data.images.load(path_noisy + str(frame).zfill(6) + ".exr")
        Frame_1.image = bpy.data.images.load(path_noisy + str(frame + 1).zfill(6) + ".exr")
        Frame_2.image = bpy.data.images.load(path_noisy + str(frame + 2).zfill(6) + ".exr")
        scene.frame_current = frame
        scene.frame_start = 1
        scene.frame_end = file_count
        scene.render.filepath = path_denoised + str(frame).zfill(6) + ".png"
        bpy.ops.render.render(animation = False, write_still = True, scene = scene.name)
    
