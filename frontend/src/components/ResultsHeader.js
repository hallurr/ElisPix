import React from "react";
import JSZip from "jszip";
import { saveAs } from "file-saver";
import Clear from "./../images/Clear.svg";
import Download from "./../images/Download.svg";

function ResultsHeader({ allImages, resetImages, setLoading }) {
  const downloadAllImages = () => {
    const zip = new JSZip();
    allImages.forEach((image, index) => {
      zip.file(`image${index + 1}.png`, image.image, { base64: true });
    });
    zip.generateAsync({ type: "blob" }).then((content) => {
      saveAs(content, "images.zip");
      setLoading({ loading: false, text: "" });
    });
  };

  return (
    allImages.length > 0 && (
      <div style={styles.container}>
        <div style={styles.leftHeader}>
          <div style={styles.resultsTitle}>Results</div>
          <div style={styles.resultsDescription}>
            {allImages.length} images found
          </div>
        </div>
        <div style={{ display: "flex" }}>
          <button onClick={resetImages} style={styles.resetButton}>
            <div style={{ marginRight: "8px", color: "black" }}>Clear</div>
            <img src={Clear} alt="Clear" />
          </button>
          <button
            onClick={() => {
              setLoading({ loading: true, text: "Preparing download ..." });
              setTimeout(downloadAllImages, 100);
            }}
            style={styles.downloadButton}
          >
            <div style={{ marginRight: "8px" }}>Download all </div>
            <img src={Download} alt="Download" />
          </button>
        </div>
      </div>
    )
  );
}

export default ResultsHeader;

const styles = {
  leftHeader: {
    display: "flex",
    flexDirection: "column",
    textAlign: "left",
    padding: "8px 8px 8px 8px",
    color: "rgba(7, 13, 15, 1)",
    fontSize: "20px",
    gap: "10px",
  },
  resultsTitle: {
    textAlign: "left",
    color: "rgba(7, 13, 15, 1)",
    fontSize: "20px",
    fontWeight: "bold",
  },
  resultsDescription: {
    textAlign: "left",
    color: "rgba(7, 13, 15, 1)",
    fontSize: "14px",
  },
  downloadButton: {
    marginLeft: "15px",
    padding: "8px 8px 8px 8px",
    border: "none",
    cursor: "pointer",
    backgroundColor: "rgba(51, 161, 253, 1)",
    borderRadius: "10px",
    boxShadow: "0px 2px 4px rgba(0, 0, 0, 0.1)",
    color: "white",
    display: "flex",
    flexDirection: "row",
    alignItems: "center",
  },
  resetButton: {
    marginLeft: "15px",
    padding: "8px 15px 8px 15px",
    border: "none",
    cursor: "pointer",
    background: "none",
    color: "white",
    display: "flex",
    flexDirection: "row",
    alignItems: "center",
  },
  container: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    height: "100%",
    width: "100%",
    padding: "15px 0px 15px 0px",
    borderBottom: "0.5px solid black",
    position: "relative",
    //backgroundColor: "orange",
  },
};
