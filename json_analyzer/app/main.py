from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
import json
import httpx
import aiofiles
import chardet
import logging
import tempfile
import os
from typing import Optional
import io

from .models import *
from .optimized_analyzer import OptimizedBigDataAnalyzer
from .core import logger, AnalysisError, MemoryLimitExceeded, config

app = FastAPI(
    title="JSON Metadata Analyzer",
    description="FastAPI service for analyzing JSON data and extracting metadata for AI agents",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_FILE_SIZE = 5 * 1024 * 1024 * 1024  # 5GB
STREAMING_THRESHOLD = 50 * 1024 * 1024  # 50MB threshold for streaming
TIMEOUT_SECONDS = 1800  # 30 minutes for large files
MAX_MEMORY_USAGE = 2 * 1024 * 1024 * 1024  # 2GB memory limit

def get_analyzer() -> OptimizedBigDataAnalyzer:
    """Dependency to get optimized analyzer instance"""
    return OptimizedBigDataAnalyzer()

@app.post("/analyze-json", response_model=AnalysisResponse)
async def analyze_json_file(
    file: UploadFile = File(...),
    analyzer: OptimizedBigDataAnalyzer = Depends(get_analyzer)
):
    """Analyze JSON file uploaded via multipart/form-data"""

    # Validate file type
    if not file.filename.endswith(('.json', '.jsonl')):
        raise HTTPException(status_code=400, detail="File must be JSON or JSONL format")

    # Stream large files directly without loading into memory
    file_size = 0

    # Create temporary file for streaming processing
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.json', delete=False) as temp_file:
        temp_file_path = temp_file.name

        # Stream file content to disk
        while chunk := await file.read(8192):  # 8KB chunks
            file_size += len(chunk)
            if file_size > MAX_FILE_SIZE:
                os.unlink(temp_file_path)
                raise HTTPException(status_code=413, detail=f"File too large. Maximum size: {MAX_FILE_SIZE/1024/1024/1024}GB")
            temp_file.write(chunk)

    try:
        logger.info(f"Starting analysis of file: {file.filename}, size: {file_size / 1024 / 1024:.1f}MB")

        # Use optimized streaming analysis
        result = analyzer.analyze_json_structure(temp_file_path)
        result.analysis_metadata.source_info.file_size_mb = file_size / 1024 / 1024

        logger.info(f"Analysis completed successfully. Processed {result.analysis_metadata.source_info.total_records} records")
        return result

    except MemoryLimitExceeded as e:
        logger.error(f"Memory limit exceeded during file analysis: {e}")
        os.unlink(temp_file_path)
        raise HTTPException(status_code=413, detail="File too large for available memory. Try with a smaller file.")

    except AnalysisError as e:
        logger.error(f"Analysis error for file {file.filename}: {e}")
        os.unlink(temp_file_path)
        raise HTTPException(status_code=400, detail=f"Analysis failed: {str(e)}")

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error for file {file.filename}: {e}")
        os.unlink(temp_file_path)
        raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(e)}")

    except Exception as e:
        logger.error(f"Unexpected error during file analysis: {e}", exc_info=True)
        os.unlink(temp_file_path)
        raise HTTPException(status_code=500, detail="Internal server error during analysis")
    finally:
        # Clean up temp file if it still exists
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

