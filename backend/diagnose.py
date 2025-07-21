import asyncio
from app.core.supabase_client import get_supabase_client

async def diagnose_schema():
    """Connects to Supabase and prints the schema of all tables."""
    print("Connecting to Supabase to diagnose schema...")
    try:
        supabase = get_supabase_client()
        if not supabase:
            print("Failed to get Supabase client.")
            return

        # The Supabase Python client doesn't have a direct schema inspection method.
        # We can, however, list tables by querying the 'information_schema'.
        # This is a more advanced approach. A simpler way is to just try to query
        # a few known tables to see if they exist.

        print("\nAttempting to query known tables...")

        tables_to_check = [
            "organizations",
            "africa_intelligence_feed",
            "funding_opportunities_backup",
            "users" # A common table name
        ]

        for table in tables_to_check:
            try:
                print(f"Querying table: {table}...")
                # We just need to know if it exists, so we select one row.
                response = await supabase.table(table).select("id").limit(1).execute()
                if response.data:
                    print(f"  -> Success! Table '{table}' exists.")
                    # If we want to see columns, we could inspect response.data[0].keys()
                    # but for now, just confirming existence is enough.
                else:
                    # This could mean the table is empty, not that it doesn't exist.
                    # A more robust check is needed for tables that might be empty.
                    print(f"  -> Query executed, but no data returned for '{table}'. It might be empty.")

            except Exception as e:
                print(f"  -> Failed to query table '{table}'. Error: {e}")

    except Exception as e:
        print(f"An error occurred during schema diagnosis: {e}")

if __name__ == "__main__":
    asyncio.run(diagnose_schema())
