import React, { useState, useEffect } from "react";
import "./App.css";
import {
  DndContext,
  useSensor,
  useSensors,
  PointerSensor,
} from "@dnd-kit/core";
import JSZip from "jszip";
import { saveAs } from "file-saver";

function App() {
  const [allImages, setAllImages] = useState([]);
  const [displayedImages, setDisplayedImages] = useState([]);
  const [selectedImage, setSelectedImage] = useState(null);
  const [page, setPage] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const fileInputRef = React.useRef();

  const imagesPerPage = 10;
  const handleFileChange = (event) => {
    const images = event.target.files;
    if (images.length > 0) {
      callAPI(images);
    }
  };
  const downloadAllImages = () => {
    const zip = new JSZip();
    allImages.forEach((image, index) => {
      zip.file(`image${index + 1}.png`, image, { base64: true });
    });
    zip.generateAsync({ type: "blob" }).then((content) => {
      saveAs(content, "images.zip");
    });
  };

  const sensors = useSensors(useSensor(PointerSensor));

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

  const callAPI = () => {
    setIsLoading(true);
    setAllImages([]);
    const formData = new FormData();
    const images = document.getElementById("image-input").files;

    for (let i = 0; i < images.length; i++) {
      formData.append("images", images[i]);
    }

    fetch(`http://127.0.0.1:5000/process`, {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        setAllImages(data.images);
        setIsLoading(false);
        setPage(1);
      })
      .catch((error) => {
        setIsLoading(false);
        setPage(1);
      });
  };

  useEffect(() => {
    const startIndex = (page - 1) * imagesPerPage;
    const endIndex = startIndex + imagesPerPage;
    setDisplayedImages(allImages.slice(startIndex, endIndex));
  }, [allImages, page]);

  const handleNext = () => {
    setPage((prevPage) => prevPage + 1);
  };

  const handlePrevious = () => {
    setPage((prevPage) => Math.max(prevPage - 1, 1));
  };

  return (
    <div className="App">
      <div className="content">
        {!isLoading ? (
          <div>
            <DndContext
              className="content-dnd"
              sensors={sensors}
              onDragEnd={callAPI}
            >
              <div className="dropzone">
                <button
                  type="button"
                  onClick={() =>
                    fileInputRef.current && fileInputRef.current.click()
                  }
                  className="file-button"
                >
                  <b>Choose a file</b> or drag it here
                </button>
                <input
                  ref={fileInputRef}
                  id="image-input"
                  type="file"
                  onChange={handleFileChange}
                  style={{ display: "none" }}
                  multiple
                  accept="image/*"
                  className="file-input"
                />
              </div>
            </DndContext>
          </div>
        ) : (
          <div className="loader"></div>
        )}

        {allImages.length > 0 && (
          <div>
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <div className="left-header">Results ({allImages.length})</div>
              <button onClick={downloadAllImages} className="download-button">
                Download all
              </button>
            </div>
            <div className="results-box">
              <div className="image-container">
                {displayedImages.map((image, index) => (
                  <img
                    key={index}
                    src={`data:image/png;base64,${image}`}
                    alt=""
                    effect="blur"
                    onClick={() => setSelectedImage(image)}
                  />
                ))}
              </div>
            </div>
          </div>
        )}
        {selectedImage && (
          <div className="modal">
            <span className="close" onClick={() => setSelectedImage(null)}>
              &times;
            </span>
            <img
              className="modal-content"
              src={`data:image/png;base64,${selectedImage}`}
              alt=""
            />
          </div>
        )}
        {allImages.length > imagesPerPage && (
          <div className="pagination">
            <button
              onClick={handlePrevious}
              disabled={page === 1}
              className="pagination-button"
            >
              <div class="arrow arrow-left"></div>
            </button>
            <div className="pagination-text">
              Page {page} / {Math.floor(allImages.length / imagesPerPage) + 1}
            </div>
            <button
              onClick={handleNext}
              disabled={page * imagesPerPage >= allImages.length}
              className="pagination-button"
            >
              <div class="arrow arrow-right"></div>
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
