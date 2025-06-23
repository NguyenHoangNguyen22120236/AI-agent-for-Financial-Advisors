const API_URL = process.env.REACT_APP_API_URL;

export function googleLogin() {
  window.location.href = `${API_URL}/auth/google/login`;
}

export function hubspotLogin() {
  window.location.href = `${API_URL}/auth/hubspot/login`;
}