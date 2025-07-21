from fastapi import APIRouter, Depends, HTTPException
from app.core.supabase_client import get_supabase_client
from supabase import Client

router = APIRouter()

@router.get("/schema", response_model=dict)
async def get_database_schema(supabase: Client = Depends(get_supabase_client)):
    """
    Retrieves the schema of the public tables in the database by calling the
    get_schema_details RPC function.
    """
    try:
        response = await supabase.rpc('get_schema_details').execute()
        
        if response.data:
            # Process the data into a more readable format
            schema = {}
            for row in response.data:
                table = row['table_name']
                if table not in schema:
                    schema[table] = []
                schema[table].append({
                    "column_name": row['column_name'],
                    "data_type": row['data_type']
                })
            return {"schema": schema}
        else:
            return {"message": "Could not retrieve schema. The RPC function 'get_schema_details' may not be configured correctly or the database is empty."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))