const callAPI = ({ setAllImages, setIsLoading }) => {
  setIsLoading({ loading: true, text: "Processing images ..." });
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
      setIsLoading({ loading: false, text: "" });
    })
    .catch(() => {
      setIsLoading({ loading: false, text: "" });
    });
};

export default callAPI;
