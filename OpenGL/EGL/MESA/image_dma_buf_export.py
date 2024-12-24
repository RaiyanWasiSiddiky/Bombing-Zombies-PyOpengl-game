'''OpenGL extension MESA.image_dma_buf_export

This module customises the behaviour of the 
OpenGL.raw.EGL.MESA.image_dma_buf_export to provide a more 
Python-friendly API

The official definition of this extension is available here:
http://www.opengl.org/registry/specs/MESA/image_dma_buf_export.txt
'''
from OpenGL import platform, constant, arrays
from OpenGL import extensions, wrapper
import ctypes
from OpenGL.raw.EGL import _types, _glgets
from OpenGL.raw.EGL.MESA.image_dma_buf_export import *
from OpenGL.raw.EGL.MESA.image_dma_buf_export import _EXTENSION_NAME

def glInitImageDmaBufExportMESA():
    '''Return boolean indicating whether this extension is available'''
    from OpenGL import extensions
    return extensions.hasGLExtension( _EXTENSION_NAME )


### END AUTOGENERATED SECTION