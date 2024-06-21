import React, { useState } from "react";
import Image from "./Image";

function ImagesContainer({ displayedImages }) {
  const [selectedImage, setSelectedImage] = useState(null);
  return (
    <div
      style={{
        width: "90%",
        margin: "0 auto",
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
    height: "40px",
    marginTop: "30px",
    width: "100%",
  },
  thumbnail: {
    objectFit: "contain",
    boxShadow: "0px 0px 3px 3px rgba(0, 0, 0, 0.6)",
  },
  imageContainer: {
    boxSizing: "border-box",
    display: "grid",
    gridTemplateColumns: "auto auto auto",
    gridTemplateRows: "auto",
    gridAutoFlow: "row",
    gap: "10px",
    overflow: "auto",
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
