export interface Contact {
  id: string;
  name: string;
  mobile: string;
}

export interface LoginRequest {
  mobile: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
}

export interface AddContactRequest {
  name: string;
  mobile: string;
}

export interface AuthContextType {
  token: string | null;
  login: (mobile: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}
