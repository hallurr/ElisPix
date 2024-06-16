import React from "react";
import JSZip from "jszip";
import { saveAs } from "file-saver";

function ResultsHeader({ allImages, resetImages }) {
  const downloadAllImages = () => {
    const zip = new JSZip();
    allImages.forEach((image, index) => {
      zip.file(`image${index + 1}.png`, image.image, { base64: true });
    });
    zip.generateAsync({ type: "blob" }).then((content) => {
      saveAs(content, "images.zip");
    });
  };

  return (
    allImages.length > 0 && (
      <div style={styles.container}>
        <div style={styles.leftHeader}>Results ({allImages.length})</div>
        <div>
          <button onClick={resetImages} style={styles.resetButton}>
            Clear
          </button>
          <button onClick={downloadAllImages} style={styles.downloadButton}>
            Download
          </button>
        </div>
      </div>
    )
  );
}

export default ResultsHeader;

const styles = {
  leftHeader: {
    textAlign: "left",
    padding: "8px 25px 8px 25px",
    color: "rgba(7, 13, 15, 1)",
    textSize: "14px",
  },
  downloadButton: {
    marginLeft: "15px",
    padding: "8px 25px 8px 25px",
    border: "none",
    cursor: "pointer",
    backgroundColor: "rgba(51, 161, 253, 1)",
    borderRadius: "10px",
    boxShadow: "0px 2px 4px rgba(0, 0, 0, 0.1)",
    color: "white",
  },
  resetButton: {
    marginLeft: "15px",
    padding: "8px 25px 8px 25px",
    border: "none",
    cursor: "pointer",
    backgroundColor: "gray",
    borderRadius: "10px",
    boxShadow: "0px 2px 4px rgba(0, 0, 0, 0.1)",
    color: "white",
  },
  container: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    height: "100%",
  },
};
