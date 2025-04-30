from fastapi import FastAPI,File,UploadFile
from fastapi.middleware.cors import CORSMiddleware
import cv2
import numpy as np

app=FastAPI()

app.add_middleware(
  CORSMiddleware,
  allow_origins=["http://localhost:3000"],
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"]
)


@app.post("/check")
async def checkCompatible(file1:UploadFile=File(...),file2:UploadFile=File(...)):
  
  img1_bytes=await file1.read()
  img2_bytes=await file2.read()

  np_img1=np.frombuffer(img1_bytes,np.uint8)
  np_img2=np.frombuffer(img2_bytes,np.uint8)

  img1=cv2.imdecode(np_img1,cv2.IMREAD_COLOR)
  img2=cv2.imdecode(np_img2,cv2.IMREAD_COLOR)

  gray1=cv2.cvtColor(img1,cv2.COLOR_BGR2GRAY)
  gray2=cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY)

  sift=cv2.SIFT_create()

  kp=sift.detect(gray1,None)
  kp,des1=sift.compute(gray1,kp)

  print(des1)
 

  kp1=sift.detect(gray2,None)
  kp1,des2=sift.compute(gray2,kp1)

  print(des2)

  img1=cv2.drawKeypoints(gray1,kp,None,(0,0,255),flags=0)
  img2=cv2.drawKeypoints(gray2,kp1,None,(0,0,255),flags=0)

  bf=cv2.BFMatcher()
  matches=bf.knnMatch(des1,des2,k=2)
  good=[]


  for m,n in matches:
    if m.distance<0.75*n.distance:
       good.append(m)

  print(len(good))

  if(len(good)>=30):
    return {"msg":"It is a Match"}
  else:
    return {"msg":"This is not a Match"}


  matched_img=cv2.drawMatches(img1, kp1, img2, kp, good, None,flags=cv2.DrawMatchesFlags_NOT_DRAW_SINGLE_POINTS)
  cv2.imshow("Good matches",matched_img)
  cv2.waitKey(0)
  cv2.destroyAllWindows()



if __name__=="__main__":
    import uvicorn
    uvicorn.run(app,host="127.0.0.1",port=8000)


