from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.properties import NumericProperty, ReferenceListProperty,\
    ObjectProperty
from kivy.core.window import Window
from kivy.graphics import Color, Ellipse, SmoothLine, Rectangle
from kivy.graphics.instructions import Instruction, InstructionGroup
import math, random
from kivy.config import Config

def get_dis(c1,c2):
	#returns the distance between two points
	return math.sqrt((c1[0]-c2[0])**2+(c1[1]-c2[1])**2)
	
def car_to_pol(car):
	#gets polar coords relative to center from cartisian [r,t]
	global c
	dx=car[0]-c[0]
	#can't divide by 0
	if dx==0:
		dx=.0000000000000000001
	#atan(x) only outputs +/-180
	b=0
	if dx<0:
		b=180
	pol= [get_dis(c,car), math.degrees(math.atan((car[1]-c[1])/dx))+b]
	if pol[1]<0:
		pol[1]+=360
	return pol

def pol_to_car(pol):
	#gets cartisian coords to polar from center [x,y]
	global c
	car= [pol[0]*math.cos(math.radians(pol[1]))+c[0], pol[0]*math.sin(math.radians(pol[1]))+c[1]]
	return car
	
def limitpos(coords):
		#limits possible locations
		
		incr=80
		ipol=car_to_pol(coords)
		opol=ipol
		# ~ opol[0]=(ipol[0])//incr*incr + incr/2
		if opol[0]<100: opol[0]=100
		
		#trying to snap to angles too
		# ~ incr=360/(5+(opol[0]-incr)/incr)
		# ~ print(5+(opol[0]-incr)//incr)
		# ~ if incr==0:
			# ~ incr= .000000000000001
		# ~ opol[1]=(ipol[1]-90)//incr*incr + incr/2 + 90
		return pol_to_car(opol)

def find_closest_circles():
	pass

def limitoverlap(coords):
	pass
	
class SelectionWindow(Widget):
	#needs to allow input of variables
	#needs to handle click offs
	pass
	
class Conector(Widget):
	#needs to be able to path around items it isn't connected to
	#needs to handle overlap
	pass

class ItemIcon(Widget):
	#needs to avoid being placed on top of anything important
	#needs to open selection window
	#needs to differentiate between movement comand and selection comand
	#^ differentiate by time for click
	pass

class MovingIcon(Widget):
	#folows cursor while held
	#spawns ItemIcon if released at valid location
	#despawns when released
	def __init__(self, **kwargs):
		super(MovingIcon,self).__init__(**kwargs)
		global c
		self.c=c
		self.local_c=[0,0]
		if kwargs is not None:
			for key, value in kwargs.items():
				if(key=='pos'): self.local_c=value
		
	def makeicon(self,r):
		self.r=r*.9
		self.updateloc(self.local_c)
	
	def updateloc(self, coords):
		self.local_c=coords
		self.canvas.clear()
		self.icon=InstructionGroup()
		self.canvas.opacity=.3
		self.icon.add(Color(.3,.3,.3))
		
		self.icon.add(Color(1,1,1))
		self.icon.add(Ellipse(size=(2*self.r,2*self.r),pos=(self.local_c[0]-self.r,self.local_c[1]-self.r)))
		self.icon.add(SmoothLine(circle=(self.local_c[0],self.local_c[1],self.r+4),width=3))
		self.icon.add(Color(.3,.3,.3))
		self.icon.add(SmoothLine(circle=(self.local_c[0],self.local_c[1],self.r),width=3))
		for group in [self.icon]:
			self.canvas.add(group)
			
	def on_touch_move(self, touch):
		l=limitpos(touch.pos)
		self.updateloc(l)
		
	def on_touch_up(self,touch):
		print(self.isgood(touch.pos))
		self.parent.remove_widget(self)
	
	def isgood(self, coords):
		#change to findfree() find nerest avalible spot to cursor
		global inuse
		for cir in inuse:
			if (get_dis([cir[0],cir[1]],coords) <= cir[2]+self.r+5):
				return False
		return True
	
	def findfree(self,coords):
		pass
		
	
class MenuIcon(Widget):
	#spawns moving icon on touch
	def __init__(self, **kwargs):
		super(MenuIcon,self).__init__(**kwargs)
		self.local_c=[0,0]
		self.r=30
		if kwargs is not None:
			for key, value in kwargs.items():
				if(key=='pos'): self.local_c=value
		global inuse
		inuse.append([self.local_c[0],self.local_c[1],self.r])
		self.icon=InstructionGroup()
		self.icon.add(Color(1,1,1))
		self.icon.add(Ellipse(size=(2*self.r,2*self.r),pos=(self.local_c[0]-self.r,self.local_c[1]-self.r)))
		self.icon.add(SmoothLine(circle=(self.local_c[0],self.local_c[1],self.r+4),width=3))
		self.icon.add(Color(.3,.3,.3))
		self.icon.add(SmoothLine(circle=(self.local_c[0],self.local_c[1],self.r),width=3))
		for group in [self.icon]:
			self.canvas.add(group)
			
	def options(self):
		pass
	
	def on_touch_down(self,touch):
		if get_dis(self.local_c,touch.pos) < 40:
			a=MovingIcon(pos=touch.pos)
			a.makeicon(self.r)
			self.add_widget(a)

class MenuCircle(Widget):
	#base of UI objects
	def __init__(self, **kwargs):
		super(MenuCircle, self).__init__(**kwargs)
		global c
		global inuse
		r=100
		inuse=[[c[0],c[1],r]]
		self.pos=[c[0]-r,c[1]-r]
		local_c=c
		options=["start_node", "time", "variables","flow control","network","I/O","Sound/Notifications", "Interface"]
		with self.canvas:
			Color(.3,.3,.3)
			SmoothLine(circle=(c[0],c[1],r),width=3)
		mi=MenuIcon(pos=pol_to_car([r,90]))
		self.add_widget(mi)
		
class MagScreen(FloatLayout):
	def __init__(self, **kwargs):
		super(MagScreen, self).__init__(**kwargs)
		global c
		c=Window.center
		self.size=Window.size
		mc=MenuCircle()
		self.add_widget(mc)
		#make background with markers

class Magiscript(App):
	def build(self):
		self.layout=MagScreen()
		
		return self.layout
		
if __name__ == '__main__':
	Config.set('graphics','window_state','visible')
	Window.clearcolor=(1,1,1,1)
	Magiscript().run()
    
# ~ class OutStream(Label):
	# ~ def __init__(self, **kwargs):
		# ~ super(OutStream, self).__init__(**kwargs)
		# ~ self.text="test"
		# ~ self.color=[.3,.3,.3]
	# ~ def update(self,s):
		# ~ self.text=str(s)
	# ~ def on_touch_down(self,touch):
		# ~ self.update(touch)
