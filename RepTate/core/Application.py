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
"""Module Application

Module that defines the basic class from which all applications are derived.

"""
import io
#import logging
import matplotlib.pyplot as plt
from matplotlib.ticker import AutoMinorLocator, LogLocator, NullFormatter

from CmdBase import CmdBase, CmdMode
from Theory import Theory
from DataSet import DataSet
from TheoryBasic import *
from Tool import *

from MultiView import MultiView, PlotOrganizationType
from PyQt5.QtWidgets import QMenu, QApplication
from PyQt5.QtGui import QImage
from PyQt5.QtCore import Qt

from collections import OrderedDict
from TheoryBasic import TheoryPolynomial, TheoryPowerLaw, TheoryExponential, TheoryTwoExponentials
from ToolIntegral import ToolIntegral
from ToolFindPeaks import ToolFindPeaks
from ToolGradient import ToolGradient
from ToolSmooth import ToolSmooth
from ToolBounds import ToolBounds
from ToolEvaluate import ToolEvaluate
from ToolInterpolate import ToolInterpolateExtrapolate
from ToolMaterialsDatabase import ToolMaterialsDatabase
from mplcursors import cursor

class Application(CmdBase):
    """Main abstract class that represents an application
    
    """
    name = "Template"
    description = "Abstract class that defines basic functionality"
    extension = ""

    def __init__(self,
                 name="ApplicationTemplate",
                 parent=None,
                 nplot_max=4,
                 ncols=2,
                 **kwargs):
        """
        **Constructor**
        
        Keyword Arguments:
            - name {[type]} -- [description] (default: {"ApplicationTemplate"})
            - parent {[type]} -- [description] (default: {None})
        """

        super().__init__()
        self.name = name
        self.parent_manager = parent
        #self.logger = logging.getLogger('ReptateLogger')
        self.views = OrderedDict()
        self.filetypes = OrderedDict() # keep filetypes in order
        self.theories = OrderedDict()  # keep theory combobox in order
        self.availabletools = OrderedDict()     # keep tools combobox in order
        self.extratools = OrderedDict()     # keep tools combobox in order
        self.datasets = {}
        self.tools = []
        self.num_tools = 0
        self.current_view = 0
        self.num_datasets = 0
        self.legend_visible = False
        self.multiviews = []  #default view order in multiplot views
        self.nplot_max = nplot_max  # maximun number of plots
        self.nplots = nplot_max  # current number of plots
        self.ncols = ncols  #number of columns in the multiplot
        self.current_viewtab = 0

        self.autoscale = True

        # Theories available everywhere
        self.common_theories = OrderedDict()  # keep theory combobox in order
        self.common_theories[TheoryPolynomial.thname] = TheoryPolynomial
        self.common_theories[TheoryPowerLaw.thname] = TheoryPowerLaw
        self.common_theories[TheoryExponential.thname] = TheoryExponential
        self.common_theories[TheoryTwoExponentials.thname] = TheoryTwoExponentials

        # Tools available everywhere
        self.availabletools[ToolBounds.toolname] = ToolBounds
        self.availabletools[ToolEvaluate.toolname] = ToolEvaluate
        self.availabletools[ToolFindPeaks.toolname] = ToolFindPeaks
        self.availabletools[ToolGradient.toolname] = ToolGradient
        self.availabletools[ToolIntegral.toolname] = ToolIntegral
        self.availabletools[ToolInterpolateExtrapolate.toolname] = ToolInterpolateExtrapolate
        self.availabletools[ToolSmooth.toolname] = ToolSmooth
        self.extratools[ToolMaterialsDatabase.toolname] = ToolMaterialsDatabase
        
        # MATPLOTLIB STUFF
        self.set_multiplot(self.nplots, self.ncols)
        # self.multiplots = MultiView(PlotOrganizationType.OptimalRow,
        #                             self.nplots, self.ncols, self)
        # self.multiplots.plotselecttabWidget.setCurrentIndex(
        #     self.current_viewtab)
        # self.figure = self.multiplots.figure
        # self.axarr = self.multiplots.axarr  #
        # self.canvas = self.multiplots.canvas

        if (CmdBase.mode == CmdMode.cmdline):
            # self.figure.show()
            self.multiplots.show()
        self.datacursor_ = None

    def update_datacursor_artists(self):
        """Update the datacursor instance 
        Called at the end of ds.do_plot() and when plot-tab is changed"""
        try: 
            self.datacursor_.remove()
        except AttributeError:
            pass
        del self.datacursor_

        if CmdBase.mode == CmdMode.GUI:
            ds_list = [self.DataSettabWidget.currentWidget(),]
            if self.actionView_All_Sets.isChecked():
                ds_list = self.datasets.values()
            artists = []
            for ds in ds_list:
                if ds:
                    th = ds.TheorytabWidget.currentWidget()
                    for f in ds.files:
                        if f.active:
                            dt = f.data_table
                            for j in range(dt.MAX_NUM_SERIES):
                                if self.current_viewtab == 0:
                                    # all artists
                                    for i in range(self.nplots):
                                        artists.append(dt.series[i][j])
                                        if th:
                                            artists.append(th.tables[f.file_name_short].series[i][j])
                                else:
                                    # only artists of current tab
                                    artists.append(dt.series[self.current_viewtab - 1][j])
                                    if th:
                                        artists.append(th.tables[f.file_name_short].series[self.current_viewtab - 1][j])
                self.datacursor_ = cursor(pickables=artists) 
                self.datacursor_.bindings["deselect"] = 1
        else:
            axs = [self.axarr[i] for i in range(self.nplots)]
            self.datacursor_ = cursor(pickables=axs) 
            self.datacursor_.bindings["deselect"] = 1
        @self.datacursor_.connect("add")
        def _(sel):
            x, y = sel.target
            sel.annotation.set(text="%.3g; %.3g"%(x,y), size=13)
            sel.annotation.get_bbox_patch().set(alpha=0.7)
            sel.annotation.arrow_patch.set(ec="red", alpha=0.5)

    def set_multiplot(self, nplots, ncols):
        """defines the plot"""
        self.multiplots = MultiView(PlotOrganizationType.OptimalRow,
                                    nplots, ncols, self)
        self.multiplots.plotselecttabWidget.setCurrentIndex(
            self.current_viewtab)
        self.figure = self.multiplots.figure
        self.axarr = self.multiplots.axarr  #
        self.canvas = self.multiplots.canvas

    def set_view_tools(self, view_name):
        """Redefined in Child application. Called when view is changed"""
        pass

    def add_common_theories(self):
        for th in self.common_theories.values():
            self.theories[th.thname] = th
                                                
    def refresh_plot(self):
        self.view_switch(self.current_view.name)

    def copy_chart(self):
        """ Copy current chart to clipboard
        """
        buf = io.BytesIO()
        self.figure.savefig(buf, dpi=150)
        QApplication.clipboard().setImage(QImage.fromData(buf.getvalue()))
        buf.close()

    def clipboard_coordinates(self, artist):
        """Copy data to clipboard in tab-separated format"""
        try:
            x, y = artist.get_data()
        except:
            return
        line_strings = []
        for i in range(len(x)):
            line_strings.append(str(x[i]) + "\t" + str(y[i]))
        array_string = "\n".join(line_strings)
        QApplication.clipboard().setText(array_string)

    def handle_close_window(self, evt):
        """[summary]
        
        [description]
        
        Arguments:
            - evt {[type]} -- [description]
        
        Returns:
            [type] -- [description]
        """
        print("\nApplication window %s has been closed\n" % self.name)
        print(
            "Please, return to the RepTate prompt and delete the application")

    def new(self, line):
        """Create new empty dataset in the application
        
        [description]
        
        Arguments:
            - line {[type]} -- [description]
        
        Returns:
            - [type] -- [description]
        """
        self.num_datasets += 1
        if (line == ""):
            dsname = "DataSet%02d" % self.num_datasets
            dsdescription = ""
        else:
            items = line.split(',')
            dsname = items[0]
            if (len(items) > 1):
                dsdescription = items[1]
            else:
                dsdescription = ""
        ds = DataSet(dsname, dsdescription, self)
        return ds, dsname

    def do_new(self, line):
        """Create a new empty dataset in this application.
        
        [description]
        
        Arguments:
            line {str} -- [NAME [, DESCRIPTION]]
        """
        ds, dsname = self.new(line)
        self.datasets[dsname] = ds
        if (self.mode == CmdMode.batch):
            ds.prompt = ''
        else:
            ds.prompt = self.prompt[:-2] + '/' + ds.name + '> '
        ds.cmdloop()

    def delete(self, ds_name):
        """Delete a dataset from the current application
        
        [description]
        
        Arguments:
            - ds_name {[type]} -- [description]
        """
        if ds_name in self.datasets.keys():
            self.remove_ds_ax_lines(ds_name)
            for th in self.datasets[ds_name].theories.values():
                try:
                    th.destructor()
                except:
                    pass
            self.datasets[ds_name].theories.clear()
            self.datasets[ds_name].files.clear()
            del self.datasets[ds_name]
        else:
            print("Data Set \"%s\" not found" % ds_name)

    def remove_ds_ax_lines(self, ds_name):
        """Remove all dataset file artists from ax including theory ones
        
        [description]
        
        Arguments:
            - ds_name {[type]} -- [description]
        """
        try:
            ds = self.datasets[ds_name]
        except KeyError:
            return
        for th in ds.theories.values():
            for tt in th.tables.values():
                for i in range(tt.MAX_NUM_SERIES):
                    for nx in range(self.nplots):
                        self.axarr[nx].lines.remove(tt.series[nx][i])
        for file in ds.files:
            for i in range(file.data_table.MAX_NUM_SERIES):
                for nx in range(self.nplots):
                    self.axarr[nx].lines.remove(file.data_table.series[nx][i])

    def do_delete(self, name):
        """Delete a dataset from the current application
        
        [description]
        
        Arguments:
            - name {[type]} -- [description]
        """
        self.delete(name)

    def complete_delete(self, text, line, begidx, endidx):
        """Complete delete dataset command
        
        [description]
        
        Arguments:
            - text {[type]} -- [description]
            - line {[type]} -- [description]
            - begidx {[type]} -- [description]
            - endidx {[type]} -- [description]
        
        Returns:
            - [type] -- [description]
        """
        dataset_names = list(self.datasets.keys())
        if not text:
            completions = dataset_names[:]
        else:
            completions = [f for f in dataset_names if f.startswith(text)]
        return completions

    def list(self):
        """List the datasets in the current application
        
        [description]
        """
        for ds in self.datasets.values():
            print("%s:\t%s" % (ds.name, ds.description))

    def do_list(self, line):
        """List the datasets in the current application
        
        [description]
        
        Arguments:
            - line {[type]} -- [description]
        """
        self.list()

    def do_switch(self, name):
        """Switch the current dataset
        
        [description]
        
        Arguments:
            - name {[type]} -- [description]
        """
        done = False
        if name in self.datasets.keys():
            ds = self.datasets[name]
            ds.cmdloop()
        else:
            print("Dataset \"%s\" not found" % name)

    def complete_switch(self, text, line, begidx, endidx):
        """Complete the switch dataset command
        
        [description]
        
        Arguments:
            - text {[type]} -- [description]
            - line {[type]} -- [description]
            - begidx {[type]} -- [description]
            - endidx {[type]} -- [description]
        
        Returns:
            - [type] -- [description]
        """
        ds_names = list(self.datasets.keys())
        if not text:
            completions = ds_names[:]
        else:
            completions = [f for f in ds_names if f.startswith(text)]
        return completions

