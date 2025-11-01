# Technical Reference - Statistics Canada Transit MCP Server

**Complete technical documentation for 48-Hour Challenge submission**

## 📋 Official Dataset Information

- **Dataset Name**: Canadian Public Transit Network Database
- **Source**: Statistics Canada - Urban Data Lab
- **Release Date**: January 31, 2025
- **Correction Date**: May 7, 2025
- **URL**: https://www150.statcan.gc.ca/n1/pub/23-26-0003/232600032025001-eng.htm
- **License**: Open Government License - Canada
- **License URL**: https://open.canada.ca/en/open-government-licence-canada
- **Total Agencies**: 138 (confirmed from data_sources.csv)
- **Dataset Size**: 424 MB (compressed zip)

## 📊 Dataset Contents

The dataset includes:
- **GTFS files**: 138 agency folders with stops, routes, trips, schedules
- **Geospatial data**: stops_and_routes.gpkg (national dataset)
- **Metadata**: data_sources.csv, validation_summary.csv
- **Documentation**: Metadata_Report_Canadian_Public_Transit_Network.pdf

## 🏗️ System Architecture

```
┌─────────────────┐
│  ChatGPT Desktop│
└────────┬────────┘
         │ HTTPS/SSE
         ▼
┌─────────────────┐
│ Tailscale Funnel│
│ (your-machine.  │
│  tailnet.ts.net)│
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Docker Container│
│ Port 3000       │
│  ┌────────────┐ │
│  │ Uvicorn    │ │
│  │ Starlette  │ │
│  │ MCP Server │ │
│  └──────┬─────┘ │
│         │       │
│  ┌──────▼─────┐ │
│  │Data Loader │ │
│  │138 Agencies│ │
│  └──────┬─────┘ │
└─────────┼───────┘
          │
    ┌─────▼──────┐
    │ GTFS Files │
    │138 Agencies│
    │ 50k+ Stops │
    │ 2k+ Routes │
    └────────────┘
```

## 📋 System Requirements

- Linux server (tested on OMV/Debian)
- Docker 20.10+
- Docker Compose 1.29+
- Python 3.11 (in container)
- 2GB RAM minimum
- 1GB disk space (500MB for data)
- Tailscale for HTTPS access


## 📁 Complete File Contents

### File 1: `/opt/statcan-transit-mcp/statcan_transit_mcp/__init__.py`

```python
"""Statistics Canada Transit MCP Server - Challenge Submission"""
__version__ = "1.0.0"
```

### File 2: `/opt/statcan-transit-mcp/statcan_transit_mcp/data_loader.py`

See current implementation in your server. Key features:
- Loads GTFS data from 138 agency folders
- Auto-generates agency aliases (e.g., "stm" → "societe_transport_montreal")
- Provides dataset metadata (provinces, data types, schemas)
- Handles missing files gracefully
- Supports all GTFS file types

### File 3: `/opt/statcan-transit-mcp/statcan_transit_mcp/http_server.py`

See current implementation in your server. Key features:
- 3 MCP tools: describe_dataset, list_agencies, query_data
- HTTP/SSE transport for ChatGPT
- JSON-RPC 2.0 protocol
- Proper error handling with helpful messages
- Attribution in all responses

### File 4: `/opt/statcan-transit-mcp/pyproject.toml`

```toml
[project]
name = "statcan-transit-mcp"
version = "1.0.0"
description = "MCP Server for Statistics Canada Transit Data - Challenge Submission"
requires-python = ">=3.10"
dependencies = [
    "mcp>=0.9.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

### File 5: `/opt/statcan-transit-mcp/Dockerfile`

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY statcan_transit_mcp/ /app/statcan_transit_mcp/
COPY pyproject.toml /app/

RUN pip install --no-cache-dir -e .

RUN mkdir -p /app/data /app/cache

EXPOSE 3000

CMD ["python", "-m", "statcan_transit_mcp.http_server"]
```

### File 6: `/opt/statcan-transit-mcp/docker-compose.yml`

```yaml
version: '3.8'

services:
  statcan-transit-mcp:
    build: .
    container_name: statcan-transit-mcp
    restart: unless-stopped
    ports:
      - "3000:3000"
    volumes:
      - ./data:/app/data
      - ./cache:/app/cache
    environment:
      - FASTMCP_LOG_LEVEL=INFO
    stdin_open: true
    tty: true
```


## 🔧 MCP Tools Implementation (4 Tools)

### Tool 1: `describe_dataset`

**Purpose**: Browse/discover tool - provides complete dataset overview

