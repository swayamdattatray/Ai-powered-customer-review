"""
Seed script to add rich test reviews for 'Samsung Galaxy Z Fold8 Ultra 5G'
with Amazon and Flipkart sources, realistic aspect mentions, and calibrated
suspicious review signals.
"""

from database import add_review, get_connection


SAMPLE_REVIEWS = [
    # Camera / Display / Performance Positive Reviews
    ("Samsung Galaxy Z Fold8 Ultra 5G", "The camera takes stunning and crisp photos even in low light. The zoom clarity is incredible.", 5, "Amazon"),
    ("Samsung Galaxy Z Fold8 Ultra 5G", "Superb dynamic AMOLED display with buttery smooth 120Hz refresh rate. Watching videos is fantastic.", 5, "Amazon"),
    ("Samsung Galaxy Z Fold8 Ultra 5G", "Top-notch performance! The Snapdragon processor handles heavy multitasking and gaming without any lag.", 5, "Amazon"),
    ("Samsung Galaxy Z Fold8 Ultra 5G", "Both the inner and outer screens are bright and vivid. The hinge build quality feels very durable and premium.", 5, "Amazon"),
    ("Samsung Galaxy Z Fold8 Ultra 5G", "Great camera sensor and portrait mode. Colors look natural and sharp.", 4, "Flipkart"),
    ("Samsung Galaxy Z Fold8 Ultra 5G", "Fast performance and plenty of RAM. Switching between apps is lightning fast.", 5, "Flipkart"),
    ("Samsung Galaxy Z Fold8 Ultra 5G", "Excellent audio and dual speaker loudness. Sound quality is rich and clear.", 5, "Amazon"),
    ("Samsung Galaxy Z Fold8 Ultra 5G", "The main camera is awesome for outdoor photography. Very clear details.", 4, "Flipkart"),
    ("Samsung Galaxy Z Fold8 Ultra 5G", "Display resolution is unbelievable. One of the best screens ever on a folding device.", 5, "Amazon"),
    ("Samsung Galaxy Z Fold8 Ultra 5G", "Gaming performance is top tier, runs all heavy titles at max settings.", 4, "Flipkart"),
    ("Samsung Galaxy Z Fold8 Ultra 5G", "Build quality is solid with excellent glass and metal finish.", 4, "Amazon"),
    ("Samsung Galaxy Z Fold8 Ultra 5G", "Camera video stabilization is very smooth and reliable.", 4, "Amazon"),

    # Battery & Charging Complaints (Rating 1-2-3)
    ("Samsung Galaxy Z Fold8 Ultra 5G", "Battery drains quickly when both screens are used. Battery backup is insufficient for a full workday.", 2, "Amazon"),
    ("Samsung Galaxy Z Fold8 Ultra 5G", "Charging is slower than expected. Takes over an hour and battery drain is significant during multitasking.", 2, "Amazon"),
    ("Samsung Galaxy Z Fold8 Ultra 5G", "Battery life is disappointing. I have to carry a charger everywhere.", 2, "Flipkart"),
    ("Samsung Galaxy Z Fold8 Ultra 5G", "Good battery during normal usage, but drains fast when gaming.", 3, "Flipkart"),
    ("Samsung Galaxy Z Fold8 Ultra 5G", "Battery backup could be better for such a large device. Fast charging should have been 65W.", 3, "Amazon"),
    ("Samsung Galaxy Z Fold8 Ultra 5G", "Poor battery standby time. SOT is barely 4.5 hours.", 1, "Flipkart"),

    # Price & Value Complaints
    ("Samsung Galaxy Z Fold8 Ultra 5G", "The price is extremely expensive and overpriced for regular consumers. High cost with few accessories.", 2, "Amazon"),
    ("Samsung Galaxy Z Fold8 Ultra 5G", "Very expensive phone. While hardware is good, the cost makes it hard to justify.", 3, "Flipkart"),
    ("Samsung Galaxy Z Fold8 Ultra 5G", "Steep pricing. Premium design but definitely overpriced.", 3, "Amazon"),

    # Heating Complaints
    ("Samsung Galaxy Z Fold8 Ultra 5G", "The phone heats up near the camera module while recording 4K video or fast charging.", 2, "Amazon"),
    ("Samsung Galaxy Z Fold8 Ultra 5G", "Noticeable heating issue during extended gaming sessions.", 2, "Flipkart"),
    ("Samsung Galaxy Z Fold8 Ultra 5G", "Gets warm during navigation and charging.", 3, "Amazon"),

    # Suspicious Reviews (Generic Hype / Promotional)
    ("Samsung Galaxy Z Fold8 Ultra 5G", "Best phone ever! Amazing! Must buy! Totally worth every penny!", 5, "Amazon"),
    ("Samsung Galaxy Z Fold8 Ultra 5G", "100% recommended blindly go for it! Great product great service!", 5, "Amazon"),
    ("Samsung Galaxy Z Fold8 Ultra 5G", "Wow wow wow! Don't think just buy! Revolutionary masterpiece!", 5, "Flipkart"),

    # Suspicious Cluster (Identical template patterns)
    ("Samsung Galaxy Z Fold8 Ultra 5G", "Best phone ever... amazing camera... totally worth it. Must buy for everyone!", 5, "Amazon"),
    ("Samsung Galaxy Z Fold8 Ultra 5G", "Best phone ever... amazing camera... totally worth it. Must buy for everyone!", 5, "Amazon"),
    ("Samsung Galaxy Z Fold8 Ultra 5G", "Best phone ever... amazing camera... totally worth it. Must buy for everyone!", 5, "Amazon")
]


def seed_data():
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM reviews WHERE product_name = 'Samsung Galaxy Z Fold8 Ultra 5G'")
    count = c.fetchone()[0]
    conn.close()

    if count > 0:
        print(f"'Samsung Galaxy Z Fold8 Ultra 5G' already has {count} reviews in database.")
        return

    print("Seeding sample intelligence reviews for 'Samsung Galaxy Z Fold8 Ultra 5G'...")
    for product_name, text, rating, source in SAMPLE_REVIEWS:
        add_review(product_name, text, rating, source)

    print(f"Successfully added {len(SAMPLE_REVIEWS)} reviews!")


if __name__ == "__main__":
    seed_data()
