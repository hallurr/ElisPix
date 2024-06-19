import React from "react";
import "./Loader.css";

function Loader({ text }) {
  return (
    <div className="loaderContainer">
      <div className="loader"></div>
      <div className="loaderText">{text}</div>
    </div>
  );
}

export default Loader;
