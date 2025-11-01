"""GTFS Data Loader - Universal Access to All Files"""
import csv
from pathlib import Path
from typing import List, Dict, Optional

class GTFSDataLoader:
    def __init__(self, data_dir: str = "/app/data/canadian_public_transit_network_database/gtfs"):
        self.data_dir = Path(data_dir)
        self.agencies_cache = {}
        self._all_folders = None
        self._agency_aliases = {}
    
    def get_all_agency_folders(self) -> List[str]:
        if self._all_folders is None:
            if not self.data_dir.exists():
                self._all_folders = []
            else:
                self._all_folders = [d.name for d in self.data_dir.iterdir() if d.is_dir()]
        return self._all_folders
    
    def _build_agency_aliases(self):
        if self._agency_aliases:
            return
        for folder in self.get_all_agency_folders():
            agency = self.load_agency_info(folder)
            self._agency_aliases[folder.lower()] = folder
            if agency:
                name = agency.get('agency_name', '').lower()
                words = name.replace('_', ' ').replace('-', ' ').split()
                if len(words) > 1:
                    acronym = ''.join(w[0] for w in words if len(w) > 2)
                    if len(acronym) >= 2:
                        self._agency_aliases[acronym] = folder
                self._agency_aliases[name] = folder
    
    def resolve_agency_id(self, agency_id: str) -> Optional[str]:
        if not agency_id:
            return None
        self._build_agency_aliases()
        if agency_id in self.get_all_agency_folders():
            return agency_id
        return self._agency_aliases.get(agency_id.lower())
    
    def get_agency_files(self, agency_id: str) -> List[str]:
        """Get list of all txt files available for an agency"""
        resolved = self.resolve_agency_id(agency_id)
        if not resolved:
            return []
        
        agency_dir = self.data_dir / resolved
        if not agency_dir.exists():
            return []
        
        txt_files = [f.name for f in agency_dir.glob("*.txt")]
        return sorted(txt_files)
    
    def load_agency_info(self, folder_name: str) -> Optional[Dict]:
        if folder_name in self.agencies_cache:
            return self.agencies_cache[folder_name]
        
        agency_file = self.data_dir / folder_name / "agency.txt"
        if not agency_file.exists():
            return None
        
        try:
            with open(agency_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                agency_data = next(reader, None)
                if agency_data:
                    agency_data['folder_name'] = folder_name
                    self.agencies_cache[folder_name] = agency_data
                    return agency_data
        except Exception as e:
            print(f"Error loading {folder_name}: {e}")
            return None
    
    def get_dataset_metadata(self) -> Dict:
        """Get dataset overview"""
        agencies = self.get_all_agency_folders()
        
        # Count files across all agencies
        all_files = set()
        for folder in agencies:
            files = self.get_agency_files(folder)
            all_files.update(files)
        
        return {
            'dataset_name': 'Canadian Public Transit Network Database',
            'source': 'Statistics Canada',
            'total_agencies': len(agencies),
            'total_file_types': len(all_files),
            'all_available_files': sorted(list(all_files)),
            'core_files': ['agency.txt', 'routes.txt', 'stops.txt', 'stop_times.txt', 'trips.txt'],
            'usage': 'Use list_agencies to find agencies, get_agency_files to see available files, then query_data to get any file'
        }
    
    def search_agencies(self, query: str = None) -> List[Dict]:
        """Search agencies"""
        results = []
        for folder in self.get_all_agency_folders():
            agency = self.load_agency_info(folder)
            if not agency:
                continue
            
            if query:
                query_lower = query.lower()
                searchable = f"{folder} {agency.get('agency_name', '')} {agency.get('agency_url', '')}".lower()
                if query_lower not in searchable:
                    continue
            
            # Add file count
            agency['available_files'] = len(self.get_agency_files(folder))
            results.append(agency)
        
        return results
    
    def get_gtfs_data(self, agency_id: str, file_name: str, limit: int = 10000) -> List[Dict]:
        """Get data from ANY txt file"""
        resolved = self.resolve_agency_id(agency_id)
        if not resolved:
            matching = self.search_agencies(agency_id)
            if matching:
                resolved = matching[0]['folder_name']
            else:
                return []
        
        # Support both "stops" and "stops.txt"
        if not file_name.endswith('.txt'):
            file_name = f"{file_name}.txt"
        
        data_file = self.data_dir / resolved / file_name
        if not data_file.exists():
            return []
        
        results = []
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for i, row in enumerate(reader):
                    if i >= limit:
                        break
                    results.append(dict(row))
        except Exception as e:
            print(f"Error reading {file_name} for {resolved}: {e}")
        
        return results
