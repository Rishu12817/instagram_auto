import psycopg2
import sys
import os
import logging
from datetime import datetime
# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import config

print(config.DB_CONFIG)

# exit()
table_name = "dim_lookup"
# table_name = "insta_auto"
def insert_instagram_post(post_profile_name, post_active_url, post_caption):
    try:
        # Connect to Greenplum (PostgreSQL)
        conn = psycopg2.connect(**config.DB_CONFIG)
        cursor = conn.cursor()
        # print("Connecting to Greenplum Database")
        # SQL query to insert the data
        query = f"""
        INSERT INTO {table_name} (username, photo_url, caption, posted)
        VALUES (%s, %s, %s, %s)
        """

        # Execute query
        cursor.execute(query, (post_profile_name, post_active_url, post_caption, "pending"))
        conn.commit()  # Save changes

        print("✅ Data inserted successfully!")

    except Exception as e:
        print("❌ Error:", e)
    finally:
        if conn:
            cursor.close()
            conn.close()
            print("✅ Script completed successfully! ✅")

# # Example Usage
# user = "example_user"
# driver_current_url = "https://www.instagram.com/p/example_post/"
# caption = """Your true self is the one that shines the most. 🩵

# Fashion creator @__y__i__mii (Yoshimi Nakaumura) mixes and matches colorful vintage looks as a form of self-expression — creating outfits that make every day more enjoyable when she wears them.

# “Through my content, I want to convey the message that it’s important to value your individuality. I feel that by showing my true self, I can empathize with and connect with my followers, and make them smile and give them energy.”

# Photos by @__y__i__mii"""

# insert_instagram_post(user, driver_current_url, caption)
