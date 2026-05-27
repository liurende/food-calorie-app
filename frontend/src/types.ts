export interface FoodItem {
  id?: number;
  meal_id?: number;
  name: string;
  weight_g: number;
  calories: number;
  protein_g?: number | null;
  carbs_g?: number | null;
  fat_g?: number | null;
  confidence?: number | null;
}

export interface Meal {
  id: number;
  user_id: string;
  meal_type: 'breakfast' | 'lunch' | 'dinner' | 'snack';
  image_paths?: string | null;
  total_calories?: number | null;
  recorded_at: string;
  items: FoodItem[];
}

export interface RecognizeResult {
  name: string;
  weight_g: number;
  calories: number;
  protein_g?: number | null;
  carbs_g?: number | null;
  fat_g?: number | null;
  confidence: number;
  volume_cm3?: number;
}

export interface StatsData {
  date: string;
  total_calories: number;
  total_protein: number;
  total_carbs: number;
  total_fat: number;
  meals: Meal[];
}

export type MealType = 'breakfast' | 'lunch' | 'dinner' | 'snack';

export type CaptureStep = 0 | 1 | 2;
