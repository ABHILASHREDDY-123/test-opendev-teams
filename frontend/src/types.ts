interface User {
  id: string;
  mobile: string;
}

interface Contact {
  id: string;
  name: string;
  mobile: string;
  owner_id: string;
}

interface LoginForm {
  mobile: string;
  password: string;
}

interface ContactForm {
  name: string;
  mobile: string;
}