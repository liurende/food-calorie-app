import sqlite3
from database import get_db, DB_PATH

SEED_FOODS = [
    # === 主食 staples ===
    ("白米饭", "White Rice", 0.85, 116, 2.6, 25.9, 0.3, "staple"),
    ("糙米饭", "Brown Rice", 0.85, 123, 2.7, 25.6, 0.9, "staple"),
    ("黑米饭", "Black Rice", 0.85, 120, 3.0, 25.0, 1.0, "staple"),
    ("小米粥", "Millet Porridge", 0.98, 46, 1.4, 8.4, 0.7, "staple"),
    ("白粥", "Rice Porridge", 0.98, 34, 0.6, 7.8, 0.1, "staple"),
    ("馒头", "Steamed Bun", 0.45, 223, 7.0, 44.2, 1.1, "staple"),
    ("花卷", "Flower Roll", 0.42, 211, 6.4, 41.0, 1.8, "staple"),
    ("全麦面包", "Whole Wheat Bread", 0.25, 247, 13.0, 41.0, 3.4, "staple"),
    ("白面包", "White Bread", 0.22, 265, 9.0, 49.0, 3.2, "staple"),
    ("面条(煮)", "Noodles Cooked", 0.95, 138, 4.5, 28.5, 1.0, "staple"),
    ("米粉(煮)", "Rice Noodles Cooked", 0.95, 110, 1.5, 25.0, 0.3, "staple"),
    ("河粉(煮)", "Ho Fun Cooked", 0.95, 120, 2.0, 26.0, 0.5, "staple"),
    ("凉皮", "Cold Noodles", 0.90, 140, 4.0, 25.0, 2.0, "staple"),
    ("玉米(整)", "Corn Whole", 0.72, 112, 4.0, 22.8, 1.5, "staple"),
    ("玉米粒", "Corn Kernels", 0.70, 110, 3.5, 22.0, 1.3, "staple"),
    ("红薯", "Sweet Potato", 0.65, 86, 1.6, 20.1, 0.1, "staple"),
    ("紫薯", "Purple Sweet Potato", 0.67, 82, 2.0, 19.0, 0.1, "staple"),
    ("土豆", "Potato", 0.65, 77, 2.0, 17.5, 0.1, "staple"),
    ("土豆块", "Potato Chunks", 0.68, 80, 2.0, 18.0, 0.1, "staple"),
    ("土豆泥", "Mashed Potato", 0.55, 106, 2.5, 20.0, 3.0, "staple"),
    ("山药", "Chinese Yam", 0.72, 65, 1.5, 14.0, 0.1, "staple"),
    ("芋头", "Taro", 0.75, 79, 2.0, 17.0, 0.2, "staple"),
    ("燕麦片", "Oatmeal", 0.38, 367, 13.5, 61.6, 7.0, "staple"),
    ("年糕", "Rice Cake", 0.88, 154, 3.3, 33.9, 0.3, "staple"),

    # === 绿叶蔬菜 leafy greens ===
    ("菠菜", "Spinach", 0.40, 28, 2.6, 3.8, 0.3, "vegetable"),
    ("生菜", "Lettuce", 0.35, 15, 1.4, 2.8, 0.2, "vegetable"),
    ("油麦菜", "A Choy", 0.38, 20, 1.5, 3.2, 0.2, "vegetable"),
    ("小白菜", "Bok Choy", 0.42, 17, 1.5, 2.7, 0.2, "vegetable"),
    ("空心菜", "Water Spinach", 0.40, 23, 2.2, 3.6, 0.3, "vegetable"),
    ("茼蒿", "Crown Daisy", 0.38, 21, 1.9, 3.0, 0.3, "vegetable"),
    ("韭菜", "Chinese Chives", 0.50, 26, 2.4, 3.7, 0.4, "vegetable"),
    ("芹菜茎", "Celery Stalk", 0.55, 16, 0.8, 3.0, 0.2, "vegetable"),
    ("大白菜", "Napa Cabbage", 0.42, 13, 1.0, 2.2, 0.2, "vegetable"),
    ("卷心菜", "Cabbage", 0.45, 24, 1.3, 5.1, 0.1, "vegetable"),

    # === 十字花科 cruciferous ===
    ("西兰花", "Broccoli", 0.45, 34, 2.8, 6.6, 0.4, "vegetable"),
    ("花菜", "Cauliflower", 0.45, 25, 1.9, 4.9, 0.3, "vegetable"),

    # === 根茎/瓜果蔬菜 roots & gourds ===
    ("黄瓜", "Cucumber", 0.60, 16, 0.7, 2.9, 0.1, "vegetable"),
    ("番茄", "Tomato", 0.62, 18, 0.9, 3.9, 0.2, "vegetable"),
    ("胡萝卜", "Carrot", 0.55, 41, 0.9, 9.6, 0.2, "vegetable"),
    ("白萝卜", "White Radish", 0.60, 21, 0.9, 4.1, 0.1, "vegetable"),
    ("茄子", "Eggplant", 0.55, 25, 1.0, 5.7, 0.2, "vegetable"),
    ("西葫芦", "Zucchini", 0.45, 17, 1.2, 3.1, 0.3, "vegetable"),
    ("冬瓜", "Winter Melon", 0.55, 13, 0.4, 2.6, 0.2, "vegetable"),
    ("南瓜", "Pumpkin", 0.60, 26, 1.0, 5.9, 0.1, "vegetable"),
    ("丝瓜", "Luffa", 0.50, 20, 1.0, 3.6, 0.2, "vegetable"),
    ("苦瓜", "Bitter Melon", 0.50, 19, 1.0, 3.5, 0.1, "vegetable"),

    # === 豆类蔬菜 legumes ===
    ("豆角", "Green Beans", 0.60, 34, 2.5, 7.0, 0.3, "vegetable"),
    ("四季豆", "Kidney Beans Green", 0.62, 31, 2.1, 6.5, 0.2, "vegetable"),
    ("荷兰豆", "Snow Peas", 0.45, 42, 2.8, 7.6, 0.2, "vegetable"),
    ("毛豆", "Edamame", 0.65, 131, 11.9, 10.6, 5.2, "vegetable"),

    # === 辣椒 peppers ===
    ("青椒", "Green Pepper", 0.50, 20, 0.9, 4.5, 0.2, "vegetable"),
    ("红椒", "Red Bell Pepper", 0.52, 31, 1.0, 6.0, 0.3, "vegetable"),

    # === 菌菇 mushrooms ===
    ("香菇", "Shiitake Mushroom", 0.50, 34, 2.2, 6.3, 0.5, "mushroom"),
    ("平菇", "Oyster Mushroom", 0.45, 33, 3.5, 3.8, 0.4, "mushroom"),
    ("金针菇", "Enoki Mushroom", 0.42, 37, 2.7, 5.0, 0.2, "mushroom"),
    ("杏鲍菇", "King Oyster Mushroom", 0.50, 35, 1.9, 5.4, 0.1, "mushroom"),
    ("木耳", "Wood Ear Mushroom", 0.48, 265, 10.6, 55.0, 1.5, "mushroom"),
    ("银耳", "Snow Fungus", 0.45, 261, 6.6, 54.0, 0.6, "mushroom"),

    # === 肉类 meat (cooked) ===
    ("鸡胸肉(熟)", "Chicken Breast Cooked", 0.98, 165, 31.0, 0.0, 3.6, "meat"),
    ("鸡腿肉(熟)", "Chicken Thigh Cooked", 1.02, 209, 25.9, 0.0, 10.9, "meat"),
    ("鸡翅(熟)", "Chicken Wing Cooked", 0.90, 222, 20.3, 0.0, 15.5, "meat"),
    ("鸡胸肉", "Chicken Breast", 0.98, 165, 31.0, 0.0, 3.6, "meat"),
    ("鸡腿", "Chicken Leg", 1.02, 209, 25.9, 0.0, 10.9, "meat"),
    ("猪里脊(熟)", "Pork Tenderloin Cooked", 1.05, 143, 28.5, 0.0, 3.5, "meat"),
    ("猪排骨(熟)", "Pork Ribs Cooked", 1.10, 264, 18.0, 0.0, 20.0, "meat"),
    ("猪五花肉(熟)", "Pork Belly Cooked", 0.92, 518, 9.3, 0.0, 52.3, "meat"),
    ("牛肉(熟)", "Beef Cooked", 1.10, 250, 27.0, 0.0, 15.0, "meat"),
    ("牛腩(熟)", "Beef Brisket Cooked", 1.05, 280, 20.0, 0.0, 21.0, "meat"),
    ("羊肉(熟)", "Lamb Cooked", 1.05, 294, 24.6, 0.0, 21.0, "meat"),
    ("鸭肉(熟)", "Duck Cooked", 1.00, 337, 19.0, 0.1, 28.0, "meat"),
    ("鹅肉(熟)", "Goose Cooked", 1.02, 305, 20.0, 0.0, 24.0, "meat"),

    # === 水产 seafood (cooked) ===
    ("三文鱼(熟)", "Salmon Cooked", 0.98, 208, 20.4, 0.0, 13.4, "seafood"),
    ("虾仁(熟)", "Shrimp Cooked", 0.95, 99, 24.0, 0.2, 0.3, "seafood"),
    ("带鱼(熟)", "Hairtail Cooked", 1.00, 172, 18.0, 0.0, 10.8, "seafood"),
    ("鲈鱼(熟)", "Sea Bass Cooked", 0.98, 127, 18.6, 0.0, 5.5, "seafood"),
    ("鳕鱼(熟)", "Cod Cooked", 1.00, 105, 22.8, 0.0, 0.9, "seafood"),
    ("鲫鱼(熟)", "Crucian Carp Cooked", 0.98, 115, 17.5, 0.0, 4.5, "seafood"),
    ("草鱼(熟)", "Grass Carp Cooked", 0.98, 113, 16.6, 0.0, 5.2, "seafood"),
    ("龙利鱼柳(熟)", "Sole Fillet Cooked", 1.00, 91, 18.8, 0.0, 1.3, "seafood"),
    ("鱿鱼(熟)", "Squid Cooked", 0.92, 92, 15.6, 3.0, 1.4, "seafood"),
    ("虾(熟)", "Shrimp Cooked", 0.95, 99, 24.0, 0.2, 0.3, "seafood"),

    # === 豆制品 tofu ===
    ("嫩豆腐", "Soft Tofu", 0.85, 76, 4.8, 1.5, 4.8, "tofu"),
    ("老豆腐", "Firm Tofu", 0.90, 116, 12.0, 4.0, 6.0, "tofu"),
    ("豆腐", "Tofu", 0.88, 100, 8.0, 3.0, 5.0, "tofu"),
    ("豆干", "Dried Tofu", 0.92, 151, 16.0, 4.0, 8.0, "tofu"),
    ("千张", "Tofu Skin Sheets", 0.55, 162, 16.5, 3.0, 9.5, "tofu"),
    ("腐竹", "Dried Tofu Stick", 0.35, 459, 44.6, 13.0, 21.7, "tofu"),
    ("黄豆芽", "Soybean Sprouts", 0.52, 44, 4.5, 4.5, 1.6, "tofu"),
    ("绿豆芽", "Mung Bean Sprouts", 0.50, 18, 2.1, 2.1, 0.3, "tofu"),

    # === 蛋类 eggs ===
    ("煮鸡蛋", "Boiled Egg", 0.90, 155, 12.6, 1.1, 10.6, "egg"),
    ("炒鸡蛋", "Scrambled Eggs", 0.55, 196, 13.6, 1.5, 14.8, "egg"),
    ("蒸蛋", "Steamed Egg Custard", 0.85, 84, 6.0, 1.0, 6.0, "egg"),
    ("咸鸭蛋", "Salted Duck Egg", 0.88, 190, 12.7, 2.0, 14.7, "egg"),
    ("鹌鹑蛋", "Quail Egg", 0.88, 158, 13.0, 1.5, 11.0, "egg"),

    # === 水果 fruits ===
    ("苹果", "Apple", 0.60, 52, 0.3, 13.8, 0.2, "fruit"),
    ("香蕉", "Banana", 0.65, 89, 1.1, 22.8, 0.3, "fruit"),
    ("橙子", "Orange", 0.72, 47, 0.9, 11.8, 0.1, "fruit"),
    ("葡萄", "Grapes", 0.80, 69, 0.7, 18.1, 0.2, "fruit"),
    ("草莓", "Strawberry", 0.68, 32, 0.7, 7.7, 0.3, "fruit"),
    ("蓝莓", "Blueberry", 0.65, 57, 0.7, 14.5, 0.3, "fruit"),
    ("西瓜", "Watermelon", 0.75, 30, 0.6, 7.6, 0.2, "fruit"),
    ("哈密瓜", "Hami Melon", 0.72, 34, 0.8, 8.2, 0.1, "fruit"),
    ("猕猴桃", "Kiwi", 0.68, 61, 1.1, 14.7, 0.5, "fruit"),
    ("桃子", "Peach", 0.62, 39, 0.9, 9.5, 0.3, "fruit"),
    ("梨", "Pear", 0.60, 57, 0.4, 15.2, 0.1, "fruit"),
    ("芒果", "Mango", 0.65, 60, 0.8, 15.0, 0.4, "fruit"),
    ("菠萝", "Pineapple", 0.62, 50, 0.5, 13.1, 0.1, "fruit"),
    ("柚子", "Pomelo", 0.58, 38, 0.8, 9.6, 0.1, "fruit"),
    ("樱桃", "Cherry", 0.70, 63, 1.1, 16.0, 0.2, "fruit"),
    ("荔枝", "Lychee", 0.68, 66, 0.8, 16.5, 0.4, "fruit"),
    ("龙眼", "Longan", 0.70, 60, 1.3, 15.5, 0.1, "fruit"),
    ("火龙果", "Dragon Fruit", 0.65, 54, 1.1, 13.0, 0.4, "fruit"),
    ("牛油果", "Avocado", 0.72, 160, 2.0, 8.5, 14.7, "fruit"),
    ("柠檬", "Lemon", 0.58, 29, 1.1, 9.3, 0.3, "fruit"),

    # === 坚果 seeds & nuts ===
    ("花生", "Peanut", 0.55, 567, 25.8, 16.1, 49.2, "nut"),
    ("核桃", "Walnut", 0.45, 654, 15.2, 13.7, 65.2, "nut"),
    ("杏仁", "Almond", 0.52, 579, 21.2, 19.7, 49.9, "nut"),
    ("腰果", "Cashew", 0.56, 553, 18.2, 30.2, 43.9, "nut"),
    ("开心果", "Pistachio", 0.50, 562, 20.2, 27.2, 45.3, "nut"),
    ("瓜子", "Sunflower Seed", 0.40, 582, 19.3, 20.0, 49.8, "nut"),
    ("南瓜子", "Pumpkin Seed", 0.43, 559, 30.2, 10.7, 49.1, "nut"),
    ("芝麻", "Sesame Seed", 0.50, 573, 17.7, 23.5, 49.7, "nut"),

    # === 汤品 soup ===
    ("紫菜蛋花汤", "Seaweed Egg Soup", 0.98, 28, 2.0, 1.5, 1.5, "soup"),
    ("蛋花汤", "Egg Drop Soup", 0.98, 35, 2.5, 1.0, 2.0, "soup"),

    # === 快餐西式 ===
    ("炸鸡腿", "Fried Chicken Drumstick", 0.65, 259, 19.0, 8.0, 16.5, "fastfood"),
    ("薯条", "French Fries", 0.35, 312, 3.4, 41.0, 15.0, "fastfood"),

    # === 炒菜类 stir-fry (single-ingredient focused) ===
    ("炒青菜", "Stir-fried Greens", 0.55, 65, 2.5, 4.0, 4.5, "vegetable"),
    ("炒豆角", "Stir-fried Green Beans", 0.60, 89, 3.5, 12.0, 3.5, "vegetable"),
    ("番茄炒蛋", "Tomato Scrambled Eggs", 0.70, 115, 6.8, 4.2, 7.8, "vegetable"),
]

# Remove duplicates (keep first occurrence, keyed by Chinese name)
seen = set()
unique = []
for item in SEED_FOODS:
    if item[0] not in seen:
        seen.add(item[0])
        unique.append(item)
SEED_FOODS = unique


def seed():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM food_density")
    count = cursor.fetchone()[0]
    if count >= len(SEED_FOODS):
        print(f"Already seeded: {count} foods")
        conn.close()
        return

    cursor.execute("DELETE FROM food_density")
    for name, name_en, density, cal, protein, carbs, fat, category in SEED_FOODS:
        cursor.execute(
            "INSERT INTO food_density (name, name_en, density_g_cm3, calories_per_100g, protein_per_100g, carbs_per_100g, fat_per_100g, category) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (name, name_en, density, cal, protein, carbs, fat, category),
        )

    conn.commit()
    conn.close()
    print(f"Seeded {len(SEED_FOODS)} foods")


if __name__ == "__main__":
    from database import init_db

    init_db()
    seed()
