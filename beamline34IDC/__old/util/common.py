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
import Shadow
from Shadow.ShadowTools import write_shadow_surface
from Shadow.ShadowPreprocessorsXraylib import prerefl, bragg
from srxraylib.metrology import dabam
from oasys.util.oasys_util import get_sigma, get_fwhm, get_average
from oasys.util.error_profile_util import DabamInputParameters, calculate_dabam_profile, ErrorProfileInputParameters, calculate_heigth_profile
from oasys.widgets import congruence
from orangecontrib.ml.util.mocks import MockWidget
from orangecontrib.ml.util.data_structures import DictionaryWrapper
from orangecontrib.shadow.util.shadow_objects import ShadowBeam, ShadowOpticalElement, ShadowSource, ShadowOEHistoryItem
from orangecontrib.shadow.util.shadow_util import ShadowPhysics
from orangecontrib.shadow.widgets.special_elements.bl import hybrid_control
import scipy.constants as codata

m2ev = codata.c * codata.h / codata.e

def rotate(origin, point, angle):
    """
    Rotate a point counter-clockwise by a given angle around a given origin.
    """
    # Convert negative angles to positive
    angle = normalise_angle(angle)

    # Convert to radians
    angle = numpy.radians(angle)

    # Convert to radians
    ox, oy = origin
    px, py = point

    # Move point 'p' to origin (0,0)
    _px = px - ox
    _py = py - oy

    # Rotate the point 'p'
    qx = (numpy.cos(angle) * _px) - (numpy.sin(angle) * _py)
    qy = (numpy.sin(angle) * _px) + (numpy.cos(angle) * _py)

    # Move point 'p' back to origin (ox, oy)
    qx = ox + qx
    qy = oy + qy

    return [qx, qy]

def normalise_angle(angle):
    """ If angle is negative then convert it to positive. """
    return (360 + angle) if ((angle != 0) & (abs(angle) == (angle * -1))) else angle

####################################################

# WEIRD MEMORY INITIALIZATION BY FORTRAN. JUST A FIX.
def fix_Intensity(beam_out, polarization=0):
    if polarization == 0:
        beam_out._beam.rays[:, 15] = 0
        beam_out._beam.rays[:, 16] = 0
        beam_out._beam.rays[:, 17] = 0

    return beam_out

####################################################

class ShadowHistogram():
    def __init__(self, hh, vv, data_2D):
        self.hh = hh
        self.vv = vv
        self.data_2D = data_2D

def get_shadow_beam_spatial_distribution(shadow_beam, nbins=201, nolost=1, xrange=None, yrange=None):
    return __shadow_beam_get_distribution_info(shadow_beam._beam.histo2(1, 3, nbins=nbins, nolost=nolost, xrange=xrange, yrange=yrange))

def get_shadow_beam_divergence_distribution(shadow_beam, nbins=201, nolost=1, xrange=None, yrange=None):
    return __shadow_beam_get_distribution_info(shadow_beam._beam.histo2(4, 6, nbins=nbins, nolost=nolost, xrange=xrange, yrange=yrange))

def __shadow_beam_get_distribution_info(ticket):
    ticket['fwhm_h'], ticket['fwhm_quote_h'], ticket['fwhm_coordinates_h'] = get_fwhm(ticket['histogram_h'], ticket['bin_h_center'])
    ticket['fwhm_v'], ticket['fwhm_quote_v'], ticket['fwhm_coordinates_v'] = get_fwhm(ticket['histogram_v'], ticket['bin_v_center'])
    ticket['sigma_h'] = get_sigma(ticket['histogram_h'], ticket['bin_h_center'])
    ticket['sigma_v'] = get_sigma(ticket['histogram_v'], ticket['bin_v_center'])
    ticket['centroid_h'] = get_average(ticket['histogram_h'], ticket['bin_h_center'])
    ticket['centroid_v'] = get_average(ticket['histogram_v'], ticket['bin_v_center'])

    histogram = ticket["histogram"]

    peak_intensity = numpy.average(histogram[numpy.where(histogram >= numpy.max(histogram) * 0.90)])
    integral_intensity = numpy.sum(histogram)

    hh = ticket['bin_h_center']
    vv = ticket['bin_v_center']

    return ShadowHistogram(hh, vv, histogram), \
           DictionaryWrapper(
               h_sigma=ticket['sigma_h'],
               h_fwhm=ticket['fwhm_h'],
               h_centroid=ticket['centroid_h'],
               v_sigma=ticket['sigma_v'],
               v_fwhm=ticket['fwhm_v'],
               v_centroid=ticket['centroid_v'],
               integral_intensity=integral_intensity,
               peak_intensity=peak_intensity
    )

