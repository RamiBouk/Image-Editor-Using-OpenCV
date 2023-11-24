import cv2
import numpy as np
import random
from data import MyImage


kernels={
    'SobelV':np.array([[1,0,-1],[2,0,-2],[1,0,-1]]),
    'SobelH':np.array([[1,2,1],[0,0,0],[-1,-2,-1]])
    }
class SingletonMeta(type):
    """
    The Singleton class can be implemented in different ways in Python. Some
    possible methods include: base class, decorator, metaclass. We will use the
    metaclass because it is best suited for this purpose.
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """
        Possible changes to the value of the `__init__` argument do not affect
        the returned instance.
        """
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class MyEditor(metaclass=SingletonMeta):
    def __init__(self)->None:
        # execute the init
        # set current brightness
        # set current contrast
        self.brightness = 0
        self.contrast = 1
        self.history = []
        self.currentIndex = 0

    def saveFile(self,file_name):
        print('___________________________________________')
        print(file_name)
        print(type(file_name))
        cv2.imwrite(file_name,self.getBuffer());

    def _isRGB(self):
        # check if the chape has a channel not just width and height
        if(len(self.buff.shape)>2):
            return True
        return False

    def _isGray(self):
        # check if the shape doesn't have a channel 
        # check that the image is not binary
        if(len(self.buff.shape)<3 and type(self.buff)!=np.typeOfBinaryImage):
            return True
        return False
    def _isBinary(self):
        # check that the image doesn't have a channel
        # check the type of the image
        if(len(self.buff.shape)<3 and type(self.buff)==np.typeOfBinaryImage):
            return True
        return False

    def openImage(self,path):
        # init the heistory_arr with the new image
        self.history.append(MyImage(path))
        if(len(self.history)!=1):
            self.currentIndex+=1
        self._newBuffer()
        self.save()


    def getBuffer(self):
        # provide the image in the buffer
        return self.buff


    def save(self):
        # clear everything after the current image
        # add the buffer to the end of the history_arr
        if(self.currentIndex+1<len(self.history)):
            self.history[self.currentIndex+1 :] =[]
        self.history.append(self.buff)
        self.currentIndex+=1

    def TestEdit(self,type):
        # an example of editor
        self.buff+=1

    def undo(self):
        # if buffer changed
        #   clear the buffer 
        # else
        #   check if you can go backwards (throw exception if you cant)
        #   move the currentIndex backwards by one
        #   reset the buffer to the image in the new index
        comparison = self.buff == self.history[self.currentIndex]
        equal_arrays = comparison.all()
        if(equal_arrays and self.currentIndex>0):
            self.currentIndex-=1
        self._newBuffer()


    def redo(self):
        # if buffer changed
        #   throw exception
        # else 
        #   check if you can go forwards (throw exception if you cant)
        #   move the currentIndex forward by one
        #  self.buff==self.history[self.currentIndex] and  reset the buffer to the image in the new index
        comparison = self.buff == self.history[self.currentIndex]
        equal_arrays = comparison.all()
        if(equal_arrays and self.currentIndex<len(self.history)-1):
            self.currentIndex+=1
            self._newBuffer()

    def _newBuffer(self):
        # copy the image in the history[currentInedex] in the buffer
        self.buff = self.history[self.currentIndex].copy()


    def changeContr(self, contrast):
        contrast = contrast/100
        if contrast > 0:
            self.contrast =  1+contrast+6*contrast**4
        else:
            self.contrast = 1 - (-contrast)**1.5
        self._resetContBright(self.brightness,self.contrast)

    def changeBright(self, brightness):
        self.brightness = brightness
        self._resetContBright(self.brightness,self.contrast)

    def _resetContBright(self, brightness, contrast):
        self._newBuffer()
        int_image = np.int16(self.buff)
        int_image = (int_image-128) * (contrast)+128+brightness
        int_image[int_image > 255] = 255
        int_image[int_image < 0] = 0
        self.buff[:,:] = np.uint8(int_image)[:, :]

    def contrastEq(self):
        img = self.buff[:, :]
        if(len(self.buff.shape)==3):
            ycrcb = cv2.cvtColor(img, cv2.COLOR_BGR2YCR_CB)
            channels = cv2.split(ycrcb)
            # cv2.equalizeHist(channels[0],channels[0])
            h = np.cumsum(cv2.calcHist([channels[0]], [0], None, [256], [0, 256]))
            mx = np.max(channels[0])
            n, m = np.shape(channels[0])
            for i in range(n):
                channels[0][i] = np.uint8(
                    np.round(h[channels[0][i]])*(mx/(n*m)))
            cv2.merge(channels, ycrcb)
            cv2.cvtColor(ycrcb, cv2.COLOR_YCR_CB2BGR, img)
            self.buff[:, :] = img[:, :]
        else:
            cv2.equalizeHist(self.buff,self.buff)

    def applyFilter(self, filterName,param=[]):
        if(filterName=='Sobel'):
            img = self.buff
            if(self._isRGB()):
                self.rgb2gray()
            gray = self.buff
            x = cv2.Sobel(gray, cv2.CV_64F , 1,0, ksize=3, scale=1)
            y = cv2.Sobel(gray, cv2.CV_64F, 0,1, ksize=3, scale=1)
            absx= cv2.convertScaleAbs(x)
            absy = cv2.convertScaleAbs(y)
            edge = cv2.addWeighted(absx, 0.5, absy, 0.5,0)
            self.buff=edge
        elif(filterName=='Laplacian'):
            img = self.buff
            if(self._isRGB()):
                self.rgb2gray()
            gray = self.buff
            edge =cv2.convertScaleAbs(cv2.Laplacian(gray,cv2.CV_64F))
            self.buff=edge
        elif(filterName=='LoG'):
            img = self.buff
            if(self._isRGB()):
                self.rgb2gray()
            gray = self.buff
            edge = cv2.GaussianBlur(img, (3, 3), 1)
            edge =cv2.convertScaleAbs(cv2.Laplacian(edge,cv2.CV_64F))
            self.buff=edge
        elif(filterName=='salt&pepper'):
            width,height=self.buff.shape[0:2]
            for i in range(1,int(width*height*int(param[0])/100)):
                if(self._isRGB()):
                    noise=[0,0,0]
                    noise[random.randint(0,2)]=255
                    self.buff[random.randint(1,width-1),
                              random.randint(1,height-1),
                              :]=noise
                else:
                    noise=0
                    noise=random.randint(0,1)*255
                    self.buff[random.randint(1,width-1),
                              random.randint(1,height-1)
                              ]=noise
        elif(filterName=='gaussian'):
            mean=0
            var =255
            if len(param)>=1:
                mean = float(param[0])
            if len(param)==2 :
                var = float(param[1])
            sigma = var**0.05
            if(self._isRGB()):
                row,col,ch= self.buff.shape
                gauss = np.random.normal(mean,sigma,(row,col,ch))
                gauss = gauss.reshape(row,col,ch)
            else:
                row,col= self.buff.shape
                gauss = np.random.normal(mean,sigma,(row,col))
                gauss = gauss.reshape(row,col)
            self.buff = cv2.convertScaleAbs(self.buff + gauss)
        elif(filterName=='gblur'):
            size=3
            if len(param)==1:
                size=int(param[0])
            self.buff = cv2.GaussianBlur(self.buff, (size, size), 1)
        elif(filterName=='mblur'):
            size=3
            if len(param)==1:
                size=int(param[0])
            self.buff = cv2.medianBlur(self.buff, size)
        elif(filterName=='ablur'):
            size=3
            if len(param)==1:
                size=int(param[0])
            self.buff = cv2.blur(self.buff, (size,size))




    ## Filters
    def rgb2gray(self):
        if(len(self.buff.shape)==3):
            self.buff = cv2.cvtColor(self.buff, cv2.COLOR_BGR2GRAY)

    def toBinary(self,param=[]):
        seuil=125
        if len(param)==1 :
            seuil=int(param[0])
        self.rgb2gray()
        (_, self.buff) = cv2.threshold(self.buff, seuil, 255, cv2.THRESH_BINARY )

    def _applykernel(self,kernel):
        return cv2.filter2D(self.buff,-1,kernel)


    def rotate(self):
        self.buff=cv2.rotate(self.buff,cv2.ROTATE_90_CLOCKWISE)

    def flipHorizontal(self):
        self.buff=cv2.flip(self.buff,1)

    def flipVerical(self):
        self.buff=cv2.flip(self.buff,0)

    def face_recongnize(self):
        face_cascade = cv2.CascadeClassifier('models/haarcascade_frontalface_default.xml')
        img = self.buff
        try:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        except Exception as e:
            pass
        faces = face_cascade.detectMultiScale(img, 1.1, 4)
        for (x, y, w, h) in faces:
            cv2.rectangle(self.buff, (x, y), (x+w, y+h), (255, 0, 0), 2)




if __name__ == "__main__":
    editor=MyEditor()
    editor.openImage("../")
