// Store the access token in localStorage
export const setAccessToken = (token: string): void => {
  if (typeof window !== 'undefined') {
    localStorage.setItem('access_token', token);
  }
};

// Get the access token from localStorage
export const getAccessToken = (): string | null => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('access_token');
  }
  return null;
};

// Remove the access token from localStorage
export const removeAccessToken = (): void => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('access_token');
  }
};

// Check if user is authenticated
export const isAuthenticated = (): boolean => {
  return !!getAccessToken();
};

// Get user info from token (basic decoding - not secure for sensitive data)
export const getUserInfo = () => {
  const token = getAccessToken();
  if (!token) return null;

  try {
    const tokenParts = token.split('.');
    if (tokenParts.length !== 3) {
      if (!token.startsWith('mock_')) {
        console.error('Invalid token format');
      }
      return null;
    }

    const base64Url = tokenParts[1];
    if (!base64Url) {
      console.error('Missing token payload');
      return null;
    }

    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );

    return JSON.parse(jsonPayload);
  } catch (error) {
    console.error('Error decoding token:', error);
    return null;
  }
};