import React, { useEffect } from "react";
import "./Image.css";

function Image({ selectedImage, setSelectedImage }) {
  useEffect(() => {
    const handleKeyDown = (event) => {
      if (event.key === "Escape") {
        setSelectedImage(null);
      }
    };
    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
    };
  }, []);

  const handleClick = (event) => {
    if (event.target === event.currentTarget) {
      setSelectedImage(null);
    }
  };

  return (
    selectedImage && (
      <div style={styles.image} onClick={handleClick}>
        <span style={styles.close} onClick={() => setSelectedImage(null)}>
          &times;
        </span>
        <img
          style={styles.imageContent}
          src={`data:image/png;base64,${selectedImage}`}
          alt=""
        />
      </div>
    )
  );
}

export default Image;

const styles = {
  imageContent: {
    maxWidth: "85vw",
    maxHeight: "85vh",
    objectFit: "contain",
    position: "absolute",
    top: "50%",
    left: "50%",
    transform: "translate(-50%, -50%)",
    display: "block",
    paddingBottom: "20px",
  },
  close: {
    position: "absolute",
    top: "15px",
    right: "35px",
    color: "#f1f1f1",
    fontSize: "40px",
    fontWeight: "bold",
    transition: "0.3s",
  },
  image: {
    display: "block",
    position: "fixed",
    zIndex: 10,
    paddingTop: "100px",
    left: "0",
    top: "0",
    width: "100%",
    height: "90%",
    overflow: "auto",
    backgroundColor: "rgba(0, 0, 0, 0.9)",
  },
};
