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
"""Module Reptate

Main program that launches the GUI.

"""
import os
import sys
sys.path.append('core')
sys.path.append('gui')
sys.path.append('console')
sys.path.append('applications')
sys.path.append('theories')
sys.path.append('visual')
sys.path.append('tools')
from CmdBase import CmdBase, CalcMode
from QApplicationManager import QApplicationManager
#from ApplicationManager import * #solved the issue with the matplot window not opening on Mac
from PyQt5.QtWidgets import QApplication
from SplashScreen import SplashScreen
from time import time, sleep


def start_RepTate(argv):
    """
    Main RepTate application. 
    
    :param list argv: Command line parameters passed to Reptate
    """
    GUI = True
    QApplication.setStyle("Fusion")  #comment that line for a native look
    #for a list of available styles: "from PyQt5.QtWidgets import QStyleFactory; print(QStyleFactory.keys())"

    # app = QApplication(sys.argv)

    # FOR DEBUGGING PURPOSES: Set Single or MultiThread (default)
    # CmdBase.calcmode = CalcMode.singlethread

    ex = QApplicationManager()
    ex.setStyleSheet("QTabBar::tab { color:black; height: 22px; }")

    ########################################################
    # THE FOLLOWING LINES ARE FOR TESTING A PARTICULAR CASE
    # Open a particular application
    ex.handle_new_app('React')

    #####################
    # TEST Likhtman-McLeish
    # Open a Dataset
    ex.applications["React1"].new_tables_from_files([
        "data%sReact%sout1.reac" % ((os.sep, ) * 2),
    ])
    # Open a theory
    ex.applications["React1"].datasets["Set1"].new_theory("Tobita CSTR")
    # Calculate the theory
    # ex.applications["React1"].datasets["Set1"].handle_actionCalculate_Theory()

    # Open a theory
    sleep(1)
    ex.applications["React1"].datasets["Set1"].new_theory("Tobita Batch")
    # Calculate the theory
    # ex.applications["React1"].datasets["Set1"].handle_actionCalculate_Theory()

    # Open a theory
    sleep(1)
    ex.applications["React1"].datasets["Set1"].new_theory("React Mix")

    # Open a theory
    sleep(1)
    ex.applications["React1"].datasets["Set1"].new_theory("Multi-Met CSTR")

    ex.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    start_RepTate(sys.argv[1:])
