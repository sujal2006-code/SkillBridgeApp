const FEMALE_NAMES = new Set([
  'priya', 'ananya', 'neha', 'sneha', 'kavya', 'pooja', 'ishita', 'aditi', 'riya', 'shreya', 'swati', 'tanvi', 'divya', 'meera', 'nisha'
]);

export const BOY_AVATARS = [
  'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=150&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=150&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150&auto=format&fit=crop&q=80',
];

export const GIRL_AVATARS = [
  'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=150&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=150&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=150&auto=format&fit=crop&q=80',
  'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150&auto=format&fit=crop&q=80',
];

export const getStudentAvatar = (name: string, id: number = 0): string => {
  const firstName = (name || '').trim().split(' ')[0].toLowerCase();
  if (FEMALE_NAMES.has(firstName)) {
    return GIRL_AVATARS[Math.abs(id) % GIRL_AVATARS.length];
  }
  return BOY_AVATARS[Math.abs(id) % BOY_AVATARS.length];
};
