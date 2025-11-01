#!/usr/bin/env python3
"""
MCP Server for Statistics Canada - Canadian Public Transit Network Database
Universal Data Access - All 39 GTFS File Types Supported
"""

import asyncio
import json
import sys
from pathlib import Path
from typing import Dict
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from sse_starlette.sse import EventSourceResponse
import uvicorn

sys.path.insert(0, str(Path(__file__).parent))
from data_loader import GTFSDataLoader

DATASET_URL = "https://www150.statcan.gc.ca/n1/pub/23-26-0003/232600032025001-eng.htm"
LICENCE = "Open Government Licence - Canada"
LICENCE_URL = "https://open.canada.ca/en/open-government-licence-canada"

data_loader = GTFSDataLoader()

def get_tools():
    """Define MCP tools - Universal data access"""
    return [
        {
            "name": "describe_dataset",
            "description": "Get dataset overview: total agencies (138), all available file types (39 different GTFS files), and usage instructions.",
            "inputSchema": {
                "type": "object",
                "properties": {},
                "required": []
            }
        },
        {
            "name": "list_agencies",
            "description": "List all 138 transit agencies or search by name/location. Returns agency IDs and file counts.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Optional: search term (e.g., 'Montreal', 'BC', 'Ontario')"}
                },
                "required": []
            }
        },
        {
            "name": "get_agency_files",
            "description": "List all available GTFS files for a specific agency. Shows which of the 39 file types this agency has.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "agency_id": {"type": "string", "description": "Agency ID from list_agencies"}
                },
                "required": ["agency_id"]
            }
        },
        {
            "name": "query_data",
            "description": "Get data from ANY GTFS file for any agency. Supports all 39 file types including: agency, routes, stops, stop_times, trips, shapes, calendar, calendar_dates, feed_info, transfers, fare_attributes, fare_rules, frequencies, and 26 more specialized files. Returns complete data as JSON.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "agency_id": {"type": "string", "description": "Agency ID from list_agencies"},
                    "file_name": {"type": "string", "description": "File name (e.g., 'stops', 'routes', 'transfers.txt'). Can omit .txt extension."},
                    "limit": {"type": "number", "description": "Max records (default 5000, max 100000)"}
                },
                "required": ["agency_id", "file_name"]
            }
        }
    ]

def describe_dataset_tool() -> Dict:
    """Tool 1: Dataset overview"""
    try:
        metadata = data_loader.get_dataset_metadata()
        
        return {"content": [{"type": "text", "text": json.dumps({
            "dataset": metadata['dataset_name'],
            "source": metadata['source'],
            "url": DATASET_URL,
            "licence": LICENCE,
            "licence_url": LICENCE_URL,
            "total_agencies": metadata['total_agencies'],
            "total_file_types": metadata['total_file_types'],
            "all_available_files": metadata['all_available_files'],
            "core_files": metadata['core_files'],
            "usage": metadata['usage'],
            "note": "All 39 GTFS file types are supported. Use get_agency_files to see which files each agency has."
        }, indent=2)}]}
    except Exception as e:
        return {"content": [{"type": "text", "text": json.dumps({
            "error": f"Failed to load metadata: {str(e)}"
        })}]}

def list_agencies_tool(query: str = None) -> Dict:
    """Tool 2: List/search agencies"""
    try:
        agencies = data_loader.search_agencies(query)
        
        if not agencies:
            msg = "No agencies found"
            if query:
                msg += f" matching '{query}'"
            return {"content": [{"type": "text", "text": json.dumps({
                "agencies": [],
                "count": 0,
                "message": msg
            })}]}
        
        results = []
        for agency in agencies[:100]:
            results.append({
                "agency_id": agency.get('folder_name', ''),
                "name": agency.get('agency_name', 'Unknown'),
                "url": agency.get('agency_url', ''),
                "phone": agency.get('agency_phone', ''),
                "available_files": agency.get('available_files', 0)
            })
        
        return {"content": [{"type": "text", "text": json.dumps({
            "agencies": results,
            "count": len(agencies),
            "showing": len(results),
            "message": f"Found {len(agencies)} agencies. Use get_agency_files to see available data files.",
            "attribution": f"Data from Statistics Canada - {LICENCE}"
        }, indent=2)}]}
    
    except Exception as e:
        return {"content": [{"type": "text", "text": json.dumps({
            "error": f"Failed to search agencies: {str(e)}"
        })}]}

def get_agency_files_tool(agency_id: str) -> Dict:
    """Tool 3: List files for an agency"""
    try:
        if not agency_id or not agency_id.strip():
            return {"content": [{"type": "text", "text": json.dumps({
                "error": "agency_id is required"
            })}]}
        
        files = data_loader.get_agency_files(agency_id)
        
        if not files:
            resolved = data_loader.resolve_agency_id(agency_id)
            if not resolved:
                return {"content": [{"type": "text", "text": json.dumps({
                    "error": f"Agency '{agency_id}' not found. Use list_agencies to find valid IDs.",
                    "files": []
                })}]}
        
        return {"content": [{"type": "text", "text": json.dumps({
            "agency_id": agency_id,
            "files": files,
            "count": len(files),
            "message": f"Agency has {len(files)} GTFS files. Use query_data with file_name to get data.",
            "core_files": [f for f in files if f in ['agency.txt', 'routes.txt', 'stops.txt', 'stop_times.txt', 'trips.txt']]
        }, indent=2)}]}
    
    except Exception as e:
        return {"content": [{"type": "text", "text": json.dumps({
            "error": f"Failed to get files: {str(e)}"
        })}]}

