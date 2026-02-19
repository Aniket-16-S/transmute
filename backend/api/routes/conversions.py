import json
from pathlib import Path
import uuid
import hashlib
from fastapi import APIRouter, Request, Depends, HTTPException
from converters import ConverterInterface
from registry import ConverterRegistry
from core import get_settings
from db import ConversionDB, FileDB, ConversionRelationsDB
from ..deps import get_file_db, get_conversion_db, get_conversion_relations_db


router = APIRouter(prefix="/conversions", tags=["conversions"])
registry = ConverterRegistry()
settings = get_settings()
UPLOAD_DIR = settings.upload_dir
TEMP_DIR = settings.tmp_dir
CONVERTED_DIR = settings.output_dir

@router.get("/complete")
def list_conversions(
    file_db: FileDB = Depends(get_file_db),
    conv_db: ConversionDB = Depends(get_conversion_db),
    conv_rel_db: ConversionRelationsDB = Depends(get_conversion_relations_db)
):
    converted_files = conv_db.list_files()
    og_files = file_db.list_files()
    converted_files_dict = {f['id']: f for f in converted_files}
    og_files_dict = {f['id']: f for f in og_files}
    relations = conv_rel_db.list_relations()
    for rel in relations:        
        og_id = rel['original_file_id']
        conv_id = rel['converted_file_id']
        og_files_dict[og_id]['conversion'] = converted_files_dict.get(conv_id)
    return {"conversions": list(og_files_dict.values())}

@router.post("/")
async def create_conversion(
    request: Request,
    file_db: FileDB = Depends(get_file_db),
    conversion_db: ConversionDB = Depends(get_conversion_db),
    conversion_relations_db: ConversionRelationsDB = Depends(get_conversion_relations_db)
):
    body = await request.json()

    # Validate required fields
    original_id = body.get("id")
    output_format = body.get("output_format")
    if not original_id or not output_format:
        raise HTTPException(status_code=400, detail="Missing required fields: 'id' and 'output_format'")

    # Ensure the original file exists in the database
    original_metadata = file_db.get_file_metadata(original_id)
    if original_metadata is None:
        raise HTTPException(status_code=404, detail=f"No file found with id {original_id}")
    
    input_format = original_metadata['media_type']
    
    # Find the appropriate converter for this conversion
    converter_type = registry.get_converter_for_conversion(input_format, output_format)
    if converter_type is None:
        raise HTTPException(
            status_code=400, 
            detail=f"No converter found for {input_format} to {output_format}"
        )

    # Perform the conversion
    converter: ConverterInterface = converter_type(
        f'{UPLOAD_DIR}/{original_id}.{input_format}', 
        f'{TEMP_DIR}/', 
        input_format, 
        output_format
    )
    output_files = converter.convert()
    
    # Move converted file to output directory
    converted_id = str(uuid.uuid4())
    moved_output_file = Path(output_files[0]).rename(f'{CONVERTED_DIR}/{converted_id}.{output_format}')

    # Create metadata for converted file
    converted_metadata = dict(original_metadata)
    converted_metadata['id'] = converted_id
    converted_metadata['media_type'] = output_format
    converted_metadata['extension'] = f".{output_format}"
    converted_metadata['storage_path'] = str(moved_output_file)
    converted_metadata['size_bytes'] = moved_output_file.stat().st_size
    converted_metadata['sha256_checksum'] = hashlib.sha256(moved_output_file.read_bytes()).hexdigest()
    # Remove created_at from original metadata since it is different for converted
    converted_metadata.pop('created_at', None)
    
    # Save to database
    conversion_db.insert_file_metadata(converted_metadata)
    conversion_relations_db.insert_conversion_relation({
        'original_file_id': original_id,
        'converted_file_id': converted_id
    })

    return converted_metadata