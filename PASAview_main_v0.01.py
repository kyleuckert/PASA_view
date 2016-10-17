import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import MouseEvent
from matplotlib.figure import Figure

from mpldatacursor import datacursor

import numpy as np

import scipy as scipy
from scipy.optimize import curve_fit
from scipy import signal

from Tkinter import *
from ttk import *
import tkFileDialog

#import labTOF_plot
import sys

import warnings

import read_lecroy_binary

class labTOF(Frame):

	#define parent window
	def __init__(self, parent):
		#from Tkinter frame:
		#Frame.__init__(self, parent, background="white")   
		#from ttk frame:
		Frame.__init__(self, parent)

		#save a reference to the parent widget
		self.parent = parent

		#delegate the creation of the user interface to the initUI() method
		#self.parent.title("Lab TOF")
		#self.pack(fill=BOTH, expand=1)
		self.fig = Figure(figsize=(4,4), dpi=100)
		#fig = Figure(facecolor='white', edgecolor='white')
		self.fig.subplots_adjust(bottom=0.15, left=0.15)

		self.canvas = FigureCanvasTkAgg(self.fig, self)
		self.toolbar = NavigationToolbar2TkAgg(self.canvas, self)
		self.toolbar.pack(side=TOP)
		#canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True) 
		
		#list containing time domain values
		self.time=[]
		#list containing mass domain values
		self.mass=[]
		#flag to indicate whether time or mass is displayed
		#time flag=0
		#mass flag=1
		self.time_mass_flag=0
		self.num_len_flag=0
		#flag to indicate MS or MSMS calibration
		#MS = 0
		#MSMS = 1
		self.MSMS_flag=-99
		#list containing intensity values
		self.intensity=[]
		#list containing calibration values
		self.cal_time=[]
		self.cal_mass=[]
		self.label_mass=[]
		self.label_time=[]
		self.label_intensity=[]
		#calibration point id
		self.cid=-99
		self.initUI()
		#zero mass corresponds to ~40% of parent mass time
		self.MSMS_zero_time=0.40838#0.4150#0.4082
        
        
	#container for other widgets
	def initUI(self):
		#set the title of the window using the title() method
		self.parent.title("PASA View")
		
		#apply a theme to widget
		self.style = Style()
		self.style.theme_use('default')
		
		#the Frame widget (accessed via the delf attribute) in the root window
		#it is expanded in both directions
		#CHANGE all pack to grid layout
		self.pack(fill=BOTH, expand=1)

		menubar = Menu(self.parent)
		self.parent.config(menu=menubar)
		
		#contains file menu items
		fileMenu = Menu(menubar, tearoff=0)
		menubar.add_cascade(label="File", menu=fileMenu)
		fileMenu.add_command(label="Open", command=self.onOpen)
		fileMenu.add_command(label="Quit", command=self.quit_destroy)


		#generate figure (no data at first)
		self.reset_figure([0,1], [[],[]], ' ')
		
		#create instance of the button widget
		#command specifies the method to be called
		quitButton = Button(self, text="Quit", command = self.quit_destroy)
		#quitButton.place(x=50, y=50)
		quitButton.pack(side=RIGHT, padx=5, pady=5)
		#quitButton.grid(row=5, column=5, padx=5)

		#convert to wavenumber domain
		self.wavenumberButton = Button(self, text="Wavenumber Domain", command = self.wavenumber_domain, state=DISABLED)
		self.wavenumberButton.pack(side=RIGHT, padx=5, pady=5)

		#convert to wavelength domain
		self.wavelengthButton = Button(self, text="Wavelength Domain", command = self.wavelength_domain, state=DISABLED)
		self.wavelengthButton.pack(side=RIGHT, padx=5, pady=5)

		#remove all spectra from plotting windows
		self.resetButton = Button(self, text="Reset", command = self.reset_plots, state=DISABLED)
		self.resetButton.pack(side=RIGHT, padx=5, pady=5)

		#smooth spectrum
		self.smoothButton = Button(self, text="Smooth", command = self.smooth_data, state=DISABLED)
		self.smoothButton.pack(side=RIGHT, padx=5, pady=5)


	#convert to wavelength domain
	#disabled until spectrum is plotted
	def wavelength_domain(self):
		self.num_len_flag=1
		self.generate_figure([self.time,self.intensity], [self.label_mass, self.label_intensity], 'wavenumber ($\mu$m)')
	
	#convert to wavenumber domain	
	def wavenumber_domain(self):
		self.num_len_flag=0
		self.generate_figure([[10000/x for x in self.time],self.intensity], [self.label_time, self.label_intensity], 'wavenumber (cm$^{-1}$)')
		

	#convert to mass domain
	#disabled until calibration is defined
	def mass_domain(self):
		self.time_mass_flag=1
		self.generate_figure([self.mass,self.intensity], [self.label_mass, self.label_intensity], 'mass (Da)')
	
	#convert to time domain	
	def time_domain(self):
		self.time_mass_flag=0
		#plot in micro seconds
		self.generate_figure([[1*x for x in self.time],self.intensity], [self.label_time, self.label_intensity], 'wavelength ($\mu$m)')
		
	#smooth data
	def smooth_data(self):
		#smooth self.time/mass/int variables - permanant
		#probably not a good idea
		#purpose of smoothing function: to display smoothed plot
		self.SmoothDialog(self.parent)
		#wait for dialog to close
		self.top.wait_window(self.top)
		smoothed_signal = scipy.signal.savgol_filter(self.intensity,self.window,self.poly)
		#convert from array to list
		self.intensity=smoothed_signal.tolist()
		#print 'intensity: ', len(self.intensity), type(self.intensity)
		if self.time_mass_flag == 1:
			#print 'mass: ', len(self.mass), type(self.mass)
			self.mass_domain()
		else:
			#print 'time: ', len(self.time), type(self.time)
			self.time_domain()

	#reset plotting window
	def reset_plots(self):
		#generate figure (no data at first)
		self.reset_figure([0,1], [[],[]], ' ')

	#plot figure
	def generate_figure(self, data, label, xaxis_title):
		#clear figure
		#plt.clf()
		ax = self.fig.add_subplot(111)
		#clear axis
		#ax.cla()
		spectrum=ax.plot(data[0],data[1])
		ax.set_xlabel(xaxis_title)
		ax.set_ylabel('reflectance')
		#add peak labels
		#for index, label_x in enumerate(label[0]):
			#ax.text(0.94*label_x, 1.05*label[1][index], str("%.1f" % label_x))
			#ax.annotate(str("%.1f" % label_x), xy=(label_x, label[1][index]), xytext=(1.1*label_x, 1.1*label[1][index]), arrowprops=dict(facecolor='black', shrink=0.1),)
		
		#remove self.label_time values
		#set label_peaks to generate figure again with loop that allows peak labeling (datacursor()) - set flag, reset flag in loop
		##otherwise label will appear when selecting peaks for calibration
		#have Tim download mpldatacursor package with pip?
		#need to figure out how to remove labels
		##canvas.delete("all") in function with a redraw function?
		#datacursor(spectrum, display='multiple', draggable=True, formatter='{x:.1f}'.format, bbox=None)
		
		self.canvas.show()
		self.canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True)
		#self.can.grid(row=1, column=0, columnspan=6, rowspan=3, padx=5, sticky=E+W+S+N)

		self.toolbar.update()
		self.canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=True)

	#def delete_figure(self):
		#Canvas.delete("all")
		#.destroy()


	#reset figure plot
	def reset_figure(self, data, label, xaxis_title):
		#clear figure
		plt.clf()
		ax = self.fig.add_subplot(111)
		#clear axis
		ax.cla()
		spectrum=ax.plot(data[0],data[1])
		ax.set_xlabel(xaxis_title)
		ax.set_ylabel('reflectance')

		self.canvas.show()
		self.canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True)

		self.toolbar.update()
		self.canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=True)


	#open file
	def onOpen(self):
		#displays .txt files in browser window
		#only reads time domain data files
		ftypes = [('binary files', '*.trc'), ('txt files', '*.txt')]
		dlg = tkFileDialog.Open(self, filetypes = ftypes)
		fl = dlg.show()
		
		if fl != '':
			if fl[-3:] == 'trc':
				self.time, self.intensity = read_lecroy_binary.read_timetrace(fl)
			elif fl[-3:] == 'txt':
				data = self.readFile(fl)
				self.time=data[0]
				self.intensity=data[1]
			#plots data in time domain
			self.time_domain()
			#self.labelButton.config(state=NORMAL)
			#self.deletelabelButton.config(state=NORMAL)
			#allows for smoothing of data
			self.smoothButton.config(state=NORMAL)
			#allows for resetting of plotting environment
			self.resetButton.config(state=NORMAL)
			self.wavenumberButton.config(state=NORMAL)
			self.wavelengthButton.config(state=NORMAL)

	#called when Smooth button is pressed
	#asks user for smooth input data
	def SmoothDialog(self, parent):
		top = self.top = Toplevel(self.parent)
		#window length for smoothing function
		#must be greater than poly value, positive, odd (51)
		Label(top, text="Window Length:").grid(row=0, column=0, sticky=W, padx=5, pady=5)
		self.w=Entry(top)
		self.w.grid(row=0, column=1, padx=5, pady=5)

		#polynomial order
		#must be less than window length (3)
		Label(top, text="Polynomial Order:").grid(row=1, column=0, sticky=W, padx=5, pady=5)
		self.p=Entry(top)
		self.p.grid(row=1, column=1, padx=5, pady=5)
		
		#calls DialogSmoothOK to set these values
		b=Button(top, text="OK", command=self.DialogSmoothOK)
		b.grid(row=2, column=1, padx=5, pady=5)
	
	#called from smooth dialog box within smooth routine
	def DialogSmoothOK(self):
		#sets user-defined window length
		self.window=float(self.w.get())
		#sets user-defined polynomail order
		self.poly=float(self.p.get())
		self.top.destroy()
		
	#called from mass dialog box within calibration routine
	def DialogOK(self):
		#sets user-defined mass calibration value to mass cal list
		self.cal_mass.append(float(self.e.get()))
		#closes dialog box
		self.top.destroy()
	

	#function for file input
	def readFile(self, filename):
		file=open(filename,'r')
		#there is some extra formatting on the first line - delete this data
		header=file.readline()
		header=file.readline()
		header=file.readline()
		header=file.readline()
		header=file.readline()
		#read each row in the file
		#list for temporary time data
		time=[]
		#list for temporary intensity data
		intensity=[]
		for line in file:
			#check file format:
			if ',' in line:
				#read each row - store data in columns
				temp = line.split(',')
				time.append(float(temp[0]))
				intensity.append(float(temp[1].rstrip('/n')))
			if '\t' in line:
				temp = line.split('\t')
				time.append(float(temp[0]))
				intensity.append(float(temp[1].rstrip('/n')))
			if ' ' in line:
				temp = line.split(' ')
				time.append(float(temp[0]))
				intensity.append(float(temp[1].rstrip('/n')))

		data=[time, intensity]
		return data



	#need to destroy parent before quitting, otherwise python crashes on Windows
	def quit_destroy(self):
		self.parent.destroy()
		self.parent.quit()

#quadratic function for time to mass conversion
def func_quad(x, a, b):
	return (1E10)*a*(x**2)+b

def func_lin(x, a, b):
	return (1E10)*a*x+b


def main():
	warnings.filterwarnings("ignore")
	#the root window is created
	root = Tk()

	#The geometry() method sets a size for the window and positions it on the screen.
	#The first two parameters are width and height of the window.
	#The last two parameters are x and y screen coordinates. 
	root.geometry("1000x500+200+50")
	
	#create the instance of the application class
	app = labTOF(root)
	
	#enter the main loop
	root.mainloop()  

if __name__ == '__main__':
	main()  