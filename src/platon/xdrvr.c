/*************************************************************************
* subroutine xwin_  : xdrvr - X window Driver for GGIP - support         *
*                                                                        *
* This is a simple Fortran callable interface routine to Xlib/Xwindow    *
* that implements a few commonly used graphics primitives                *
*                                                                        *
* (C) 1992-2016 - A.L. Spek, Vakgroep Kristal- en Structuurchemie,       *
*                 Bijvoet Centre for Biomolecular Research,              *
*                 Utrecht University, The Netherlands                    *
*                                                                        *
*                          ====================                          *
*                                                                        *
* *ind == -1 : check for X11-graphics capability                         *
* *ind ==  0 : close the window	                                         *
* *ind ==  1 : open Xwindow(*x, *y , *z = menu-border) 	                 *
*              on input:  *x & *y --> *x:*y ratio = fraction display     *
*              *buf --> window name                                      *
*              on output: *x & *y --> pixel resolution x, y              *
* *ind ==  2 : draw to *x, *y		                                 *
* *ind ==  3 : move to *x, *y 			                         *
* *ind ==  5 : eventloop (mouse/keyboard)                                *
* *ind ==  6 : clear screen	                                         *
* *ind ==  7 : xflush                                                    *
* *ind ==  8 : ResetInputFocus                                           *
* *ind ==  9 : Check for interrupt                                       *
* *ind == 10 : Set LineWidth                                             *
* *ind == 11 : Get Display Resolution                                    *
* *ind == 12 : Reverse B&W                                               *
* *ind == 13 : Get X-WINDOW Open/Closed Status                           *
*                                                                        *
* *ind == 99 : select pen-colour                                         *
* *ind >  99 : Modify Menu_Option String  Contents (Box on Right)        *   
*                                                                        *
* *ind > 199 : String going into Box below Drawing Canvas                *
*************************************************************************/

#include <X11/Xlib.h>
#include <X11/Xutil.h>
#include <X11/Xos.h>
#include <X11/keysym.h>
#include <string.h>
#include <stdio.h>
#include <math.h>
#include <time.h>
#include <sys/times.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/time.h>
#include <sys/resource.h>
#include <stdlib.h>

#define icon_bitmap_width 60
#define icon_bitmap_height 40
static char icon_bitmap_bits[] = {
   0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
   0xff, 0xff, 0xff, 0xff, 0x3f, 0x8e, 0x11, 0xfe, 0xff, 0xff, 0xff, 0xff,
   0xdf, 0x75, 0xdb, 0xfd, 0xff, 0xff, 0xff, 0xff, 0xdf, 0xf7, 0xdb, 0xfd,
   0xf7, 0xdf, 0xff, 0xff, 0xdf, 0x34, 0x1b, 0xfe, 0xeb, 0xdf, 0xff, 0xff,
   0xdf, 0x75, 0xdb, 0xff, 0xdd, 0xdf, 0xff, 0xff, 0xdf, 0x75, 0xdb, 0xff,
   0xbe, 0xdf, 0xff, 0xff, 0x3f, 0x8e, 0xd1, 0xff, 0xbe, 0xdf, 0xff, 0xff,
   0xff, 0xff, 0xff, 0xff, 0xbe, 0xdf, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
   0x80, 0xdf, 0xff, 0xff, 0x03, 0x00, 0x00, 0xf0, 0xbe, 0xdf, 0xff, 0xff,
   0xfb, 0xff, 0xff, 0xf7, 0xbe, 0xdf, 0xff, 0xff, 0xfb, 0xff, 0xff, 0xf7,
   0xbe, 0xdc, 0xcf, 0xff, 0xfb, 0xff, 0xff, 0xf7, 0xbe, 0x1c, 0xc8, 0xff,
   0x0b, 0xfe, 0xff, 0xf4, 0xff, 0xff, 0xff, 0xff, 0x1b, 0xfc, 0x7f, 0xf6,
   0xff, 0xff, 0xff, 0xff, 0x3b, 0xf8, 0x3f, 0xf7, 0xff, 0xff, 0xff, 0xff,
   0x7b, 0xf0, 0x9f, 0xf7, 0xff, 0xff, 0xff, 0xff, 0xfb, 0xe0, 0xcf, 0xf7,
   0xc1, 0xff, 0xbf, 0xff, 0xfb, 0xc1, 0xe7, 0xf7, 0xbe, 0xff, 0xbf, 0xff,
   0xfb, 0x83, 0xf3, 0xf7, 0xfe, 0xff, 0xbf, 0xff, 0xfb, 0x07, 0xf9, 0xf7,
   0xfe, 0xff, 0xbf, 0xff, 0xfb, 0x8f, 0xfc, 0xf7, 0xc1, 0xe0, 0xb0, 0xfb,
   0xfb, 0x4f, 0xfc, 0xf7, 0xbf, 0x5e, 0xaf, 0xfd, 0xfb, 0x27, 0xf8, 0xf7,
   0xbf, 0x5e, 0xaf, 0xfe, 0xfb, 0x73, 0xf0, 0xf7, 0xbf, 0x5e, 0x20, 0xff,
   0xfb, 0xf9, 0xe0, 0xf7, 0xbf, 0x5e, 0xbf, 0xfe, 0xfb, 0xfc, 0xc1, 0xf7,
   0xbe, 0x5e, 0xaf, 0xfd, 0x7b, 0xfe, 0x83, 0xf7, 0xc1, 0xe0, 0xb0, 0xfb,
   0x3b, 0xff, 0x07, 0xf7, 0xff, 0xfe, 0xff, 0xff, 0x9b, 0xff, 0x0f, 0xf6,
   0xff, 0xfe, 0xff, 0xff, 0xcb, 0xff, 0x1f, 0xf4, 0xff, 0xfe, 0xff, 0xff,
   0xfb, 0xff, 0xff, 0xf7, 0xff, 0xfe, 0xff, 0xff, 0xfb, 0xff, 0xff, 0xf7,
   0xff, 0xff, 0xff, 0xff, 0xfb, 0xff, 0xff, 0xf7, 0xff, 0xff, 0xff, 0xff,
   0x03, 0x00, 0x00, 0xf0, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
   0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff,
   0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff, 0xff};
