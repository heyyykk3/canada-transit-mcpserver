# Statistics Canada Transit MCP Server

**48-Hour Challenge Submission - MCP for Statistics Canada LODE Dataset**

## 🎯 What This Is

An MCP (Model Context Protocol) server that connects ChatGPT Desktop to Statistics Canada's **Canadian Public Transit Network Database**, providing access to GTFS (General Transit Feed Specification) data for **138 transit agencies** across Canada.

## 📊 Dataset Information

- **Dataset**: Canadian Public Transit Network Database
- **Source**: Statistics Canada - Urban Data Lab
- **Release Date**: January 31, 2025
- **Correction Date**: May 7, 2025
- **URL**: https://www150.statcan.gc.ca/n1/pub/23-26-0003/232600032025001-eng.htm
- **License**: Open Government License - Canada
- **Total Agencies**: 138 (covering all Canadian provinces and territories)

## ✨ Features

- � **3 M CP Tools** for dataset exploration and querying
- 📊 **Complete GTFS Data Access** - stops, routes, trips, schedules, shapes
- 🚏 **138 Transit Agencies** across Canada
- 🗺️ **50,000+ Transit Stops** with coordinates
- 🚌 **2,000+ Routes** (bus, subway, rail, ferry)
- 🔗 **HTTP/SSE Transport** for ChatGPT Desktop
- 🔒 **No Authentication Required** (public data)
- 🐳 **Docker Deployment** on OMV/Linux servers
- 🌐 **HTTPS Access** via Tailscale Funnel

## 🚀 Quick Start

### Prerequisites
- Linux server (OMV/Debian) with Docker
- Tailscale for HTTPS access
- ChatGPT Desktop app

### Installation

**Step 1: Create project directory**
```bash
ssh root@your-server
mkdir -p /opt/statcan-transit-mcp
cd /opt/statcan-transit-mcp
```

**Step 2: Download the dataset**
```bash
mkdir -p data
cd data
wget "https://www150.statcan.gc.ca/n1/en/pub/23-26-0003/2025001/zip/canadian_public_transit_network_database.zip?st=52TbFElb" -O canadian_public_transit_network_database.zip
apt install unzip -y
unzip canadian_public_transit_network_database.zip
cd ..
```

**Step 3: Create server files**

See `TECHNICAL_REFERENCE.md` for complete file contents:
- `statcan_transit_mcp/__init__.py`
- `statcan_transit_mcp/data_loader.py`
- `statcan_transit_mcp/http_server.py`
- `pyproject.toml`
- `Dockerfile`
- `docker-compose.yml`

**Step 4: Build and run**
```bash
docker-compose build --no-cache
docker-compose up -d
```

**Step 5: Enable Tailscale Funnel**
```bash
nohup tailscale funnel 3000 &
```

Your SSE URL: `https://your-machine-name.your-tailnet.ts.net/sse`

**Step 6: Connect to ChatGPT Desktop**
1. Open ChatGPT Desktop → Settings → MCP
2. Add new server
3. URL: `https://your-machine-name.your-tailnet.ts.net/sse`
4. Authentication: None
5. Save and enable

## 🔧 Available Tools (4 Tools)

### 1. `describe_dataset`
Browse/discover tool - Get complete dataset overview.

**Example queries:**
- "Describe the Statistics Canada transit dataset"
- "What file types are available?"
- "How many different GTFS files exist?"

**Returns:**
- Dataset name, source, license
- Total agencies (138)
- Total file types (39 different GTFS files)
- List of all available file types
- Core files that all agencies have
- Usage instructions

### 2. `list_agencies`
List or search transit agencies across Canada.

**Example queries:**
- "List all transit agencies"
- "Find agencies in Montreal"
- "Show me BC Transit agencies"
- "Search for agencies in Ontario"

**Returns:**
- Agency ID (folder name for use in queries)
- Agency name
- Website URL
- Phone number
- Number of available files for each agency

### 3. `get_agency_files` (NEW!)
Discover which GTFS files are available for a specific agency.

**Example queries:**
- "What files does STM have?"
- "Show me available data for TTC"
- "List all files for Vancouver TransLink"

**Parameters:**
- `agency_id`: Agency ID from list_agencies

**Returns:**
- List of all .txt files available for that agency
- File count
- Core files vs optional files

**Why this matters:** Not all agencies have all 39 file types. Use this to discover what data exists before querying.

### 4. `query_data` (UNIVERSAL ACCESS)
Query data from ANY of the 39 GTFS file types for any agency.

**Example queries:**
- "Get all stops from Montreal STM"
- "Show me TTC routes"
- "Get transfers data for Vancouver"
- "Fetch fare_attributes for Ottawa"
- "Get timetables for GO Transit"

**Parameters:**
- `agency_id`: Agency folder name (from list_agencies)
- `file_name`: Any GTFS file (e.g., 'stops', 'routes', 'transfers.txt', 'fare_attributes')
- `limit`: Max records (default 5000, max 100000)

