import React from "react";
import {
  DndContext,
  useSensor,
  useSensors,
  PointerSensor,
} from "@dnd-kit/core";
import Upload from "./../images/Upload.svg";

function ImageUpload({ setAllFiles }) {
  const fileInputRef = React.useRef();
  const sensors = useSensors(useSensor(PointerSensor));
  const handleFileChange = (event) => {
    setAllFiles(event.target?.files);
  };

  return (
    <div style={styles.center}>
      <DndContext
        style={styles.contentDnd}
        sensors={sensors}
        onDragEnd={() => {
          setAllFiles(fileInputRef.current.files);
        }}
      >
        <div style={styles.imageUpload}>
          <button
            type="button"
            onClick={() => fileInputRef.current && fileInputRef.current.click()}
            style={styles.fileButton}
          >
            <img src={Upload} alt="Upload" style={{ height: "30px" }} />
            <div>
              <b>Choose a file</b> or drag it here
            </div>
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
    margin: "auto",
    flex: 1,
  },
  contentDnd: {
    alignItems: "center",
    justifyContent: "center",
  },
  imageUpload: {
    width: "30%",
    height: "30%",
    padding: "15px",
    display: "flex",
    border: "2px dotted rgba(0, 0, 0, 0.15)",
    borderRadius: "5px",
    fontSize: "medium",
    alignItems: "center",
    background: "white",
  },
  fileButton: {
    display: "flex",
    boxSizing: "border-box",
    appearance: "none",
    WebkitAppearance: "none",
    MozAppearance: "none",
    background: "none",
    border: "none",
    outline: "none",
    width: "calc(100%)",
    height: "calc(100%)",
    cursor: "pointer",
    flexDirection: "column",
    alignItems: "center",
    justifyContent: "center",
    gap: "15px",
    padding: "10px",
  },
  fileInput: {
    display: "none",
  },
};