def plot_shadow_beam_spatial_distribution(shadow_beam, nbins=201, nolost=1, title="X,Z", xrange=None, yrange=None):
    return Shadow.ShadowTools.plotxy(shadow_beam._beam, 1, 3, nbins=nbins, nolost=nolost, title=title, xrange=xrange, yrange=yrange)

def plot_shadow_beam_divergence_distribution(shadow_beam, nbins=201, nolost=1, title="X',Z'", xrange=None, yrange=None):
    return Shadow.ShadowTools.plotxy(shadow_beam._beam, 4, 6, nbins=nbins, nolost=nolost, title=title, xrange=xrange, yrange=yrange)

def save_source_beam(source_beam, file_name="source_beam.dat"):
    source_beam.getOEHistory(0)._shadow_source_start.src.write("parameters_start_" + file_name)
    source_beam.getOEHistory(0)._shadow_source_end.src.write("parameters_end_" + file_name)
    source_beam.writeToFile(file_name)

def load_source_beam(file_name="source_beam.dat"):
    source_beam = ShadowBeam()
    source_beam.loadFromFile(file_name)

    # commented because of a shadow3 bug to be determined
    #shadow_source_start = ShadowSource.create_src_from_file(congruence.checkFile("parameters_start_" + file_name))
    #shadow_source_end   = ShadowSource.create_src_from_file(congruence.checkFile("parameters_end_" + file_name))
    shadow_source_start = __load_shadow_source(ShadowSource.create_src(), congruence.checkFile("parameters_start_" + file_name))
    shadow_source_end   = __load_shadow_source(ShadowSource.create_src(), congruence.checkFile("parameters_end_" + file_name))

    source_beam.history.append(ShadowOEHistoryItem(shadow_source_start=shadow_source_start,
                                                   shadow_source_end=shadow_source_end,
                                                   widget_class_name="UndeterminedSource"))

    return source_beam

def save_shadow_beam(shadow_beam, file_name="shadow_beam.dat"):
    shadow_beam.getOEHistory(-1)._shadow_oe_start._oe.write("parameters_start_" + file_name)
    shadow_beam.getOEHistory(-1)._shadow_oe_end._oe.write("parameters_end_" + file_name)
    shadow_beam.writeToFile(file_name)

def load_shadow_beam(file_name="shadow_beam.dat"):
    shadow_beam = ShadowBeam()
    shadow_beam.loadFromFile(file_name)

    # commented because of a shadow3 bug to be determined
    #shadow_oe_start = ShadowOpticalElement.create_oe_from_file(congruence.checkFile("parameters_start_" + file_name))
    #shadow_oe_end   = ShadowOpticalElement.create_oe_from_file(congruence.checkFile("parameters_end_" + file_name))
    shadow_oe_start = __load_shadow_oe(ShadowOpticalElement.create_empty_oe(), congruence.checkFile("parameters_start_" + file_name))
    shadow_oe_end   = __load_shadow_oe(ShadowOpticalElement.create_empty_oe(), congruence.checkFile("parameters_end_" + file_name))

    shadow_beam.history.append(ShadowOEHistoryItem(shadow_oe_start=shadow_oe_start,
                                                   shadow_oe_end=shadow_oe_end,
                                                   widget_class_name="UndeterminedOpticalElement"))
    return shadow_beam

from configparser import RawConfigParser

def __load_shadow_source(shadow_source, file_name):
    __load_shadow_file(shadow_source.src, file_name)
    return shadow_source

def __load_shadow_oe(shadow_oe, file_name):
    __load_shadow_file(shadow_oe._oe, file_name)
    return shadow_oe

def __load_shadow_file(shadow_element, file_name):
    with open(file_name) as f: file_content = '[dummy_section]\n' + f.read()

    config_parser = RawConfigParser()
    config_parser.optionxform = str
    config_parser.read_string(file_content)

    for name, value in config_parser.items("dummy_section"):
        if value.isdigit(): value = int(value)
        elif value.replace('.','',1).replace('-','',1).replace('E','',1).isdigit(): value = float(value)
        else: value = value.encode()

        setattr(shadow_element, name, value)

class PreProcessorFiles:
    NO = 0
    YES_FULL_RANGE = 1
    YES_SOURCE_RANGE = 2

####################################################

