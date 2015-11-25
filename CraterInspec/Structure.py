# Library import
from PDS_Extractor import *
import numpy as np
import pandas as pd
import matplotlib.pylab as plt
from mpl_toolkits.basemap import Basemap
from matplotlib import cm
import os,sys
from palettable.colorbrewer.diverging import RdBu_9_r,BrBG_10_r


class Structure(object):
    ''' A class able to gather information on Topography and Image about
    a specified area around a geological unit (Crater or dome).

    parameters:

    - structure : Name of the structure. Either "Crater" or "Dome".
    - ide : This class allow to defined the unit by its name "n" or its
    index "i".
    - idx : Corresponding name or index

    attributes:

    - structure : Type of the geological unit (Crater/Dome)
    - racine : path for project
    - ppdlola : resolution of the Lola image
    - ppdwac : resolution of the Wac image
    - Name/Diameter/Radius/Lat/Long : property of the geological unit
    - Taille_Window : Size of the window to consider around the unit

    methods:
    
    - Lambert_Window :  This method is used to determine the bottom-left
    and upper-right coordinates for a square Lambert Azimuthal
    equal area projection centered at (lat0,long0 with a size radius).

    - Cylindrical_Window : This method is used to determine the bottom-left
    and upper-right coordinates for a cylindrical projection
    centered at (lat0,long0 with a size radius). See
    Wikipedia

    
    Example:
    
    For instance, say we want to image the crater Copernicus. We can the
    define an instance of the class
    C = Structure('n','Copernicus','Crater')
    -
    '''

    racine = '/Users/thorey/Documents/These/Projet/FFC/CraterInspector'
    
    def __init__(self,ide,idx,structure):
        '''
        - structure : Name of the structure. Either "Crater" or "Dome".
        - ide : This class allow to defined the unit by its name "n" or its
        index "i".
        - idx : Corresponding name or index

        
        '''

        self.structure = structure
        self.racine = Structure.racine
        self.ppdlola = 512
        self.ppdwac = 128

        if structure == 'Dome':
            self.structures = pd.read_csv(os.path.join(self.racine,'Data',
            'Data_Dome.csv'))
        elif structure == 'Crater':
            self.structures = pd.read_csv(os.path.join(self.racine,'Data',
            'Data_Crater.csv'))
        else:
            raise ValueError("Structure %s is not recognized. Possible\n\
                             values are: %s"% (structure, ', '.join(['Dome','Crater'])))

        inde = {'n':'Name','i':'Index'}
        df = self.structures[self.structures[inde[ide]] == idx]
        if len(df) == 0:
            raise ValueError("The tuple (%s,%s) does not correspond\n \
                             to any structure in the dataset. "%(ide,idx))
            
        [setattr(self,f,float(df[f])) for f in df.columns if f not in ['Name']]

        assert self.Long>0.0, 'Longitude has to span 0-360 !!!'
        self.Name = df.Name.iloc[0]
        self.Taille_Window = 0.8*self.Diameter

        

    def _kp_func(self,lat,lon,lat0,long0):
        kp = float(1.0) + np.sin(lat0)*np.sin(lat) + np.cos(lat0)*np.cos(lat)*np.cos(lon-long0)
        kp = np.sqrt(float(2)/kp)
        return kp

    def Lambert_Window(self,radius,lat0,long0):
        '''
        This method is used to determine the bottom-left
        and upper-right coordinates for a square Lambert Azimuthal
        equal area projection centered at (lat0,long0 with a size radius).
        '''
        
        radius = radius*360.0/(np.pi*2*1734.4)
        radius = radius*np.pi / 180.0
        lat0 = lat0*np.pi/180.0
        long0 = long0*np.pi/180.0

        bot = self._kp_func(lat0-radius,long0,lat0,long0)
        bot = bot * ( np.cos(lat0)*np.sin(lat0-radius) - np.sin(lat0)*np.cos(lat0-radius) )
        x = bot
        y = bot
        rho = np.sqrt(x**2 + y**2)
        c = 2.0 * np.arcsin(rho/float(2.0))
        latll = np.arcsin(np.cos(c)*np.sin(lat0)  + y*np.sin(c)*np.cos(lat0)/rho ) * float(180.0) / np.pi
        lon = long0  + np.arctan2(x*np.sin(c), rho*np.cos(lat0)*np.cos(c) - y*np.sin(lat0)*np.sin(c))
        longll = lon * 180.0 / np.pi

        x = -bot
        y = -bot
        rho = np.sqrt(x**2 + y**2)
        c = 2.0 * np.arcsin(rho/2.0)
        lattr =np.arcsin(np.cos(c)*np.sin(lat0)  + y*np.sin(c)*np.cos(lat0)/rho ) * float(180.0) / np.pi
        lon = long0  + np.arctan2(x*np.sin(c), rho*np.cos(lat0)*np.cos(c) - y*np.sin(lat0)*np.sin(c))
        longtr = lon * 180.0 / np.pi

        return longll,longtr,latll,lattr

    def Cylindrical_Window(self,radius,lat0,long0):
        '''
        This method is used to determine the bottom-left
        and upper-right coordinates for a cylindrical projection
        centered at (lat0,long0 with a size radius). See
        Wikipedia
        '''
        # Radian conversion
        radi = radius*2*np.pi/(2*1734.4*np.pi)
        lamb0 = long0*np.pi/180.0
        phi0 = lat0*np.pi/180.0

        #Long/lat min (see wikipedia)
        longll = -radi/np.cos(phi0)+lamb0
        latll = np.arcsin((-radi+np.sin(phi0)/np.cos(phi0))*np.cos(phi0))
        if np.isnan(latll):
            latll = -90*np.pi/180.0

        #Long/lat max (see wikipedia)
        longtr = radi/np.cos(phi0)+lamb0
        lattr = np.arcsin((radi+np.tan(phi0))*np.cos(phi0))

        return longll*180/np.pi,longtr*180/np.pi,latll*180/np.pi,lattr*180/np.pi

    def _Add_Scale(self,m,ax1):
        ''' Add scale to the map instance '''
        
        lol,loM,lam,laM = self.Lambert_Window(0.6*self.Taille_Window,self.Lat,self.Long)
        m.drawmapscale(loM,lam, self.Long,self.Lat,10,
                       barstyle='fancy', units='km',
                       fontsize=24, yoffset=None,
                       labelstyle='simple',
                       fontcolor='k',
                       fillcolor1='w',
                       fillcolor2='k', ax=ax1,
                       format='%d',
                       zorder=2)

    def Lola_Image(self,save,name = 'BaseLola.png'):
        '''
        Return the lola image corresponding to the window.
        A blue triangle is added as well as a scale for completnesss
        of the plot.

        This method is encouraged to be modified according to specific need.
        '''
        fig = plt.figure(figsize=(24,14))
        ax1 = fig.add_subplot(111)
        ax1.set_rasterization_zorder(3)

        lon_m,lon_M,lat_m,lat_M = self.Lambert_Window(self.Taille_Window,self.Lat,self.Long)
        m = Basemap(llcrnrlon =lon_m, llcrnrlat=lat_m, urcrnrlon=lon_M, urcrnrlat=lat_M,
                    resolution='i',projection='laea',rsphere = 1734400, lat_0 = self.Lat,lon_0 = self.Long)

        lonm,lonM,latm,latM = self.Cylindrical_Window(self.Taille_Window,self.Lat,self.Long)

        Xl,Yl,Zl = LolaMap(lonm,lonM,latm,latM,self.ppdlola).Image()
        Xl,Yl = m(Xl,Yl)

        m.pcolormesh(Xl,Yl,Zl,cmap = 'gist_earth' , alpha = .5, ax  = ax1,zorder = 1)
        m.contour(Xl,Yl,Zl,20, colors = 'black', alpha = 1.0 , zorder=2)

        xc,yc = m(self.Long,self.Lat)
        ax1.scatter(xc,yc,s=200,marker ='v',zorder =2)

        self._Add_Scale(m,ax1)
        ax1.set_title('Crater %s, %d km in diameter'%(self.Name,self.Diameter),size = 42)

        path = os.path.join(self.racine,'Data','Image',name)
        if save == True:
            fig.savefig(path,rasterized=True, dpi=200,bbox_inches='tight',pad_inches=0.1)

    def Wac_Image(self,save,name = 'BaseWac.png'):
        '''
        Return the Wac image corresponding to the window.
        A blue triangle is added as well as a scale for completnesss
        of the plot.

        This method is encouraged to be modified according to specific need.
        '''
        
        fig = plt.figure(figsize=(24,14))
        ax1 = fig.add_subplot(111)
        ax1.set_rasterization_zorder(3)

        lon_m,lon_M,lat_m,lat_M = self.Lambert_Window(self.Taille_Window,self.Lat,self.Long)
        m = Basemap(llcrnrlon =lon_m, llcrnrlat=lat_m, urcrnrlon=lon_M, urcrnrlat=lat_M,
                    resolution='i',projection='laea',rsphere = 1734400, lat_0 = self.Lat,lon_0 = self.Long)

        lonm,lonM,latm,latM = self.Cylindrical_Window(self.Taille_Window,self.Lat,self.Long)

        Xw,Yw,Zw = WacMap(lonm,lonM,latm,latM,self.ppdwac).Image()
        Xw,Yw = m(Xw,Yw)
        m.pcolormesh(Xw,Yw,Zw,cmap = cm.gray ,ax  = ax1,zorder = 1)

        xc,yc = m(self.Long,self.Lat)
        ax1.scatter(xc,yc,s=200,marker ='v',zorder =2)

        self._Add_Scale(m,ax1)
        ax1.set_title('Crater %s, %d km in diameter'%(self.Name,self.Diameter),size = 42)

        path = os.path.join(self.racine,'Data','Image',name)
        if save == True:
            fig.savefig(path,rasterized=True, dpi=200,bbox_inches='tight',pad_inches=0.1)

    def Overlay(self,save,name = 'BaseOverlay.png'):

        '''
        Return an ovelay of Lola image over the Wac image
        corresponding to the window.
        A blue triangle is added as well as a scale for completnesss
        of the plot.

        This method is encouraged to be modified according to specific need.
        '''
        
        fig = plt.figure(figsize=(10,8))
        ax1 = fig.add_subplot(111)
        ax1.set_rasterization_zorder(3)

        lon_m,lon_M,lat_m,lat_M = self.Lambert_Window(self.Taille_Window,self.Lat,self.Long)
        m = Basemap(llcrnrlon =lon_m, llcrnrlat=lat_m, urcrnrlon=lon_M, urcrnrlat=lat_M,
                    resolution='i',projection='laea',rsphere = 1734400, lat_0 = self.Lat,lon_0 = self.Long)

        lonm,lonM,latm,latM = self.Cylindrical_Window(self.Taille_Window,self.Lat,self.Long)

        Xw,Yw,Zw = WacMap(lonm,lonM,latm,latM,self.ppdwac).Image()
        Xw,Yw = m(Xw,Yw)
        m.pcolormesh(Xw,Yw,Zw,cmap = cm.gray ,ax  = ax1,zorder = 1)

        Xl,Yl,Zl = LolaMap(lonm,lonM,latm,latM,self.ppdlola).Image()
        Xl,Yl = m(Xl,Yl)
        m.contourf(Xl,Yl,Zl,100,cmap='gist_earth', alpha = 0.4 , zorder=2 , antialiased=True)

        xc,yc = m(self.Long,self.Lat)
        ax1.scatter(xc,yc,s=200,marker ='v',zorder =2)

        self._Add_Scale(m,ax1)
        ax1.set_title('Crater %s, %d km in diameter'%(self.Name,self.Diameter),size = 42)

        path = os.path.join(self.racine,'Image',name)
        if save == True:
            fig.savefig(path,rasterized=True, dpi=200,bbox_inches='tight',pad_inches=0.1)

    def _Deg(self,radius):
        return radius*360/(2*np.pi*1734.4)
