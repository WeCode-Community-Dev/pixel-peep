import { ChangeEvent, useState } from "react"

export function FileUploader()
{
    const[file1,setFile1]=useState<File|null>(null)
    const[file2,setFile2]=useState<File|null>(null)
    const[result,setResult]=useState("")
    const[loading,setLoading]=useState(false)
    const handleFileChange1=(event:ChangeEvent<HTMLInputElement>)=>{
        if(event.target.files)
        {
            setFile1(event.target.files[0])
        }

    }

    const handleFileChange2=(event:ChangeEvent<HTMLInputElement>)=>{
    if(event.target.files)
    {
        setFile2(event.target.files[0])
    }
    }

    const handleImage=async ():Promise<void>=>{

        if(!file1 || !file2)
        {
            setResult("Please upload Image")
            return 
        }

        setLoading(true)

        const formData=new FormData()
        formData.append('file1',file1!)
        formData.append('file2',file2!)

        const response=await fetch("http://127.0.0.1:8000/check",{
            method:"POST",
            body:formData
        })

        const data=await response.json()
        
        if(response.status==200)
        {
            setResult(data.msg)
        }

        else
        {
            setResult("Error")
        }
        
        setLoading(false)
    }
    return(
        <div>
        <div className="flex content-evenly grid grid-cols-12">
        
        <div className="grid col-span-8 m-20">
            <div>
            <label htmlFor="file-upload1" className="cursor-pointer border border-gray-400 bg-white text-black rounded-md">Upload Image</label>
            <input type="file" onChange={handleFileChange1} id="file-upload1" style={{display:'none'}}></input>
            </div>
           

            <div className="w-[400px] h-[400px] border border-gray-400 overflow-hidden mt-2">
            {file1&&(
                <div>
                    <img src={URL.createObjectURL(file1)} alt="Uploaded preview" className="object-contain w-full h-full"></img>
                </div>
            )}
            </div>
        </div>
 
        <div className="grid col-span-4 m-20">
            <div>
            <label htmlFor="file-upload2" className="cursor-pointer border border-gray-400 bg-white text-black rounded-md">Upload Image</label>
            <input type="file" onChange={handleFileChange2} id="file-upload2" style={{display:'none'}}></input>
            </div>
           

            <div className="w-[400px] h-[400px] border border-gray-400 overflow-hidden">
            {file2&&(
                <div>
                    <img src={URL.createObjectURL(file2)} alt="Uploaded preview" className="object-contain w-full h-full"></img>
                </div>
            )}
            </div>
        </div>

        </div>

        <div className="flex justify-center">
           <button className="cursor-pointer border border-gray-500 bg-white text-black rounded-md" onClick={handleImage}>Check!!</button>
        </div>

        <div className="flex justify-center mt-4">
            {loading &&(
                <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-gray-800"></div>
            )}

        </div>

        <div className="flex justify-center mt-10 text-2xl">
            {result}
        </div>

        </div>
            
       

        
    )
}