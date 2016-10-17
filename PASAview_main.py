import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.backend_bases import MouseEvent
from matplotlib.figure import Figure

import numpy as np
import bisect

import scipy as scipy
from scipy.optimize import curve_fit
from scipy import signal

from Tkinter import *
from ttk import *
import tkFileDialog

#import PASAview_plot
import sys

import warnings


class PASAview(Frame):

	#define parent window
	def __init__(self, parent):
		Frame.__init__(self, parent)

		#save a reference to the parent widget
		self.parent = parent

		#delegate the creation of the user interface to the initUI() method
		self.fig = Figure(figsize=(12,8), dpi=100)
		self.fig.subplots_adjust(bottom=0.15, left=0.13, right=0.95, top=0.95)

		self.canvas = FigureCanvasTkAgg(self.fig, self)
		self.toolbar = NavigationToolbar2TkAgg(self.canvas, self)
		self.toolbar.pack(side=TOP)

		#frame for buttons (at bottom)
		#buttons are arranged on grid, not pack
		self.frame_button = Frame(self)
		self.frame_button.pack(side = 'bottom', fill=BOTH, expand=1)
		
		#global variables
		#list containing wavelength domain values
		self.wavelength=[]
		self.wavelength_reference=[]
		#list containing wavenumber domain values
		self.wavenumber=[]
		self.wavenumber_reference=[]
		#list containing reflectance values
		self.refl=[]
		self.refl_reference=[]

		#list containing filename for legend
		self.spec_name=[]
		self.spec_name_reference=[]
		self.legend_fontsize=10
		
		#offset/scale values
		self.offset=[0.0]
		self.scale=[1.0]
		self.offset_reference=[]
		self.scale_reference=[]
		
		#flag to indicate autoscaling or user-defined scaling of axis
		#autoscale flag=0
		#user-defined flag=1
		self.define_axis_flag=0
		self.xlim=[1.6,3.6]
		self.ylim=[0,1]

		#linestyle definition
		self.linestyle_format=['k-']
		self.linestyle_format_reference=[]

		#flag to indicate whether wavelength or wavenumber is displayed
		#wavelength flag=0
		#wavenumber flag=1
		self.wavelength_wavenumber_flag=0

		#list containing label values
		self.label_wavelength=[]
		self.label_wavenumber=[]
		self.label_refl=[]
		self.label_size = float(10)
		#self.label_format = "%.0f"
		self.label_value = []
		#self.digits_after = 0
		#self.label_offset = 0.0
		#calibration point id
		self.cid=-99
		self.initUI()

	#container for other widgets
	def initUI(self):
		#set the title of the window using the title() method
		self.parent.title("PASA View")
		
		#apply a theme to widget
		self.style = Style()
		self.style.theme_use('default')
		
		#the Frame widget (accessed via the delf attribute) in the root window
		#it is expanded in both directions
		self.pack(fill=BOTH, expand=1)

		menubar = Menu(self.parent)
		self.parent.config(menu=menubar)
		
		#contains file menu items
		fileMenu = Menu(menubar, tearoff=0)
		menubar.add_cascade(label="File", menu=fileMenu)
		self.openMenu=Menu(menubar, tearoff=0)
		fileMenu.add_cascade(label="Open", menu=self.openMenu, state=NORMAL)
		self.openMenu.add_command(label="Open PASA Spectrum", command=self.onOpen)
		self.openMenu.add_command(label="Open Reference Spectrum", command=self.onOpenReference, state=DISABLED)
		#fileMenu.add_command(label="Open", command=self.onOpen)
		fileMenu.add_command(label="Export Data (ASCII file)", command=self.onExport)
		fileMenu.add_command(label="Quit", command=self.quit_destroy)

		#generate figure (no data at first)
		self.generate_figure([0,1], [[],[]], ' ', [[],[]])


		Label(self.frame_button, text="Modify Spectrum").grid(row=0, column=0, padx=5, pady=5, sticky=W)

		#smooth spectrum
		self.smoothButton = Button(self.frame_button, text="Smooth", command = self.smooth_data, state=DISABLED)
		self.smoothButton.grid(row=0, column=1, padx=5, pady=5, sticky=W)

		#offset spectrum
		self.offsetButton = Button(self.frame_button, text="Offset", command = self.offset_data, state=DISABLED)
		self.offsetButton.grid(row=0, column=2, padx=5, pady=5, sticky=W)


		Label(self.frame_button, text="Label Spectrum").grid(row=1, column=0, padx=5, pady=5, sticky=W)

		#label features in figure
		self.labelButton = Button(self.frame_button, text="Label Feature", command = self.label_feature, state=DISABLED)
		self.labelButton.grid(row=1, column=1, padx=5, pady=5, sticky=W)

		#remove all labels
		self.deletelabelButton = Button(self.frame_button, text="Remove Labels", command = self.delete_labels, state=DISABLED)
		self.deletelabelButton.grid(row=1, column=2, padx=5, pady=5, sticky=W)

		#define the font size of labels
		self.formatelabelButton = Button(self.frame_button, text="Format Label", command = self.format_labels)
		self.formatelabelButton.grid(row=1, column=3, padx=5, pady=5, sticky=W)


		Label(self.frame_button, text="Convert Domain").grid(row=2, column=0, padx=5, pady=5, sticky=W)

		#convert to wavelength domain
		self.wavelengthButton = Button(self.frame_button, text="Wavelength", command = self.wavelength_domain, state=DISABLED)
		self.wavelengthButton.grid(row=2, column=1, padx=5, pady=5, sticky=W)

		#convert to wavenumber domain
		self.wavenumberButton = Button(self.frame_button, text="Wavenumber", command = self.wavenumber_domain, state=DISABLED)
		self.wavenumberButton.grid(row=2, column=2, padx=5, pady=5, sticky=W)


		Label(self.frame_button, text="Configure Plot").grid(row=3, column=0, padx=5, pady=5, sticky=W)

		#define axes
		self.axesButton = Button(self.frame_button, text="Define Axes", command = self.define_axes, state=DISABLED)
		self.axesButton.grid(row=3, column=1, padx=5, pady=5, sticky=W)

		#define linestyle and legend
		self.legendButton = Button(self.frame_button, text="Legend Format", command = self.define_legend, state=DISABLED)
		self.legendButton.grid(row=3, column=2, padx=5, pady=5, sticky=W)

		#remove all spectra from plotting windows, reset variables
		self.resetButton = Button(self.frame_button, text="Reset", command = self.reset_plots, state=DISABLED)
		self.resetButton.grid(row=3, column=5, padx=5, pady=5, sticky=W)

		#quit PASAview
		self.quitButton = Button(self.frame_button, text="Quit", command = self.quit_destroy)
		self.quitButton.grid(row=3, column=6, padx=5, pady=5, sticky=E)


	#plot figure
	def generate_figure(self, data, label, xaxis_title, data_reference):
		#clear figure
		plt.clf()
		ax = self.fig.add_subplot(111)
		#clear axis
		ax.cla()
		spectrum=ax.plot(data[0],data[1], self.linestyle_format[0], label=self.spec_name)
		ax.set_xlabel(xaxis_title)#, fontsize=6)
		ax.set_ylabel('reflectance')#, fontsize=6)
		#for autoscale
		if self.define_axis_flag == 0:
			ax.autoscale_view()
		#for user-defined scaling
		if self.define_axis_flag == 1:
			ax.set_xlim(self.xlim)
			ax.set_ylim(self.ylim)


		#add reference spectra
		for index, wave in enumerate(data_reference[0]):
			ax.plot(wave, data_reference[1][index], self.linestyle_format_reference[index], label=self.spec_name_reference[index])

		#insert legend
		#the position could be user-defined
		#might consider adding this...
		ax.legend(fontsize=self.legend_fontsize)

		#add labels
		for index, label_x in enumerate(label[0]):
			an1 = ax.annotate(self.label_value[index], xy=(label_x, label[1][index]), xytext=(label_x, label[1][index]), fontsize=self.label_size)
			an1.draggable(state=True)

		
		self.canvas.show()
		self.canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True)

		self.toolbar.update()
		self.canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=True)


	#reset figure
	def reset_figure(self, data, label, xaxis_title):
		#clear figure
		plt.clf()
		ax = self.fig.add_subplot(111)
		#clear axis
		ax.cla()
		spectrum=ax.plot(data[0],data[1])
		ax.set_xlabel(xaxis_title)#, fontsize=6)
		ax.set_ylabel('reflectance')#, fontsize=6)
		#for autoscale
		if self.define_axis_flag == 0:
			ax.autoscale_view()
		#for user-defined scaling
		if self.define_axis_flag == 1:
			ax.set_xlim(self.xlim)
			ax.set_ylim(self.ylim)

		for index, label_x in enumerate(label[0]):
			an1 = ax.annotate(str(self.label_format % round(label_x + self.label_offset, int(self.digits_after))), xy=(label_x, label[1][index]), xytext=(label_x, label[1][index]), fontsize=self.label_size)
			an1.draggable(state=True)

		self.canvas.show()
		self.canvas.get_tk_widget().pack(side=BOTTOM, fill=BOTH, expand=True)
		self.toolbar.update()
		self.canvas._tkcanvas.pack(side=TOP, fill=BOTH, expand=True)


	#open file
	def onOpen(self):
		#displays .txt files in browser window
		#only reads wavelength domain data files
		ftypes = [('txt files', '*.txt'), ('csv files', '*.csv'), ('ASCII files', '*.asc')]
		dlg = tkFileDialog.Open(self, filetypes = ftypes)
		fl = dlg.show()
		self.spec_name=fl.rsplit('/',1)[1][0:-4]
		
		if fl != '':
			if fl[-3:] == 'txt':
				data = self.readFile(fl)
				self.refl=data[1]
				#self.refl = [x+0.00075 for x in data[1]]
				self.wavelength=data[0]
				if self.wavelength_wavenumber_flag==0:
					self.wavelength_domain()
				elif self.wavelength_wavenumber_flag==1:
					self.wavenumber_domain()

			elif fl[-3:] == 'csv':
				data = self.readFile(fl)
				self.refl=data[1]
				#self.refl = [x+0.00075 for x in data[1]]
				self.wavelength=data[0]
				if self.wavelength_wavenumber_flag==0:
					self.wavelength_domain()
				elif self.wavelength_wavenumber_flag==1:
					self.wavenumber_domain()

			elif fl[-3:] == 'asc':
				data = self.readFile(fl)
				#ignore data with refl values less than 0
				index_pos=bisect.bisect(data[1], 0)
				self.refl_reference.append(data[1][index_pos:])
				self.wavelength_reference.append(data[0][index_pos:])
				self.wavelength=data[0]
				if self.wavelength_wavenumber_flag==0:
					self.wavelength_domain()
				elif self.wavelength_wavenumber_flag==1:
					self.wavenumber_domain()


			#allows reference spectrum to be added
			self.openMenu.entryconfig("Open Reference Spectrum", state=NORMAL)
			#allows labels to be generated
			self.labelButton.config(state=NORMAL)
			self.deletelabelButton.config(state=NORMAL)
			#allows for smoothing/offset of data
			self.smoothButton.config(state=NORMAL)
			self.offsetButton.config(state=NORMAL)
			#allows for domain conversion
			self.wavelengthButton.config(state=NORMAL)
			self.wavenumberButton.config(state=NORMAL)
			#allows plot to be configured
			self.axesButton.config(state=NORMAL)
			self.resetButton.config(state=NORMAL)
			self.legendButton.config(state=NORMAL)

	def onOpenReference(self):
		#displays .txt files in browser window
		#only reads wavelength domain data files
		ftypes = [('txt files', '*.txt'), ('csv files', '*.csv'), ('ASCII files', '*.asc')]
		dlg = tkFileDialog.Open(self, filetypes = ftypes)
		fl = dlg.show()
		self.spec_name_reference.append(fl.rsplit('/',1)[1][0:-4])
		self.linestyle_format_reference.append('g-')
		
		if fl != '':
			if fl[-3:] == 'txt':
				data = self.readFile(fl)
				#self.refl_reference=data[1]
				self.refl_reference.append(data[1])
				self.wavelength_reference.append(data[0])
				if self.wavelength_wavenumber_flag==0:
					self.wavelength_domain()
				elif self.wavelength_wavenumber_flag==1:
					self.wavenumber_domain()

			elif fl[-3:] == 'csv':
				data = self.readFile(fl)
				#self.refl_reference=data[1]
				self.refl_reference.append(data[1])
				self.wavelength_reference.append(data[0])
				if self.wavelength_wavenumber_flag==0:
					self.wavelength_domain()
				elif self.wavelength_wavenumber_flag==1:
					self.wavenumber_domain()

			elif fl[-3:] == 'asc':
				data = self.readFile(fl)
				#ignore leading negative values
				index_pos=bisect.bisect(data[1], 0)
				self.refl_reference.append(data[1][index_pos:])
				self.wavelength_reference.append(data[0][index_pos:])
				if self.wavelength_wavenumber_flag==0:
					self.wavelength_domain()
				elif self.wavelength_wavenumber_flag==1:
					self.wavenumber_domain()
		
	#function for file input
	def readFile(self, filename):
		file=open(filename,'r')
		if filename[-3:] == 'asc':
			#there is some extra formatting on the first several lines
			header=file.readline()
			header=file.readline()
			header=file.readline()
			header=file.readline()
			header=file.readline()
			header=file.readline()
			header=file.readline()
			header=file.readline()
			header=file.readline()
			header=file.readline()
			header=file.readline()
			header=file.readline()
			header=file.readline()
			header=file.readline()
			header=file.readline()
			
		header=file.readline()
		#read each row in the file
		#list for temporary wavelength data
		wavelength=[]
		#list for temporary reflectance data
		refl=[]
		for line in file:
			#check file format:
			if ',' in line:
				#read each row - store data in columns
				wavelength = line.split(',')
				wavelength.append(float(temp[0]))
				refl.append(float(temp[1].rstrip('/n')))
			elif '\t' in line:
				temp = line.split('\t')
				wavelength.append(float(temp[0]))
				refl.append(float(temp[1].rstrip('/n')))
			elif '      ' in line:
				temp = line.split('      ')
				wavelength.append(float(temp[1]))
				refl.append(float(temp[2]))
			elif '     ' in line:
				temp = line.split('     ')
				wavelength.append(float(temp[0]))
				refl.append(float(temp[1].rstrip('/n')))
			elif ' ' in line:
				temp = line.split(' ')
				wavelength.append(float(temp[0]))
				refl.append(float(temp[1].rstrip('/n')))

		data=[wavelength, refl]
		return data


	#export data to txt file
	def onExport(self):
		#save header info (date/time, ask user for instrument)?
		#ask for save file name
		savefile = tkFileDialog.asksaveasfile(mode='wb', defaultextension=".txt")
		# asksaveasfile return `None` if dialog closed with "cancel".
		if savefile is None:
			return
		#export wavelength or wavenumber domain data depending on flag (what is plotted)
		if self.wavelength_wavenumber_flag == 0:
			x=self.wavelength
		else:
			x=self.wavenumber
		y=self.refl
		
		for i in range(len(x)):
			savefile.write(str(x[i]))
			savefile.write(' ')
			savefile.write(str(y[i]))
			savefile.write('\r\n')
		savefile.close()


	#convert to wavelength domain
	#disabled until spectrum is plotted
	def wavelength_domain(self):
		self.wavelength_wavenumber_flag=0
		self.generate_figure([self.wavelength,self.refl], [self.label_wavelength, self.label_refl], 'wavelength ($\mu$m)', [self.wavelength_reference ,self.refl_reference])
	
	#convert to wavenumber domain	
	#disabled until spectrum is plotted
	def wavenumber_domain(self):
		self.wavelength_wavenumber_flag=1
		self.label_wavenumber=[10000/x for x in self.label_wavelength]
		#convert wavelength reference spectra to wavenumber
		self.wavenumber_reference=[]
		for i in self.wavelength_reference:
			temp=[10000/x for x in i]
			self.wavenumber_reference.append(temp)
		self.wavenumber = [10000/x for x in self.wavelength]
		self.generate_figure([self.wavenumber,self.refl], [self.label_wavenumber, self.label_refl], 'wavenumber (cm$^{-1}$)', [self.wavenumber_reference ,self.refl_reference])
		
	#smooth data
	#disabled until spectrum is plotted
	def smooth_data(self):
		#purpose of smoothing function: to display smoothed plot
		self.SmoothDialog(self.parent)
		#wait for dialog to close
		self.top.wait_window(self.top)
		if self.window != 0:
			smoothed_signal = scipy.signal.savgol_filter(self.refl,self.window,self.poly)
			#convert from array to list
			self.refl=smoothed_signal.tolist()
		
		if self.spec_name_reference != []:
			for index, name in enumerate(self.spec_name_reference):
				if self.window_reference[index] !=0:
					smoothed_signal = scipy.signal.savgol_filter(self.refl_reference[index],self.window_reference[index],self.poly_reference[index])
					self.refl_reference[index]=smoothed_signal.tolist()

		if self.wavelength_wavenumber_flag == 1:
			self.wavenumber_domain()
		else:
			self.wavelength_domain()

	#called when Smooth button is pressed
	#asks user for smooth input data
	def SmoothDialog(self, parent):
		top = self.top = Toplevel(self.parent)
		Label(top, text="PASA Spectrum:").grid(row=0, column=0, sticky=W, padx=5, pady=5)

		#window length for smoothing function
		#must be greater than poly value, positive, odd (51)
		Label(top, text=self.spec_name).grid(row=1, column=0, sticky=W, padx=5, pady=5)

		Label(top, text="Window Length:").grid(row=1, column=1, sticky=W, padx=5, pady=5)
		self.w=Entry(top)
		self.w.insert(0, '51')
		self.w.grid(row=1, column=2, padx=5, pady=5)

		#polynomial order
		#must be less than window length (3)
		Label(top, text="Polynomial Order:").grid(row=1, column=3, sticky=W, padx=5, pady=5)
		self.p=Entry(top)
		self.p.insert(0, '3')
		self.p.grid(row=1, column=4, padx=5, pady=5)

		index = -2
		if self.spec_name_reference != []:
			Label(top, text="Reference Spectrum:").grid(row=2, column=0, sticky=W, padx=5, pady=5)
			for index, name in enumerate(self.spec_name_reference):
				if index == 0:
					self.rw=[' ']*len(self.spec_name_reference)
					self.rp=[' ']*len(self.spec_name_reference)
				Label(top, text=name).grid(row=3+index, column=0, sticky=W, padx=5, pady=5)
				Label(top, text="Window Length:").grid(row=3+index, column=1, sticky=W, padx=5, pady=5)
				self.rw[index]=Entry(top)
				self.rw[index].insert(0, '0')
				self.rw[index].grid(row=3+index, column=2, padx=5, pady=5)
		
				Label(top, text="Polynomial Order:").grid(row=3+index, column=3, sticky=W, padx=5, pady=5)
				self.rp[index]=Entry(top)
				self.rp[index].insert(0, '0')
				self.rp[index].grid(row=3+index, column=4, padx=5, pady=5)

		
		#calls DialogSmoothOK to set these values
		b=Button(top, text="OK", command=self.DialogSmoothOK)
		b.grid(row=4+index, column=4, padx=5, pady=5)

	#called from smooth dialog box within smooth routine
	def DialogSmoothOK(self):
		#sets user-defined window length
		self.window=float(self.w.get())
		#sets user-defined polynomail order
		self.poly=float(self.p.get())
		if self.spec_name_reference != []:
			self.window_reference=[]
			self.poly_reference=[]
			for index, wave in enumerate(self.wavelength_reference):
				#self.spec_name_reference.append(str(self.rn.get()))
				self.window_reference.append(float(self.rw[index].get()))
				self.poly_reference.append(float(self.rp[index].get()))
		self.top.destroy()


	#offset data
	#disabled until spectrum is plotted
	def offset_data(self):
		self.OffsetDialog(self.parent)
		#wait for dialog to close
		self.top.wait_window(self.top)
		#scale/offset spectrum
		self.refl = [(x*self.scale)+self.offset for x in self.refl]
		if self.spec_name_reference != []:
			temp_refl = []
			for index, name in enumerate(self.spec_name_reference):
				temp_refl.append([(x*self.scale_reference[index]) + self.offset_reference[index] for x in self.refl_reference[index]])
			self.refl_reference = temp_refl
		if self.wavelength_wavenumber_flag == 1:
			self.wavenumber_domain()
		else:
			self.wavelength_domain()

	#called when Offset button is pressed
	#asks user for smooth input data
	def OffsetDialog(self, parent):
		top = self.top = Toplevel(self.parent)
		Label(top, text="PASA Spectrum:").grid(row=1, column=0, sticky=W, padx=5, pady=5)
		Label(top, text=self.spec_name).grid(row=2, column=0, sticky=W, padx=5, pady=5)
		Label(top, text="Offset:").grid(row=2, column=1, sticky=W, padx=5, pady=5)
		self.po=Entry(top)
		self.po.insert(0, '0')
		self.po.grid(row=2, column=2, padx=5, pady=5)
		
		Label(top, text="Scale:").grid(row=2, column=3, sticky=W, padx=5, pady=5)
		self.ps=Entry(top)
		self.ps.insert(0, '1.0')
		self.ps.grid(row=2, column=4, padx=5, pady=5)

		index = -2
		if self.spec_name_reference != []:
			Label(top, text="Reference Spectrum:").grid(row=3, column=0, sticky=W, padx=5, pady=5)
			for index, name in enumerate(self.spec_name_reference):
				if index == 0:
					self.ro=[' ']*len(self.spec_name_reference)
					self.rs=[' ']*len(self.spec_name_reference)
				Label(top, text=name).grid(row=4+index, column=0, sticky=W, padx=5, pady=5)
				Label(top, text="Offset:").grid(row=4+index, column=1, sticky=W, padx=5, pady=5)
				self.ro[index]=Entry(top)
				self.ro[index].insert(0, '0')
				self.ro[index].grid(row=4+index, column=2, padx=5, pady=5)
		
				Label(top, text="Scale:").grid(row=4+index, column=3, sticky=W, padx=5, pady=5)
				self.rs[index]=Entry(top)
				self.rs[index].insert(0, '1.0')
				self.rs[index].grid(row=4+index, column=4, padx=5, pady=5)
	
		#calls DialogOffsetOK to set these values
		b=Button(top, text="OK", command=self.DialogOffsetOK)
		b.grid(row=5+index, column=4, padx=5, pady=5)

	#called from offset dialog box within smooth routine
	def DialogOffsetOK(self):
		self.offset = float(self.po.get())
		self.scale = float(self.ps.get())
		if self.spec_name_reference != []:
			self.offset_reference=[]
			self.scale_reference=[]
			for index, wave in enumerate(self.wavelength_reference):
				#self.spec_name_reference.append(str(self.rn.get()))
				self.offset_reference.append(float(self.ro[index].get()))
				self.scale_reference.append(float(self.rs[index].get()))
		self.top.destroy()


	#format labels
	def format_labels(self):
		self.FormatLabelDialog(self.parent)
		#wait for dialog to close
		self.top.wait_window(self.top)
		self.label_size = float(self.label_size)
		#self.label_format = "%."+self.digits_after+"f"
		if self.wavelength_wavenumber_flag==0:
			self.wavelength_domain()
		elif self.wavelength_wavenumber_flag==1:
			self.wavelength_domain()

	def FormatLabelDialog(self, parent):
		top = self.top = Toplevel(self.parent)
		#font size
		Label(top, text="Font Size:").grid(row=0, column=0, sticky=W, padx=5, pady=5)
		self.fs=Entry(top)
		self.fs.insert(0, '10')
		self.fs.grid(row=0, column=1, padx=5, pady=5)
		
		#calls DialogLabelOK to set these values
		b=Button(top, text="OK", command=self.DialogLabelOK)
		b.grid(row=3, column=1, padx=5, pady=5)

	#called from label dialog box within label format routine
	def DialogLabelOK(self):
		#sets user-defined font size
		self.label_size=float(self.fs.get())
		self.top.destroy()
		
	#function to label features on figure in order to save figure as an image file with labels
	#disabled until spectrum is plotted
	def label_feature(self):
		#ask for peak (on_click_label)
		self.cid=self.canvas.mpl_connect('button_press_event', self.on_click_label)
			
	#called when click is made to label peak
	def on_click_label(self, event):
		temp_len=len(self.label_refl)
		#if wavelength flag is set
		if self.wavelength_wavenumber_flag==0:
			#temp_len=len(self.label_wavenumber)
			#when the click is made within the plotting window
			if event.inaxes is not None:
				self.label_wavelength.append(event.xdata)
				self.label_refl.append(event.ydata)
				#self.LabelDialog(self.parent)
				#self.wavelength_domain()
			#if click is outside plotting window
			else:
				print 'Clicked ouside axes bounds but inside plot window'		
		#if the wavenumber flag is set
		elif self.wavelength_wavenumber_flag==1:
			#temp_len=len(self.label_wavelength)
			#when the click is made within the plotting window
			if event.inaxes is not None:
				self.label_wavenumber.append(event.xdata)
				self.label_refl.append(event.ydata)
				#self.LabelDialog(self.parent)
				#self.wavenumber_domain()
			#if click is outside plotting window
			else:
				print 'Clicked ouside axes bounds but inside plot window'		
		#self.peak_intensity=event.ydata
		#plot label		
		#disconnect from click event when a new peak label value is set
		if temp_len < len(self.label_refl):
			self.LabelDialog(self.parent)
			self.canvas.mpl_disconnect(self.cid)

	#asks user for featue label associated with selection
	def LabelDialog(self, parent):
		top = self.top = Toplevel(self.parent)
		Label(top, text="Spectral Feature:").pack()
		self.v=Entry(top)
		self.v.insert(0, 'H$_2$O')
		self.v.pack(padx=5)
		#calls DialogOK to set mass value to input		
		b=Button(top, text="OK", command=self.DialogOK)
		b.pack(pady=5)

	#called from label dialog box within feature label routine
	def DialogOK(self):
		#sets user-defined mass calibration value to mass cal list
		self.label_value.append(self.v.get())
		#replots with labels
		if self.wavelength_wavenumber_flag==0:
			self.wavelength_domain()
		elif self.wavelength_wavenumber_flag==1:
			self.wavelength_domain()
		#closes dialog box
		self.top.destroy()

	#remove labels when button is selected
	#disabled until spectrum is plotted
	def delete_labels(self):
		#deletes peak label arrays
		self.label_wavenumber=[]
		self.label_wavelength=[]
		self.label_refl=[]
		#if wavelength/wavenumber flag is set
		if self.wavelength_wavenumber_flag==0:
			self.wavelength_domain()
		elif self.wavelength_wavenumber_flag==1:
			self.wavenumber_domain()


	#called when define axes button is pressed
	#asks user to define axes range
	#disabled until spectrum is plotted
	def define_axes(self):
		self.DefineAxes(self.parent)
		#wait for dialog to close
		self.top.wait_window(self.top)
		self.define_axis_flag=1
		if self.wavelength_wavenumber_flag == 1:
			self.wavenumber_domain()
		else:
			self.wavelength_domain()

	def DefineAxes(self, parent):
		top = self.top = Toplevel(self.parent)

		#x axis range
		Label(top, text="X Axis:").grid(row=0, column=0, sticky=W, padx=5, pady=5)
		self.x1=Entry(top)
		if self.wavelength_wavenumber_flag == 0:
			self.x1.insert(0, 1.6)
		elif self.wavelength_wavenumber_flag == 1:
			self.x1.insert(0, 2780)
		self.x1.grid(row=0, column=1, padx=5, pady=5)
		self.x2=Entry(top)
		if self.wavelength_wavenumber_flag == 0:
			self.x2.insert(0, 3.6)
		elif self.wavelength_wavenumber_flag == 1:
			self.x2.insert(0, 6250)
		self.x2.grid(row=0, column=2, padx=5, pady=5)

		#y axis range
		Label(top, text="Y Axis:").grid(row=1, column=0, sticky=W, padx=5, pady=5)
		self.y1=Entry(top)
		self.y1.insert(0, self.ylim[0])
		self.y1.grid(row=1, column=1, padx=5, pady=5)
		self.y2=Entry(top)
		self.y2.insert(0, self.ylim[1])
		self.y2.grid(row=1, column=2, padx=5, pady=5)
		#calls DialogSmoothOK to set these values
		b=Button(top, text="OK", command=self.DialogAxesOK)
		b.grid(row=2, column=1, padx=5, pady=5)

	#called from axes define dialog box
	def DialogAxesOK(self):
		#sets user-defined x axis values
		x_temp1=float(self.x1.get())
		x_temp2=float(self.x2.get())
		self.xlim=[x_temp1, x_temp2]
		#sets user-defined y axis values
		y_temp1=float(self.y1.get())
		y_temp2=float(self.y2.get())
		self.ylim=[y_temp1, y_temp2]
		self.top.destroy()


	#called when legend button is pressed
	#asks user to define linestyle, legend name, legend font size
	#disabled until spectrum is plotted
	def define_legend(self):
		self.DefineLegend(self.parent)
		#wait for dialog to close
		self.top.wait_window(self.top)
		if self.wavelength_wavenumber_flag == 1:
			self.wavenumber_domain()
		else:
			self.wavelength_domain()

	def DefineLegend(self, parent):
		top = self.top = Toplevel(self.parent)
		#PASA spectrum
		Label(top, text="PASA Spectrum:").grid(row=1, column=0, sticky=W, padx=5, pady=5)
		Label(top, text="Name:").grid(row=2, column=0, sticky=W, padx=5, pady=5)
		self.pn=Entry(top)
		self.pn.insert(0, self.spec_name)
		self.pn.grid(row=2, column=1, padx=5, pady=5)
		
		Label(top, text="Linestyle:").grid(row=2, column=3, sticky=W, padx=5, pady=5)
		self.pl=Entry(top)
		self.pl.insert(0, self.linestyle_format[0])
		self.pl.grid(row=2, column=4, padx=5, pady=5)

		index = -2
		if self.spec_name_reference != []:
			Label(top, text="Reference Spectrum:").grid(row=3, column=0, sticky=W, padx=5, pady=5)
			for index, name in enumerate(self.spec_name_reference):
				if index == 0:
					self.rn=[' ']*len(self.spec_name_reference)
					self.rl=[' ']*len(self.spec_name_reference)
				Label(top, text="Name:").grid(row=4+index, column=0, sticky=W, padx=5, pady=5)
				self.rn[index]=Entry(top)
				self.rn[index].insert(0, name)
				self.rn[index].grid(row=4+index, column=1, padx=5, pady=5)
		
				Label(top, text="Linestyle:").grid(row=4+index, column=3, sticky=W, padx=5, pady=5)
				self.rl[index]=Entry(top)
				self.rl[index].insert(0, self.linestyle_format_reference[index])
				self.rl[index].grid(row=4+index, column=4, padx=5, pady=5)
			
		#asks for legend font size
		Label(top, text="Legend:").grid(row=5+index, column=0, sticky=W, padx=5, pady=5)
		Label(top, text="Font Size:").grid(row=6+index, column=0, sticky=W, padx=5, pady=5)
		self.lf=Entry(top)
		self.lf.insert(0, self.legend_fontsize)
		self.lf.grid(row=6+index, column=4, padx=5, pady=5)

		#calls DialogLegendOK to set these values
		b=Button(top, text="OK", command=self.DialogLegendOK)
		b.grid(row=7+index, column=4, padx=5, pady=5)

	#called from linestyle define dialog box
	def DialogLegendOK(self):
		#sets user-defined x axis values
		self.spec_name = str(self.pn.get())
		self.linestyle_format = [str(self.pl.get())]
		if self.spec_name_reference != []:
			self.spec_name_reference=[]
			self.linestyle_format_reference=[]
			for index, wave in enumerate(self.wavelength_reference):
				#self.spec_name_reference.append(str(self.rn.get()))
				self.spec_name_reference.append(str(self.rn[index].get()))
				self.linestyle_format_reference.append(str(self.rl[index].get()))
		self.legend_fontsize = (self.lf.get())
		self.top.destroy()

	#reset plotting window
	#disabled until spectrum is plotted
	def reset_plots(self):
		#generate figure (no data at first)
		#resets all necessary variables
		self.wavelength_reference=[]
		self.wavenumber_reference=[]
		self.refl_reference=[]
		self.wavelength_wavenumber_flag=0
		self.label_wavelength=[]
		self.label_wavenumber=[]
		self.label_refl=[]
		self.label_value=[]
		self.define_axis_flag=0
		self.xlim=[1.6,3.6]
		self.ylim=[0,1]
		self.linestyle_format=['k-']
		self.reset_figure([0,1], [[],[]], ' ')
		self.spec_name_reference = []
		self.spec_name = []
		self.rn = []
		self.rl = []
		self.ro = []
		self.rs = []
		self.rw = []
		self.rp = []
		
		#prohibits reference spectrum to be added
		self.openMenu.entryconfig("Open Reference Spectrum", state=DISABLED)
		#prohibits labels to be generated
		self.labelButton.config(state=DISABLED)
		self.deletelabelButton.config(state=DISABLED)
		#prohibits for modification of data
		self.smoothButton.config(state=DISABLED)
		self.offsetButton.config(state=DISABLED)
		#prohibits for domain conversion
		self.wavelengthButton.config(state=DISABLED)
		self.wavenumberButton.config(state=DISABLED)
		#prohibits plot to be configured
		self.axesButton.config(state=DISABLED)
		self.legendButton.config(state=DISABLED)
		self.resetButton.config(state=DISABLED)

	#need to destroy parent before quitting, otherwise python crashes on Windows
	def quit_destroy(self):
		self.parent.destroy()
		self.parent.quit()


def main():
	warnings.filterwarnings("ignore")
	#the root window is created
	root = Tk()

	#The geometry() method sets a size for the window and positions it on the screen.
	#The first two parameters are width and height of the window.
	#The last two parameters are x and y screen coordinates. 
	root.geometry("1000x700+100+30")
	
	#create the instance of the application class
	app = PASAview(root)
	
	#enter the main loop
	root.mainloop()  

if __name__ == '__main__':
	main()  