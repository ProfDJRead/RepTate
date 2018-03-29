# RepTate: Rheology of Entangled Polymers: Toolkit for the Analysis of Theory and Experiments
# --------------------------------------------------------------------------------------------------------
#
# Authors:
#     Jorge Ramirez, jorge.ramirez@upm.es
#     Victor Boudara, victor.boudara@gmail.com
#
# Useful links:
#     http://blogs.upm.es/compsoftmatter/software/reptate/
#     https://github.com/jorge-ramirez-upm/RepTate
#     http://reptate.readthedocs.io
#
# --------------------------------------------------------------------------------------------------------
#
# Copyright (2017): Jorge Ramirez, Victor Boudara, Universidad Politécnica de Madrid, University of Leeds
#
# This file is part of RepTate.
#
# RepTate is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# RepTate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with RepTate.  If not, see <http://www.gnu.org/licenses/>.
#
# --------------------------------------------------------------------------------------------------------
"""Module ApplicationSANS

Module for the analysis of data from SANS experiments

"""
from CmdBase import CmdBase, CmdMode
from Application import Application
from QApplicationWindow import QApplicationWindow
from View import View
from FileType import TXTColumnFile
import numpy as np


class ApplicationSANS(CmdBase):
    """Application to Analyze Data from SANS experiments
    
    [description]
    """
    name = "SANS"
    description = "Small Angle Neutron Scattering Experiments"
    extension = "sans"

    def __new__(cls, name="SANS", parent=None):
        """[summary]
        
        [description]
        
        Keyword Arguments:
            - name {[type]} -- [description] (default: {"SANS"})
            - parent {[type]} -- [description] (default: {None})
        
        Returns:
            - [type] -- [description]
        """
        return GUIApplicationSANS(
            name,
            parent) if (CmdBase.mode == CmdMode.GUI) else CLApplicationSANS(
                name, parent)


class BaseApplicationSANS:
    """[summary]
    
    [description]
    """
    help_file = 'http://reptate.readthedocs.io/en/latest/manual/Applications/SANS/SANS.html'

    def __init__(self, name="SANS", parent=None):
        """
        **Constructor**
        
        Keyword Arguments:
            - name {[type]} -- [description] (default: {"SANS"})
            - parent {[type]} -- [description] (default: {None})
        """
        from TheoryDebye import TheoryDebye
        super().__init__(name, parent)

        # VIEWS
        self.views["log(I(q))"] = View(
            name="log(I(q))",
            description="log Intensity",
            x_label="log(q)",
            y_label="log(I(q))",
            x_units="$\mathrm{\AA}^{-1}$",
            y_units="-",
            log_x=False,
            log_y=False,
            view_proc=self.viewLogSANS,
            n=1,
            snames=["I(q)"])
        self.views["I(q)"] = View(
            name="I(q)",
            description="Intensity",
            x_label="q",
            y_label="I(q)",
            x_units="$\mathrm{\AA}^{-1}$",
            y_units="-",
            log_x=False,
            log_y=False,
            view_proc=self.viewSANS,
            n=1, 
            snames=["I(q)"])
        self.views["Zimm"] = View(
            name="Zimm",
            description="Zimm plot (1/I(q) vs q^2)",
            x_label="$\mathrm{q}^2$",
            y_label="1/I(q)",
            x_units="$\mathrm{\AA}^{-2}$",
            y_units="-",
            log_x=False,
            log_y=False,
            view_proc=self.viewZimm,
            n=1, 
            snames=["Zimm"])
        self.views["Kratky"] = View(
            name="Kratky",
            description="Kratky plot (q^2*I(q) vs q)",
            x_label="q",
            y_label="$\mathrm{q}^2\cdot \mathrm{I(q)}$",
            x_units="$\mathrm{\AA}^{-1}$",
            y_units="$\mathrm{\AA}^{-2}$",
            log_x=False,
            log_y=False,
            view_proc=self.viewKratky,
            n=1, 
            snames=["Kratky"])

        #set multiviews
        self.multiviews = [
            self.views["log(I(q))"]
        ]  #default view order in multiplot views, set only one item for single view
        self.nplots = len(self.multiviews)

        # FILES
        ftype = TXTColumnFile("SANS files", "sans", "SANS files",
                              ['q', 'I(q)'], ['Mw', 'Phi'],
                              ['1/A', '-'])
        self.filetypes[ftype.extension] = ftype

        # THEORIES
        self.theories[
            TheoryDebye.thname] = TheoryDebye
        self.add_common_theories()

        #set the current view
        self.set_views()

    def viewLogSANS(self, dt, file_parameters):
        """[summary]
        
        [description]
        
        Arguments:
            - dt {[type]} -- [description]
            - file_parameters {[type]} -- [description]
        
        Returns:
            - [type] -- [description]
        """
        x = np.zeros((dt.num_rows, 1))
        y = np.zeros((dt.num_rows, 1))
        x[:, 0] = np.log10(dt.data[:, 0])
        y[:, 0] = np.log10(np.abs(dt.data[:, 1]))
        return x, y, True

    def viewSANS(self, dt, file_parameters):
        """[summary]
        
        [description]
        
        Arguments:
            - dt {[type]} -- [description]
            - file_parameters {[type]} -- [description]
        
        Returns:
            - [type] -- [description]
        """
        x = np.zeros((dt.num_rows, 1))
        y = np.zeros((dt.num_rows, 1))
        x[:, 0] = dt.data[:, 0]
        y[:, 0] = dt.data[:, 1]
        return x, y, True

    def viewKratky(self, dt, file_parameters):
        """[summary]
        
        [description]
        
        Arguments:
            - dt {[type]} -- [description]
            - file_parameters {[type]} -- [description]
        
        Returns:
            - [type] -- [description]
        """
        x = np.zeros((dt.num_rows, 1))
        y = np.zeros((dt.num_rows, 1))
        x[:, 0] = dt.data[:, 0]
        y[:, 0] = dt.data[:, 0]*dt.data[:, 0]*dt.data[:, 1]
        return x, y, True

    def viewZimm(self, dt, file_parameters):
        """[summary]
        
        [description]
        
        Arguments:
            - dt {[type]} -- [description]
            - file_parameters {[type]} -- [description]
        
        Returns:
            - [type] -- [description]
        """
        x = np.zeros((dt.num_rows, 1))
        y = np.zeros((dt.num_rows, 1))
        x[:, 0] = dt.data[:, 0]*dt.data[:, 0]
        y[:, 0] = 1.0/dt.data[:, 1]
        return x, y, True

class CLApplicationSANS(BaseApplicationSANS, Application):
    """[summary]
    
    [description]
    """

    def __init__(self, name="SANS", parent=None):
        """
        **Constructor**
        
        Keyword Arguments:
            - name {[type]} -- [description] (default: {"SANS"})
            - parent {[type]} -- [description] (default: {None})
        """
        super().__init__(name, parent)


class GUIApplicationSANS(BaseApplicationSANS, QApplicationWindow):
    """[summary]
    
    [description]
    """

    def __init__(self, name="SANS", parent=None):
        """
        **Constructor**
        
        Keyword Arguments:
            - name {[type]} -- [description] (default: {"SANS"})
            - parent {[type]} -- [description] (default: {None})
        """
        super().__init__(name, parent)