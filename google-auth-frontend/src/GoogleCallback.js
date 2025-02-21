import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

const GoogleCallback = () => {
  const navigate = useNavigate();

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const code = params.get("code");

    if (code) {
      axios.post("http://127.0.0.1:8000/api/auth/google/callback", { code })
        .then(response => {
          console.log("Login Successful:", response.data);
          localStorage.setItem("user", JSON.stringify(response.data.user));
          navigate("/dashboard");  
        })
        .catch(error => console.error("Google Login Error", error));
    }
  }, [navigate]);

  return <h2>Processing login...</h2>;
};

export default GoogleCallback;
