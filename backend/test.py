import train
import cv2
import glob
import os



def test_images(folder_dir,des_from_train):
    match_list=[]
    sift=cv2.SIFT_create()
    bf=cv2.BFMatcher()
    for test_img_path in glob.iglob(f"{folder_dir}/*"):
        image=cv2.imread(test_img_path)
        gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        kp=sift.detect(gray,None)
        kp,des_test=sift.compute(gray,kp)
    
        for train_img_path,des_train in des_from_train.items():
            matches=bf.knnMatch(des_train,des_test,k=2)
            good=[]
            for m,n in matches:
                if m.distance<0.75*n.distance:
                    good.append(m) 
 
            # print(good)
            if(len(good)>=30):
                match_list.append(f"{os.path.basename(train_img_path)} matches with {os.path.basename(test_img_path)}")
            else:
                match_list.append(f"{os.path.basename(train_img_path)} doesn't match with {os.path.basename(test_img_path)}")


    
    return match_list  