#define MAX_COLORS    16
#define MOUSE_OPTIONS 25
#define MENU_CHAR     11 
#define EV_MASK \
   (StructureNotifyMask | ButtonPressMask | ExposureMask | KeyPressMask )

static int            def_colors(void);
static int            version   = 30815;
static int            lastevent = -1;
static int            myfont    = 1;
static int            wopen     = 0;
XEvent                report;
static Colormap       cmap;
static Display        *theDisplay;
static int            theScreen;
static int            colors[MAX_COLORS];
static char           buffer[100];
static int            count,ibaw, icol;
static XComposeStatus compose;
static KeySym         keysym;
static int            MapColor(XColor * color);
XFontStruct           *initFont(GC theGC, char fontName[]);
static XFontStruct    *fontStruct;
Bool                  predproc(Display *display, XEvent *event, char *arg);
/***************************************************************************/
int xwin_(int *x, int *y, int * z, int *ind, char *buf) {
  static Window        theWindow;		/* X stuff - some	*/
  static Window        theFocus;
  static GC            theGC;			/* static to save value */
  XSizeHints           size_hints;		/* between calls from   */
  XIconSize            *size_list;		/* xwin.c		*/
  XEvent               theEvent;
  XGCValues            values;
  XSetWindowAttributes theWindowAttributes;
  XWindowAttributes    theWindowAtt;
  Pixmap               icon_pixmap;
  Region               region;
  static int           window_mode = 0;
  static int           xlx, yly, dx, dy;           /* more statics for     */
  static int           start_xlx, start_yly;       /* line drawing         */
  static int           width, height, menu, msinp; /* window size          */
  static int           theDepth;
  static unsigned int  theWidth, theHeight, dwidth,dheight;  /* display size */
  static unsigned long theBlackPixel;
  static unsigned long theWhitePixel;
  static int           revert_to;
  static char          *menu_opt[MOUSE_OPTIONS + 1] ;
  static int           m_sopt[MOUSE_OPTIONS + 1]; 
  static int           n_sopt[MOUSE_OPTIONS + 1]; 
  static int           om_sopt[MOUSE_OPTIONS + 1]; 
  static int           on_sopt[MOUSE_OPTIONS + 1]; 
  static int           cm_opt[MOUSE_OPTIONS + 1];
  unsigned int         wx = 0, wy = 0;              /* window location     */
  unsigned int         border_width = 0;            /* no border 	   */
  unsigned int         icon_width, icon_height;       
  unsigned long        foreground_pixel;
  unsigned long        theWindowMask;
  static float         menu_step, menu_y, xstep, ystep, ibx, iby;
  int                  menu_x;
  int                  iex;
  char                 window_name[25];
  char                 *icon_name    = "X-WIN";
  char                 *display_name = NULL;
  int                  color_select;
  int                  window_size   = 0;
  int                  mopt;
  int                  i, j;
  static int           first         = 1;
  if (*ind == -1) {              /* check for X11        */
    theDisplay = XOpenDisplay(display_name);
    if(theDisplay != NULL) *z = 1; else *z =  0;
    if (*z == 1) XCloseDisplay(theDisplay);
  } else if (*ind == 0) { 		/* close the window	*/
      if (wopen == 1) XFlush(theDisplay);
      XFreeGC(theDisplay, theGC);
      XCloseDisplay(theDisplay);
      wopen = 0;
      return(0);
  } else if (*ind == 1) {         /* open Xwindow		*/
      if (*z !=  version) {
        printf("\nWrong version of xdrvr.c(%d) linked (%d required)\n", 
         version, *z);
        return(0);
      }
      strcpy(window_name, buf);
      if ((theDisplay = XOpenDisplay(display_name)) == NULL) {
        printf( "\n\n:: X-GGIP: cannot connect to X server %s\n\n",
                 XDisplayName(display_name));
       *x = -1;
       return(0);
      } else {  
        theWidth  = DisplayWidth(theDisplay, theScreen);
        theHeight = DisplayHeight(theDisplay, theScreen);
        theDepth  = DefaultDepth(theDisplay, theScreen);
        printf("\n:: DisplayWidth  = %d, DisplayHeight = %d, \
          DisplayDepth  = %d\n\n", theWidth, theHeight, theDepth);
        wopen = 1;
      }
      theScreen      = DefaultScreen(theDisplay);
      theBlackPixel  = BlackPixel(theDisplay, theScreen);
      theWhitePixel  = WhitePixel(theDisplay, theScreen);
      dheight        = *x * theHeight / *y;
      dwidth         = 4  * dheight / 3;
      width          = dwidth * 9/ 10;
      height         = dheight * 9 / 10;
      msinp          = dheight - height;
      *x             = width - 1;
      *y             = height - 1;
      menu           = dwidth - width;
      *z             = menu;
      window_mode    = 1;
      if (dwidth < 1000) myfont = 2;
      if (ibaw == 0) { 
        theWindowAttributes.border_pixel      = theWhitePixel;
        theWindowAttributes.background_pixel  = theBlackPixel;
      } else {
        theWindowAttributes.border_pixel      = theBlackPixel;
        theWindowAttributes.background_pixel  = theWhitePixel;
      }
      theWindowAttributes.override_redirect = False;
      theWindowMask = CWBackPixel | CWBorderPixel | CWOverrideRedirect ; 
      XGetInputFocus(theDisplay, &theFocus, &revert_to);
      theWindow = XCreateWindow(theDisplay,
                                RootWindow(theDisplay, theScreen),
                                wx, wy, dwidth, dheight,
                                border_width, theDepth,
                                InputOutput, CopyFromParent,
                                theWindowMask,
                                &theWindowAttributes);
      icon_pixmap = XCreateBitmapFromData(theDisplay,
                                          theWindow,
                                          icon_bitmap_bits,
                                          icon_bitmap_width,
                                          icon_bitmap_height);
      size_hints.flags 	  = PPosition | PSize | PMinSize;
      size_hints.x 	  = wx;
      size_hints.y 	  = wy;
      size_hints.width 	  = dwidth;
      size_hints.height 	  = dheight;
      size_hints.min_width  = dwidth;
      size_hints.min_height = dheight;
      XSetStandardProperties(theDisplay,
                             theWindow,
                             window_name,
                             icon_name, 
                             icon_pixmap,
                             0, 0,
                             &size_hints);
/**** Event - section ****/
      region = XCreateRegion();
      if (ibaw == 0) {
        values.foreground = WhitePixel(theDisplay, theScreen);
        values.background = BlackPixel(theDisplay, theScreen);
      } else {
        values.foreground = BlackPixel(theDisplay, theScreen);
        values.background = WhitePixel(theDisplay, theScreen);
      }
      theGC = XCreateGC(theDisplay,
                     theWindow,
                     (GCForeground|GCBackground),
                     &values);
      def_colors();			/* define colors	*/
      XMapWindow(theDisplay, theWindow);
/* make shure that window is ready to receive graphics */
      XSelectInput (theDisplay, theWindow, ExposureMask);
      XMapRaised (theDisplay, theWindow);
      XFlush(theDisplay);
      do {
        XNextEvent (theDisplay, &report);
      } while (report.type != Expose);
      XSelectInput (theDisplay, theWindow, NoEventMask);
      fontStruct = initFont(theGC, "9X15");
      XFlush(theDisplay);
      for (i = 0; i < MOUSE_OPTIONS + 1; i++) om_sopt[i] = 1;
      for (i = 0; i < MOUSE_OPTIONS + 1; i++) on_sopt[i] = 0;
      XSetForeground(theDisplay, theGC, colors[2]);
      return(0);
  } else if (*ind == 2) {			/* draw to x,y		*/
      xlx = *x;
      yly = (height - *y - 1);
      dx  = start_xlx - xlx;
      dy  = start_yly - yly;
      if (dx == 0 && dy == 0) {
        XDrawPoint(theDisplay, theWindow, theGC, xlx, yly);
      } else {
          XDrawLine(theDisplay, theWindow, theGC, xlx, yly,
                    start_xlx, start_yly);
      }
      start_xlx = xlx;
      start_yly = yly;
      return(0);
  } else if (*ind == 3) {	                   /* move to x, y */		
      start_xlx = *x;
      start_yly = (height - *y - 1);
      return(0);
  } else if (*ind == 5) {                 /* event loop           */
/* EVENT TYPES -1 : NILL
                0 : EXPOSE_EVENT
                1 : MOUSE_CLICK ON CANVAS    RETURN X,Y       1   |   2
                2 : MOUSE_CLICK ON MENU_BAR  RETURN X,Y       ----|----
                3 : MOUSE_CLICK ON MENU_BAR  RETURN X,Y       3   |   4
                4 : MOUSE_CLICK ON MENU_BAR  RETURN X,Y
*/
      if (window_mode == 1) {
/* show menu options */
        XSetForeground(theDisplay, theGC, colors[1 - ibaw]);
        menu_step = (float)height / (float)(MOUSE_OPTIONS + 1);
        ystep     = menu_step / 6;
        menu_x    = width + 2 ;
        menu_y    = menu_step / 2;
        ibx = width;
        iex = dwidth;
        iby = menu_step;
        XDrawLine(theDisplay, theWindow, theGC, (int)ibx, 0, (int)ibx, dheight);
        XDrawLine(theDisplay, theWindow, theGC, 0, height, dwidth, height);
        for (i = 0; i < MOUSE_OPTIONS + 1; i++) {
          XDrawLine(theDisplay, theWindow, theGC, iex, (int)iby,
                  (int)ibx, (int)iby);
          xstep   = (float)menu / (float)om_sopt[i];
          if (ibaw == 0) {
            XSetForeground(theDisplay, theGC, theBlackPixel);
          } else {
            XSetForeground(theDisplay, theGC, theWhitePixel);
          }
          for (j = 1; j < om_sopt[i]; j++) {
            XDrawLine(theDisplay, theWindow, theGC, 
                   (int)(ibx + j * xstep),
                   (int)(iby - ystep),
                   (int)(ibx + j * xstep),
                   (int)iby);
          }
          if (on_sopt[i] > 0) { 
            j = on_sopt[i];
            XDrawLine(theDisplay, theWindow, theGC, 
                   (int)(ibx + (j - 1) * xstep),
                   (int)(iby - ystep),
                   (int)(ibx + j * xstep),
                   (int)(iby - ystep));
          }
          XSetForeground(theDisplay, theGC, colors[1 -ibaw]);
          if (m_sopt[i] > 0) {
            xstep   = (float)menu / (float)m_sopt[i];
            for (j = 1; j < m_sopt[i]; j++) {
              om_sopt[i] = m_sopt[i];
              XDrawLine(theDisplay, theWindow, theGC, 
                     (int)(ibx + j * xstep),
                     (int)(iby - ystep),
                     (int)(ibx + j * xstep),
                     (int)iby);
            } 
          }
          on_sopt[i] = n_sopt[i];
          if (n_sopt[i] > 0) { 
            j = n_sopt[i];
            XDrawLine(theDisplay, theWindow, theGC, 
                   (int)(ibx + (j - 1) * xstep),
                   (int)(iby - ystep),
                   (int)(ibx + j * xstep),
                   (int)(iby - ystep));
          }
          icol = cm_opt[i];
          if (ibaw == 1) {
            if (icol == 1)
              icol = 0;
            else if (icol == 0)
              icol = 1;
          }
          XSetForeground(theDisplay, theGC, colors[icol]);
          XDrawImageString(theDisplay, theWindow, theGC, menu_x,
                         (int)menu_y, menu_opt[i], MENU_CHAR);
          XSetForeground(theDisplay, theGC, colors[1 - ibaw]);
          menu_y += menu_step;
          iby    += menu_step;
        }
        XSetForeground(theDisplay, theGC, colors[3]);
        XDrawImageString(theDisplay, theWindow, theGC, 
                         width + msinp * 5 / 77,
                       dheight - msinp * 30 / 77, "MenuActive", 10);
        XSetForeground(theDisplay, theGC, colors[1 -ibaw]);
        XDrawImageString(theDisplay, theWindow, theGC, 
                         width + msinp * 35 / 77,
                         dheight - msinp * 60 / 77, "Exit", 4);
        XDrawImageString(theDisplay, theWindow, theGC, msinp * 5 / 77, 
          dheight - msinp * 55 / 77, 
"INSTRUCTION INPUT via KEYBOARD or LEFT-MOUSE-CLICKS (HELP with RIGHT CLICKS)",
 76);
        XDrawImageString(theDisplay, theWindow, theGC, msinp * 5 / 77,
                       dheight - msinp * 10 / 77, ">>", 2);
        XSelectInput(theDisplay, theWindow, EV_MASK);
        XFlush(theDisplay);
    l1: XGetInputFocus(theDisplay, &theFocus, &revert_to);
        XNextEvent(theDisplay, &theEvent);
        switch (theEvent.type) {
          case Expose:
            if (theEvent.xexpose.count != 0) goto l1;
            if (lastevent <= 0) goto l1;
            *x   = 0;
            *y   = 0;
            *ind = 0;
            lastevent = 0;
// temperary
            goto l1;
//          break;
          case KeyPress:
            count=XLookupString(&(theEvent.xkey),buf, 80,&keysym,&compose);
            if (keysym == XK_Shift_L) goto l1; 
            *ind = 5; 
            break;
          case ButtonPress:
/* receive *x   - x-position button-click
           *y   - y-position button-click
           *z   - button-number button-click
           *ind - click field (1,2,3,4)
*/
            *x = theEvent.xbutton.x;
            *y = theEvent.xbutton.y;
            *z = theEvent.xbutton.button;
            if (*x <= width && *y <= height) {
              lastevent = 1;
	      *ind      = 1; 
            } else if (*x < width && *y > height) {
                lastevent = 3;
                *ind      = 3;
            } else if (*x > width && *y > height) {
                lastevent = 4;
                *ind      = 4;
            } else if (*x > width && *y < height) {
                *y =  *y / menu_step;
                *x = 1 + (*x - width) * m_sopt[*y] / (dwidth - width);
                lastevent = 2;
                *ind      = 2;
                if (*y == 2 || *y == MOUSE_OPTIONS) {
                  XSetForeground(theDisplay, theGC, colors[0 + ibaw]);
                  menu_x    = width + 2 ;
                  menu_y    = menu_step / 2;
                  ibx = width;
                  iex = dwidth;
                  iby = menu_step;
                  for (i = 0; i < (MOUSE_OPTIONS + 1); i++) {
                    XDrawLine(theDisplay, theWindow, theGC, iex, (int)iby,
                         (int)ibx, (int)iby);
                    xstep   = (float)menu / (float)m_sopt[i];
                    for (j = 1; j < m_sopt[i]; j++) {
                      XDrawLine(theDisplay, theWindow, theGC, 
                        (int)(ibx + j * xstep), (int)(iby - ystep),
                        (int)(ibx + j * xstep), (int)iby);
                    }
                    XDrawImageString(theDisplay, theWindow, theGC, menu_x,
                      (int)menu_y, menu_opt[i], MENU_CHAR);
                      menu_y += menu_step;
                    iby    += menu_step;
                  }

                }
            }
       	    break;
          default: goto l1;
        }
        XSetForeground(theDisplay, theGC, colors[2]);
        XDrawImageString(theDisplay, theWindow, theGC, 
                         width + msinp * 5 / 77,
                         dheight - msinp * 30 / 77, "  WORKING ", 10);
        XSetForeground(theDisplay, theGC, colors[0 + ibaw]);
        XDrawImageString(theDisplay, theWindow, theGC, 
                         width + msinp * 35 / 77,
                         dheight - msinp * 60 / 77, "Exit", 4);
        for (i = 0; i < 4 ; i++) {
          XDrawImageString(theDisplay, theWindow, theGC, 
           msinp * 5 / 77,
           dheight - msinp * (10 + i * 15) / 77, 
"                                                                 \
              ", 79);
        }
        XFlush(theDisplay);
        XSetForeground(theDisplay, theGC, colors[1 - ibaw]);
      } else {
        *x = 0; *y = 0; *z = 0; *ind = -1;
      }
      return(0);
  } else if (*ind == 6) {			/* clear screen		*/
/*

      XGetWindowAttributes(theDisplay, theWindow, &theWindowAtt);
      if ((theWindowAtt.width  != width ) ||
          (theWindowAtt.height != height) ) {
        width  = theWindowAtt.width;
        height = theWindowAtt.height;
      }                      
*/
      XClearArea(theDisplay, theWindow, 0,0,0,0,0);
/*
      XFillRectangle(theDisplay, theWindow, theGC,
                   width + 1, 0, menu, height);
*/
      XFlush(theDisplay);
      return(0);
  } else if (*ind == 7) {                  /* flush buffer */
      if (wopen == 1) XFlush(theDisplay);
      return(0);
  } else if (*ind == 8) {
      XSetInputFocus(theDisplay, theFocus, revert_to, CurrentTime);
      return(0);
  } else if (*ind == 9) {
      if (window_mode == 1) {
        XSelectInput(theDisplay, theWindow, EV_MASK);
        if (XCheckIfEvent (theDisplay, &theEvent, predproc, "1") == True) {
          *ind = 0;
          *x = theEvent.xbutton.x;
          *y = theEvent.xbutton.y;
          if (*x <= width && *y <= height) {
            *ind = 1; 
          } else if (*x > width && *y < height) {
              *ind = 2;
          } else if (*x < width && *y > height) {
              *ind = 3;
          } else if (*x > width && *y > height) {
              *ind = 4;
          }
        } else {
            *x = 0; *y = 0 ; *z = 0 ; *ind = 0;  
        }
      } else {
        *x = 0; *y = 0; *z = 0; *ind = -1;
      }
      return(0);
  } else if (*ind == 10) {
      if (dheight >= 750)
      XSetLineAttributes(theDisplay, theGC, *x, LineSolid,CapRound,JoinRound);
      return(0);
  } else if (*ind == 11) {
     *x = DisplayWidth(theDisplay,  theScreen);
     *y = DisplayHeight(theDisplay, theScreen);
     *z = DefaultDepth(theDisplay,  theScreen);
     return(0);
  } else if (*ind == 12) {
      ibaw = *z;
      return (0);
  } else if (*ind == 13) {
      *z = wopen;
      return (0);
  } else if (*ind == 99) {		/* change pen color	*/
      color_select     = *x; 
      if (color_select == 0) {
        if (ibaw == 0) {
          foreground_pixel = theBlackPixel;
        } else {
          foreground_pixel = theWhitePixel;
        }
      } else if (color_select == 1)
      if (ibaw == 0) {
        foreground_pixel = theWhitePixel;
      }
      else {
        foreground_pixel = theBlackPixel;
      }
    else
      foreground_pixel = colors[color_select];
    XSetForeground(theDisplay, theGC, foreground_pixel);
    return(0);
  } else if (*ind > 99 && *ind < 101 + MOUSE_OPTIONS) {
      if (first == 1) {
        for (j = 0; j < MOUSE_OPTIONS + 1; ++j) {
          menu_opt[j] = (char *) calloc(MENU_CHAR, 1); 
          m_sopt[j] = 1;
          cm_opt[j] = 1;
        }
        first = 0;
      }
      strcpy (menu_opt[*ind - 100], buf);
      m_sopt[*ind - 100] = *z % 100;
      n_sopt[*ind - 100] = *z / 100;
      cm_opt[*ind - 100] = *y;
      return(0);
  } else if (*ind >  199) {
      if (window_mode == 1) {
        XSetForeground(theDisplay, theGC, colors[*y]);
        XDrawImageString(theDisplay, theWindow, theGC, msinp * 25 / 77, 
        dheight - msinp * (10  - (200 - *ind) * 15) / 77, buf, *x - 1);
        XSetForeground(theDisplay, theGC, colors[1 - ibaw]);
      }
  } else {	                                              /* big trouble*/ 
    printf("Error: Unknown function call in xwin_ : IND= %d\n", *ind);
  }
  return(0);
}                                                                /* End win */
/****************************************************************************/
int def_colors() {
  int depth;
  Visual *visual;
  XColor exact_def;
  int ncolors = MAX_COLORS;
  int i;

  static char *name[] =				/* colors here	*/
	{"Black", "White", "Red", "Green", "Blue", "Yellow", 
         "Orange", "Violet", "Brown", "Pink", "Magenta", "Cyan",
         "Gold", "NavyBlue", "Grey", "Lime Green"}; 

  depth  = DisplayPlanes(theDisplay, theScreen);
  cmap   = DefaultColormap(theDisplay, theScreen);
  
  if ( depth == 1 ) 		/* mono screen	*/
  {
    for ( i = 0; i < MAX_COLORS; i++ )
    {
       colors[i] = WhitePixel(theDisplay, theScreen);
    }
  }

  else
  {
    for (i = 0; i < MAX_COLORS; i++ )
    {

      if ( !XParseColor(theDisplay, cmap, name[i], &exact_def) )
      {
        printf( "Xwin: color %s not in database\n", name[i]);
        exit(-1);
      }

      colors[i] = MapColor(&exact_def);
    }

  }
  return(0);
}     

