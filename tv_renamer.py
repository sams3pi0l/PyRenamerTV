#!/usr/bin/env python3
"""
TV Series File Renamer using TMDB API
Alternative to tvnamer with TheMovieDB support
"""

import os
import re
import json
import requests
from pathlib import Path
from typing import Optional, Dict, List, Tuple


class TMDBRenamer:
    """Rename TV series files using TMDB API"""
    
    def __init__(self, api_token: str, config_file: str = "mytvnamerconfig.json"):
        self.api_token = api_token
        self.base_url = "https://api.themoviedb.org/3"
        self.config = self.load_config(config_file)
        self.headers = {
            "Authorization": f"Bearer {api_token}",
            "accept": "application/json"
        }
        
    def load_config(self, config_file: str) -> Dict:
        """Load tvnamer config file"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Config file {config_file} not found, using defaults")
            return self.default_config()
    
    def default_config(self) -> Dict:
        """Default configuration"""
        return {
            "filename_with_episode": "%(seriesname)s (%(seasonnumber)dx%(episode)s) %(episodename)s%(ext)s",
            "language": "en",
            "replace_invalid_characters_with": "_",
        }
    
    def parse_filename(self, filename: str) -> Optional[Dict[str, str]]:
        """
        Parse filename to extract series name, season, episode numbers, resolution, and source
        Uses patterns from tvnamer config
        """
        patterns = self.config.get('filename_patterns', [])
        
        # Common patterns (simplified for clarity)
        common_patterns = [
            # S01E01 format
            r'(?P<seriesname>.+?)[\s._-][Ss](?P<seasonnumber>\d+)[\s._-]?[Ee](?P<episodenumber>\d+)',
            # 1x01 format
            r'(?P<seriesname>.+?)[\s._-](?P<seasonnumber>\d+)[xX](?P<episodenumber>\d+)',
            # LOST.101 format
            r'(?P<seriesname>.+?)[\s._-](?P<seasonnumber>\d)(?P<episodenumber>\d{2})',
        ]
        
        for pattern in common_patterns:
            match = re.search(pattern, filename, re.VERBOSE | re.IGNORECASE)
            if match:
                data = match.groupdict()
                # Clean series name
                data['seriesname'] = re.sub(r'[._]', ' ', data['seriesname']).strip()
                
                # Extract resolution (720p, 1080p, 2160p)
                resolution_match = re.search(r'\b(720p|1080p|2160p)\b', filename, re.IGNORECASE)
                data['resolution'] = resolution_match.group(1) if resolution_match else None
                
                # Extract source (BluRay, WEB-DL, HDTV, etc.)
                source_patterns = [
                    (r'\bWEB-DL\b', 'WEB-DL'),
                    (r'\bWEBDL\b', 'WEB-DL'),
                    (r'\bWEB\.DL\b', 'WEB-DL'),
                    (r'\bWEBRip\b', 'WEBRip'),
                    (r'\bWEB-Rip\b', 'WEBRip'),
                    (r'\bWEB\.Rip\b', 'WEBRip'),
                    (r'\bBluRay\b', 'BluRay'),
                    (r'\bBLURAY\b', 'BluRay'),
                    (r'\bBlu-Ray\b', 'BluRay'),
                    (r'\bBDRip\b', 'BDRip'),
                    (r'\bBRRip\b', 'BRRip'),
                    (r'\bHDTV\b', 'HDTV'),
                    (r'\bDVDRip\b', 'DVDRip'),
                    (r'\bDVD-Rip\b', 'DVDRip'),
                    (r'\bDVD\.Rip\b', 'DVDRip'),
                ]
                data['source'] = None
                for src_pattern, normalized_name in source_patterns:
                    source_match = re.search(src_pattern, filename, re.IGNORECASE)
                    if source_match:
                        data['source'] = normalized_name
                        break
                
                # Extract web platform (AMZN, NF, ATVP, DSNP, etc.) for WEB-DL/WEBRip
                data['platform'] = None
                if data['source'] in ['WEB-DL', 'WEBRip']:
                    # Look for platform between resolution and WEB-DL/WEBRip
                    # Pattern: (resolution).?(PLATFORM).?(WEB-DL)
                    platform_pattern = r'(?:720p|1080p|2160p)[\s._-]?([A-Z]{2,5})[\s._-]?(?:WEB-DL|WEBDL|WEB\.DL|WEBRip|WEB-Rip|WEB\.Rip)'
                    platform_match = re.search(platform_pattern, filename, re.IGNORECASE)
                    if platform_match:
                        data['platform'] = platform_match.group(1).upper()
                
                return data
        
        return None
    
    def search_series(self, series_name: str) -> Optional[int]:
        """Search for TV series on TMDB and return series ID"""
        url = f"{self.base_url}/search/tv"
        params = {
            "query": series_name,
            "language": self.config.get("language", "en")
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['results']:
                # Show search results
                print(f"\nFound {len(data['results'])} results for '{series_name}':")
                for idx, show in enumerate(data['results'][:5], 1):
                    year = show.get('first_air_date', 'N/A')[:4] if show.get('first_air_date') else 'N/A'
                    print(f"  {idx}. {show['name']} ({year}) - ID: {show['id']}")
                
                # Return first result ID (or allow user selection)
                return data['results'][0]['id']
            else:
                print(f"No results found for '{series_name}'")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"Error searching series: {e}")
            return None
    
    def get_episode_info(self, series_id: int, season: int, episode: int) -> Optional[Dict]:
        """Get episode information from TMDB"""
        url = f"{self.base_url}/tv/{series_id}/season/{season}/episode/{episode}"
        params = {
            "language": self.config.get("language", "en")
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error getting episode info: {e}")
            return None
    
    def get_series_info(self, series_id: int) -> Optional[Dict]:
        """Get TV series information from TMDB"""
        url = f"{self.base_url}/tv/{series_id}"
        params = {
            "language": self.config.get("language", "en")
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error getting series info: {e}")
            return None
    
    def sanitize_filename(self, filename: str) -> str:
        """Remove invalid characters from filename"""
        invalid_chars = r'[<>:"/\\|?*]'
        replacement = self.config.get("replace_invalid_characters_with", "_")
        return re.sub(invalid_chars, replacement, filename)
    
    def rename_jimmy_kimmel_file(self, filepath: str, dry_run: bool = True) -> bool:
        """
        Rename Jimmy Kimmel Live files
        Example: Jimmy.Kimmel.2026.04.30.Meryl.Streep.720p.WEB.h264-EDITH
        Becomes: Jimmy Kimmel Live! (2026.04.30) Meryl Streep (720p) (HDTV)
        """
        path = Path(filepath)
        filename = path.stem  # Filename without extension
        
        # Check if it starts with Jimmy.Kimmel
        if not filename.startswith("Jimmy.Kimmel"):
            return False
        
        # Pattern: Jimmy.Kimmel.YYYY.MM.DD.Guest.Name.720p.Source.codec-GROUP
        # Match date pattern YYYY.MM.DD
        date_pattern = r'Jimmy\.Kimmel\.(\d{4}\.\d{2}\.\d{2})\.(.+?)\.720p'
        match = re.search(date_pattern, filename)
        
        if not match:
            print(f"Could not parse Jimmy Kimmel filename: {filename}")
            return False
        
        date = match.group(1)  # e.g., 2026.04.30
        guest_part = match.group(2)  # e.g., Meryl.Streep
        
        # Remove dots from guest name
        guest_name = guest_part.replace('.', ' ')
        
        # Build new filename
        extension = path.suffix.lower()
        new_filename = f"Jimmy Kimmel Live! ({date}) {guest_name} (720p) (HDTV){extension}"
        new_path = path.parent / new_filename
        
        print(f"\n[Jimmy Kimmel Live - Special handling]")
        print(f"Date: {date}")
        print(f"Guest: {guest_name}")
        print(f"\nOld: {path.name}")
        print(f"New: {new_filename}")
        
        if dry_run:
            print("\n[DRY RUN - No changes made]")
            return True
        else:
            try:
                path.rename(new_path)
                print("\n✓ File renamed successfully!")
                return True
            except Exception as e:
                print(f"\n✗ Error renaming file: {e}")
                return False

    def rename_the_daily_show_file(self, filepath: str, dry_run: bool = True) -> bool:
        """
        Rename The Daily Show files
        Example: The.Daily.Show.2026.01.05.Mark.Kelly.720p.WEB.h264-EDITH
        Becomes: The Daily Show (2026.01.05) Mark Kelly (720p) (WEB-DL)
        """
        path = Path(filepath)
        filename = path.stem  # Filename without extension

        # Check if it starts with The.Daily.Show
        if not filename.startswith("The.Daily.Show"):
            return False

        # Pattern: The.Daily.Show.YYYY.MM.DD.Guest.Name.720p.Source.codec-GROUP
        date_pattern = r'The\.Daily\.Show\.(\d{4}\.\d{2}\.\d{2})\.(.+?)\.720p'
        match = re.search(date_pattern, filename)

        if not match:
            print(f"Could not parse The Daily Show filename: {filename}")
            return False

        date = match.group(1)  # e.g., 2026.01.05
        guest_part = match.group(2)  # e.g., Mark.Kelly

        # Remove dots from guest name
        guest_name = guest_part.replace('.', ' ')

        # Build new filename
        extension = path.suffix.lower()
        new_filename = f"The Daily Show ({date}) {guest_name} (720p) (WEB-DL){extension}"
        new_path = path.parent / new_filename

        print(f"\n[The Daily Show - Special handling]")
        print(f"Date: {date}")
        print(f"Guest: {guest_name}")
        print(f"\nOld: {path.name}")
        print(f"New: {new_filename}")

        if dry_run:
            print("\n[DRY RUN - No changes made]")
            return True
        else:
            try:
                path.rename(new_path)
                print("\n✓ File renamed successfully!")
                return True
            except Exception as e:
                print(f"\n✗ Error renaming file: {e}")
                return False
    
    def format_filename(self, series_name: str, season: int, episode: int, 
                       episode_name: str, extension: str, resolution: Optional[str] = None,
                       source: Optional[str] = None, platform: Optional[str] = None) -> str:
        """Format new filename using config template"""
        template = self.config.get("filename_with_episode", 
                                   "%(seriesname)s (%(seasonnumber)dx%(episode)s) %(episodename)s%(ext)s")
        
        # Use custom template if resolution and source are present
        if resolution and source and platform:
            template = "%(seriesname)s (%(seasonnumber)dx%(episode)s) %(episodename)s (%(resolution)s) (%(source)s) (%(platform)s)%(ext)s"
        elif resolution and source:
            template = "%(seriesname)s (%(seasonnumber)dx%(episode)s) %(episodename)s (%(resolution)s) (%(source)s)%(ext)s"
        elif resolution:
            template = "%(seriesname)s (%(seasonnumber)dx%(episode)s) %(episodename)s (%(resolution)s)%(ext)s"
        elif source:
            template = "%(seriesname)s (%(seasonnumber)dx%(episode)s) %(episodename)s (%(source)s)%(ext)s"
        
        # Ensure extension is lowercase
        extension = extension.lower()
        
        # Prepare replacement data
        data = {
            'seriesname': series_name,
            'seasonnumber': season,
            'episode': f"{episode:02d}",
            'episodenumber': f"{episode:02d}",
            'episodename': episode_name,
            'resolution': resolution if resolution else '',
            'source': source if source else '',
            'platform': platform if platform else '',
            'ext': extension
        }
        
        # Replace template variables
        new_name = template
        for key, value in data.items():
            new_name = new_name.replace(f"%({key})s", str(value))
            new_name = new_name.replace(f"%({key})d", str(value))
            new_name = new_name.replace(f"%({key})02d", f"{value:02d}" if isinstance(value, int) else str(value))
        
        return self.sanitize_filename(new_name)
    
    def rename_file(self, filepath: str, dry_run: bool = True) -> bool:
        """Rename a single TV series file"""
        path = Path(filepath)
        
        if not path.exists():
            print(f"Error: File not found: {filepath}")
            return False
        
        # Check if this is a Jimmy Kimmel file (special handling)
        if path.stem.startswith("Jimmy.Kimmel"):
            return self.rename_jimmy_kimmel_file(filepath, dry_run)
        
        # Check if this is a The Daily Show file (special handling)
        if path.stem.startswith("The.Daily.Show"):
            return self.rename_the_daily_show_file(filepath, dry_run)
        
        # Parse filename
        parsed = self.parse_filename(path.name)
        if not parsed:
            print(f"Could not parse filename: {path.name}")
            return False
        
        series_name = parsed['seriesname']
        season = int(parsed['seasonnumber'])
        episode = int(parsed['episodenumber'])
        extension = path.suffix
        resolution = parsed.get('resolution')
        source = parsed.get('source')
        platform = parsed.get('platform')
        
        print(f"\nParsed: {series_name} - S{season:02d}E{episode:02d}")
        if resolution:
            print(f"Resolution: {resolution}")
        if source:
            print(f"Source: {source}")
        if platform:
            print(f"Platform: {platform}")
        
        # Search for series
        series_id = self.search_series(series_name)
        if not series_id:
            return False
        
        # Get series info
        series_info = self.get_series_info(series_id)
        if not series_info:
            return False
        
        official_name = series_info['name']
        
        # Get episode info
        episode_info = self.get_episode_info(series_id, season, episode)
        if not episode_info:
            return False
        
        episode_name = episode_info['name']
        
        print(f"\nFound: {official_name} (S{season:02d}E{episode:02d})")
        print(f"Episode: {episode_name}")
        
        # Format new filename
        new_filename = self.format_filename(official_name, season, episode, 
                                           episode_name, extension, resolution, source, platform)
        new_path = path.parent / new_filename
        
        print(f"\nOld: {path.name}")
        print(f"New: {new_filename}")
        
        if dry_run:
            print("\n[DRY RUN - No changes made]")
            return True
        else:
            try:
                path.rename(new_path)
                print("\n✓ File renamed successfully!")
                return True
            except Exception as e:
                print(f"\n✗ Error renaming file: {e}")
                return False
    
    def rename_directory(self, directory: str, dry_run: bool = True, 
                        recursive: bool = False) -> List[str]:
        """Rename all TV series files in a directory"""
        path = Path(directory)
        video_extensions = ['.mkv', '.mp4', '.avi', '.srt']
        
        pattern = '**/*' if recursive else '*'
        files = [f for f in path.glob(pattern) 
                if f.is_file() and f.suffix.lower() in video_extensions]
        
        print(f"Found {len(files)} video files")
        
        results = []
        for file in files:
            print(f"\n{'='*60}")
            if self.rename_file(str(file), dry_run):
                results.append(str(file))
        
        return results


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Rename TV series files using TMDB')
    parser.add_argument('files', nargs='+', help='Files or directories to rename')
    parser.add_argument('--api-token', required=True, help='TMDB API Read Access Token')
    parser.add_argument('--config', default='mytvnamerconfig.json', 
                       help='Config file (default: mytvnamerconfig.json)')
    parser.add_argument('--dry-run', action='store_true', 
                       help='Show changes without renaming')
    parser.add_argument('--recursive', '-r', action='store_true',
                       help='Process directories recursively')
    
    args = parser.parse_args()
    
    renamer = TMDBRenamer(args.api_token, args.config)
    
    for item in args.files:
        path = Path(item)
        if path.is_dir():
            renamer.rename_directory(str(path), args.dry_run, args.recursive)
        elif path.is_file():
            renamer.rename_file(str(path), args.dry_run)
        else:
            print(f"Error: Not found: {item}")


if __name__ == "__main__":
    main()
