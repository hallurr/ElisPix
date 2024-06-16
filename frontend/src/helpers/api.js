const callAPI = ({ setAllImages, setIsLoading }) => {
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
    })
    .catch(() => {
      setIsLoading(false);
    });
};

export default callAPI;
