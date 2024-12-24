'''OpenGL extension NV.depth_buffer_float

This module customises the behaviour of the 
OpenGL.raw.GL.NV.depth_buffer_float to provide a more 
Python-friendly API

Overview (from the spec)
	
	This extension provides new texture internal formats whose depth
	components are stored as 32-bit floating-point values, rather than the
	normalized unsigned integers used in existing depth formats.
	Floating-point depth textures support all the functionality supported for
	fixed-point depth textures, including shadow mapping and rendering support
	via EXT_framebuffer_object.  Floating-point depth textures can store
	values outside the range [0,1].
	
	By default, OpenGL entry points taking depth values implicitly clamp the
	values to the range [0,1].  This extension provides new DepthClear,
	DepthRange, and DepthBoundsEXT entry points that allow applications to
	specify depth values that are not clamped.
	
	Additionally, this extension provides new packed depth/stencil pixel
	formats (see EXT_packed_depth_stencil) that have 64-bit pixels consisting
	of a 32-bit floating-point depth value, 8 bits of stencil, and 24 unused
	bites.  A packed depth/stencil texture internal format is also provided.
	
	This extension does not provide support for WGL or GLX pixel formats with
	floating-point depth buffers.  The existing (but not commonly used)
	WGL_EXT_depth_float extension could be used for this purpose.
	

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/NV/depth_buffer_float.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.GL import _types, _glgets
from OpenGL.raw.GL.NV.depth_buffer_float import *
from OpenGL.raw.GL.NV.depth_buffer_float import _EXTENSION_NAME

def glInitDepthBufferFloatNV():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )


### END AUTOGENERATED SECTION