def write_reflectivity_file(symbol="Pt", shadow_file_name="Pt.dat", energy_range=[4000, 16000], energy_step=1.0):
    symbol = symbol.strip()
    density = ShadowPhysics.getMaterialDensity(symbol)

    prerefl(interactive=False,
            SYMBOL=symbol,
            DENSITY=density,
            E_MIN=energy_range[0],
            E_MAX=energy_range[1],
            E_STEP=energy_step,
            FILE=congruence.checkFileName(shadow_file_name))

    return shadow_file_name

def write_bragg_file(crystal="Si", miller_indexes=[1, 1, 1], shadow_file_name="Si111.dat", energy_range=[4000, 16000], energy_step=1.0):
    bragg(interactive=False,
          DESCRIPTOR=crystal.strip(),
          H_MILLER_INDEX=miller_indexes[0],
          K_MILLER_INDEX=miller_indexes[1],
          L_MILLER_INDEX=miller_indexes[2],
          TEMPERATURE_FACTOR=1.0,
          E_MIN=energy_range[0],
          E_MAX=energy_range[1],
          E_STEP=energy_step,
          SHADOW_FILE=congruence.checkFileName(shadow_file_name))

    return shadow_file_name

def write_dabam_file(figure_error_rms=None, dabam_entry_number=20, heigth_profile_file_name="KB.dat", seed=8787):
    server = dabam.dabam()
    server.set_input_silent(True)
    server.set_server(dabam.default_server)
    server.load(dabam_entry_number)

    input_parameters = DabamInputParameters(dabam_server=server)
    input_parameters.si_to_user_units = 1000.0
    input_parameters.center_y = 1
    input_parameters.modify_y = 2
    input_parameters.new_length_y = 100.0
    input_parameters.filler_value_y = 0.0
    if figure_error_rms is None:
        input_parameters.renormalize_y = 0
    else:
        input_parameters.renormalize_y = 1
        input_parameters.error_type_y = 0
        input_parameters.rms_y = 3.5
    input_parameters.kind_of_profile_x = 0
    input_parameters.dimension_x = 20.0
    input_parameters.step_x = 1.0
    input_parameters.power_law_exponent_beta_x = 2.0
    input_parameters.montecarlo_seed_x = seed
    input_parameters.error_type_x = 0
    input_parameters.rms_x = 0.5

    xx, yy, zz = calculate_dabam_profile(input_parameters)

    write_shadow_surface(zz, xx, yy, heigth_profile_file_name)

    return heigth_profile_file_name

####################################################
#
# diffraction_plane: 1- Sagittal, 2- Tangential, 3- Both (2D), 4- Both (1D+1D)
# calcType: 1- Slits, 2-Mirror/Grating Size, 3-Mirror Size + Error, 4-Grating Size + Error
# nf: Near Field Calculation 0- No, 1- Yes
# focal_length: Focal Distance of the Wavefront for the Near Field calculation (-1 for the default)
# image_distance: Image Distance of the Beam after the Near Field calculation (-1 for the default)
#
def get_hybrid_input_parameters(shadow_beam, diffraction_plane=2, calcType=1, nf=0, focal_length=-1, image_distance=-1, verbose=False):
    input_parameters = hybrid_control.HybridInputParameters()
    input_parameters.ghy_lengthunit = 2
    input_parameters.widget = MockWidget(verbose=verbose)
    input_parameters.shadow_beam = shadow_beam
    input_parameters.ghy_diff_plane = diffraction_plane
    input_parameters.ghy_calcType = calcType
    input_parameters.ghy_distance = image_distance
    input_parameters.ghy_focallength = focal_length
    input_parameters.ghy_nf = nf
    input_parameters.ghy_nbins_x = 100
    input_parameters.ghy_nbins_z = 100
    input_parameters.ghy_npeak = 20
    input_parameters.ghy_fftnpts = 50000
    input_parameters.file_to_write_out = 0
    input_parameters.ghy_automatic = 0

    return input_parameters

def rotate_axis_system(input_beam, rotation_angle=270.0):
    empty_element = Shadow.OE()

    empty_element.ALPHA = rotation_angle
    empty_element.DUMMY = 0.1
    empty_element.FWRITE = 3
    empty_element.F_REFRAC = 2
    empty_element.T_IMAGE = 0.0
    empty_element.T_INCIDENCE = 0.0
    empty_element.T_REFLECTION = 180.0
    empty_element.T_SOURCE = 0.0

    return ShadowBeam.traceFromOE(input_beam.duplicate(), ShadowOpticalElement(empty_element), widget_class_name="EmptyElement")
