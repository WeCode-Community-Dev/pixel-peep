import { AxiosError } from "axios";
import { axiosInstance } from "./axiosInstance";

export const uploadImages = async (images: File[]) => {
  try {
    if (images.length==0){
      throw new Error('Select atleast one image')
    }
    const formData = new FormData();
    images.forEach((image) => {
      formData.append("images", image);
    });

    const response=await axiosInstance.post('/images',formData)
    return response.data
  } catch (error) {
    if (error instanceof AxiosError){
        throw new Error(error.response?.data?.detail)
    }else if (error instanceof Error){
      throw new Error(error.message)
    }
  }
};
