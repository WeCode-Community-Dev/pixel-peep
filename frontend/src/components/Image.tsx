// Props type for the ImagePreview component
interface ImagePreviewProps {
  file: File;
  index: number;
}

const ImagePreview: React.FC<ImagePreviewProps> = ({ file, index }) => {
  const fileUrl = URL.createObjectURL(file);

  return (
    <div
      key={index}
      className="relative rounded overflow-hidden border max-w-[200px] border-gray-300 shadow-sm p-2"
    >
      <img
        src={fileUrl}
        alt={`preview-${index}`}
        className="object-cover w-full  rounded"
      />
      <div className="mt-2 text-sm">
        <p>
          <span className="text-blue-600 font-medium">File name:</span> {file.name}
        </p>
        <p>
          <span className="text-blue-600 font-medium">File size:</span> {Math.floor(file.size / 1000)} KB
        </p>
      </div>
    </div>
  );
};

export default ImagePreview;
