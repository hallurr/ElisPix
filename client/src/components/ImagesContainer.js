import React, { useState } from "react";
import Image from "./Image";

function ImagesContainer({ displayedImages }) {
  const [selectedImage, setSelectedImage] = useState(null);
  return (
    <div
      style={{
        display: "flex",
        flexDirection: "column",
        width: "100%",
      }}
    >
      <div style={styles.resultsTitle}>Results ({displayedImages.length})</div>
      <div style={styles.imageContainer}>
        {displayedImages.map((image, index) => (
          <div key={index} style={styles.imgHolder}>
            <img
              key={index}
              style={styles.thumbnail}
              src={`data:image/png;base64,${image.thumbnail}`}
              alt=""
              effect="blur"
              onClick={() => setSelectedImage(image.image)}
            />
          </div>
        ))}
        {selectedImage && (
          <Image
            selectedImage={selectedImage}
            setSelectedImage={setSelectedImage}
          />
        )}
      </div>
    </div>
  );
}

export default ImagesContainer;

const styles = {
  resultsTitle: {
    textAlign: "left",
    color: "rgba(7, 13, 15, 1)",
    fontSize: "16px",
  },
  thumbnail: {
    objectFit: "contain",
    boxShadow: "0px 0px 3px 3px rgba(0, 0, 0, 0.6)",
  },
  imageContainer: {
    display: "grid",
    gridTemplateColumns: "repeat(5, 1fr)",
    gridTemplateRows: "auto",
    gridAutoFlow: "row",
    gap: "10px",
    margin: "20px 0px 20px 0px",
    height: "100%",
    width: "100%",
    overflow: "auto",
    padding: "10px",
  },
  imgHolder: {
    position: "relative",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    marginTop: "10px",
    marginBottom: "10px",
  },
};
