import React, { useState, useEffect } from "react";
import ImagesContainer from "./components/ImagesContainer";
import ResultsHeader from "./components/ResultsHeader";
import ImageUpload from "./components/ImageUpload";
import "./App.css";
import Header from "./images/Header.svg";
import Loader from "./components/Loader";
import callAPI from "./helpers/api";

const sendToApi = (files, setAllImages, setIsLoading) => {
  callAPI({ setAllImages, setIsLoading, files });
};

function App() {
  const [allImages, setAllImages] = useState([]);
  const [allFiles, setAllFiles] = useState([]);
  const [isLoading, setIsLoading] = useState({ loading: false, text: "" });
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    sendToApi(allFiles, setAllImages, setIsLoading);
  }, [allFiles]);

  const refreshResults = () => {
    sendToApi(allFiles, setAllImages, setIsLoading);
  };

  useEffect(() => {
    const handleScroll = () => {
      const show = window.scrollY > 70;
      if (show !== scrolled) {
        setScrolled(show);
      }
    };

    document.addEventListener("scroll", handleScroll);
    return () => {
      document.removeEventListener("scroll", handleScroll);
    };
  }, [scrolled]);

  return (
    <div className="App">
      <div className={`headerContainer ${scrolled ? "scrolled" : ""}`}>
        <img
          src={Header}
          className={`headerImage ${scrolled ? "scrolled" : ""}`}
          alt="Header"
        />
        <ResultsHeader
          allImages={allImages}
          clearImages={() => {
            setAllImages([]);
          }}
          setLoading={setIsLoading}
          refreshResults={refreshResults}
        />
      </div>
      <div className="content">
        {isLoading.loading && <Loader text={isLoading.text} />}
        {!isLoading.loading &&
          (allImages.length === 0 ? (
            <ImageUpload setAllFiles={setAllFiles} />
          ) : (
            <ImagesContainer displayedImages={allImages} />
          ))}
      </div>
    </div>
  );
}

export default App;
