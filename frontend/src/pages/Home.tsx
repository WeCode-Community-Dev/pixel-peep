import { useState } from "react";

const Home = () => {
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files) {
      setSelectedFiles(Array.from(files));
    }
  };

  const handleSubmit = async() => {
    try {
        
    } catch (error) {
        
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
            accept="image/*"
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
      </form>

      { selectedFiles.length > 0 && (
        <div className="p-4 grid grid-cols-2 sm:grid-cols-3 gap-4 w-full">
          {selectedFiles.map((file, idx) => (
            <div key={idx} className="relative rounded overflow-hidden border border-gray-300 shadow-sm p-2">
              <img
                src={URL.createObjectURL(file)}
                alt={`preview-${idx}`}
                className="object-cover "
              />
              <p><span className="text-blue-600">File name:</span> {file.name}</p>
              <p><span className="text-blue-600">File size:</span> {Math.floor(file.size/1000)} KB</p>

            </div>
          ))}
        </div>
      )}

    </div>
  );
};

export default Home;