**Supports ALL 39 File Types:**
- **Core (all 138 agencies):** agency, routes, stops, stop_times, trips
- **Near-universal (95%+):** shapes, calendar_dates
- **Common (50%+):** feed_info, calendar
- **Optional (10-30%):** fare_attributes, transfers, fare_rules, frequencies
- **Specialized (1-5 agencies):** timetables, pathways, levels, attributions, and 25 more

**Returns:**
- Complete file data as JSON
- Record count
- Attribution
- Available files if requested file doesn't exist

## 📁 Project Structure

```
/opt/statcan-transit-mcp/
├── statcan_transit_mcp/
│   ├── __init__.py
│   ├── data_loader.py        # GTFS data access
│   └── http_server.py         # MCP server (3 tools)
├── data/
│   └── canadian_public_transit_network_database/
│       ├── gtfs/              # 138 agency folders
│       ├── data_sources.csv   # Agency metadata
│       └── stops_and_routes.gpkg  # Geospatial data
├── docker-compose.yml
├── Dockerfile
└── pyproject.toml
```

## 🎮 Usage Examples

**In ChatGPT Desktop:**

### Dataset Discovery
```
"Describe the Statistics Canada transit dataset"
→ Returns: 138 agencies, provinces, data types, schemas
```

### Agency Search
```
"Find transit agencies in Montreal"
→ Returns: STM (Société de transport de Montréal) with ID and details

"List all BC Transit agencies"
→ Returns: 30+ BC Transit regional systems
```

### Data Queries
```
"Get 10 stops from Montreal STM"
→ Returns: Stop names, coordinates, codes

"Show me all TTC subway routes"
→ Returns: Line 1 (Yonge-University), Line 2 (Bloor-Danforth), etc.

"Get stop times for route 161 in STM"
→ Returns: Arrival/departure times for each stop
```

### Complex Analysis
```
"Get all stops from STM and find ones with 'Patricia' in the name"
→ ChatGPT gets all stops, filters for 'Patricia'
→ Returns: Sherbrooke / Patricia, Poirier / Patricia with coordinates
```

## 🔍 What Data Is Available - 39 GTFS File Types!

The dataset contains **39 different GTFS file types** across 138 agencies. Here's the complete breakdown:

### Core Files (100% - All 138 Agencies Have These)
1. ✅ **agency.txt** (138) - Agency contact info, timezone, phone
2. ✅ **routes.txt** (138) - All routes with names, types, colors
3. ✅ **stops.txt** (138) - All transit stops with coordinates
4. ✅ **stop_times.txt** (138) - Arrival/departure times
5. ✅ **trips.txt** (138) - Individual trip schedules

### Near-Universal (95%+)
6. ✅ **shapes.txt** (136) - Geographic route paths for mapping
7. ✅ **calendar_dates.txt** (134) - Service exceptions (holidays)

### Common (50%+)
8. ✅ **feed_info.txt** (106) - Dataset metadata and version
9. ✅ **calendar.txt** (74) - Regular service schedules

### Optional (10-30%)
10. **fare_attributes.txt** (39) - Fare pricing information
11. **transfers.txt** (33) - Transfer rules between routes
12. **fare_rules.txt** (31) - Fare application rules
13. **frequencies.txt** (14) - Headway-based service

### Specialized (1-5 agencies)
14. **directions.txt** (5) - Direction names
15. **timetables.txt** (4) - Timetable definitions
16. **timetable_stop_order.txt** (3) - Stop order in timetables
17. **stop_attributes.txt** (3) - Additional stop metadata
18. **runcut.txt** (3) - Run cutting information
19. **location_groups.txt** (3) - Location groupings
20. **linked_datasets.txt** (3) - Dataset relationships
21. **farezone_attributes.txt** (3) - Fare zone details
22. **calendar_attributes.txt** (3) - Calendar metadata
23. **booking_rules.txt** (3) - Booking requirements
24. **areas.txt** (3) - Geographic areas
25. **stop_amentities.txt** (2) - Stop amenities
26. **__Licence.txt** (2) - License information

### Rare (1 agency each)
27-39. **trip_pattern.txt, translations.txt, timetable_pages.txt, timetable_notes.txt, timetable_notes_references.txt, stop_order_exceptions.txt, signup_periods.txt, route_names_exceptions.txt, route_directions.txt, pathways.txt, levels.txt, direction_names_exceptions.txt, attributions.txt**

**Total: 39 different file types!**

Use `get_agency_files` tool to see which files each agency has, then `query_data` to access any file.

## 🛠️ Management Commands

