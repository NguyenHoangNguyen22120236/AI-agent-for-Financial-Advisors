import { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

function AuthCallback() {
  const navigate = useNavigate();
  const { setUser } = useAuth();

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get("token");

    if (token) {
      // Save token to localStorage
      localStorage.setItem("access_token", token);

      // Optional: fetch /auth/me to preload user info
      fetch(`${process.env.REACT_APP_API_URL}/auth/me`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.user) {
            setUser(data.user);  // update global context
            navigate("/");   // redirect to app
          } else {
            navigate("/login");
          }
        })
        .catch(() => {
          navigate("/login");
        });
    } else {
      navigate("/login"); // no token = failed login
    }
  }, [navigate, setUser]);

  return <p>Logging you in...</p>;
}

export default AuthCallback;