# FILE TYPE STUFF

    def filetype_available(self):
        """List available file types in the current application
        
        [description]
        """
        ftypes = list(self.filetypes.values())
        for ftype in ftypes:
            print("%s:\t%s\t*.%s" % (ftype.name, ftype.description,
                                     ftype.extension))

    def do_filetype_available(self, line):
        """List available file types in the current application
        
        [description]
        
        Arguments:
            - line {[type]} -- [description]
        """
        self.filetype_available()

# VIEW STUFF

    def set_views(self):
        """Set current view and assign availiable view
        labels to viewComboBox if in GUI mode
        
        [description]
        """
        for i, view_name in enumerate(self.views):  #loop over the keys
            if i == 0:
                #index 0 is the defaut view
                self.current_view = self.views[view_name]
            #add view name to the list of views avaliable
            if CmdBase.mode == CmdMode.GUI:
                self.viewComboBox.insertItem(i, view_name)
                self.viewComboBox.setItemData(i, self.views[view_name].description, Qt.ToolTipRole)

        if CmdBase.mode == CmdMode.GUI:
            #index 0 is the defaut selection
            self.viewComboBox.setCurrentIndex(0)

    def view_available(self):
        """List available views in the current application
        
        [description]
        """
        for view in self.views.values():
            if (view == self.current_view):
                print("*%s:\t%s" % (view.name, view.description))
            else:
                print("%s:\t%s" % (view.name, view.description))

    def do_view_available(self, line):
        """List available views in the current application
        
        [description]
        
        Arguments:
            - line {[type]} -- [description]
        """
        self.view_available()

    def view_switch(self, name):
        """Change to another view from open application
        
        [description]
        
        Arguments:
            - name {[type]} -- [description]
        """
        if name in list(self.views.keys()):
            self.current_view = self.views[name]
            if self.current_viewtab == 0:
                self.multiviews[0] = self.views[name]
            else:
                self.multiviews[self.current_viewtab - 1] = self.views[name]
        else:
            print("View \"%s\" not found" % name)
        # Update the plots!
        # Loop over datasets and call do_plot()
        temp = self.autoscale
        self.autoscale = True
        self.update_all_ds_plots()
        self.autoscale = temp

    def update_all_ds_plots(self):
        """[summary]
        
        [description]
        """
        for ds in self.datasets.values():
            ds.do_plot()

    def do_view_switch(self, name):
        """Change to another view from open application
        
        [description]
        
        Arguments:
            - name {[type]} -- [description]
        """
        self.view_switch(name)

    def complete_view_switch(self, text, line, begidx, endidx):
        """Complete switch view command
        
        [description]
        
        Arguments:
            - text {[type]} -- [description]
            - line {[type]} -- [description]
            - begidx {[type]} -- [description]
            - endidx {[type]} -- [description]
        
        Returns:
            - [type] -- [description]
        """
        view_names = list(self.views.keys())
        if not text:
            completions = view_names[:]
        else:
            completions = [f for f in view_names if f.startswith(text)]
        return completions

