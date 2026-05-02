export const validateMobile = (mobile: string): { valid: boolean; error?: string } => {
  const digitsOnly = /^\d+$/.test(mobile);
  if (!digitsOnly) {
    return { valid: false, error: 'Mobile must contain only digits' };
  }
  if (mobile.length < 10) {
    return { valid: false, error: 'Mobile must be at least 10 digits' };
  }
  return { valid: true };
};

export const validatePassword = (password: string): { valid: boolean; error?: string } => {
  if (password.length < 6) {
    return { valid: false, error: 'Password must be at least 6 characters' };
  }
  return { valid: true };
};

export const validateName = (name: string): { valid: boolean; error?: string } => {
  if (!name || name.trim().length === 0) {
    return { valid: false, error: 'Name is required' };
  }
  return { valid: true };
};
