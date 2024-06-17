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
    boxShadow: "0px 0px 3px 3px rgba(0, 0, 0, 0.6)",
  },
  imageContainer: {
    display: "grid",
    gridTemplateColumns: "repeat(5, 1fr)",
    gridTemplateRows: "auto",
    gridAutoFlow: "row",
    gap: "10px",
    margin: "20px 40px 20px 40px",
    height: "calc(100vh - 350px)",
    width: "100%",
    overflow: "auto",
    alignItems: "flex-start",
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
