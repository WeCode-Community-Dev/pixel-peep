import { AxiosError } from "axios";
import { axiosInstance } from "./axiosInstance";

export const uploadImages = async (images: File[]) => {
  try {
    const formData = new FormData();
    images.forEach((image) => {
      formData.append("images", image);
    });

    const response=await axiosInstance.post('/images',formData)
    return response.data
  } catch (error) {
    if (error instanceof AxiosError){
        throw new Error(error.response?.data)
    }
  }
};
