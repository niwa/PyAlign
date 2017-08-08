# -*- coding: utf-8 -*-
"""
Created on Fri Jun 23 10:37:04 2017

@author: geddesag

Python build of Dan's align60 idl code

Overview:

Read in the align6 ini into a text edit widgit

Button to reset it as the master.ini

Button to execute the align exe

Replot all the output files with full interactivity

"""
import matplotlib
import Tkinter
import time


import ScrolledText

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from numpy import *
import shutil
import subprocess
import FileDialog


class App():
    
    def __init__(self):
        """Build the gui"""
        self.root = Tkinter.Tk()
        self.root.title('PyAlign - contact alex.geddes@niwa.co.nz')
        self.root.protocol('WM_DELETE_WINDOW', self.on_close)

        
        textcontainer=Tkinter.Frame(self.root,borderwidth=1,relief='sunken')
        
        self.text_window=Tkinter.Text(textcontainer,width=40,height=40,undo=True,wrap="none",borderwidth=0)
        textvsb=Tkinter.Scrollbar(textcontainer,orient="vertical",command=self.text_window.yview)
        texthsb=Tkinter.Scrollbar(textcontainer,orient="horizontal",command=self.text_window.xview)
        self.text_window.configure(yscrollcommand=textvsb.set,xscrollcommand=texthsb.set)
        self.text_window.grid(row=0,column=0,sticky='nsew')
        textvsb.grid(row=0,column=1,sticky="ns")
        texthsb.grid(row=1,column=0,sticky="ew")
        textcontainer.grid_rowconfigure(0,weight=1)
        textcontainer.grid_columnconfigure(0,weight=1)
        textcontainer.grid(row=0,column=0)
        
        self.run_button=Tkinter.Button(self.root,text="Run Align",command=lambda:self.run())
        self.run_button.grid(row=1,column=0)

        reset_button=Tkinter.Button(self.root,text="Reset File",command=lambda:self.reset())
        reset_button.grid(row=2,column=0)
        
        self.plot_window=FigureCanvasTkAgg(f,self.root)
        self.plot_window.show()
        self.plot_window.get_tk_widget().grid(column=1,row=0)
        toolbar_frame=Tkinter.Frame(self.root)
        toolbar_frame.grid(row=1,column=1,sticky='w')
        toolbar=NavigationToolbar2TkAgg(self.plot_window,toolbar_frame)
        toolbar.update()
        
        """Load the existing file and plot it up"""
        self.load_file('master_align6.inp')
        self.plot_all()
        self.root.mainloop()
    def reset(self):
        """Copy the master inp file back to align6.inp"""
        shutil.copy('master_align6.inp',filename)
        self.load_file(filename)
    def run(self):
        """Call the save file function and then run allign6.exe and then plot
        when complete"""
        self.save_file()
        proc=subprocess.Popen("align6.exe").communicate()
        self.plot_all()
        
    def load_file(self,filename):
        """read in and display the file"""
        text_in=(open(filename,'rb')).read()
        
        self.text_window.insert('1.0',text_in)
        
    def save_file(self):
        """Write the displayed text back to the file"""
        text_out=self.text_window.get('1.0',Tkinter.END+'-1c')
        open(filename,'wb').write(text_out)
    def on_close(self):
        """When you close the gui, this calls the save file command, feel free
        to remove or maybe call reset instead"""
        self.save_file()
        self.root.destroy()
        
    def plot_all(self):
        """Clear the figure and readd the subplots (there position and format
        can change so rather than clearign the axis, i clear the figure)"""
        
        f.clf()
        fringes=f.add_subplot(3,2,1)
        ils=f.add_subplot(3,2,2)
        apod=f.add_subplot(3,2,3)
        cifg=f.add_subplot(3,2,4)
        sheary=f.add_subplot(3,2,5)
        shearz=f.add_subplot(3,2,6)
        
        """Load in the data from the ergsalign folder"""
        fringes_data=loadtxt("ergsalign/sketcha.dat",unpack=True)
        cifg_data=loadtxt("ergsalign/cifg.dat",unpack=True)
        ils_data=loadtxt("ergsalign/ils.dat",unpack=True)
        misalign_data=loadtxt("ergsalign/misalign.dat",unpack=True)
        modulation_data=loadtxt("ergsalign/modulat.dat",unpack=True)
        
        """Fringes plot"""
        fringes.imshow(fringes_data.T,origin="lower",cmap='Reds')
        fringes.set_title("Haidinger Fringes")
        for tick in fringes.get_xticklabels():
            tick.set_rotation(90)
        
        
        """ILS plot, plot centred around the maximum real signal"""
        ils.set_title("ILS")
        xdps=30
        max_plc=ils_data[1].argmax()
        
        ils.plot(ils_data[0][max_plc-xdps:max_plc+xdps],ils_data[1][max_plc-xdps:max_plc+xdps],label="Real")
        ils.set_ylabel("Real (A.U.)",color="b")


        ils.plot(ils_data[0][max_plc-xdps:max_plc+xdps],ils_data[2][max_plc-xdps:max_plc+xdps],label="Imag.",color='g')
                
        ils.set_xlabel(r"Wavenumber ($cm^{-1}$)")
        for tick in ils.get_xticklabels():
            tick.set_rotation(90)

        ax=ils.twinx()
        ax.set_ylabel("Imaginary (A.U.)",color='g')
        ax.tick_params(labelright='off')




    
        """Apodization plot"""
        apod.set_title("Apodization Function")
        apod.set_ylabel("Modulation Efficiency",color='b')
        apod.set_xlabel("OPD (cm)")
        apod.plot(modulation_data[0],modulation_data[1])
        ax=apod.twinx()
        ax.set_ylabel("Phase (rad)",color='g')
        ax.plot(modulation_data[0],modulation_data[2],color='g')
        
        """CIFG plot"""
        cifg.set_title("CIFG")
        zpind=where(cifg_data[0]==0)[0][0]
        cifg.plot(cifg_data[0][zpind:],cifg_data[1][zpind:],label="Real Modulation")
        cifg.set_ylabel("Real Modulation",color='b')
        cifg.set_xlabel("OPD (cm)")
        ax=cifg.twinx()
        ax.plot(cifg_data[0][zpind:],cifg_data[2][zpind:],color='g',label="Phase (rad)")
        ax.set_ylabel("Phase (rad)",color='g')
        
        """Shear Y and Shear Z plots"""
        sheary.set_title("Shear Y (function of opd)")
        sheary.plot(misalign_data[0],misalign_data[1])
        sheary.set_ylabel("OPD (cm)",color='b')
        
        shearz.set_title("Shear Z (function of opd)")
        shearz.plot(misalign_data[0],misalign_data[2])
        shearz.set_ylabel("OPD (cm)",color='b')
        f.tight_layout()

        self.plot_window.show()
        
        #matplotlib.pyplot.draw()
    
if __name__=='__main__':
    """Create the figure object, I've left it outside the class, might change it"""
    f=Figure(figsize=(9,8),dpi=100)


   # rc('text',usetex=True)
    """Set the filename to look for, this may also change"""
    filename="align6.inp"
    
    """Launch the app"""
    app=App()