```bash
# View logs
docker-compose logs -f

# Restart server
docker-compose restart

# Stop server
docker-compose stop

# Check health
curl http://localhost:3000/health

# Test tools list
curl -X POST http://localhost:3000/ -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'

# Rebuild after changes
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## 🌐 Access URLs

- **Local**: `http://localhost:3000`
- **Tailscale Funnel**: `https://your-machine-name.your-tailnet.ts.net`
- **Health check**: `/health`
- **SSE endpoint**: `/sse` (for ChatGPT connection)
- **JSON-RPC**: `/` (POST)

## 📝 Real-World Example

**You ask ChatGPT**: "Find stops with 'patricia' in Montreal STM"

**ChatGPT workflow**:
1. Uses `list_agencies` with query="montreal" → gets agency_id: "societe_transport_montreal"
2. Uses `query_data` with agency_id="societe_transport_montreal", data_type="stops", limit=10000
3. Filters results for stops containing "patricia"
4. Returns:
   - **Sherbrooke / Patricia** (stop 50747) - 45.455402, -73.641252
   - **Poirier / Patricia** (stop 55917) - 45.519952, -73.696873

## � Troubleshooting

**Container won't start:**
```bash
docker-compose logs
```

**Port already in use:**
```bash
docker ps
# Stop conflicting container or change port in docker-compose.yml
```

**Tailscale Funnel not working:**
```bash
tailscale status
# Restart: nohup tailscale funnel 3000 &
```

**ChatGPT can't connect:**
- Verify Tailscale Funnel is running
- Check URL format: `https://machine-name.tailnet.ts.net/sse`
- Ensure server is enabled in ChatGPT MCP settings
- Try disconnecting and reconnecting

**Tools not showing in ChatGPT:**
- Rebuild container: `docker-compose down && docker-compose build --no-cache && docker-compose up -d`
- Completely restart ChatGPT Desktop
- Verify tools: `curl -X POST http://localhost:3000/ -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'`

## �� Dataset Statistics

- **Total Agencies**: 138 (confirmed from data_sources.csv)
- **Total File Types**: 39 different GTFS files
- **Total Stops**: ~50,000+ across all agencies
- **Total Routes**: ~2,000+ across all agencies
- **Provinces Covered**: All Canadian provinces and territories
- **Data Format**: GTFS (CSV .txt files)
- **Geospatial Format**: GeoPackage (.gpkg)
- **Dataset Size**: 424 MB (compressed zip)
- **File Coverage**: 
  - 5 core files: 100% (all 138 agencies)
  - 2 near-universal: 95%+ coverage
  - 4 common: 50%+ coverage
  - 28 specialized: 1-30% coverage

## 🎯 Challenge Requirements Met

✅ **MCP Server**: HTTP/SSE transport compatible with ChatGPT  
✅ **No Authentication**: Public endpoint, no credentials required  
✅ **Browse/Discover Tool**: `describe_dataset` provides complete schema and metadata  
✅ **Query Tools**: 4 tools (`list_agencies`, `get_agency_files`, `query_data`) return structured JSON  
✅ **Dataset Source**: Statistics Canada LODE - Canadian Public Transit Network Database (138 agencies)  
✅ **Schema Introspection**: `get_agency_files` shows available data, `describe_dataset` lists all 39 file types  
✅ **Universal Data Access**: Supports ALL 39 GTFS file types automatically  
✅ **Error Handling**: Helpful error messages with suggestions and available files list  
✅ **License Attribution**: Open Government License - Canada properly attributed in all responses  
✅ **Performance**: Queries return within 5-10 seconds  
✅ **No Tracking**: No analytics, telemetry, or PII collection  
✅ **Reliability**: Docker restart policy, graceful error handling  

## 📄 License & Attribution

**Server Code**: Open source  
**Dataset**: Open Government License - Canada  
**GTFS Specification**: Creative Commons Attribution 3.0  

**Required Citation**:
Statistics Canada. (2025). Canadian Public Transit Network Database. https://www150.statcan.gc.ca/n1/pub/23-26-0003/232600032025001-eng.htm

## 🤝 Credits

- **Dataset**: Statistics Canada - Urban Data Lab, Centre for Special Business Projects
- **Supported by**: Housing, Infrastructure and Communities Canada (HICC)
- **Data Contributors**: 138 Canadian transit agencies who provide open GTFS data

## 📧 Support

**For dataset issues**: statcan.lode-ecdo.statcan@statcan.gc.ca  
**For MCP server issues**: Check logs and TECHNICAL_REFERENCE.md  
**For ChatGPT integration**: Refer to OpenAI's MCP documentation  

---

**Version**: 1.0.0  
**Release Date**: May 2025  
**Dataset Release**: January 31, 2025 (Corrected: May 7, 2025)  
**Built for**: 48-Hour MCP Challenge  
**Agencies**: 138 across Canada  
**File Types**: 39 different GTFS files  
**Tools**: 4 (describe_dataset, list_agencies, get_agency_files, query_data)  
**Data Access**: Universal - ALL file types supported
