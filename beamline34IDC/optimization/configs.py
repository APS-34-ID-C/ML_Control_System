#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------- #
# Copyright (c) 2021, UChicago Argonne, LLC. All rights reserved.         #
#                                                                         #
# Copyright 2021. UChicago Argonne, LLC. This software was produced       #
# under U.S. Government contract DE-AC02-06CH11357 for Argonne National   #
# Laboratory (ANL), which is operated by UChicago Argonne, LLC for the    #
# U.S. Department of Energy. The U.S. Government has rights to use,       #
# reproduce, and distribute this software.  NEITHER THE GOVERNMENT NOR    #
# UChicago Argonne, LLC MAKES ANY WARRANTY, EXPRESS OR IMPLIED, OR        #
# ASSUMES ANY LIABILITY FOR THE USE OF THIS SOFTWARE.  If software is     #
# modified to produce derivative works, such modified software should     #
# be clearly marked, so as not to confuse it with the version available   #
# from ANL.                                                               #
#                                                                         #
# Additionally, redistribution and use in source and binary forms, with   #
# or without modification, are permitted provided that the following      #
# conditions are met:                                                     #
#                                                                         #
#     * Redistributions of source code must retain the above copyright    #
#       notice, this list of conditions and the following disclaimer.     #
#                                                                         #
#     * Redistributions in binary form must reproduce the above copyright #
#       notice, this list of conditions and the following disclaimer in   #
#       the documentation and/or other materials provided with the        #
#       distribution.                                                     #
#                                                                         #
#     * Neither the name of UChicago Argonne, LLC, Argonne National       #
#       Laboratory, ANL, the U.S. Government, nor the names of its        #
#       contributors may be used to endorse or promote products derived   #
#       from this software without specific prior written permission.     #
#                                                                         #
# THIS SOFTWARE IS PROVIDED BY UChicago Argonne, LLC AND CONTRIBUTORS     #
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT       #
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS       #
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL UChicago     #
# Argonne, LLC OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,        #
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,    #
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;        #
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER        #
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT      #
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN       #
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE         #
# POSSIBILITY OF SUCH DAMAGE.                                             #
# ----------------------------------------------------------------------- #

from beamline34IDC.simulation.facade.focusing_optics_interface import  MotorResolution
import numpy as np

motor_resolutions = MotorResolution.getInstance()
DEFAULT_MOVEMENT_RANGES = {'hkb_4': [-0.2, 0.2], # in mm
                           'vkb_4': [-0.2, 0.2], # in mm
                           'hkb_3': [-100, 100], # in mrad
                           'vkb_3': [-100, 100], # in mrad
                           'hkb_q': [-20, 20], # in mm
                           'vkb_q': [-20, 20], # in mm
                           'hkb_1_2': [-5, 5], # in mm
                           'vkb_1_2': [-5, 5] # in mm
                           }

# I am adding this because the focusing system interface does not currently contain resolution
# values for hkb_q, vkb_q, hkb_1_2, and vkb_1_2 motors.
DEFAULT_MOTOR_RESOLUTIONS = {'hkb_4': motor_resolutions.get_hkb_motor_4_translation_resolution()[0],
                             'vkb_4': motor_resolutions.get_vkb_motor_4_translation_resolution()[0],
                             'hkb_3': motor_resolutions.get_hkb_motor_3_pitch_resolution()[0],
                             'vkb_3': motor_resolutions.get_vkb_motor_3_pitch_resolution()[0],
                             'hkb_q': 0.1, # in mm
                             'vkb_q': 0.1, # in mm
                             'hkb_1_2': 1e-4, # in mm
                             'vkb_1_2': 1e-4 # in mm
                             }

DEFAULT_MOTOR_TOLERANCES = DEFAULT_MOTOR_RESOLUTIONS


# These values only apply for the simulation with 50k simulated beams
DEFAULT_LOSS_TOLERANCES = {'centroid': 2e-4,
                           'fwhm': 2e-4,
                           'peak_intensity': -np.inf}