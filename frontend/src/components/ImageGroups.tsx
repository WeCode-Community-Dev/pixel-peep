import React from "react";
import ImagePreview from "./Image";

// Props type for ImageGroups
interface ImageGroupsProps {
  groups: File[][];
}

const ImageGroups: React.FC<ImageGroupsProps> = ({ groups }) => {
  return (
    <div className="grid gap-4">
      <h1 className="text-2xl text-center  font-bold">Image Groups</h1>
      {groups.map((group, groupIndex) => (
        <>
          <h2 className="text-xl font-bold">{`Group: ${groupIndex+1}`}</h2>
          <div
            key={groupIndex}
            className="p-4 grid grid-cols-2 sm:grid-cols-3 gap-4 w-full bg-gray-800 outline"
          >
            {group.map((file, idx) => (
              <ImagePreview file={file} index={idx} />
            ))}
          </div>
        </>
      ))}
    </div>
  );
};

export default ImageGroups;
