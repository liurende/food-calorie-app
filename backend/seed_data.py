import sqlite3
from database import get_db, DB_PATH

SEED_FOODS = [
    # 主食 staples
    ("白米饭", "White Rice", 0.85, 116, 2.6, 25.9, 0.3, "staple"),
    ("糙米饭", "Brown Rice", 0.85, 123, 2.7, 25.6, 0.9, "staple"),
    ("馒头", "Steamed Bun", 0.45, 223, 7.0, 44.2, 1.1, "staple"),
    ("面条(煮)", "Noodles (cooked)", 0.95, 138, 4.5, 28.5, 1.0, "staple"),
    ("全麦面包", "Whole Wheat Bread", 0.25, 247, 13.0, 41.0, 3.4, "staple"),
    ("白面包", "White Bread", 0.22, 265, 9.0, 49.0, 3.2, "staple"),
    ("玉米", "Corn", 0.72, 112, 4.0, 22.8, 1.5, "staple"),
    ("红薯", "Sweet Potato", 0.65, 86, 1.6, 20.1, 0.1, "staple"),
    ("土豆", "Potato", 0.65, 77, 2.0, 17.5, 0.1, "staple"),
    ("小米粥", "Millet Porridge", 0.98, 46, 1.4, 8.4, 0.7, "staple"),
    ("凉皮", "Cold Noodles", 0.90, 140, 4.0, 25.0, 2.0, "staple"),
    ("蔬菜沙拉", "Vegetable Salad", 0.40, 45, 1.5, 5.0, 2.5, "vegetable"),

    # 肉类 meat
    ("鸡胸肉(熟)", "Chicken Breast (cooked)", 0.98, 165, 31.0, 0.0, 3.6, "meat"),
    ("鸡腿肉(熟)", "Chicken Thigh (cooked)", 1.02, 209, 25.9, 0.0, 10.9, "meat"),
    ("猪里脊(熟)", "Pork Tenderloin (cooked)", 1.05, 143, 28.5, 0.0, 3.5, "meat"),
    ("猪五花肉(熟)", "Pork Belly (cooked)", 0.92, 518, 9.3, 0.0, 52.3, "meat"),
    ("牛肉(瘦,熟)", "Beef Lean (cooked)", 1.10, 250, 27.0, 0.0, 15.0, "meat"),
    ("羊肉(熟)", "Lamb (cooked)", 1.05, 294, 24.6, 0.0, 21.0, "meat"),
    ("鸭肉(熟)", "Duck (cooked)", 1.00, 337, 19.0, 0.1, 28.0, "meat"),

    # 水产 seafood
    ("三文鱼(熟)", "Salmon (cooked)", 0.98, 208, 20.4, 0.0, 13.4, "seafood"),
    ("虾仁(熟)", "Shrimp (cooked)", 0.95, 99, 24.0, 0.2, 0.3, "seafood"),
    ("带鱼(熟)", "Hairtail (cooked)", 1.00, 172, 18.0, 0.0, 10.8, "seafood"),

    # 蔬菜 vegetables
    ("炒青菜", "Stir-fried Greens", 0.55, 65, 2.5, 4.0, 4.5, "vegetable"),
    ("番茄炒蛋", "Tomato Scrambled Eggs", 0.70, 115, 6.8, 4.2, 7.8, "vegetable"),
    ("西兰花(熟)", "Broccoli (cooked)", 0.45, 34, 2.8, 6.6, 0.4, "vegetable"),
    ("黄瓜", "Cucumber", 0.60, 16, 0.7, 2.9, 0.1, "vegetable"),
    ("胡萝卜(熟)", "Carrot (cooked)", 0.55, 41, 0.9, 9.6, 0.2, "vegetable"),
    ("菠菜(熟)", "Spinach (cooked)", 0.40, 28, 2.6, 3.8, 0.3, "vegetable"),
    ("炒豆角", "Stir-fried Green Beans", 0.60, 89, 3.5, 12.0, 3.5, "vegetable"),

    # 豆制品 tofu
    ("麻婆豆腐", "Mapo Tofu", 0.90, 120, 9.0, 5.0, 8.0, "tofu"),
    ("炒豆腐", "Fried Tofu", 0.65, 156, 13.0, 5.0, 10.0, "tofu"),

    # 汤类 soup
    ("鸡蛋汤", "Egg Drop Soup", 0.98, 35, 2.5, 1.0, 2.0, "soup"),
    ("紫菜蛋花汤", "Seaweed Egg Soup", 0.98, 28, 2.0, 1.5, 1.5, "soup"),

    # 中式菜肴 Chinese dishes
    ("宫保鸡丁", "Kung Pao Chicken", 0.75, 128, 16.0, 5.8, 4.5, "dish"),
    ("红烧肉", "Braised Pork Belly", 0.88, 462, 8.1, 5.4, 45.0, "dish"),
    ("糖醋里脊", "Sweet and Sour Pork", 0.72, 215, 15.0, 22.0, 8.0, "dish"),
    ("鱼香肉丝", "Yu Xiang Shredded Pork", 0.70, 156, 13.0, 8.0, 8.5, "dish"),
    ("回锅肉", "Twice-Cooked Pork", 0.78, 328, 18.0, 5.0, 26.0, "dish"),
    ("水煮鱼", "Boiled Fish", 0.75, 145, 18.5, 2.0, 7.5, "dish"),
    ("酸菜鱼", "Pickled Fish", 0.80, 130, 17.0, 3.0, 6.0, "dish"),
    ("地三鲜", "Di San Xian", 0.60, 120, 2.0, 15.0, 6.5, "dish"),
    ("干煸四季豆", "Dry-fried Green Beans", 0.55, 110, 3.5, 10.0, 7.0, "dish"),

    # 蛋类 eggs
    ("炒鸡蛋", "Scrambled Eggs", 0.55, 196, 13.6, 1.5, 14.8, "egg"),
    ("煮鸡蛋", "Boiled Egg", 0.90, 155, 12.6, 1.1, 10.6, "egg"),

    # 快餐 fast food
    ("炸鸡腿", "Fried Chicken Drumstick", 0.65, 259, 19.0, 8.0, 16.5, "fastfood"),
    ("薯条", "French Fries", 0.35, 312, 3.4, 41.0, 15.0, "fastfood"),
    ("汉堡", "Hamburger", 0.42, 257, 12.9, 26.6, 11.6, "fastfood"),
    ("披萨", "Pizza", 0.50, 266, 11.0, 33.0, 10.0, "fastfood"),

    # 水果 fruits
    ("苹果", "Apple", 0.60, 52, 0.3, 13.8, 0.2, "fruit"),
    ("香蕉", "Banana", 0.65, 89, 1.1, 22.8, 0.3, "fruit"),
    ("橙子", "Orange", 0.72, 47, 0.9, 11.8, 0.1, "fruit"),
    ("葡萄", "Grapes", 0.80, 69, 0.7, 18.1, 0.2, "fruit"),
]


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