@app.post("/analyze-json-url", response_model=AnalysisResponse)
async def analyze_json_url(
    request: UrlRequest,
    analyzer: OptimizedBigDataAnalyzer = Depends(get_analyzer)
):
    """Analyze JSON data from URL"""

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            response = await client.get(str(request.url))
            response.raise_for_status()

            # Check content size
            content_length = len(response.content)
            if content_length > MAX_FILE_SIZE:
                raise HTTPException(status_code=413, detail=f"Content too large. Maximum size: {MAX_FILE_SIZE/1024/1024}MB")

            # Detect encoding if not provided
            encoding = request.encoding
            if not encoding:
                encoding_result = chardet.detect(response.content)
                encoding = encoding_result.get('encoding', 'utf-8')

            # Decode content
            text_content = response.content.decode(encoding)

            # Parse JSON
            try:
                data = json.loads(text_content)
            except json.JSONDecodeError:
                # Try JSONL format
                json_objects = []
                for line in text_content.strip().split('\n'):
                    if line.strip():
                        json_objects.append(json.loads(line))
                data = json_objects

            # Analyze
            if content_length > 10 * 1024 * 1024:  # 10MB threshold for streaming
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                    json.dump(data, temp_file)
                    temp_file_path = temp_file.name

                try:
                    result = analyzer.analyze_json_structure(temp_file_path)
                    result.analysis_metadata.source_info.source_type = SourceType.URL
                    result.analysis_metadata.source_info.file_size_mb = content_length / 1024 / 1024
                    return result
                finally:
                    os.unlink(temp_file_path)
            else:
                result = analyzer.analyze_json_structure(data)
                result.analysis_metadata.source_info.source_type = SourceType.URL
                result.analysis_metadata.source_info.file_size_mb = content_length / 1024 / 1024
                return result

    except httpx.HTTPError as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch URL: {str(e)}")
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON format: {str(e)}")
    except Exception as e:
        logger.error(f"URL analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/analyze-json-data", response_model=AnalysisResponse)
async def analyze_json_data(
    request: DirectDataRequest,
    analyzer: OptimizedBigDataAnalyzer = Depends(get_analyzer)
):
    """Analyze JSON data sent directly in request body"""

    try:
        # Estimate data size
        data_str = json.dumps(request.data)
        data_size = len(data_str.encode('utf-8'))

        if data_size > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail=f"Data too large. Maximum size: {MAX_FILE_SIZE/1024/1024/1024}GB")

        # Analyze
        result = analyzer.analyze_json_structure(request.data)
        result.analysis_metadata.source_info.source_type = SourceType.DIRECT_DATA
        result.analysis_metadata.source_info.file_size_mb = data_size / 1024 / 1024
        return result

    except Exception as e:
        logger.error(f"Direct data analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/analyze-json-file-path")
async def analyze_json_file_path(
    file_path: str,
    analyzer: OptimizedBigDataAnalyzer = Depends(get_analyzer)
):
    """Analyze JSON file from server file system (for testing with large files)"""

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail=f"File not found: {file_path}")

    # Security check - only allow files from jsonfiles directory
    if not os.path.abspath(file_path).startswith(os.path.abspath("../jsonfiles")):
        raise HTTPException(status_code=403, detail="Access denied. Only files from jsonfiles directory allowed")

    try:
        file_size = os.path.getsize(file_path)
        logger.info(f"Analyzing file: {file_path}, size: {file_size/1024/1024:.2f}MB")

        result = analyzer.analyze_json_structure(file_path)
        result.analysis_metadata.source_info.source_type = SourceType.FILE_UPLOAD
        result.analysis_metadata.source_info.file_size_mb = file_size / 1024 / 1024
        return result

    except Exception as e:
        logger.error(f"File analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "JSON Metadata Analyzer"}

@app.get("/")
async def root():
    """Root endpoint with service information"""
    return {
        "service": "JSON Metadata Analyzer",
        "version": "1.0.0",
        "description": "FastAPI service for analyzing JSON data and extracting metadata for AI agents",
        "endpoints": {
            "POST /analyze-json": "Upload JSON file for analysis",
            "POST /analyze-json-url": "Analyze JSON from URL",
            "POST /analyze-json-data": "Analyze JSON data directly",
            "GET /health": "Health check",
            "GET /docs": "Interactive API documentation"
        },
        "limits": {
            "max_file_size_gb": MAX_FILE_SIZE / 1024 / 1024 / 1024,
            "streaming_threshold_mb": STREAMING_THRESHOLD / 1024 / 1024,
            "timeout_seconds": TIMEOUT_SECONDS,
            "max_memory_usage_gb": MAX_MEMORY_USAGE / 1024 / 1024 / 1024
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)