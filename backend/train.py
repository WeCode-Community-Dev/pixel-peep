import cv2
import glob



def train_images(folder_dir):
    des_list={}
    sift=cv2.SIFT_create()
    for train_img_path in glob.iglob(f'{folder_dir}/*'):
        image=cv2.imread(train_img_path)
        gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

        kp=sift.detect(gray,None)
        kp,des_train=sift.compute(gray,kp)
        des_list[train_img_path]=des_train
        
    return des_list






      


        


        










#This is to show the image in a separate window.
# cv2.imshow("gray image",gray)
# cv2.waitKey(0)
# cv2.destroyAllWindows()