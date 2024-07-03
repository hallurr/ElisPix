import React from "react";
import JSZip from "jszip";
import { saveAs } from "file-saver";
import Clear from "./../images/Clear.svg";
import Download from "./../images/Download.svg";
import Refresh from "./../images/Refresh.svg";

function ResultsHeader({ allImages, clearImages, setLoading, refreshResults }) {
  const downloadAllImages = () => {
    const zip = new JSZip();
    allImages.forEach((image, _) => {
      zip.file(`${image.filename}.png`, image.image, { base64: true });
    });
    zip.generateAsync({ type: "blob" }).then((content) => {
      saveAs(content, "images.zip");
      setLoading({ loading: false, text: "" });
    });
  };

  return (
    allImages.length > 0 && (
      <div style={styles.container}>
        <div style={styles.leftHeader}></div>
        <div style={{ display: "flex", gap: "10px" }}>
          <button onClick={refreshResults} style={styles.resetButton}>
            <div style={{ marginRight: "8px", color: "black" }}>
              Reprocess images
            </div>
            <img src={Refresh} alt="Refresh" />
          </button>
          <button onClick={clearImages} style={styles.resetButton}>
            <div style={{ marginRight: "8px", color: "black" }}>
              Clear results
            </div>
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
    gap: "10px",
  },
  resultsDescription: {
    textAlign: "left",
    color: "rgba(7, 13, 15, 1)",
    fontSize: "14px",
  },
  downloadButton: {
    padding: "8px 8px 8px 8px",
    border: "none",
    cursor: "pointer",
    backgroundColor: "rgba(51, 161, 253, 1)",
    borderRadius: "10px",
    color: "white",
    display: "flex",
    flexDirection: "row",
    alignItems: "center",
  },
  resetButton: {
    padding: "8px 15px 8px 15px",
    border: "none",
    cursor: "pointer",
    background: "#e7e7e7",
    color: "white",
    borderRadius: "10px",
    display: "flex",
    flexDirection: "row",
    alignItems: "center",
  },
  container: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "15px 0px 15px 0px",
    position: "relative",
    backgroundColor: "white",
    width: "100%",
  },
};
