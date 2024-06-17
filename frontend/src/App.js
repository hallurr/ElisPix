import React, { useState } from "react";
import ImagesContainer from "./components/ImagesContainer";
import ResultsHeader from "./components/ResultsHeader";
import ImageUpload from "./components/ImageUpload";
import "./App.css";
import Header from "./images/Header.svg";
import Loader from "./components/Loader";

function App() {
  const [allImages, setAllImages] = useState([]);
  const [isLoading, setIsLoading] = useState({ loading: false, text: "" });

  return (
    <div className="App">
      <img src={Header} className="headerImage" alt="Header" />
      <div className="content">
        {isLoading.loading && <Loader text={isLoading.text} />}
        {!isLoading.loading &&
          (allImages.length === 0 ? (
            <ImageUpload
              setAllImages={setAllImages}
              setIsLoading={setIsLoading}
            />
          ) : (
            <div style={{ display: "flex", flexDirection: "column" }}>
              <ResultsHeader
                allImages={allImages}
                resetImages={() => {
                  setAllImages([]);
                }}
                setLoading={setIsLoading}
              />
              <ImagesContainer displayedImages={allImages} />
            </div>
          ))}
      </div>
    </div>
  );
}

export default App;