static int MapColor(XColor * color)
{
  static int err=0;
  if (!XAllocColor (theDisplay, cmap, color)) {
    static XColor defs_in_out[256];
    int already=0;
    int imin=-1;
    float dmin=1.0e10;
    int icol;
    /* First time around ask X for all available colors */
    if (!already) {
      for (icol=0;icol<256;icol++) defs_in_out[icol].pixel=icol;
      XQueryColors(theDisplay, cmap, defs_in_out, 256);
      already=1;
    }
    /* Locate closest color, and allocate it. */
    for (icol=0;icol<256;icol++) {
      float d,dr,dg,db;
      dr=(defs_in_out[icol].red - color->red);
      dg=(defs_in_out[icol].green - color->green);
      db=(defs_in_out[icol].blue - color->blue);
      d=dr*dr+dg*dg+db*db;
      if (d<dmin) {
        imin=icol;
        dmin=d;
      }
    }
    if (icol>0) {
      if (!XAllocColor (theDisplay, cmap, &defs_in_out[imin])) {
        fprintf(stderr,"Could not even find suitable replacement color!\n");
      } else {
        color->pixel=defs_in_out[imin].pixel;
      }
    }
    if (!err) {
      fprintf (stderr,
       "W: Failed to allocate all necessary colors exactly\n\n");
      fflush (stderr);
      err = 1;
    }
  }
  return color->pixel;
}