def query_data_tool(agency_id: str, file_name: str, limit: int = 5000) -> Dict:
    """Tool 4: Query any GTFS file"""
    try:
        if not agency_id or not agency_id.strip():
            return {"content": [{"type": "text", "text": json.dumps({
                "error": "agency_id is required"
            })}]}
        
        if not file_name or not file_name.strip():
            return {"content": [{"type": "text", "text": json.dumps({
                "error": "file_name is required. Use get_agency_files to see available files."
            })}]}
        
        limit = min(limit if limit else 5000, 100000)
        
        data = data_loader.get_gtfs_data(agency_id, file_name, limit=limit)
        
        if not data:
            resolved = data_loader.resolve_agency_id(agency_id)
            if not resolved:
                return {"content": [{"type": "text", "text": json.dumps({
                    "error": f"Agency '{agency_id}' not found. Use list_agencies first.",
                    "data": [],
                    "count": 0
                })}]}
            else:
                available_files = data_loader.get_agency_files(agency_id)
                return {"content": [{"type": "text", "text": json.dumps({
                    "error": f"File '{file_name}' not found for agency '{resolved}'. Available files: {available_files}",
                    "data": [],
                    "count": 0,
                    "available_files": available_files
                })}]}
        
        return {"content": [{"type": "text", "text": json.dumps({
            "data": data,
            "count": len(data),
            "agency_id": agency_id,
            "file_name": file_name,
            "limit_applied": limit,
            "message": f"Retrieved {len(data)} records" + (f" (limited to {limit})" if len(data) == limit else ""),
            "attribution": f"Data from Statistics Canada - {LICENCE}"
        }, indent=2)}]}
    
    except Exception as e:
        return {"content": [{"type": "text", "text": json.dumps({
            "error": f"Query failed: {str(e)}"
        })}]}

async def health(request):
    """Health check"""
    count = len(data_loader.get_all_agency_folders())
    metadata = data_loader.get_dataset_metadata()
    return JSONResponse({
        "status": "healthy",
        "dataset": "Canadian Public Transit Network Database",
        "source": "Statistics Canada",
        "agencies": count,
        "file_types": metadata['total_file_types'],
        "tools": 4,
        "version": "1.0.0",
        "licence": LICENCE
    })

async def sse_endpoint(request):
    """SSE endpoint"""
    async def event_generator():
        yield {
            "event": "message",
            "data": json.dumps({
                "jsonrpc": "2.0",
                "method": "notifications/initialized",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {
                        "name": "statcan-transit",
                        "version": "1.0.0"
                    },
                    "capabilities": {"tools": {}}
                }
            })
        }
        try:
            while True:
                await asyncio.sleep(30)
        except asyncio.CancelledError:
            pass
    return EventSourceResponse(event_generator())

async def mcp_handler(request):
    """MCP JSON-RPC handler"""
    try:
        data = await request.json()
        method = data.get("method")
        params = data.get("params", {})
        request_id = data.get("id")
        
        if method == "initialize":
            result = {
                "protocolVersion": "2024-11-05",
                "serverInfo": {
                    "name": "statcan-transit",
                    "version": "1.0.0"
                },
                "capabilities": {"tools": {}}
            }
        elif method == "tools/list":
            result = {"tools": get_tools()}
        elif method == "tools/call":
            tool_name = params.get("name")
            tool_args = params.get("arguments", {})
            
            if tool_name == "describe_dataset":
                result = describe_dataset_tool()
            elif tool_name == "list_agencies":
                result = list_agencies_tool(tool_args.get("query"))
            elif tool_name == "get_agency_files":
                result = get_agency_files_tool(tool_args.get("agency_id", ""))
            elif tool_name == "query_data":
                result = query_data_tool(
                    tool_args.get("agency_id", ""),
                    tool_args.get("file_name", ""),
                    tool_args.get("limit", 5000)
                )
            else:
                return JSONResponse({
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
                })
        else:
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"}
            })
        
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        })
    except Exception as e:
        return JSONResponse({
            "jsonrpc": "2.0",
            "error": {"code": -32603, "message": str(e)}
        }, status_code=500)

app = Starlette(
    debug=False,
    routes=[
        Route("/health", health),
        Route("/sse", sse_endpoint),
        Route("/sse", mcp_handler, methods=["POST"]),
        Route("/", mcp_handler, methods=["POST"]),
    ],
)

if __name__ == "__main__":
    print("=" * 80)
    print("Statistics Canada Transit MCP Server v1.0.0")
    print("Universal GTFS Data Access - All 39 File Types Supported")
    print("=" * 80)
    print(f"Dataset: Canadian Public Transit Network Database")
    print(f"Source: Statistics Canada")
    print(f"Licence: {LICENCE}")
    print("=" * 80)
    print("Loading agencies...")
    count = len(data_loader.get_all_agency_folders())
    metadata = data_loader.get_dataset_metadata()
    print(f"✓ Loaded {count} transit agencies")
    print(f"✓ {metadata['total_file_types']} different GTFS file types available")
    print(f"✓ 4 MCP tools: describe_dataset, list_agencies, get_agency_files, query_data")
    print(f"✓ Server ready on http://0.0.0.0:3000")
    print("=" * 80)
    uvicorn.run(app, host="0.0.0.0", port=3000)
