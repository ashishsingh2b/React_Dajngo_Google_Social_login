import React, { useEffect, useState } from "react";
import axios from "axios";

const App = () => {
  const [googleUrl, setGoogleUrl] = useState("");

  useEffect(() => {
    axios
      .get("http://127.0.0.1:8000/api/auth/google/authorization")
      .then((response) => {
        setGoogleUrl(response.data.authorization_url);
      })
      .catch((error) => console.error("Error fetching Google auth URL", error));
  }, []);

  const getAuthCode = () => {
    const params = new URLSearchParams(window.location.search);
    return params.get("code");
  };

  const loginWithGoogle = async () => {
    const code = getAuthCode();
    if (!code) return;

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/api/auth/google/login",
        { code }
      );
      console.log("Login Successful:", response.data);
      localStorage.setItem("user", JSON.stringify(response.data.user));
    } catch (error) {
      console.error("Google Login Error", error);
    }
  };

  return (
    <div style={styles.container}>
      <h1 style={styles.title}>Google Authentication</h1>
      <div style={styles.buttonContainer}>
        <a href={googleUrl} style={{ textDecoration: "none" }}>
          <button style={styles.button}>Sign in with Google</button>
        </a>
        <button style={styles.button} onClick={loginWithGoogle}>
          Complete Login
        </button>
      </div>
    </div>
  );
};

// Inline CSS styles
const styles = {
  container: {
    display: "flex",
    flexDirection: "column",
    justifyContent: "center",
    alignItems: "center",
    height: "100vh",
    backgroundColor: "#f4f4f4",
  },
  title: {
    fontSize: "24px",
    marginBottom: "20px",
    color: "#333",
  },
  buttonContainer: {
    display: "flex",
    flexDirection: "column",
    gap: "15px",
  },
  button: {
    padding: "12px 20px",
    fontSize: "16px",
    cursor: "pointer",
    borderRadius: "5px",
    border: "none",
    backgroundColor: "#4285F4",
    color: "white",
  },
};

export default App;