XFontStruct *initFont(GC theGC, char fontName[])
{
 XFontStruct *fontStruct;
 if (myfont == 1)
 {fontName = "9x15";}
 else
 {fontName = "6x12";}
 fontStruct = XLoadQueryFont(theDisplay, fontName);
 if(fontStruct !=0)
   {
	XSetFont(theDisplay,theGC,fontStruct->fid);
   }
 return(fontStruct);
}

Bool predproc(display, event, arg)
Display *display;
XEvent  *event; 
char    *arg;
{
  switch (event->type)
      {
        case KeyPress:
          return(True);
      	case ButtonPress:
          return(True);
        case Expose:
          return(False);
        default:
          return(False);
      }
}
float eltime_(et)
float et[2];
{
  clock_t clicks;
  clicks = clock();
  return ( (float) clicks / CLOCKS_PER_SEC );
}

int chandir_(char *path,int ftnlen)
{
	char localpath[255];
	int i;

	for(i=0;i<ftnlen;i++) localpath[i]=path[i];
	localpath[ftnlen]='\0';
	chdir(localpath);
	return(0);
}

int callsystem_(char *s, int ftnlen)
{
  int status;
  int i, j = 0;
  char *t = malloc(ftnlen + 1);
  for (i=0;i<ftnlen;i++)
  {
    t[i]=s[i];
    if (t[i]!=' ') j=i;
  }
  t[j+1]='\0';
  status = system(t);
  return status;
}


