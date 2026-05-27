const BASE = '/api';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`${res.status}: ${err}`);
  }
  return res.json();
}

export const api = {
  uploadImages: async (files: File[]) => {
    const form = new FormData();
    files.forEach((f) => form.append('files', f));
    const res = await fetch(`${BASE}/upload`, { method: 'POST', body: form });
    return res.json();
  },

  recognize: (imagePaths: string[], knownDistanceCm = 30) =>
    request<import('../types').RecognizeResult[]>(`/recognize`, {
      method: 'POST',
      body: JSON.stringify({ image_paths: imagePaths, known_distance_cm: knownDistanceCm }),
    }),

  createMeal: (meal: {
    user_id: string; meal_type: string; total_calories?: number;
    image_paths?: string; items: import('../types').FoodItem[];
  }) => request<{ id: number }>('/meals', { method: 'POST', body: JSON.stringify(meal) }),

  getMeals: (userId: string, date: string) =>
    request<import('../types').Meal[]>(`/meals?user_id=${userId}&date=${date}`),

  deleteMeal: (id: number) => request<{ status: string }>(`/meals/${id}`, { method: 'DELETE' }),

  getStats: (userId: string, range = 'daily', date?: string) =>
    request<import('../types').StatsData>(
      `/stats?user_id=${userId}&range=${range}${date ? `&target_date=${date}` : ''}`
    ),

  searchFoods: (q: string) =>
    request<Array<{
      id: number; name: string; name_en?: string;
      density_g_cm3: number; calories_per_100g: number;
      protein_per_100g?: number; carbs_per_100g?: number; fat_per_100g?: number;
      category?: string;
    }>>(`/foods/search?q=${encodeURIComponent(q)}`),
};
