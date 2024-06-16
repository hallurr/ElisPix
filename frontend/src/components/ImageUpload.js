import React from "react";
import {
  DndContext,
  useSensor,
  useSensors,
  PointerSensor,
} from "@dnd-kit/core";
import callAPI from "../helpers/api";

function ImageUpload({ setAllImages, setIsLoading }) {
  const fileInputRef = React.useRef();
  const sensors = useSensors(useSensor(PointerSensor));
  const handleFileChange = (event) => {
    const images = event.target?.files;
    if (images.length > 0) {
      callAPI({ setAllImages, setIsLoading });
    }
  };

  return (
    <div style={styles.center}>
      <DndContext
        style={styles.contentDnd}
        sensors={sensors}
        onDragEnd={() => {
          callAPI({ setAllImages, setIsLoading });
        }}
      >
        <div style={styles.imageUpload}>
          <button
            type="button"
            onClick={() => fileInputRef.current && fileInputRef.current.click()}
            style={styles.fileButton}
          >
            <b>Choose a file</b> or drag it here
          </button>
          <input
            style={styles.fileInput}
            ref={fileInputRef}
            id="image-input"
            type="file"
            onChange={handleFileChange}
            multiple
            accept="image/*"
          />
        </div>
      </DndContext>
    </div>
  );
}

export default ImageUpload;

const styles = {
  center: {
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    width: "50%",
  },
  contentDnd: {
    width: "100%",
    alignItems: "center",
    justifyContent: "center",
  },
  imageUpload: {
    width: "100%",
    height: "125px",
    border: "1px solid rgba(0, 0, 0, 0.3)",
    borderRadius: "5px",
    fontSize: "medium",
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    background: "white",
  },
  fileButton: {
    boxSizing: "border-box",
    appearance: "none",
    WebkitAppearance: "none",
    MozAppearance: "none",
    background: "none",
    border: "none",
    outline: "none",
    width: "calc(100% - 30px)",
    height: "calc(100%)",
    cursor: "pointer",
  },
  fileInput: {
    display: "none",
  },
};
