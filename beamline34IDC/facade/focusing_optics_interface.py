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
import numpy


class Movement:
    ABSOLUTE = 0
    RELATIVE = 1

class AngularUnits:
    MILLIRADIANS = 0
    DEGREES = 1
    RADIANS = 2

class DistanceUnits:
    MILLIMETERS = 0
    MICRON      = 1

class MotorResolution:
    __instance = None
                                           #value #digits to round
    __coh_slits_motors_resolution        = [1e-7, 7]  # mm
    __vkb_motor_1_2_bender_resolution    = [1e-7, 7]  # mm
    __vkb_motor_3_pitch_resolution       = [1e-4, 4]  # deg
    __vkb_motor_4_translation_resolution = [1e-3, 3]  # mm
    __hkb_motor_1_2_bender_resolution    = [1e-7, 7]  # mm
    __hkb_motor_3_pitch_resolution       = [1e-4, 4]  # deg
    __hkb_motor_4_translation_resolution = [1e-3, 3]  # mm

    @staticmethod
    def getInstance():
      if MotorResolution.__instance == None: MotorResolution()
      return MotorResolution.__instance

    def __init__(self):
      if MotorResolution.__instance != None: raise Exception("This class is a singleton!")
      else: MotorResolution.__instance = self

    def get_coh_slits_motors_resolution(self, units=DistanceUnits.MICRON):        return self.__get_translational_resolution(self.__coh_slits_motors_resolution, units)
    def get_vkb_motor_1_2_bender_resolution(self, units=DistanceUnits.MICRON):    return self.__get_translational_resolution(self.__vkb_motor_1_2_bender_resolution, units)
    def get_vkb_motor_3_pitch_resolution(self, units=AngularUnits.MILLIRADIANS):  return self.__get_rotational_resolution(self.__vkb_motor_3_pitch_resolution, units)
    def get_vkb_motor_4_translation_resolution(self, units=DistanceUnits.MICRON): return self.__get_translational_resolution(self.__vkb_motor_4_translation_resolution, units)
    def get_hkb_motor_1_2_bender_resolution(self, units=DistanceUnits.MICRON):    return self.__get_translational_resolution(self.__hkb_motor_1_2_bender_resolution, units)
    def get_hkb_motor_3_pitch_resolution(self, units=AngularUnits.MILLIRADIANS):  return self.__get_rotational_resolution(self.__hkb_motor_3_pitch_resolution, units)
    def get_hkb_motor_4_translation_resolution(self, units=DistanceUnits.MICRON): return self.__get_translational_resolution(self.__hkb_motor_4_translation_resolution, units)

    @classmethod
    def __get_translational_resolution(cls, resolution_array, units=DistanceUnits.MICRON):
        if units==DistanceUnits.MILLIMETERS: return resolution_array
        elif units==DistanceUnits.MICRON:    return [1e3*resolution_array[0], resolution_array[1] - 3]
        else: raise ValueError("Units not recognized")

    @classmethod
    def __get_rotational_resolution(cls, resolution_array, units=AngularUnits.MILLIRADIANS):
        if units==AngularUnits.DEGREES:        return resolution_array
        elif units==AngularUnits.MILLIRADIANS: return [1e3*numpy.radians(resolution_array[0]), resolution_array[1] - 1]
        elif units==AngularUnits.RADIANS:      return [numpy.radians(resolution_array[0]),     resolution_array[1] + 2]
        else: raise ValueError("Units not recognized")

class AbstractFocusingOptics():

    #####################################################################################
    # This methods represent the run-time interface, to interact with the optical system
    # in real time, like in the real beamline

    def modify_coherence_slits(self, coh_slits_h_center=None, coh_slits_v_center=None, coh_slits_h_aperture=None, coh_slits_v_aperture=None, units=DistanceUnits.MICRON): raise NotImplementedError()
    def get_coherence_slits_parameters(self, units=DistanceUnits.MICRON): raise NotImplementedError() # center x, center z, aperture x, aperture z

    # V-KB -----------------------

    def move_vkb_motor_1_bender(self, pos_upstream, movement=Movement.ABSOLUTE, units=DistanceUnits.MICRON): raise NotImplementedError()
    def get_vkb_motor_1_bender(self, units=DistanceUnits.MICRON): raise NotImplementedError()
    def move_vkb_motor_2_bender(self, pos_downstream, movement=Movement.ABSOLUTE, units=DistanceUnits.MICRON): raise NotImplementedError()
    def get_vkb_motor_2_bender(self, units=DistanceUnits.MICRON): raise NotImplementedError()
    def move_vkb_motor_3_pitch(self, angle, movement=Movement.ABSOLUTE, units=AngularUnits.MILLIRADIANS): raise NotImplementedError()
    def get_vkb_motor_3_pitch(self, units=AngularUnits.MILLIRADIANS): raise NotImplementedError()
    def move_vkb_motor_4_translation(self, translation, movement=Movement.ABSOLUTE, units=DistanceUnits.MICRON): raise NotImplementedError()
    def get_vkb_motor_4_translation(self, units=DistanceUnits.MICRON): raise NotImplementedError()

    # H-KB -----------------------

    def move_hkb_motor_1_bender(self, pos_upstream, movement=Movement.ABSOLUTE, units=DistanceUnits.MICRON): raise NotImplementedError()
    def get_hkb_motor_1_bender(self, units=DistanceUnits.MICRON): raise NotImplementedError()
    def move_hkb_motor_2_bender(self, pos_downstream, movement=Movement.ABSOLUTE, units=DistanceUnits.MICRON): raise NotImplementedError()
    def get_hkb_motor_2_bender(self, units=DistanceUnits.MICRON): raise NotImplementedError()
    def move_hkb_motor_3_pitch(self, angle, movement=Movement.ABSOLUTE, units=AngularUnits.MILLIRADIANS): raise NotImplementedError()
    def get_hkb_motor_3_pitch(self, units=AngularUnits.MILLIRADIANS): raise NotImplementedError()
    def move_hkb_motor_4_translation(self, translation, movement=Movement.ABSOLUTE, units=DistanceUnits.MICRON): raise NotImplementedError()
    def get_hkb_motor_4_translation(self, units=DistanceUnits.MICRON): raise NotImplementedError()

    def get_photon_beam(self, **kwargs): raise NotImplementedError()
