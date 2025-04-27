import { useState } from "react";
import { uploadImages } from "../services/imageServices";
import ImageGroups from "../components/ImageGroups";
import ImagePreview from "../components/Image";

const Home = () => {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [groups, setGroups] = useState<File[][]>([]);
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setGroups([])
    const files = e.target.files;
    if (files) {
      setSelectedFiles(Array.from(files));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    try {
      e.preventDefault();
      const response = await uploadImages(selectedFiles);
      const grps: File[][] = [];
      response.groups.forEach((group: number[]) => {
        const grp: File[] = [];
        group.forEach((idx) => {
          grp.push(selectedFiles[idx]);
        });
        grps.push(grp);
      });
      setGroups(grps);
      setSelectedFiles([])
    } catch (error) {
      if (error instanceof Error) {
        // Axios error (network/server related)   
        console.error('error:', error.message);
        alert(error.message)
      } else {
        // Non-Axios error (JS runtime error)
        console.error('Unexpected error:');
      }
    }
  };

  return (
    <div className="flex flex-col  items-center gap-2">
      <h1 className=" m-4 text-3xl text-blue-600 font-bold">Pixel Peep</h1>
      <p className="text-center">
        Detect duplicates, edited, and pirated versions of an image.
      </p>

      <form className="" onSubmit={handleSubmit}>
        <label className="w-full">
          <input
            type="file"
            accept=".jpg, .jpeg, .png, .bmp, .webp, .tiff, .gif"
            multiple
            onChange={handleFileChange}
            className="block w-full text-sm text-gray-200
                     file:mr-4 file:py-2 file:px-4
                     file:rounded-full file:border-0
                     file:text-sm file:font-semibold
                     file:bg-blue-50 file:text-blue-700
                     hover:file:bg-blue-100
                     cursor-pointer"
          />
        </label>
        <button
          className="m-2 w-full bg-green-500 hover:bg-green-600"
          type="submit"
        >
          Submit
        </button>
      </form>

      {selectedFiles.length > 0 && (
        <div className="p-4 grid grid-cols-2 sm:grid-cols-3 gap-4 w-full">
          {selectedFiles.map((file, idx) => (
            <ImagePreview file={file} index={idx}/>
  
          ))}
        </div>
      )}

     {groups.length>0 && <ImageGroups groups={groups} />}
    </div>
  );
};

export default Home;