# THEORY STUFF

    def theory_available(self):
        """List available theories in the current application
        
        [description]
        """
        for t in list(self.theories.values()):
            print("%s:\t%s" % (t.thname, t.description))

    def do_theory_available(self, line):
        """List available theories in the current application
        
        [description]
        
        Arguments:
            line {[type]} -- [description]
        """
        self.theory_available()

# TOOL STUFF
    def tool_available(self):
        """List available tools in the current application
        
        [description]
        """
        for t in list(self.availabletools.values()):
            print("%s:\t%s" % (t.toolname, t.description))
        for t in list(self.extratools.values()):
            print("%s:\t%s" % (t.toolname, t.description))

    def do_tool_available(self, line):
        """List available tools in the current application
        
        [description]
        
        Arguments:
            line {[type]} -- [description]
        """
        self.tool_available()

    def do_tool_add(self, line):
        """Add a new tool of the type specified to the list of tools"""
        tooltypes = list(self.availabletools.keys())
        extratooltypes = list(self.extratools.keys())
        if ((line in tooltypes) or (line in extratooltypes)):
            self.num_tools += 1
            to_id = "%s%02d" % (line, self.num_tools)
            if (line in tooltypes):
                to = self.availabletools[line](to_id, self)
            elif (line in extratooltypes):
                to = self.extratools[line](to_id, self)
            self.tools.append(to)
            if self.mode == CmdMode.GUI:
                pass
            else:
                if (self.mode == CmdMode.batch):
                    to.prompt = ''
                else:
                    to.prompt = self.prompt[:-2] + '/' + to.name + '> '
                to.cmdloop()
            return to
        else:
            print("Tool \"%s\" does not exists" % line)

    def complete_tool_add(self, text, line, begidx, endidx):
        """Complete new tool command"""
        tool_names = list(self.availabletools.keys()) + list(self.extratools.keys()) 
        if not text:
            completions = tool_names[:]
        else:
            completions = [f for f in tool_names if f.startswith(text)]
        return completions

    def do_tool_delete(self, name):
        """Delete a tool from the current application"""
        listtools = [x.name for x in self.tools]
        try:
            idx = listtools.index(name)
            self.tools[idx].destructor()
            del self.tools[idx]
        except AttributeError as e:
            print("Tool \"%s\" not found" % name)
            
    def complete_tool_delete(self, text, line, begidx, endidx):
        """Complete delete tool command"""
        listtools = [x.name for x in self.tools]
        if not text:
            completions = listtools[:]
        else:
            completions = [f for f in listtools if f.startswith(text)]
        return completions
        
    def do_tool_list(self, line):
        """List opened tools"""
        for t in self.tools:
            if t.active:
                print(t.name + " *")
            else:
                print(t.name)

    def do_tool_switch(self, line):
        """Change the active tool"""
        listtools = [x.name for x in self.tools]
        try:
            idx = listtools.index(name)
            self.tools[idx].cmdloop()
        except AttributeError as e:
            print("Tool\"%s\" not found" % line)

    def complete_tool_switch(self, text, line, begidx, endidx):
        """Complete the tool switch command"""
        completions = self.complete_tool_delete(text, line, begidx, endidx)
        return completions

    def do_tool_activate(self, name):
        listtools = [x.name for x in self.tools]
        try:
            idx = listtools.index(name)
            self.tools[idx].do_activate(name)
        except AttributeError as e:
            print("Tool \"%s\" not found" % name)
        except ValueError as e:
            print("Tool \"%s\" not found" % name)

    def complete_tool_activate(self, text, line, begidx, endidx):
        """Complete the tool switch command"""
        completions = self.complete_tool_delete(text, line, begidx, endidx)
        return completions

