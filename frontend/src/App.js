import React, { useState } from "react";
import ImagesContainer from "./components/ImagesContainer";
import ResultsHeader from "./components/ResultsHeader";
import ImageUpload from "./components/ImageUpload";
import "./App.css";
import Header from "./images/Header.svg";

function App() {
  const [allImages, setAllImages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  return (
    <div className="App">
      <img src={Header} alt="Header" className="header-image" />
      <div className="content">
        {isLoading && <div className="loader"></div>}
        {!isLoading &&
          (allImages.length === 0 ? (
            <ImageUpload
              setAllImages={setAllImages}
              setIsLoading={setIsLoading}
            />
          ) : (
            <div
              style={{ display: "flex", flexDirection: "column", width: "70%" }}
            >
              <ResultsHeader
                allImages={allImages}
                resetImages={() => {
                  setAllImages([]);
                }}
              />
              <ImagesContainer displayedImages={allImages} />
            </div>
          ))}
      </div>
    </div>
  );
}

export default App;