**Input**: None required

**Output**:
- Dataset name, source, URL, license
- Total agencies (138)
- Total file types (39)
- List of all 39 available file types
- Core files that all agencies have
- Usage instructions

**Example Response**:
```json
{
  "dataset": "Canadian Public Transit Network Database",
  "source": "Statistics Canada",
  "total_agencies": 138,
  "total_file_types": 39,
  "all_available_files": ["agency.txt", "routes.txt", ...],
  "core_files": ["agency.txt", "routes.txt", "stops.txt", "stop_times.txt", "trips.txt"]
}
```

### Tool 2: `list_agencies`

**Purpose**: List or search transit agencies

**Input**:
- `query` (optional): Search term to filter agencies

**Output**:
- Array of agencies with ID, name, URL, phone, file count
- Total count
- Attribution

**Example Response**:
```json
{
  "agencies": [
    {
      "agency_id": "societe_transport_montreal",
      "name": "Société de transport de Montréal",
      "url": "http://www.stm.info",
      "phone": "",
      "available_files": 9
    }
  ],
  "count": 1
}
```

### Tool 3: `get_agency_files` (NEW!)

**Purpose**: Discover which GTFS files are available for a specific agency

**Input**:
- `agency_id` (required): Agency ID from list_agencies

**Output**:
- List of all .txt files available
- File count
- Core files vs optional files

**Example Response**:
```json
{
  "agency_id": "societe_transport_montreal",
  "files": ["agency.txt", "calendar.txt", "calendar_dates.txt", "feed_info.txt", "routes.txt", "shapes.txt", "stops.txt", "stop_times.txt", "trips.txt"],
  "count": 9,
  "core_files": ["agency.txt", "routes.txt", "stops.txt", "stop_times.txt", "trips.txt"]
}
```

### Tool 4: `query_data` (UNIVERSAL ACCESS)

**Purpose**: Query data from ANY of the 39 GTFS file types

**Input**:
- `agency_id` (required): Agency folder name
- `file_name` (required): Any GTFS file (can omit .txt extension)
- `limit` (optional): Max records (default 5000, max 100000)

**Supports ALL 39 File Types**: agency, routes, stops, stop_times, trips, shapes, calendar, calendar_dates, feed_info, transfers, fare_attributes, fare_rules, frequencies, directions, timetables, pathways, levels, and 22 more!

**Output**:
- Array of data records
- Count
- Attribution
- Available files if requested file doesn't exist

**Example Response**:
```json
{
  "data": [
    {
      "stop_id": "43",
      "stop_name": "Station Angrignon",
      "stop_lat": "45.446466",
      "stop_lon": "-73.603118"
    }
  ],
  "count": 1,
  "agency_id": "societe_transport_montreal",
  "file_name": "stops.txt"
}
```


## 🚀 Complete Deployment Steps

### Step 1: Prepare Server

```bash
ssh root@your-omv-server
mkdir -p /opt/statcan-transit-mcp
cd /opt/statcan-transit-mcp
```

### Step 2: Download Dataset

```bash
mkdir -p data
cd data
wget "https://www150.statcan.gc.ca/n1/en/pub/23-26-0003/2025001/zip/canadian_public_transit_network_database.zip?st=52TbFElb" -O canadian_public_transit_network_database.zip
apt install unzip -y
unzip canadian_public_transit_network_database.zip
cd ..
```

**Note**: The zip contains 138 agency folders in `gtfs/` directory.

### Step 3: Create Directory Structure

```bash
mkdir -p statcan_transit_mcp
mkdir -p cache
```

### Step 4: Create All Files

Copy the file contents from sections above into their respective locations.

### Step 5: Build and Start

```bash
docker-compose build --no-cache
docker-compose up -d
```

### Step 6: Verify

```bash
# Check container
docker-compose ps

# Check logs
docker-compose logs

# Test health
curl http://localhost:3000/health

# Test tools list
curl -X POST http://localhost:3000/ -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
```

### Step 7: Enable Tailscale Funnel

```bash
nohup tailscale funnel 3000 &
tailscale status
```

Your SSE URL: `https://your-machine-name.your-tailnet.ts.net/sse`

### Step 8: Connect ChatGPT Desktop

1. Open ChatGPT Desktop
2. Settings → MCP
3. Add new server
4. URL: `https://your-machine-name.your-tailnet.ts.net/sse`
5. Authentication: None
6. Save and enable

### Step 9: Test in ChatGPT

- "What tools do you have from Statistics Canada Transit?"
- "Describe the dataset"
- "How many agencies are in Montreal?"
- "Get 5 stops from STM"


