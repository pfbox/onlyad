"""Seed script to populate the database with sample ads.

Usage:
    uv run python seed.py           # Seed only if DB is empty
    uv run python seed.py --force   # Delete existing ads and re-seed
    uv run python seed.py --add     # Add more ads without deleting existing
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from app.database import engine, Base, SessionLocal
from app.models.ad import Ad
from app.models.vote import Vote
from app.models.view import View

Base.metadata.create_all(bind=engine)

sample_ads = [
    # Tech
    {"title": "Apple iPhone 16 Pro - Titanium", "brand": "Apple", "description": "The most powerful iPhone ever. A17 Pro chip, titanium design, and pro camera system.", "media_url": "/uploads/placeholder.mp4", "media_type": "video", "category": "tech", "tags": "apple,iphone,smartphone,tech,premium"},
    {"title": "Samsung Galaxy S25 Ultra", "brand": "Samsung", "description": "200MP camera. Built-in S Pen. Galaxy AI. The ultimate smartphone experience.", "media_url": "/uploads/placeholder.mp4", "media_type": "video", "category": "tech", "tags": "samsung,galaxy,smartphone,tech,android"},
    {"title": "Amazon Prime - Fast & Free Delivery", "brand": "Amazon", "description": "Get free two-day shipping, Prime Video, and exclusive deals. Join Prime today.", "media_url": "/uploads/placeholder.mp4", "media_type": "video", "category": "tech", "tags": "amazon,shopping,prime,delivery,subscription"},
    {"title": "Google Pixel 9 Pro - AI Camera", "brand": "Google", "description": "Best Take, Magic Eraser, and 7 years of updates. The smartest phone.", "media_url": "/uploads/placeholder.mp4", "media_type": "video", "category": "tech", "tags": "google,pixel,smartphone,ai,camera"},
    {"title": "Microsoft Surface Laptop 7", "brand": "Microsoft", "description": "Copilot+ PC with Snapdragon X Elite. 20 hours battery. AI-powered productivity.", "media_url": "/uploads/placeholder.mp4", "media_type": "video", "category": "tech", "tags": "microsoft,surface,laptop,ai,productivity"},
    {"title": "AirPods Pro 3 - Adaptive Audio", "brand": "Apple", "description": "Next-level noise cancellation. Personalized spatial audio. USB-C charging.", "media_url": "/uploads/placeholder.mp4", "media_type": "video", "category": "tech", "tags": "apple,airpods,audio,wireless,premium"},
    {"title": "Dell XPS 16 - Creator's Dream", "brand": "Dell", "description": "4K OLED display. Intel Core Ultra. NVIDIA RTX graphics. Ultimate creative workstation.", "media_url": "/uploads/placeholder.mp4", "media_type": "video", "category": "tech", "tags": "dell,laptop,creator,4k,workstation"},

    # Sports
    {"title": "New Nike Air Max - Just Do It", "brand": "Nike", "description": "Experience ultimate comfort with the all-new Air Max 2024. Lightweight, responsive cushioning.", "media_url": "/uploads/placeholder.mp4", "media_type": "video", "category": "sports", "tags": "nike,shoes,sports,running,athletic"},
    {"title": "Adidas Ultraboost - Impossible Is Nothing", "brand": "Adidas", "description": "Responsive Boost midsole. Primeknit upper. Run like never before.", "media_url": "/uploads/placeholder.mp4", "media_type": "video", "category": "sports", "tags": "adidas,shoes,sports,running,boost"},
    {"title": "Under Armour Curry 12", "brand": "Under Armour", "description": "Steph Curry's signature shoe. UA Flow cushioning. Game-changing grip.", "media_url": "/uploads/placeholder.mp4", "media_type": "video", "category": "sports", "tags": "under-armour,basketball,shoes,curry,sports"},
    {"title": "Peloton Bike+ - Ride at Home", "brand": "Peloton", "description": "24-inch rotating screen. Auto-resistance. Thousands of live and on-demand classes.", "media_url": "/uploads/placeholder.mp4", "media_type": "video", "category": "sports", "tags": "peloton,fitness,bike,exercise,home"},
    {"title": "The North Face Summit Series", "brand": "The North Face", "description": "Expedition-grade gear. Built for extreme conditions. Never stop exploring.", "media_url": "/uploads/placeholder.mp4", "media_type": "video", "category": "sports", "tags": "north-face,outdoor,hiking,gear,adventure"},

    # Food & Beverage
    {"title": "Coca-Cola - Taste the Feeling", "brand": "Coca-Cola", "description": "Share a Coke with someone you love. The classic taste that brings people together.", "media_url": "/uploads/placeholder.mp4", "media_type": "video", "category": "food", "tags": "coca-cola,drink,refreshment,soda,beverage"},
    {"title": "McDonald's Big Mac", "brand": "McDonald's", "description": "Two all-beef patties, special sauce, lettuce, cheese, pickles, onions on a sesame seed bun.", "media_url": "/uploads/placeholder.mp4", "media_type": "video", "category": "food", "tags": "mcdonalds,burger,fast-food,big-mac"},
    {"title": "Pepsi - That's What I Like", "brand": "Pepsi", "description": "The bold, refreshing taste of Pepsi. Perfect for any occasion.", "media_url": "/uploads/placeholder.mp4", "media_type": "video", "category": "food", "tags": "pepsi,drink,refreshment,soda,beverage"},
    {"title": "Starbucks Pumpkin Spice Latte", "brand": "Starbucks", "description": "The return of fall's favorite drink. Espresso, steamed milk, pumpkin spice flavors.", "media_url": "/uploads/placeholder.mp4", "media_type": "video", "category": "food", "tags": "starbucks,coffee,latte,fall,seasonal"},
    {"title": "Oreo - Stay Playful", "brand": "Oreo", "description": "The world's favorite cookie. Twist, lick, dunk. Which way do you Oreo?", "media_url": "/uploads/placeholder.mp4", "media_type": "video", "category": "food", "tags": "oreo,cookies,snack,chocolate,fun"},
    {"title": "Chipotle - Real Ingredients", "brand": "Chipotle", "description": "Fresh, real food made daily. Build your perfect burrito, bowl, or tacos.", "media_url": "/uploads/placeholder.mp4", "media_type": "video", "category": "food", "tags": "chipotle,mexican,food,fresh,burrito"},

    # Auto
    {"title": "Tesla Model 3 - Electric Revolution", "brand": "Tesla", "description": "0-60 in 3.1 seconds. 358 miles range. The future of driving is here.", "media_url": "/uploads/placeholder.mp4", "media_type": "video", "category": "auto", "tags": "tesla,electric,car,auto,green,sustainable"},
    {"title": "BMW i4 - Electric Gran Coupe", "brand": "BMW", "description": "Up to 536 hp. 300+ mile range. The ultimate electric driving machine.", "media_url": "/uploads/placeholder.mp4", "media_type": "video", "category": "auto", "tags": "bmw,electric,car,luxury,sport"},
    {"title": "Ford F-150 Lightning", "brand": "Ford", "description": "Built Ford Tough. Now electric. Power your home, worksite, and adventures.", "media_url": "/uploads/placeholder.mp4", "media_type": "video", "category": "auto", "tags": "ford,truck,electric,work,power"},
    {"title": "Porsche Taycan Turbo", "brand": "Porsche", "description": "Electric performance redefined. 0-60 in 2.4s. 750 hp. Soul, electrified.", "media_url": "/uploads/placeholder.mp4", "media_type": "video", "category": "auto", "tags": "porsche,electric,sports,luxury,performance"},

    # Entertainment
    {"title": "Netflix - Watch Anywhere", "brand": "Netflix", "description": "Stream the latest movies and shows. Cancel anytime. First month free.", "media_url": "/uploads/placeholder.mp4", "media_type": "video", "category": "entertainment", "tags": "netflix,streaming,entertainment,movies,shows"},
    {"title": "Spotify Premium - Music for Everyone", "brand": "Spotify", "description": "Ad-free music, offline listening, and unlimited skips. Try 3 months free.", "media_url": "/uploads/placeholder.mp4", "media_type": "video", "category": "entertainment", "tags": "spotify,music,streaming,audio,podcast"},
    {"title": "Disney+ - The Best Stories", "brand": "Disney+", "description": "Marvel, Star Wars, Pixar, and more. Stream the stories you love.", "media_url": "/uploads/placeholder.mp4", "media_type": "video", "category": "entertainment", "tags": "disney,streaming,marvel,star-wars,family"},
    {"title": "YouTube Premium", "brand": "YouTube", "description": "No ads. Background play. YouTube Music included. Download videos to watch offline.", "media_url": "/uploads/placeholder.mp4", "media_type": "video", "category": "entertainment", "tags": "youtube,streaming,video,music,premium"},

    # Gaming
    {"title": "Sony PlayStation 5 - Play Has No Limits", "brand": "Sony", "description": "Lightning-fast SSD. Haptic feedback. 3D audio. The next generation of gaming.", "media_url": "/uploads/placeholder.mp4", "media_type": "video", "category": "gaming", "tags": "sony,playstation,ps5,gaming,console"},
    {"title": "Xbox Series X - Power Your Dreams", "brand": "Microsoft", "description": "12 TFLOPS of power. 4K at 120fps. Game Pass Ultimate. The most powerful Xbox.", "media_url": "/uploads/placeholder.mp4", "media_type": "video", "category": "gaming", "tags": "xbox,consoles,gaming,microsoft,game-pass"},
    {"title": "Nintendo Switch OLED", "brand": "Nintendo", "description": "Play at home or on the go. Vibrant 7-inch OLED screen. Mario, Zelda, and more.", "media_url": "/uploads/placeholder.mp4", "media_type": "video", "category": "gaming", "tags": "nintendo,switch,gaming,portable,family"},

    # Travel
    {"title": "Airbnb - Belong Anywhere", "brand": "Airbnb", "description": "Find unique places to stay with local hosts in 190+ countries.", "media_url": "/uploads/placeholder.mp4", "media_type": "video", "category": "travel", "tags": "airbnb,travel,accommodation,rental,experience"},
    {"title": "Booking.com - Dream Destinations", "brand": "Booking.com", "description": "Hotels, flights, car rentals. Plan your perfect trip with free cancellation.", "media_url": "/uploads/placeholder.mp4", "media_type": "video", "category": "travel", "tags": "booking,travel,hotel,flight,rental"},
    {"title": "Expedia - Travel More", "brand": "Expedia", "description": "Bundle flights + hotels and save. 24/7 customer support. Rewards program.", "media_url": "/uploads/placeholder.mp4", "media_type": "video", "category": "travel", "tags": "expedia,travel,flight,hotel,package"},

    # Beauty & Fashion
    {"title": "Dove Real Beauty", "brand": "Dove", "description": "Real beauty is about being comfortable in your own skin. Join the movement.", "media_url": "/uploads/placeholder.mp4", "media_type": "video", "category": "beauty", "tags": "dove,beauty,skincare,confidence,real"},
    {"title": "Fenty Beauty by Rihanna", "brand": "Fenty Beauty", "description": "Beauty for all. 50 shades of foundation. Makeup that celebrates every skin tone.", "media_url": "/uploads/placeholder.mp4", "media_type": "video", "category": "beauty", "tags": "fenty,makeup,beauty,inclusive,rihanna"},
    {"title": "Zara - New Collection", "brand": "Zara", "description": "Discover the latest trends. Sustainable fashion. Express delivery available.", "media_url": "/uploads/placeholder.mp4", "media_type": "video", "category": "fashion", "tags": "zara,fashion,clothing,trendy,style"},
    {"title": "Nike Dri-FIT Training Gear", "brand": "Nike", "description": "Stay dry, stay cool. Dri-FIT technology wicks sweat. Performance redefined.", "media_url": "/uploads/placeholder.mp4", "media_type": "video", "category": "fashion", "tags": "nike,clothing,training,activewear,fitness"},

    # Toys & Kids
    {"title": "LEGO - Build the Future", "brand": "LEGO", "description": "Inspire creativity and imagination. The possibilities are endless.", "media_url": "/uploads/placeholder.mp4", "media_type": "video", "category": "toys", "tags": "lego,toys,creative,building,fun"},
    {"title": "Barbie Dreamhouse 2024", "brand": "Mattel", "description": "The ultimate Barbie experience. 3 stories, 10 rooms, working elevator, pool slide.", "media_url": "/uploads/placeholder.mp4", "media_type": "video", "category": "toys", "tags": "barbie,doll,toys,imagination,fun"},
    {"title": "Hot Wheels Ultimate Garage", "brand": "Hot Wheels", "description": "Multi-level garage with loop track. Stores 100+ cars. Endless racing fun.", "media_url": "/uploads/placeholder.mp4", "media_type": "video", "category": "toys", "tags": "hot-wheels,cars,toys,racing,garage"},
]


def seed(force=False, add=False):
    db = SessionLocal()
    try:
        if force:
            print("Clearing existing data...")
            db.query(Vote).delete()
            db.query(View).delete()
            db.query(Ad).delete()
            db.commit()
            print("Cleared. Seeding fresh...")
        elif add:
            print(f"Adding {len(sample_ads)} more ads...")
        else:
            existing = db.query(Ad).count()
            if existing > 0:
                print(f"Database already has {existing} ads. Use --force to re-seed or --add to add more.")
                return

        added = 0
        for data in sample_ads:
            ad = Ad(**data)
            db.add(ad)
            added += 1

        db.commit()
        total = db.query(Ad).count()
        print(f"Added {added} ads. Total: {total} ads in database.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    force = "--force" in sys.argv
    add = "--add" in sys.argv
    seed(force=force, add=add)