# LEGEND STUFF

    def legend(self):
        """[summary]
        
        [description]
        """
        self.legend_visible = not self.legend_visible
        self.set_legend_properties()
        self.canvas.draw()

    def do_legend(self, line):
        """[summary]
        
        [description]
        
        Arguments:
            - line {[type]} -- [description]
        """
        self.legend()


# OTHER STUFF

    def update_plot(self):
        """[summary]
        
        [description]
        """
        self.set_axes_properties(self.autoscale)
        #self.set_legend_properties()
        if CmdBase.mode == CmdMode.GUI:
            self.update_legend()
        self.canvas.draw()

    def set_axes_properties(self, autoscale=True):
        """[summary]
        
        [description]
        """
        for nx in range(self.nplots):
            view = self.multiviews[nx]
            ax = self.axarr[nx]
            if (view.log_x):
                ax.set_xscale("log")
                #ax.xaxis.set_minor_locator(LogLocator(subs=range(10)))
                locmaj = LogLocator(base=10.0, subs=(1.0, ), numticks=100)
                ax.xaxis.set_major_locator(locmaj)
                locmin = LogLocator(
                    base=10.0, subs=np.arange(2, 10) * .1, numticks=100)
                ax.xaxis.set_minor_locator(locmin)
                ax.xaxis.set_minor_formatter(NullFormatter())
            else:
                ax.set_xscale("linear")
                ax.xaxis.set_minor_locator(AutoMinorLocator())
            if (view.log_y):
                ax.set_yscale("log")
                #ax.yaxis.set_minor_locator(LogLocator(subs=range(10)))
                locmaj = LogLocator(base=10.0, subs=(1.0, ), numticks=100)
                ax.yaxis.set_major_locator(locmaj)
                locmin = LogLocator(
                    base=10.0, subs=np.arange(2, 10) * .1, numticks=100)
                ax.yaxis.set_minor_locator(locmin)
                ax.yaxis.set_minor_formatter(NullFormatter())
            else:
                ax.set_yscale("linear")
                ax.yaxis.set_minor_locator(AutoMinorLocator())

            ax.set_xlabel(view.x_label + ' [' + view.x_units + ']')
            ax.set_ylabel(view.y_label + ' [' + view.y_units + ']')
            
            if not self.ax_opts['label_size_auto']:
                ax.xaxis.label.set_size(self.ax_opts['fontsize'])
                ax.yaxis.label.set_size(self.ax_opts['fontsize'])

            ax.xaxis.label.set_color(self.ax_opts['color_label'])
            ax.yaxis.label.set_color(self.ax_opts['color_label'])
            
            ax.xaxis.label.set_style(self.ax_opts['style'])
            ax.yaxis.label.set_style(self.ax_opts['style'])

            ax.xaxis.label.set_family(self.ax_opts['family'])
            ax.yaxis.label.set_family(self.ax_opts['family'])

            ax.xaxis.label.set_weight(self.ax_opts['fontweight'])
            ax.yaxis.label.set_weight(self.ax_opts['fontweight'])

            ax_thick = self.ax_opts['axis_thickness']
            ax.tick_params(which='major', width=1.00*ax_thick, length=5*ax_thick)
            ax.tick_params(which='minor', width=0.75*ax_thick, length=2.5*ax_thick)
            
            if not self.ax_opts['tick_label_size_auto']:
                ax.tick_params(which='major', labelsize=self.ax_opts['tick_label_size'])
                ax.tick_params(which='minor', labelsize=self.ax_opts['tick_label_size']*.8)

            ax.grid(self.ax_opts['grid'])

            for pos in ['top', 'bottom', 'left', 'right']:
                ax.spines[pos].set_linewidth(ax_thick)
                ax.spines[pos].set_color(self.ax_opts['color_ax'])
            ax.tick_params(which='both', color=self.ax_opts['color_ax'], labelcolor=self.ax_opts['color_ax'])
            
            if autoscale:
                self.axarr[nx].relim(True)
                self.axarr[nx].autoscale(True)
                self.axarr[nx].autoscale_view()
                self.axarr[nx].set_aspect("auto")

    def set_legend_properties(self):
        """[summary]
        
        [description]
        """
        # pass
        leg = self.axarr[0].legend(frameon=True, ncol=2)
        if (self.legend_visible):
            leg.draggable()
        else:
            try:
                leg.remove()
            except AttributeError as e:
                pass
                #print("legend: %s"%e)