## 📊 GTFS Data Structure

### Core Files (All 138 Agencies Have These)

1. **stops.txt** - Transit stop locations
   - Columns: stop_id, stop_code, stop_name, stop_lat, stop_lon, wheelchair_boarding
   - ~50,000+ stops across all agencies

2. **routes.txt** - Transit routes
   - Columns: route_id, route_short_name, route_long_name, route_type, route_color
   - ~2,000+ routes across all agencies
   - route_type: 0=Tram, 1=Subway, 2=Rail, 3=Bus, 4=Ferry

3. **trips.txt** - Individual trips
   - Columns: trip_id, route_id, service_id, trip_headsign, direction_id, shape_id

4. **stop_times.txt** - Arrival/departure times
   - Columns: trip_id, stop_id, arrival_time, departure_time, stop_sequence
   - Largest file (can be 100MB+ for major agencies)

5. **calendar.txt** - Service schedules
   - Columns: service_id, monday-sunday (0/1), start_date, end_date

6. **shapes.txt** - Route geographic paths
   - Columns: shape_id, shape_pt_lat, shape_pt_lon, shape_pt_sequence

### Optional Files (Some Agencies)

7. **agency.txt** - Agency information
   - Columns: agency_id, agency_name, agency_url, agency_timezone, agency_phone

8. **feed_info.txt** - Dataset metadata
   - Columns: feed_publisher_name, feed_lang, feed_start_date, feed_end_date

9. **calendar_dates.txt** - Service exceptions
   - Columns: service_id, date, exception_type

### TransLink Extras

10. **transfers.txt** - Transfer rules
11. **directions.txt** - Direction names
12. **signup_periods.txt** - Service periods

## 📈 Performance Metrics

- **Startup time**: ~2-3 seconds
- **Agency search**: <100ms
- **Data query (1000 records)**: <500ms
- **Data query (10000 records)**: <2s
- **Memory usage**: ~200MB
- **Disk usage**: ~500MB (data)

## 🔐 Security & Privacy

- ✅ No authentication required (public data)
- ✅ Read-only operations
- ✅ No user tracking or analytics
- ✅ No PII collection
- ✅ Tailscale provides network security
- ✅ HTTPS via Tailscale Funnel

## 🐛 Common Issues & Solutions

**Issue**: Container won't start
```bash
docker-compose logs
# Check for port conflicts or missing files
```

**Issue**: ChatGPT can't connect
- Verify Tailscale Funnel: `tailscale status`
- Check URL format: `https://machine-name.tailnet.ts.net/sse`
- Restart ChatGPT Desktop completely

**Issue**: Tools not showing
- Rebuild: `docker-compose down && docker-compose build --no-cache && docker-compose up -d`
- Disconnect and reconnect in ChatGPT

**Issue**: Query returns no data
- Check agency_id is correct (use list_agencies first)
- Some agencies don't have all file types
- Increase limit parameter

## �� References

- [MCP Specification](https://modelcontextprotocol.io/)
- [GTFS Reference](https://gtfs.org/)
- [Statistics Canada Dataset](https://www150.statcan.gc.ca/n1/pub/23-26-0003/232600032025001-eng.htm)
- [Open Government License](https://open.canada.ca/en/open-government-licence-canada)
- [Tailscale Funnel](https://tailscale.com/kb/1223/funnel)

## 📝 Challenge Requirements Checklist

✅ **HTTP/SSE Transport**: Implemented with Starlette + SSE  
✅ **No Authentication**: Public endpoint, no credentials  
✅ **Browse/Discover Tool**: `describe_dataset` provides schema  
✅ **Query Tools**: `list_agencies` and `query_data`  
✅ **Dataset Source**: Statistics Canada LODE (138 agencies)  
✅ **Schema Introspection**: Column descriptions provided  
✅ **Error Handling**: Helpful messages with suggestions  
✅ **License Attribution**: Proper attribution in all responses  
✅ **Performance**: <10s response times  
✅ **No Tracking**: No analytics or PII collection  
✅ **Reliability**: Docker restart policy, error recovery  

---

**Version**: 1.0.0  
**Last Updated**: May 2025  
**Dataset Release**: January 31, 2025 (Corrected: May 7, 2025)  
**Agencies**: 138 (confirmed from data_sources.csv)  
**File Types**: 39 different GTFS files  
**Tools**: 4 (describe_dataset, list_agencies, get_agency_files, query_data)  
**Data Access**: Universal - ALL 39 file types supported automatically  
**License**: Open Government License - Canada
