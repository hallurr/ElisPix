import React, { useState } from "react";
import Image from "./Image";

function ImagesContainer({ displayedImages }) {
  const [selectedImage, setSelectedImage] = useState(null);
  return (
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
  );
}

export default ImagesContainer;

const styles = {
  thumbnail: {
    objectFit: "contain",
    maxWidth: "90%",
    maxHeight: "90%",
    boxShadow: "0px 0px 3px 3px rgba(0, 0, 0, 0.6)",
  },
  imageContainer: {
    padding: "15px",
    display: "grid",
    gridTemplateColumns: "repeat(5, 1fr)",
    gridTemplateRows: "auto",
    gridAutoFlow: "row",
  },
  imgHolder: {
    position: "relative",
    maxHeight: "20vh",
    maxWidth: "30vh",
    overflow: "hidden",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
  },
};
